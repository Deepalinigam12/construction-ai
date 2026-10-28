"""Deterministic estimation engine (INR). The LLM only adds commentary on top."""
from .schemas import MaterialLine, Phase, PlanRequest, PlanResult, ValuationRequest, ValuationResult, Factor

# Per sq ft of built-up area, typical RCC framed construction
MATERIAL_RATES = [
    ("Cement (OPC 53)", 0.40, "bags", 400),
    ("TMT steel", 4.0, "kg", 65),
    ("River/M-sand", 1.8, "cft", 60),
    ("Coarse aggregate", 1.35, "cft", 45),
    ("Bricks / AAC blocks", 8.0, "nos", 9),
    ("Tiles & flooring", 1.0, "sqft", 85),
    ("Paint (all coats)", 0.06, "litres", 380),
]
QUALITY_RATE = {"basic": 1500, "standard": 1900, "premium": 2800}  # all-in Rs/sqft
COMMERCIAL_MULT = 1.15

PHASES = [
    ("Site prep & excavation", 0.06, ["Clearing & marking", "Excavation", "PCC bed"]),
    ("Foundation", 0.12, ["Footing reinforcement", "Footing concrete", "Plinth beam"]),
    ("Structure (columns, slabs)", 0.28, ["Column & beam casting", "Slab shuttering", "Slab concrete & curing"]),
    ("Masonry", 0.14, ["Brickwork", "Lintels", "Sunshades"]),
    ("MEP rough-in", 0.10, ["Conduits & wiring", "Plumbing lines", "Drainage"]),
    ("Plaster & waterproofing", 0.10, ["Internal plaster", "External plaster", "Terrace waterproofing"]),
    ("Flooring & finishes", 0.12, ["Tiling", "Doors & windows", "Putty & paint"]),
    ("Fixtures & handover", 0.08, ["Electrical fixtures", "Sanitaryware", "Snag list & cleaning"]),
]


def estimate_plan(req: PlanRequest) -> PlanResult:
    area = req.built_area_sqft  # total built-up area across all floors
    mats, mat_total = [], 0.0
    for item, per_sqft, unit, rate in MATERIAL_RATES:
        qty = round(per_sqft * area, 1)
        cost = round(qty * rate * req.city_cost_factor, 0)
        mats.append(MaterialLine(item=item, quantity=qty, unit=unit, est_cost=cost))
        mat_total += cost
    rate = QUALITY_RATE[req.quality] * req.city_cost_factor * (COMMERCIAL_MULT if req.project_type == "commercial" else 1)
    total = round(rate * area, 0)
    labour = max(total - mat_total, 0)
    # duration: ~ 26 weeks for 1500 sqft, grows sub-linearly; +3 wks per extra floor
    weeks = max(12, round(26 * (area / 1500) ** 0.5 + 3 * (req.floors - 1)))
    sched, cursor = [], 1
    for name, share, tasks in PHASES:
        dur = max(1, round(weeks * share))
        sched.append(Phase(phase=name, start_week=cursor, duration_weeks=dur, tasks=tasks))
        cursor += dur
    return PlanResult(
        materials=mats, material_cost=mat_total, labour_and_finishing_cost=labour, total_cost=total,
        cost_per_sqft=round(total / area, 0), schedule=sched, total_weeks=cursor - 1,
        ai_notes=["Estimates use typical Indian market rates; add 10% contingency for price swings."],
        source="demo",
    )


def estimate_value(req: ValuationRequest) -> ValuationResult:
    base = req.base_rate_per_sqft or {"apartment": 5500, "house": 6500, "villa": 8500, "commercial": 9000, "plot": 4000}[req.property_type]
    factors: list[Factor] = []
    mult = 1.0

    def add(name: str, pct: float):
        nonlocal mult
        if pct:
            factors.append(Factor(name=name, impact_pct=round(pct, 1)))
            mult *= 1 + pct / 100

    if req.property_type != "plot":
        add(f"Age ({req.age_years} yrs)", -min(req.age_years * 1.0, 30))
        add(f"Condition: {req.condition}", {"poor": -15, "average": -5, "good": 0, "excellent": 6}[req.condition])
        add("Amenities", min(len(req.amenities) * 2, 10))
    value = round(base * req.area_sqft * mult, 0)
    return ValuationResult(
        estimated_value=value, low=round(value * 0.9, 0), high=round(value * 1.1, 0),
        price_per_sqft=round(value / req.area_sqft, 0), factors=factors,
        summary=f"Rule-based estimate for a {req.property_type} in {req.location} at a base rate of Rs {base:,.0f}/sqft.",
        source="demo",
    )
