from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str

class EditRequest(BaseModel):
    svg_code: str
    instruction: str
    selected_element_id: Optional[str] = None

class SvgResponse(BaseModel):
    svg_code: str
    model_used: str
    status: str
