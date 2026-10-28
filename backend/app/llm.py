"""Thin wrapper over the multimodal LLM. Always returns a validated schema object.
If no API key is set (or the call/validation fails) the supplied fallback runs, so the app never breaks."""
import base64, json, os, re
from typing import Callable, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

try:
    import anthropic
except ImportError:  # keeps demo mode working without the SDK
    anthropic = None

T = TypeVar("T", bound=BaseModel)
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def llm_enabled() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY")) and anthropic is not None


def extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start : end + 1])


def ask_json(
    system: str,
    prompt: str,
    schema: Type[T],
    fallback: Callable[[], T],
    images: Optional[list[tuple[str, bytes]]] = None,
    max_tokens: int = 1500,
) -> T:
    if not llm_enabled():
        return fallback()
    content: list[dict] = [
        {"type": "image", "source": {"type": "base64", "media_type": mime, "data": base64.b64encode(raw).decode()}}
        for mime, raw in (images or [])
    ]
    content.append({
        "type": "text",
        "text": f"{prompt}\n\nRespond with ONLY one JSON object (no markdown) matching this JSON Schema:\n"
                f"{json.dumps(schema.model_json_schema())}",
    })
    client = anthropic.Anthropic()
    for _ in range(2):  # one retry on malformed output
        try:
            r = client.messages.create(
                model=MODEL, max_tokens=max_tokens, system=system,
                messages=[{"role": "user", "content": content}],
            )
            raw = "".join(b.text for b in r.content if b.type == "text")
            obj = schema.model_validate(extract_json(raw))
            if "source" in schema.model_fields:
                obj = obj.model_copy(update={"source": "ai"})
            return obj
        except (ValueError, ValidationError):
            continue
        except Exception:
            break
    return fallback()
