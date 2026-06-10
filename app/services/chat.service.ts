import api from "@/app/lib/api";

export interface ChatSession {
  id: string;
  title: string;
  model: string;
  created_at: string;
}

export interface ChatMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
}

class ChatService {
  async createSession(
    title: string
  ) {
    const response = await api.post(
      "/api/v1/chat/session",
      {
        title,
        model: "gemini-2.5-flash",
      }
    );

    return response.data;
  }

  async getSessions() {
    const response = await api.get(
      "/api/v1/chat/sessions"
    );

    return response.data;
  }

  async getSession(
    sessionId: string
  ) {
    const response = await api.get(
      `/api/v1/chat/session/${sessionId}`
    );

    return response.data;
  }

  async sendMessage(
    sessionId: string,
    message: string
  ) {
    const response = await api.post(
      "/api/v1/chat/message",
      {
        session_id: sessionId,
        message,
      }
    );

    return response.data;
  }

  async deleteSession(
    sessionId: string
  ) {
    const response = await api.delete(
      `/api/v1/chat/session/${sessionId}`
    );

    return response.data;
  }
}

export default new ChatService();
