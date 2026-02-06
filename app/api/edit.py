from fastapi import APIRouter, HTTPException
from app.models.schemas import EditRequest, SvgResponse
from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT_EDIT, get_edit_prompt
from app.core.gemini_client import call_gemini
from app.core.svg_guard import clean_svg_code, validate_svg

router = APIRouter()

@router.post("/edit", response_model=SvgResponse)
async def edit_svg(request: EditRequest):
    """
    Edits an existing SVG based on instruction.
    Uses Gemini 3 Pro.
    """
    try:
        # 1. Construct Prompt
        prompt = get_edit_prompt(
            current_svg=request.svg_code, 
            instructions=request.instruction,
            selected_id=request.selected_element_id
        )
        
        # 2. Call LLM
        raw_response = await call_gemini(
            model_name=settings.GEMINI_PRO_MODEL,
            system_instruction=SYSTEM_PROMPT_EDIT,
            prompt=prompt
        )
        
        # 3. Extract SVG
        svg_code = clean_svg_code(raw_response)
        
        # 4. Validate
        is_valid, message = validate_svg(svg_code)
        if not is_valid:
            raise HTTPException(status_code=422, detail=f"Edited SVG invalid: {message}")

        return SvgResponse(
            svg_code=svg_code,
            model_used=settings.GEMINI_PRO_MODEL,
            status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
