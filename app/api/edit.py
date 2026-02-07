from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.prompts import (
    SYSTEM_PROMPT_CLEANUP,
    SYSTEM_PROMPT_EDIT,
    SYSTEM_PROMPT_SEMANTIC_LABEL,
    get_cleanup_prompt,
    get_edit_prompt,
    get_semantic_label_prompt,
)
from app.core.svg_pipeline import extract_svg_hierarchy, generate_valid_svg_with_retry
from app.models.schemas import (
    CleanupRequest,
    SemanticLabelRequest,
    SemanticLabelResponse,
    SvgResponse,
)

router = APIRouter()


async def _read_reference_image(image: UploadFile) -> tuple[bytes, str]:
    allowed_mimes = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    if not image.content_type or image.content_type not in allowed_mimes:
        raise HTTPException(
            status_code=400,
            detail="Reference image must be PNG, JPG, or WEBP (SVG is not supported).",
        )
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Reference image is empty.")
    return image_bytes, image.content_type


@router.post("/edit", response_model=SvgResponse)
async def edit_svg(
    svg_code: str = Form(...),
    instruction: str = Form(...),
    selected_element_id: str | None = Form(None),
    image: UploadFile | None = File(None),
):
    """
    Edits an existing SVG based on instruction.
    Uses Gemini 3 Pro.
    """
    try:
        image_bytes = None
        image_mime = None
        if image is not None:
            image_bytes, image_mime = await _read_reference_image(image)

        prompt = get_edit_prompt(
            current_svg=svg_code,
            instructions=instruction,
            selected_id=selected_element_id,
            has_reference_image=bool(image_bytes),
        )

        svg_code = await generate_valid_svg_with_retry(
            model_name=settings.GEMINI_PRO_MODEL,
            system_instruction=SYSTEM_PROMPT_EDIT,
            prompt=prompt,
            image_bytes=image_bytes,
            image_mime=image_mime,
            retry_count=1,
            task_hint=instruction,
        )

        return SvgResponse(
            svg_code=svg_code,
            model_used=settings.GEMINI_PRO_MODEL,
            status="success",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic-label", response_model=SemanticLabelResponse)
async def semantic_label_svg(request: SemanticLabelRequest):
    try:
        prompt = get_semantic_label_prompt(request.svg_code)
        svg_code = await generate_valid_svg_with_retry(
            model_name=settings.GEMINI_PRO_MODEL,
            system_instruction=SYSTEM_PROMPT_SEMANTIC_LABEL,
            prompt=prompt,
            retry_count=1,
            task_hint="Semantic labeling and hierarchy cleanup",
        )
        hierarchy = extract_svg_hierarchy(svg_code)

        return SemanticLabelResponse(
            svg_code=svg_code,
            model_used=settings.GEMINI_PRO_MODEL,
            status="success",
            hierarchy=hierarchy,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup", response_model=SvgResponse)
async def cleanup_svg(request: CleanupRequest):
    try:
        prompt = get_cleanup_prompt(request.svg_code)
        svg_code = await generate_valid_svg_with_retry(
            model_name=settings.GEMINI_PRO_MODEL,
            system_instruction=SYSTEM_PROMPT_CLEANUP,
            prompt=prompt,
            retry_count=1,
            task_hint="Smart cleanup: simplify paths, normalize ids, reduce node count",
        )

        return SvgResponse(
            svg_code=svg_code,
            model_used=settings.GEMINI_PRO_MODEL,
            status="success",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
