import xml.etree.ElementTree as ET
from fastapi import HTTPException

from app.core.gemini_client import call_gemini
from app.core.svg_guard import clean_svg_code, validate_svg


def _get_local_tag_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def build_svg_correction_prompt(
    invalid_svg: str,
    validation_message: str,
    task_hint: str = "",
) -> str:
    hint_text = f"\nOriginal task context:\n{task_hint}\n" if task_hint else "\n"
    return (
        "The SVG below is invalid and must be corrected immediately.\n"
        f"Validation failure: {validation_message}\n"
        f"{hint_text}"
        "Return ONLY the complete corrected <svg>.\n"
        "Do not explain anything.\n\n"
        "INVALID SVG:\n"
        f"{invalid_svg}"
    )


async def generate_valid_svg_with_retry(
    *,
    model_name: str,
    system_instruction: str,
    prompt: str,
    image_bytes: bytes | None = None,
    image_mime: str | None = None,
    retry_count: int = 1,
    task_hint: str = "",
) -> str:
    raw_response = await call_gemini(
        model_name=model_name,
        system_instruction=system_instruction,
        prompt=prompt,
        image_bytes=image_bytes,
        image_mime=image_mime,
    )
    svg_code = clean_svg_code(raw_response)
    is_valid, message = validate_svg(svg_code)

    attempts = 0
    while not is_valid and attempts < retry_count:
        correction_prompt = build_svg_correction_prompt(
            invalid_svg=svg_code,
            validation_message=message,
            task_hint=task_hint or prompt,
        )
        raw_response = await call_gemini(
            model_name=model_name,
            system_instruction=system_instruction,
            prompt=correction_prompt,
        )
        svg_code = clean_svg_code(raw_response)
        is_valid, message = validate_svg(svg_code)
        attempts += 1

    if not is_valid:
        raise HTTPException(status_code=422, detail=f"Generated SVG invalid: {message}")

    return svg_code


def extract_svg_hierarchy(svg_code: str) -> list[dict]:
    root = ET.fromstring(svg_code)

    def walk(element: ET.Element) -> list[dict]:
        nodes: list[dict] = []
        for child in list(element):
            node_id = child.attrib.get("id")
            child_nodes = walk(child)
            if not node_id:
                nodes.extend(child_nodes)
                continue
            nodes.append(
                {
                    "id": node_id,
                    "tag": _get_local_tag_name(child.tag),
                    "children": child_nodes,
                }
            )
        return nodes

    return walk(root)
