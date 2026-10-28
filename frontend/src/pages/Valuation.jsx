import { useState } from "react";
import { inr, postJSON } from "../api.js";
import { DemoNote, ErrorBox, Field, useAsync } from "../components/ui.jsx";

const AMENITIES = ["lift", "parking", "security", "power backup", "garden", "gym"];

export default function Valuation() {
  const [f, setF] = useState({ location: "Indore", property_type: "apartment", area_sqft: 1100, age_years: 4, bedrooms: 2, condition: "good", amenities: ["parking"], base_rate_per_sqft: "" });
  const [{ loading, error, data }, run] = useAsync();
  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === "number" ? Number(e.target.value) : e.target.value });
  const toggle = (a) => setF({ ...f, amenities: f.amenities.includes(a) ? f.amenities.filter((x) => x !== a) : [...f.amenities, a] });
  const submit = () => run(() => postJSON("/api/valuation/estimate", { ...f, base_rate_per_sqft: f.base_rate_per_sqft === "" ? null : Number(f.base_rate_per_sqft) }));

  return (
    <>
      <h2>Property valuation</h2>
      <p className="lede">An indicative value range. For a loan or sale, get a certified valuer's report.</p>
      <div className="split">
        <section className="panel">
          <Field label="Location"><input value={f.location} onChange={set("location")} /></Field>
          <Field label="Property type">
            <select value={f.property_type} onChange={set("property_type")}>{["apartment", "house", "villa", "commercial", "plot"].map((x) => <option key={x}>{x}</option>)}</select>
          </Field>
          <Field label="Area (sq ft)"><input type="number" value={f.area_sqft} onChange={set("area_sqft")} /></Field>
          <Field label="Age (years)"><input type="number" value={f.age_years} onChange={set("age_years")} /></Field>
          <Field label="Condition">
            <select value={f.condition} onChange={set("condition")}>{["poor", "average", "good", "excellent"].map((x) => <option key={x}>{x}</option>)}</select>
          </Field>
          <Field label="Local rate per sq ft (optional, overrides default)"><input type="number" value={f.base_rate_per_sqft} onChange={set("base_rate_per_sqft")} /></Field>
          <div className="chips" role="group" aria-label="Amenities">
            {AMENITIES.map((a) => <button type="button" key={a} className={f.amenities.includes(a) ? "chip on" : "chip"} aria-pressed={f.amenities.includes(a)} onClick={() => toggle(a)}>{a}</button>)}
          </div>
          <button className="primary" disabled={loading} onClick={submit}>{loading ? "Estimating..." : "Estimate value"}</button>
          <ErrorBox message={error} />
        </section>
        <section className="panel result">
          {!data ? <p className="muted">Your valuation appears here.</p> : (
            <>
              <div className="big">{inr(data.estimated_value)}</div>
              <p className="muted">Range {inr(data.low)} to {inr(data.high)} ({inr(data.price_per_sqft)}/sq ft)</p>
              <DemoNote source={data.source} />
              <p>{data.summary}</p>
              <h4>What moved the price</h4>
              {data.factors.length === 0 ? <p className="muted">No adjustments applied.</p> : (
                <table><tbody>{data.factors.map((x) => <tr key={x.name}><td>{x.name}</td><td className={x.impact_pct < 0 ? "neg" : "pos"}>{x.impact_pct > 0 ? "+" : ""}{x.impact_pct}%</td></tr>)}</tbody></table>
              )}
            </>
          )}
        </section>
      </div>
    </>
  );
}
