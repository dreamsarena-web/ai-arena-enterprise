"use client";

import { useEffect, useState } from "react";
import { Send, Trash2 } from "lucide-react";
import chatService from "@/app/services/chat.service";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Session {
  id: string;
  title: string;
  created_at: string;
}

export default function ChatPage() {
  const [sessions, setSessions] =
    useState<Session[]>([]);

  const [sessionId, setSessionId] =
    useState<string>("");

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [prompt, setPrompt] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  async function loadSessions() {
    try {
      const data =
        await chatService.getSessions();

      setSessions(data);
    } catch (error) {
      console.error(error);
    }
  }

  async function createSession() {
    const title =
      prompt.slice(0, 40) || "New Chat";

    const session =
      await chatService.createSession(
        title
      );

    setSessionId(session.id);

    await loadSessions();

    return session.id;
  }

  async function loadSession(
    id: string
  ) {
    const data =
      await chatService.getSession(id);

    setSessionId(id);

    setMessages(
      data.messages.map((m: any) => ({
        role: m.role,
        content: m.content,
      }))
    );
  }

  async function sendMessage() {
    if (!prompt.trim()) return;

    setLoading(true);

    try {
      let currentSession =
        sessionId;

      if (!currentSession) {
        currentSession =
          await createSession();
      }

      const userMessage = prompt;

      setMessages((prev) => [
        ...prev,
        {
          role: "user",
          content: userMessage,
        },
      ]);

      setPrompt("");

      const result =
        await chatService.sendMessage(
          currentSession,
          userMessage
        );

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.response,
        },
      ]);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  async function deleteSession(
    id: string
  ) {
    await chatService.deleteSession(
      id
    );

    if (id === sessionId) {
      setSessionId("");
      setMessages([]);
    }

    loadSessions();
  }

  return (
    <div className="flex h-screen">
      <aside className="w-72 border-r p-4 overflow-y-auto">
        <h2 className="font-bold mb-4">
          Saved Chats
        </h2>

        {sessions.map((session) => (
          <div
            key={session.id}
            className="border rounded p-2 mb-2"
          >
            <button
              onClick={() =>
                loadSession(
                  session.id
                )
              }
              className="w-full text-left"
            >
              {session.title}
            </button>

            <button
              onClick={() =>
                deleteSession(
                  session.id
                )
              }
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </aside>

      <main className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6">
          {messages.map(
            (message, index) => (
              <div
                key={index}
                className="mb-4"
              >
                <strong>
                  {message.role}
                </strong>

                <p>
                  {message.content}
                </p>
              </div>
            )
          )}
        </div>

        <div className="p-4 border-t flex gap-2">
          <input
            value={prompt}
            onChange={(e) =>
              setPrompt(
                e.target.value
              )
            }
            className="flex-1 border rounded px-3 py-2"
            placeholder="Type a message..."
          />

          <button
            onClick={sendMessage}
            disabled={loading}
            className="px-4 py-2 border rounded"
          >
            <Send size={18} />
          </button>
        </div>
      </main>
    </div>
  );
}
