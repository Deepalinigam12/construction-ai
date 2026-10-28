import httpx
from .schemas import WeatherAdvisory

GEO = "https://geocoding-api.open-meteo.com/v1/search"
FC = "https://api.open-meteo.com/v1/forecast"


async def get_advisory(city: str) -> WeatherAdvisory:
    async with httpx.AsyncClient(timeout=10) as c:
        g = (await c.get(GEO, params={"name": city, "count": 1})).json()
        if not g.get("results"):
            raise LookupError(f"City '{city}' not found")
        p = g["results"][0]
        f = (await c.get(FC, params={
            "latitude": p["latitude"], "longitude": p["longitude"], "timezone": "auto", "forecast_days": 5,
            "current": "temperature_2m,wind_speed_10m",
            "hourly": "precipitation,precipitation_probability",
            "daily": "temperature_2m_max,precipitation_sum,wind_speed_10m_max",
        })).json()
    cur = f["current"]
    rain24 = round(sum(f["hourly"]["precipitation"][:24]), 1)
    prob = max(f["hourly"]["precipitation_probability"][:24] or [0])
    wind = max(cur["wind_speed_10m"], f["daily"]["wind_speed_10m_max"][0])
    temp = cur["temperature_2m"]
    adv, score = [], 0
    if rain24 >= 5 or prob >= 60:
        adv.append("Rain likely: postpone concreting, plastering and external painting; cover stacked cement and steel."); score += 2
    if wind >= 40:
        adv.append("Strong wind: stop crane lifts and work on scaffolds or edges."); score += 2
    elif wind >= 25:
        adv.append("Breezy: secure sheeting and loose materials; limit lifting."); score += 1
    if temp >= 38:
        adv.append("Very hot: pour early morning, increase curing frequency, provide shade and water for workers."); score += 1
    if temp <= 5:
        adv.append("Cold: protect fresh concrete from frost.")
        score += 1
    if not adv:
        adv.append("Conditions are good for general site work.")
    days = [{"date": d, "max_c": t, "rain_mm": r, "wind_kmh": w} for d, t, r, w in zip(
        f["daily"]["time"], f["daily"]["temperature_2m_max"], f["daily"]["precipitation_sum"], f["daily"]["wind_speed_10m_max"])]
    return WeatherAdvisory(
        city=f'{p["name"]}, {p.get("admin1", "")}'.strip(", "), temperature_c=temp, wind_kmh=wind,
        rain_mm_next_24h=rain24, rain_probability_pct=prob, forecast_days=days, advisories=adv,
        go_no_go="no-go" if score >= 3 else "caution" if score >= 1 else "go",
    )
