import httpx
import os


class AIOrchestrator:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

    async def call_gemini(self, prompt: str) -> dict:
        """Call Google Gemini"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}"

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    url,
                    json={
                        "contents": [
                            {"parts": [{"text": prompt}]}
                        ]
                    }
                )

                data = response.json()

                text = data["candidates"][0]["content"]["parts"][0]["text"]

                return {
                    "model": "gemini-2.0-flash",
                    "provider": "Google",
                    "response": text,
                    "status": "success"
                }

        except Exception as e:
            return {
                "model": "gemini-2.0-flash",
                "provider": "Google",
                "error": str(e),
                "status": "failed"
            }

    async def call_openrouter(self, prompt: str, model: str = "meta-llama/llama-3.3-70b-instruct:free") -> dict:
        """Call OpenRouter (Llama, Mistral, etc.)"""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                )

                data = response.json()

                text = data["choices"][0]["message"]["content"]

                return {
                    "model": model.split("/")[-1],
                    "provider": "OpenRouter",
                    "response": text,
                    "status": "success"
                }

        except Exception as e:
            return {
                "model": model,
                "provider": "OpenRouter",
                "error": str(e),
                "status": "failed"
            }

    async def execute_battle(self, prompt: str) -> list:
        """Execute battle between 2 models"""
        import asyncio

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
