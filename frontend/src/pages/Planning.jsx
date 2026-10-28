import { useState } from "react";
import { inr, postJSON } from "../api.js";
import { DemoNote, ErrorBox, Field, List, useAsync } from "../components/ui.jsx";

export default function Planning() {
  const [f, setF] = useState({ project_type: "residential", built_area_sqft: 1500, floors: 2, quality: "standard", city_cost_factor: 1 });
  const [{ loading, error, data }, run] = useAsync();
  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === "number" ? Number(e.target.value) : e.target.value });
  const maxWeek = data ? data.total_weeks : 1;

  return (
    <>
      <h2>Project planning</h2>
      <p className="lede">Material quantities, cost and a week-by-week schedule from a few inputs.</p>
      <div className="split">
        <section className="panel">
          <Field label="Project type">
            <select value={f.project_type} onChange={set("project_type")}><option>residential</option><option>commercial</option></select>
          </Field>
          <Field label="Total built-up area (sq ft)"><input type="number" value={f.built_area_sqft} onChange={set("built_area_sqft")} /></Field>
          <Field label="Floors"><input type="number" min="1" value={f.floors} onChange={set("floors")} /></Field>
          <Field label="Finish quality">
            <select value={f.quality} onChange={set("quality")}><option>basic</option><option>standard</option><option>premium</option></select>
          </Field>
          <Field label="City cost factor (1.0 = average)"><input type="number" step="0.05" value={f.city_cost_factor} onChange={set("city_cost_factor")} /></Field>
          <button className="primary" disabled={loading} onClick={() => run(() => postJSON("/api/planning/estimate", f))}>
            {loading ? "Calculating..." : "Build plan"}
          </button>
          <ErrorBox message={error} />
        </section>
        <section className="panel result">
          {!data ? <p className="muted">Your estimate appears here.</p> : (
            <>
              <div className="stats">
                <div><small>Total cost</small><strong>{inr(data.total_cost)}</strong></div>
                <div><small>Per sq ft</small><strong>{inr(data.cost_per_sqft)}</strong></div>
                <div><small>Duration</small><strong>{data.total_weeks} weeks</strong></div>
              </div>
              <DemoNote source={data.source} />
              <h4>Schedule</h4>
              <div className="gantt">
                {data.schedule.map((p) => (
                  <div className="g-row" key={p.phase} title={p.tasks.join(", ")}>
                    <span>{p.phase}</span>
                    <div className="g-track">
                      <i style={{ left: `${((p.start_week - 1) / maxWeek) * 100}%`, width: `${(p.duration_weeks / maxWeek) * 100}%` }} />
                    </div>
                    <em>{p.duration_weeks} wk</em>
                  </div>
                ))}
              </div>
              <h4>Materials</h4>
              <table>
                <thead><tr><th>Item</th><th>Qty</th><th>Cost</th></tr></thead>
                <tbody>
                  {data.materials.map((m) => (
                    <tr key={m.item}><td>{m.item}</td><td>{m.quantity.toLocaleString("en-IN")} {m.unit}</td><td>{inr(m.est_cost)}</td></tr>
                  ))}
                  <tr className="sum"><td colSpan="2">Materials subtotal</td><td>{inr(data.material_cost)}</td></tr>
                  <tr className="sum"><td colSpan="2">Labour, services and finishing</td><td>{inr(data.labour_and_finishing_cost)}</td></tr>
                </tbody>
              </table>
              <h4>Notes</h4>
              <List items={data.ai_notes} />
            </>
          )}
        </section>
      </div>
    </>
  );
}
