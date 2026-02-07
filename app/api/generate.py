from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.schemas import SvgResponse
from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT_GENERATE, USE_CASE_HINTS, get_generate_prompt
from app.core.svg_pipeline import generate_valid_svg_with_retry

router = APIRouter()
VALID_USE_CASES = set(USE_CASE_HINTS.keys())

@router.post("/generate", response_model=SvgResponse)
async def generate_svg(
    prompt: str = Form(...),
    use_case: str = Form("icon"),
    image: UploadFile | None = File(None),
):
    """
    Generates a new SVG based on natural language prompt.
    Optionally accepts a reference image to guide generation.
    """
    try:
        if use_case not in VALID_USE_CASES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid use_case. Must be one of: {', '.join(sorted(VALID_USE_CASES))}",
            )

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

        prompt_text = get_generate_prompt(
            intent=prompt,
            use_case=use_case,
            has_reference_image=bool(image_bytes),
        )

        svg_code = await generate_valid_svg_with_retry(
            model_name=settings.GEMINI_PRO_MODEL,
            system_instruction=SYSTEM_PROMPT_GENERATE,
            prompt=prompt_text,
            image_bytes=image_bytes,
            image_mime=image_mime,
            retry_count=1,
            task_hint=f"Use-case: {use_case}. Intent: {prompt}",
        )

        return SvgResponse(
            svg_code=svg_code,
            model_used=settings.GEMINI_PRO_MODEL,
            status="success"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
