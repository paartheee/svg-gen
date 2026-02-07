from typing import Literal, Optional

from pydantic import BaseModel

class GenerateRequest(BaseModel):
    prompt: str
    use_case: Literal["icon", "ui-illustration", "logo", "educational-diagram"] = "icon"

class EditRequest(BaseModel):
    svg_code: str
    instruction: str
    selected_element_id: Optional[str] = None


class CleanupRequest(BaseModel):
    svg_code: str


class SemanticLabelRequest(BaseModel):
    svg_code: str


class SvgResponse(BaseModel):
    svg_code: str
    model_used: str
    status: str


class SemanticLabelResponse(SvgResponse):
    hierarchy: list[dict]
