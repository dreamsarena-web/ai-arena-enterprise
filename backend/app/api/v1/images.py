from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services.image_service import ImageService

router = APIRouter()


class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=500)
    style: Optional[str] = "realistic"
    width: Optional[int] = 1024
    height: Optional[int] = 1024


class ImageResponse(BaseModel):
    success: bool
    url: Optional[str] = None
    prompt: Optional[str] = None
    enhanced_prompt: Optional[str] = None
    style: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    seed: Optional[int] = None
    error: Optional[str] = None


@router.post("/generate", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    """توليد صورة باستخدام AI"""
    
    valid_styles = ["realistic", "anime", "3d", "painting", "cartoon", "cyberpunk"]
    if request.style not in valid_styles:
        raise HTTPException(status_code=400, detail=f"Style must be one of: {valid_styles}")
    
    valid_sizes = [(512, 512), (1024, 1024), (1024, 768), (768, 1024)]
    if (request.width, request.height) not in valid_sizes:
        raise HTTPException(status_code=400, detail="Invalid size")
    
    result = await ImageService.generate_image(
        prompt=request.prompt,
        style=request.style,
        width=request.width,
        height=request.height
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate image"))
    
    return result
