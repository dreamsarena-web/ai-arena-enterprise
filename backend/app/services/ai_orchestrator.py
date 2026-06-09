import httpx
import os
import asyncio


class AIOrchestrator:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.mistral_key = os.getenv("MISTRAL_API_KEY", "")

    async def call_gemini(self, prompt: str) -> dict:
        """Call Google Gemini"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"

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

                if response.status_code != 200:
                    return {
                        "model": "gemini-2.5-flash",
                        "provider": "Google",
                        "error": f"Status {response.status_code}: {data}",
                        "status": "failed"
                    }

                if "candidates" not in data:
                    return {
                        "model": "gemini-2.5-flash",
                        "provider": "Google",
                        "error": f"No candidates: {data}",
                        "status": "failed"
                    }

                text = data["candidates"][0]["content"]["parts"][0]["text"]

                return {
                    "model": "gemini-2.5-flash",
                    "provider": "Google",
                    "response": text,
                    "status": "success"
                }

        except Exception as e:
            return {
                "model": "gemini-2.5-flash",
                "provider": "Google",
                "error": str(e),
                "status": "failed"
            }

    async def call_mistral(self, prompt: str) -> dict:
        """Call Mistral AI"""
        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            model = "mistral-small-latest"

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.mistral_key}",
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

                if response.status_code != 200:
                    return {
                        "model": model,
                        "provider": "Mistral",
                        "error": f"Status {response.status_code}: {data}",
                        "status": "failed"
                    }

                if "choices" not in data:
                    return {
                        "model": model,
                        "provider": "Mistral",
                        "error": f"No choices: {data}",
                        "status": "failed"
                    }

                text = data["choices"][0]["message"]["content"]

                return {
                    "model": "mistral-small",
                    "provider": "Mistral",
                    "response": text,
                    "status": "success"
                }

        except Exception as e:
            return {
                "model": "mistral-small",
                "provider": "Mistral",
                "error": str(e),
                "status": "failed"
            }

    async def execute_battle(self, prompt: str) -> list:
        results = await asyncio.gather(
            self.call_gemini(prompt),
            self.call_mistral(prompt),
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
