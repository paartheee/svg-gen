from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.schemas import SvgResponse
from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT_GENERATE
from app.core.gemini_client import call_gemini
from app.core.svg_guard import clean_svg_code, validate_svg

router = APIRouter()

@router.post("/generate", response_model=SvgResponse)
async def generate_svg(
    prompt: str = Form(...),
    image: UploadFile | None = File(None),
):
    """
    Generates a new SVG based on natural language prompt.
    Optionally accepts a reference image to guide generation.
    """
    try:
        image_bytes = None
        image_mime = None
        if image is not None:
            allowed_mimes = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
            if not image.content_type or image.content_type not in allowed_mimes:
                raise HTTPException(
                    status_code=400,
                    detail="Reference image must be PNG, JPG, or WEBP (SVG is not supported).",
                )
            image_bytes = await image.read()
            if not image_bytes:
                raise HTTPException(status_code=400, detail="Reference image is empty.")
            image_mime = image.content_type

        prompt_text = f"Generate an SVG for this intent: {prompt}"
        if image_bytes:
            prompt_text = (
                "Use the provided image as a visual reference for layout, shapes, and overall style. "
                + prompt_text
            )

        # 1. Call LLM
        raw_response = await call_gemini(
            model_name=settings.GEMINI_FLASH_MODEL,
            system_instruction=SYSTEM_PROMPT_GENERATE,
            prompt=prompt_text,
            image_bytes=image_bytes,
            image_mime=image_mime,
        )
        
        # 2. Extract SVG
        svg_code = clean_svg_code(raw_response)
        
        # 3. Validate
        is_valid, message = validate_svg(svg_code)
        if not is_valid:
            # In a real app, we might retry or return an error. 
            # For now, we return it but mark status? Or just error.
            # Let's error to be safe as per "SVG INVARIANTS (MUST ALWAYS HOLD)"
            raise HTTPException(status_code=422, detail=f"Generated SVG invalid: {message}")

        return SvgResponse(
            svg_code=svg_code,
            model_used=settings.GEMINI_FLASH_MODEL,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
