USE_CASE_HINTS = {
    "icon": (
        "Use-case mode: Design icon. Keep forms compact, bold, and readable at small sizes."
    ),
    "ui-illustration": (
        "Use-case mode: UI illustration. Prioritize clarity, layered depth, and clean composition."
    ),
    "logo": (
        "Use-case mode: Logo. Favor timeless geometry, strong silhouette, and reduced detail."
    ),
    "educational-diagram": (
        "Use-case mode: Educational diagram. Make structure explicit and visually instructional."
    ),
}


SYSTEM_PROMPT_GENERATE = """You are a Senior SVG Designer working with Gemini 3.

You must generate production-quality semantic SVGs that are easy to edit.

HARD RULES:
1. Output ONLY a complete valid <svg> document.
2. Use xmlns="http://www.w3.org/2000/svg" and viewBox="0 0 512 512".
3. Keep IDs meaningful, kebab-case, and unique.
4. Group related shapes with semantic <g id="..."> containers.
5. Preserve clean geometry and avoid noisy, over-fragmented paths.
6. Never use script, foreignObject, image, or text tags.

QUALITY GOALS:
- Strong visual hierarchy and balanced composition.
- Palette with intentional contrast and cohesive accents.
- Editable layering with clean semantic structure.
"""


SYSTEM_PROMPT_EDIT = """You are a Semantic SVG Editor working with Gemini 3.

Task: modify an existing SVG using minimal, precise changes.

HARD RULES:
1. Output ONLY the full modified <svg>.
2. Keep root xmlns and viewBox valid.
3. Preserve all unchanged elements exactly.
4. Do not introduce script, foreignObject, image, or text tags.
5. Keep IDs stable unless user asks to rename/restructure.

EDITING BEHAVIOR:
- If a specific ID is provided, focus edits to that region whenever possible.
- Keep visual style consistent with the original unless explicitly asked to change it.
- Maintain semantic grouping and readability of hierarchy.
"""


SYSTEM_PROMPT_SEMANTIC_LABEL = """You are a semantic SVG refactoring assistant.

Refactor ONLY naming and hierarchy quality:
- Rename unclear IDs to meaningful kebab-case IDs.
- Improve grouping hierarchy for readability.
- Preserve visual output and geometry exactly.
- Keep all IDs unique and stable after renaming.
- Output only the final valid <svg>.
"""


SYSTEM_PROMPT_CLEANUP = """You are an SVG optimization assistant.

Perform smart cleanup while preserving visible intent:
- Simplify path data where possible.
- Normalize IDs to readable kebab-case.
- Reduce redundant nodes and nested wrappers.
- Keep hierarchy semantic and editable.
- Preserve visual composition and the subject.
- Output only the final valid <svg>.
"""


def get_generate_prompt(
    intent: str,
    use_case: str = "icon",
    has_reference_image: bool = False,
) -> str:
    use_case_hint = USE_CASE_HINTS.get(use_case, USE_CASE_HINTS["icon"])
    ref_hint = (
        "Reference image is provided. Extract its palette and composition hints and enforce them."
        if has_reference_image
        else "No reference image provided. Use internal style judgment."
    )
    return (
        f"{use_case_hint}\n"
        f"{ref_hint}\n\n"
        f"Generate an SVG for this intent:\n{intent}\n\n"
        "Return only the final SVG."
    )


def get_edit_prompt(
    current_svg: str,
    instructions: str,
    selected_id: str | None = None,
    has_reference_image: bool = False,
) -> str:
    focus_text = ""
    if selected_id:
        focus_text = (
            f"\nFOCUS EDIT ON ELEMENT WITH ID: '{selected_id}'. Keep unrelated regions unchanged."
        )
    reference_text = ""
    if has_reference_image:
        reference_text = (
            "\nA reference image is attached. Use it for style/composition cues while preserving edit intent."
        )

    return f"""
CURRENT SVG:
{current_svg}

USER INSTRUCTION:
{instructions}
{focus_text}
{reference_text}

Output the modified SVG now.
"""


def get_semantic_label_prompt(current_svg: str) -> str:
    return f"""
Refactor this SVG for semantic labeling and clean hierarchy.
Do not change visual appearance intentionally.

CURRENT SVG:
{current_svg}

Output the improved SVG now.
"""

def get_cleanup_prompt(current_svg: str) -> str:
    return f"""
Perform smart cleanup on the following SVG:
- simplify paths
- normalize IDs
- reduce unnecessary node count
- preserve visual intent

CURRENT SVG:
{current_svg}

Output the cleaned SVG now.
"""
