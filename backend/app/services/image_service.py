import httpx
import os
import random
import base64
import urllib.parse


class ImageService:
    """خدمة توليد الصور مع عدة مزودين"""
    
    HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
    
    STYLE_PROMPTS = {
        "realistic": "ultra realistic, 8k uhd, professional photography, highly detailed, sharp focus",
        "anime": "anime style, manga art, vibrant colors, studio ghibli inspired",
        "3d": "3d render, octane render, cinematic lighting, unreal engine 5",
        "painting": "oil painting, classical art style, detailed brushstrokes, masterpiece",
        "cartoon": "cartoon style, disney pixar animation, colorful, vibrant",
        "cyberpunk": "cyberpunk style, neon lights, futuristic city, dark atmosphere",
    }
    
    @staticmethod
    async def try_pollinations(
        prompt: str,
        width: int,
        height: int,
        seed: int
    ) -> dict:
        """محاولة 1: Pollinations AI (مجاني بدون مفتاح)"""
        try:
            encoded_prompt = urllib.parse.quote(prompt)
            # بدون نموذج flux (لأنه صار مدفوع)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true"
            
            async with httpx.AsyncClient(timeout=90, follow_redirects=True) as client:
                response = await client.get(image_url)
                
                if response.status_code == 200 and len(response.content) > 1000:
                    return {
                        "success": True,
                        "url": image_url,
                        "provider": "Pollinations",
                    }
                else:
                    return {"success": False, "error": f"Pollinations status: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": f"Pollinations error: {str(e)}"}
    
    @staticmethod
    async def try_huggingface(
        prompt: str,
        width: int,
        height: int,
        seed: int
    ) -> dict:
        """محاولة 2: Hugging Face"""
        
        if not ImageService.HF_TOKEN:
            return {"success": False, "error": "HF_TOKEN not configured"}
        
        model = "stabilityai/stable-diffusion-xl-base-1.0"
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
                "num_inference_steps": 25,
                "guidance_scale": 7.5,
                "seed": seed,
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    image_bytes = response.content
                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    image_url = f"data:image/png;base64,{image_base64}"
                    
                    return {
                        "success": True,
                        "url": image_url,
                        "provider": "Hugging Face",
                    }
                elif response.status_code == 503:
                    return {
                        "success": False,
                        "error": "النموذج بيتم تحضيره، انتظر 30 ثانية وحاول مرة أخرى"
                    }
                else:
                    return {"success": False, "error": f"HF status: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": f"HF error: {str(e)}"}
    
    @staticmethod
    async def generate_image(
        prompt: str,
        style: str = "realistic",
        width: int = 1024,
        height: int = 1024
    ) -> dict:
        """توليد صورة مع تجربة عدة مزودين"""
        
        style_prompt = ImageService.STYLE_PROMPTS.get(style, ImageService.STYLE_PROMPTS["realistic"])
        enhanced_prompt = f"{prompt}, {style_prompt}, high quality, masterpiece"
        seed = random.randint(1, 1000000)
        
        # المحاولة 1: Pollinations (الأسرع والأسهل)
        result = await ImageService.try_pollinations(enhanced_prompt, width, height, seed)
        
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
        
        # المحاولة 2: Hugging Face (لو فشل Pollinations)
        result = await ImageService.try_huggingface(enhanced_prompt, width, height, seed)
        
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
        
        # كل المزودين فشلوا
        return {
            "success": False,
            "error": "جميع مزودي الصور غير متاحين حالياً، حاول بعد قليل"
        }
