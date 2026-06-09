import httpx
import os
import random
import base64
from io import BytesIO


class ImageService:
    """خدمة توليد الصور الاحترافية باستخدام Hugging Face"""
    
    HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # نماذج Hugging Face المجانية والقوية
    MODELS = {
        "default": "stabilityai/stable-diffusion-xl-base-1.0",
        "realistic": "stabilityai/stable-diffusion-xl-base-1.0",
        "anime": "cagliostrolab/animagine-xl-3.1",
        "3d": "stabilityai/stable-diffusion-xl-base-1.0",
        "painting": "stabilityai/stable-diffusion-xl-base-1.0",
        "cartoon": "stabilityai/stable-diffusion-xl-base-1.0",
        "cyberpunk": "stabilityai/stable-diffusion-xl-base-1.0",
    }
    
    STYLE_PROMPTS = {
        "realistic": "ultra realistic, 8k uhd, professional photography, highly detailed, sharp focus, photorealistic",
        "anime": "anime style, manga art, vibrant colors, studio ghibli inspired, beautiful",
        "3d": "3d render, octane render, cinematic lighting, unreal engine 5, highly detailed",
        "painting": "oil painting, classical art style, detailed brushstrokes, masterpiece, museum quality",
        "cartoon": "cartoon style, disney pixar animation, colorful, family friendly, vibrant",
        "cyberpunk": "cyberpunk style, neon lights, futuristic city, blade runner aesthetic, dark atmosphere",
    }
    
    @staticmethod
    async def generate_with_huggingface(
        prompt: str,
        model: str,
        width: int = 1024,
        height: int = 1024,
        seed: int = None
    ) -> dict:
        """توليد صورة باستخدام Hugging Face"""
        
        if not ImageService.HF_TOKEN:
            return {
                "success": False,
                "error": "HUGGINGFACE_TOKEN not configured"
            }
        
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        headers = {
            "Authorization": f"Bearer {ImageService.HF_TOKEN}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
            }
        }
        
        if seed:
            payload["parameters"]["seed"] = seed
        
        try:
            async with httpx.AsyncClient(timeout=180) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    # Hugging Face يرجع الصورة كـ bytes
                    image_bytes = response.content
                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    image_url = f"data:image/png;base64,{image_base64}"
                    
                    return {
                        "success": True,
                        "url": image_url,
                        "provider": "Hugging Face",
                        "model": model,
                    }
                
                elif response.status_code == 503:
                    # النموذج بيتم تحميله
                    error_data = response.json()
                    estimated_time = error_data.get("estimated_time", 20)
                    
                    return {
                        "success": False,
                        "error": f"النموذج بيتم تحضيره، انتظر {int(estimated_time)} ثانية وحاول مرة أخرى",
                        "retry_after": estimated_time,
                    }
                
                elif response.status_code == 429:
                    return {
                        "success": False,
                        "error": "تم تجاوز الحد المسموح، انتظر دقيقة وحاول مرة أخرى",
                    }
                
                else:
                    error_text = response.text[:200]
                    return {
                        "success": False,
                        "error": f"Status {response.status_code}: {error_text}",
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "الطلب استغرق وقت طويل، حاول مرة أخرى",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}",
            }
    
    @staticmethod
    async def generate_image(
        prompt: str,
        style: str = "realistic",
        width: int = 1024,
        height: int = 1024
    ) -> dict:
        """توليد صورة مع تحسين الـ prompt"""
        
        style_prompt = ImageService.STYLE_PROMPTS.get(style, ImageService.STYLE_PROMPTS["realistic"])
        enhanced_prompt = f"{prompt}, {style_prompt}, high quality, masterpiece, best quality"
        
        model = ImageService.MODELS.get(style, ImageService.MODELS["default"])
        seed = random.randint(1, 1000000)
        
        result = await ImageService.generate_with_huggingface(
            prompt=enhanced_prompt,
            model=model,
            width=width,
            height=height,
            seed=seed
        )
        
        if result["success"]:
            result.update({
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "style": style,
                "width": width,
                "height": height,
                "seed": seed,
            })
        
        return result
