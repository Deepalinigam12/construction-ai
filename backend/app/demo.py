"""Offline fallbacks used when no API key is configured."""
from .schemas import ChatReply, CrackResult, Hazard, SafetyResult

NOTE = "DEMO MODE: no AI key configured, so this is a generic sample, not an analysis of your image."


def safety_demo(notes: str) -> SafetyResult:
    return SafetyResult(
        summary=f"{NOTE} Add ANTHROPIC_API_KEY to backend/.env for real image analysis.",
        risk_level="medium",
        hazards=[Hazard(name="Unprotected edge / working at height", severity="high",
                        description="Typical hazard on active slabs and scaffolds.",
                        corrective_action="Install guardrails and toe boards; enforce full-body harness use.")],
        ppe_issues=["Check helmets and high-visibility vests on all workers", "Safety footwear required near rebar"],
        recommendations=["Hold a daily toolbox talk", "Keep walkways clear of debris"],
        source="demo",
    )


def crack_demo(notes: str) -> CrackResult:
    return CrackResult(
        crack_type="Unknown (demo)", severity="medium", width_estimate="n/a",
        probable_causes=["Shrinkage", "Differential settlement", "Thermal movement"],
        recommended_actions=["Mark and monitor with tell-tale gauges for 4 weeks", "Consult a structural engineer if width grows"],
        urgent=False, summary=f"{NOTE}", source="demo",
    )


def chat_demo(message: str) -> ChatReply:
    m = message.lower()
    if any(k in m for k in ("cure", "curing")):
        a = "Keep concrete moist for at least 7 days (10-14 for blended cement) and shield it from direct sun and wind."
    elif any(k in m for k in ("rain", "weather", "monsoon")):
        a = "Avoid pouring concrete in heavy rain; cover fresh work and check the Weather tab for a go/no-go call."
    elif any(k in m for k in ("cement", "mix", "m20", "m25")):
        a = "M20 (1:1.5:3) suits slabs and beams in residential work; use M25 or higher for columns and severe exposure."
    elif "crack" in m:
        a = "Hairline cracks under 0.3 mm are usually cosmetic. Wider, diagonal or growing cracks need an engineer's review."
    else:
        a = "I can help with materials, curing, scheduling, safety and cost questions. (Demo mode: add an API key for full answers.)"
    return ChatReply(answer=a, suggestions=["How long should slabs cure?", "Is it safe to pour concrete tomorrow?"], source="demo")
