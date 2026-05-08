"use client";

import { useState } from "react";
import SourceCitation from "./SourceCitation";
import RetrievalTrace from "./RetrievalTrace";
import RefusalMessage from "./RefusalMessage";
import { apiClient } from "@/lib/api";
import type { QueryResponse, SourceCitation as SourceCitationType } from "@/types";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources: SourceCitationType[];
  refused: boolean;
  refusalReason?: string;
  confidence?: number;
  retrievalTrace?: QueryResponse["retrieval_trace"];
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [showTrace, setShowTrace] = useState<Record<string, boolean>>({});

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question, sources: [], refused: false }]);
    setLoading(true);

    try {
      const response = await apiClient.askQuestion({ question });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer || "",
          sources: response.sources,
          refused: response.refused,
          confidence: response.confidence ?? undefined,
          retrievalTrace: response.retrieval_trace ?? undefined,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: err instanceof Error ? err.message : "An error occurred",
          sources: [],
          refused: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleTrace = (messageIndex: number): void => {
    setShowTrace((prev) => ({
      ...prev,
      [String(messageIndex)]: !prev[String(messageIndex)],
    }));
  };

  return (
    <div className="flex flex-col">
      <div className="mb-4 max-h-[60vh] space-y-4 overflow-y-auto">
        {messages.length === 0 && (
          <div className="py-12 text-center text-gray-500">
            Ask a question about your uploaded documents.
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`rounded-lg p-4 ${
              msg.role === "user" ? "bg-brand-50 ml-12" : "bg-white border border-gray-200 mr-12"
            }`}
          >
            <p className="whitespace-pre-wrap text-sm text-gray-800">{msg.content}</p>

            {msg.refused && msg.role === "assistant" && (
              <RefusalMessage
                reason={msg.content}
                confidence={msg.confidence}
                suggestion="Try rephrasing your question or uploading more relevant documents."
              />
            )}

            {msg.sources.length > 0 && (
              <div className="mt-3 space-y-2">
                <p className="text-xs font-medium text-gray-500">Sources:</p>
                {msg.sources.map((source) => (
                  <SourceCitation key={source.chunk_id} citation={source} />
                ))}
              </div>
            )}

            {msg.retrievalTrace && msg.role === "assistant" && (
              <div className="mt-3">
                <button
                  onClick={() => toggleTrace(idx)}
                  className="text-xs text-brand-600 hover:underline"
                >
                  {showTrace[String(idx)] ? "Hide" : "Show"} Retrieval Trace
                </button>
                {showTrace[String(idx)] && (
                  <RetrievalTrace trace={msg.retrievalTrace} />
                )}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="py-4 text-center text-sm text-gray-500">Thinking...</div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your documents..."
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
