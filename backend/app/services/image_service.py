import httpx
import os
import random
import base64
import urllib.parse


class ImageService:
    """خدمة توليد الصور المحسّنة"""
    
    HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
    
    STYLE_PROMPTS = {
        "realistic": "ultra realistic, 8k, professional photography, highly detailed",
        "anime": "anime style, manga art, vibrant colors, beautiful",
        "3d": "3d render, octane render, cinematic, detailed",
        "painting": "oil painting, classical art, detailed brushstrokes",
        "cartoon": "cartoon style, disney pixar, colorful, vibrant",
        "cyberpunk": "cyberpunk, neon lights, futuristic, dark",
    }
    
    @staticmethod
    async def generate_image(
        prompt: str,
        style: str = "realistic",
        width: int = 1024,
        height: int = 1024
    ) -> dict:
        """توليد صورة باستخدام Pollinations (يرجع URL مباشر)"""
        
        style_prompt = ImageService.STYLE_PROMPTS.get(style, "")
        enhanced_prompt = f"{prompt}, {style_prompt}, high quality, masterpiece"
        seed = random.randint(1, 1000000)
        
        # نبني URL لـ Pollinations
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true"
        
        # نرجع الـ URL مباشرة بدون اختبار (المتصفح راح يحمّلها)
        return {
            "success": True,
            "url": image_url,
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "style": style,
            "width": width,
            "height": height,
            "seed": seed,
            "provider": "Pollinations",
        }
