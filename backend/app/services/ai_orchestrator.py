import httpx
import os
import asyncio


class AIOrchestrator:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

    async def call_gemini(self, prompt: str) -> dict:
        """Call Google Gemini"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {
                                "parts": [{"text": prompt}]
                            }
                        ]
                    }
                )

                data = response.json()

                # طباعة الـ response الكامل في حالة الخطأ
                if response.status_code != 200:
                    return {
                        "model": "gemini-1.5-flash",
                        "provider": "Google",
                        "error": f"Status {response.status_code}: {data}",
                        "status": "failed"
                    }

                if "candidates" not in data:
                    return {
                        "model": "gemini-1.5-flash",
                        "provider": "Google",
                        "error": f"No candidates in response: {data}",
                        "status": "failed"
                    }

                text = data["candidates"][0]["content"]["parts"][0]["text"]

                return {
                    "model": "gemini-1.5-flash",
                    "provider": "Google",
                    "response": text,
                    "status": "success"
                }

        except Exception as e:
            return {
                "model": "gemini-1.5-flash",
                "provider": "Google",
                "error": str(e),
                "status": "failed"
            }

    async def call_openrouter(self, prompt: str) -> dict:
        """Call OpenRouter (Llama)"""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            model = "meta-llama/llama-3.2-3b-instruct:free"

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ai-arena.com",
                        "X-Title": "AI Arena"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                )

                data = response.json()

                if response.status_code != 200:
                    return {
                        "model": model,
                        "provider": "OpenRouter",
                        "error": f"Status {response.status_code}: {data}",
                        "status": "failed"
                    }

                if "choices" not in data:
                    return {
                        "model": model,
                        "provider": "OpenRouter",
                        "error": f"No choices in response: {data}",
                        "status": "failed"
                    }

                text = data["choices"][0]["message"]["content"]

                return {
                    "model": "llama-3.2-3b",
                    "provider": "OpenRouter",
                    "response": text,
                    "status": "success"
                }

        except Exception as e:
            return {
                "model": "llama-3.2-3b",
                "provider": "OpenRouter",
                "error": str(e),
                "status": "failed"
            }

    async def execute_battle(self, prompt: str) -> list:
        """Execute battle between 2 models"""
        results = await asyncio.gather(
            self.call_gemini(prompt),
            self.call_openrouter(prompt),
            return_exceptions=True
        )

        final_results = []
        for result in results:
            if isinstance(result, Exception):
                final_results.append({
                    "model": "unknown",
                    "error": str(result),
                    "status": "failed"
                })
            else:
                final_results.append(result)

        return final_results
