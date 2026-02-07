import google.genai as genai
from app.core.config import settings
from google.genai import types
# Configure global API key
if settings.GEMINI_API_KEY:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    # genai.configure(api_key=settings.GEMINI_API_KEY)

async def call_gemini(
    model_name: str,
    system_instruction: str,
    prompt: str,
    image_bytes: bytes | None = None,
    image_mime: str | None = None,
) -> str:
    """
    Wrapper for Gemini API calls.
    """
    try:
        if image_bytes:
            contents = [
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=image_mime or "image/png",
                ),
            ]
        else:
            contents = prompt
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=types.ThinkingConfig(thinking_level="low"),
                temperature=0.1, 
                top_p=0.95,
                top_k=40,
            )
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini {model_name}: {e}")
        # In a real app, we'd raise a proper HTTP exception or custom error
        raise e
