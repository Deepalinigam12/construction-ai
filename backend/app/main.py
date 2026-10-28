import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import demo, planning, weather
from .llm import ask_json, llm_enabled, MODEL
from .schemas import *

app = FastAPI(title="Multimodal Construction Intelligence Platform", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"], allow_headers=["*"],
)

MAX_IMG = 8 * 1024 * 1024
OK_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


async def read_image(f: UploadFile) -> tuple[str, bytes]:
    if f.content_type not in OK_TYPES:
        raise HTTPException(415, "Upload a JPG, PNG, WEBP or GIF image.")
    data = await f.read()
    if not data:
        raise HTTPException(400, "The image file is empty.")
    if len(data) > MAX_IMG:
        raise HTTPException(413, "Image is larger than 8 MB.")
    return f.content_type, data


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_enabled": llm_enabled(), "model": MODEL if llm_enabled() else None}


SAFETY_SYS = ("You are a construction site safety officer. Inspect the image and notes for hazards, missing PPE "
              "(helmet, vest, boots, harness, gloves), unsafe scaffolding, housekeeping and electrical issues. "
              "Only report what is visible; if the image is not a construction scene say so in summary with low risk.")
CRACK_SYS = ("You are a structural engineer. Classify the crack in the image (hairline, shrinkage, settlement, "
             "flexural, shear, diagonal, etc.), estimate severity and width, list probable causes and corrective actions. "
             "Never claim certainty; set urgent=true only for signs of structural distress. If no crack is visible, say so.")


@app.post("/api/safety/analyze", response_model=SafetyResult)
async def safety(image: UploadFile = File(...), notes: str = Form("")):
    img = await read_image(image)
    return ask_json(SAFETY_SYS, f"Site notes: {notes or 'none'}", SafetyResult,
                    fallback=lambda: demo.safety_demo(notes), images=[img])


@app.post("/api/cracks/analyze", response_model=CrackResult)
async def cracks(image: UploadFile = File(...), notes: str = Form("")):
    img = await read_image(image)
    return ask_json(CRACK_SYS, f"Location / notes: {notes or 'none'}", CrackResult,
                    fallback=lambda: demo.crack_demo(notes), images=[img])


@app.post("/api/planning/estimate", response_model=PlanResult)
def plan(req: PlanRequest):
    result = planning.estimate_plan(req)
    n = ask_json(
        "You are a construction project planner in India.",
        f"Give a 1-sentence summary and 3 short practical risk/saving notes for this plan: "
        f"{req.model_dump_json()} total cost Rs {result.total_cost:,.0f}, {result.total_weeks} weeks.",
        Narrative, fallback=lambda: Narrative(summary="", notes=result.ai_notes))
    return result.model_copy(update={"ai_notes": n.notes or result.ai_notes,
                                     "source": "ai" if llm_enabled() else "demo"})


@app.post("/api/valuation/estimate", response_model=ValuationResult)
def valuation(req: ValuationRequest):
    result = planning.estimate_value(req)
    n = ask_json(
        "You are a real-estate valuer in India. Comment on local market context without inventing precise statistics.",
        f"Write a 2-sentence valuation summary for: {req.model_dump_json()}; estimate Rs {result.estimated_value:,.0f}.",
        Narrative, fallback=lambda: Narrative(summary=result.summary))
    return result.model_copy(update={"summary": n.summary or result.summary,
                                     "source": "ai" if llm_enabled() else "demo"})


@app.get("/api/weather", response_model=WeatherAdvisory)
async def weather_advisory(city: str = "Indore"):
    try:
        return await weather.get_advisory(city)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except Exception:
        raise HTTPException(502, "Weather service unreachable. Check your connection and try again.")


@app.post("/api/assistant/chat", response_model=ChatReply)
def chat(req: ChatRequest):
    history = "\n".join(f"{m.role}: {m.content}" for m in req.history[-8:])
    return ask_json(
        "You are a construction knowledge assistant for site engineers in India. Be concise, practical, cite IS codes "
        "when relevant, and flag when a licensed engineer must decide.",
        f"City: {req.city or 'unknown'}\nConversation so far:\n{history}\nuser: {req.message}\n"
        "Return answer and up to 3 short follow-up suggestions.",
        ChatReply, fallback=lambda: demo.chat_demo(req.message))
