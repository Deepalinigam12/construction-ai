import { useEffect, useRef, useState } from "react";
import { getJSON, postJSON } from "../api.js";
import { Badge, ErrorBox, useAsync } from "../components/ui.jsx";

function WeatherCard({ city, setCity }) {
  const [draft, setDraft] = useState(city);
  const [{ loading, error, data }, run] = useAsync();
  const load = (c) => run(() => getJSON(`/api/weather?city=${encodeURIComponent(c)}`));
  useEffect(() => { load(city); }, []);
  const lvl = { go: "low", caution: "medium", "no-go": "high" };
  return (
    <section className="panel">
      <h3>Weather advisory</h3>
      <form className="row" onSubmit={(e) => { e.preventDefault(); setCity(draft); load(draft); }}>
        <input aria-label="City" value={draft} onChange={(e) => setDraft(e.target.value)} />
        <button className="primary">Check</button>
      </form>
      <ErrorBox message={error} />
      {loading && <p className="muted">Loading forecast...</p>}
      {data && (
        <>
          <p><b>{data.city}</b> <Badge level={lvl[data.go_no_go]}>{data.go_no_go}</Badge></p>
          <div className="stats">
            <div><small>Temp</small><strong>{data.temperature_c}°C</strong></div>
            <div><small>Wind</small><strong>{data.wind_kmh} km/h</strong></div>
            <div><small>Rain 24h</small><strong>{data.rain_mm_next_24h} mm</strong></div>
          </div>
          <ul className="plain">{data.advisories.map((a, i) => <li key={i}>{a}</li>)}</ul>
          <table><thead><tr><th>Day</th><th>Max</th><th>Rain</th><th>Wind</th></tr></thead>
            <tbody>{data.forecast_days.map((d) => <tr key={d.date}><td>{d.date}</td><td>{d.max_c}°C</td><td>{d.rain_mm} mm</td><td>{d.wind_kmh} km/h</td></tr>)}</tbody></table>
        </>
      )}
    </section>
  );
}

function Chat({ city }) {
  const [msgs, setMsgs] = useState([{ role: "assistant", content: "Ask me about materials, curing, scheduling, codes or site problems." }]);
  const [text, setText] = useState("");
  const [sugg, setSugg] = useState(["How long should slabs cure?", "What mix suits residential columns?"]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const end = useRef();
  useEffect(() => { end.current?.scrollIntoView({ block: "nearest" }); }, [msgs, busy]);

  const send = async (q) => {
    const message = (q ?? text).trim();
    if (!message || busy) return;
    const history = msgs.slice(1);
    setMsgs([...msgs, { role: "user", content: message }]);
    setText(""); setBusy(true); setErr("");
    try {
      const r = await postJSON("/api/assistant/chat", { message, history, city });
      setMsgs((m) => [...m, { role: "assistant", content: r.answer }]);
      setSugg(r.suggestions || []);
    } catch (e) { setErr(e.message); }
    setBusy(false);
  };

  return (
    <section className="panel chat">
      <h3>Site assistant</h3>
      <div className="log" aria-live="polite">
        {msgs.map((m, i) => <div key={i} className={`msg ${m.role}`}>{m.content}</div>)}
        {busy && <div className="msg assistant muted">Thinking...</div>}
        <div ref={end} />
      </div>
      <ErrorBox message={err} />
      <div className="chips">{sugg.map((s) => <button key={s} className="chip" onClick={() => send(s)}>{s}</button>)}</div>
      <form className="row" onSubmit={(e) => { e.preventDefault(); send(); }}>
        <input aria-label="Your question" value={text} onChange={(e) => setText(e.target.value)} placeholder="Type a question" />
        <button className="primary" disabled={busy}>Send</button>
      </form>
    </section>
  );
}

export default function Assistant() {
  const [city, setCity] = useState("Indore");
  return (
    <>
      <h2>Daily site assistance</h2>
      <p className="lede">Check whether today suits concrete, lifting or finishing work, then ask follow-up questions.</p>
      <div className="split"><WeatherCard city={city} setCity={setCity} /><Chat city={city} /></div>
    </>
  );
}
