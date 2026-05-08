import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.query import Query, QueryListResponse, QueryListItem, QueryRequest, QueryResponse
from app.services.retrieval import retrieval_service
from app.services.reranking import reranking_service
from app.services.generation import generation_service
from app.services.citation import citation_service
from app.services.refusal import refusal_service
from app.config import get_settings

router = APIRouter(tags=["queries"])
settings = get_settings()


@router.post("/queries", response_model=QueryResponse)
async def create_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """Process a question through the full retrieval-augmented generation pipeline.

    Retrieves relevant chunks, checks for refusal, generates an answer with
    citations, and records the full retrieval trace.
    """
    top_k = request.top_k or settings.RETRIEVAL_TOP_K

    chunks = await retrieval_service.retrieve(query=request.question, top_k=top_k, db=db)
    reranked = await reranking_service.rerank(query=request.question, chunks=chunks)

    should_refuse, refusal_reason = refusal_service.should_refuse(
        query=request.question,
        chunks=reranked,
        confidence=sum(c.relevance_score for c in reranked) / max(len(reranked), 1),
    )

    if should_refuse:
        query_record = Query(
            question=request.question,
            answer=None,
            refused=True,
            confidence=sum(c.relevance_score for c in reranked) / max(len(reranked), 1),
        )
        db.add(query_record)
        await db.commit()
        await db.refresh(query_record)

        return QueryResponse(
            id=query_record.id,
            question=request.question,
            answer=None,
            sources=[],
            retrieval_trace=None,
            refused=True,
            confidence=query_record.confidence,
            token_usage=None,
            created_at=query_record.created_at,
        )

    answer, token_usage = await generation_service.generate_answer(
        query=request.question,
        context=[chunk.content for chunk in reranked],
        sources=[],
    )

    citations = citation_service.assemble_citations(chunks=reranked, answer=answer)

    confidence = sum(c.relevance_score for c in reranked) / max(len(reranked), 1)

    query_record = Query(
        question=request.question,
        answer=answer,
        sources=[c.model_dump() for c in citations],
        refused=False,
        confidence=confidence,
        token_usage=token_usage,
    )
    db.add(query_record)
    await db.commit()
    await db.refresh(query_record)

    return QueryResponse(
        id=query_record.id,
        question=request.question,
        answer=answer,
        sources=citations,
        retrieval_trace=None,
        refused=False,
        confidence=confidence,
        token_usage=token_usage,
        created_at=query_record.created_at,
    )


@router.get("/queries", response_model=QueryListResponse)
async def list_queries(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> QueryListResponse:
    """List query history with pagination."""
    count_result = await db.execute(select(func.count()).select_from(Query))
    total: int = count_result.scalar() or 0

    result = await db.execute(
        select(Query).order_by(Query.created_at.desc()).offset(offset).limit(limit)
    )
    queries = list(result.scalars().all())

    return QueryListResponse(
        queries=[QueryListItem.model_validate(q) for q in queries],
        total=total,
    )


@router.get("/queries/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """Retrieve full query details including sources and retrieval trace."""
    result = await db.execute(select(Query).where(Query.id == query_id))
    query_record = result.scalar_one_or_none()

    if query_record is None:
        raise HTTPException(status_code=404, detail="Query not found")

    return QueryResponse.model_validate(query_record)
