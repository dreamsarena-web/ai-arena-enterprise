import httpx
import urllib.parse


class ImageService:
    """خدمة توليد الصور باستخدام Pollinations AI"""
    
    BASE_URL = "https://image.pollinations.ai/prompt"
    
    @staticmethod
    def build_url(
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        seed: int = None,
        model: str = "flux"
    ) -> str:
        """بناء URL لتوليد الصورة"""
        import random
        
        if seed is None:
            seed = random.randint(1, 1000000)
        
        encoded_prompt = urllib.parse.quote(prompt)
        
        params = {
            "width": width,
            "height": height,
            "seed": seed,
            "nologo": "true",
            "enhance": "true",
            "model": model,
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        
        return f"{ImageService.BASE_URL}/{encoded_prompt}?{query_string}"
    
    @staticmethod
    async def generate_image(
        prompt: str,
        style: str = "realistic",
        width: int = 1024,
        height: int = 1024
    ) -> dict:
        """توليد صورة وإرجاع الـ URL"""
        
        style_prompts = {
            "realistic": "ultra realistic, 8k uhd, professional photography, highly detailed",
            "anime": "anime style, manga art, vibrant colors, studio ghibli",
            "3d": "3d render, octane render, cinematic lighting, unreal engine 5",
            "painting": "oil painting, classical art style, detailed brushstrokes",
            "cartoon": "cartoon style, disney pixar animation, colorful",
            "cyberpunk": "cyberpunk style, neon lights, futuristic city",
        }
        
        enhanced_prompt = f"{prompt}, {style_prompts.get(style, '')}, high quality, masterpiece"
        
        import random
        seed = random.randint(1, 1000000)
        
        image_url = ImageService.build_url(
            prompt=enhanced_prompt,
            width=width,
            height=height,
            seed=seed
        )
        
        # نتحقق إن الصورة تتولد بنجاح
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.get(image_url)
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "url": image_url,
                        "prompt": prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "style": style,
                        "width": width,
                        "height": height,
                        "seed": seed,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Status {response.status_code}",
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Timeout - الصورة استغرقت وقت طويل",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
