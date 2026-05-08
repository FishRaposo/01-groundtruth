import ChatInterface from "@/components/ChatInterface";

export default function ChatPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900">Ask a Question</h1>
      <ChatInterface />
    </div>
  );
}
