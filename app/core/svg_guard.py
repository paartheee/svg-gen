import re
import xml.etree.ElementTree as ET

def clean_svg_code(raw_response: str) -> str:
    """Extracts SVG code from markdown code blocks or raw text."""
    # Remove markdown code fences
    svg_match = re.search(r'```svg\s*(.*?)\s*```', raw_response, re.DOTALL)
    if svg_match:
        return svg_match.group(1).strip()
    
    # Or just look for the svg tags
    svg_match = re.search(r'(<svg.*?</svg>)', raw_response, re.DOTALL)
    if svg_match:
        return svg_match.group(1).strip()
        
    return raw_response.strip()

def validate_svg(svg_content: str) -> tuple[bool, str]:
    """
    Validates SVG against strict invariants:
    1. Valid XML
    2. No dangerous/unsupported tags (script, foreignObject, image, text)
    3. Gradients (linearGradient, radialGradient, stop, defs) are now ALLOWED for high-quality rendering
    """
    try:
        # 1. Valid XML
        root = ET.fromstring(svg_content)
    except ET.ParseError as e:
        return False, f"Invalid XML: {str(e)}"

    # 2. Check dimensions (optional enforcement, but good to check)
    # width = root.get("width")
    # height = root.get("height")
    # if width != "512" or height != "512":
    #     return False, f"Invalid dimensions: {width}x{height}. Must be 512x512."

    # 3. Disallowed tags (removed gradients and filters to allow high-quality SVGs)
    forbidden_tags = {'script', 'foreignObject', 'image', 'text'}
    for elem in root.iter():
        tag = elem.tag
        # remove namespace if present for checking
        if '}' in tag:
            tag = tag.split('}', 1)[1]
            
        if tag in forbidden_tags:
            return False, f"Forbidden tag found: <{tag}>"

    return True, "Valid SVG"
