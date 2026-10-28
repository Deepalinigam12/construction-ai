import ImageAnalyzer from "../components/ImageAnalyzer.jsx";
import { Badge, DemoNote, List } from "../components/ui.jsx";

function Result({ r }) {
  return (
    <>
      <h3>Site risk <Badge level={r.risk_level} /></h3>
      <p>{r.summary}</p>
      <DemoNote source={r.source} />
      <h4>Hazards</h4>
      {r.hazards.length === 0 && <p className="muted">No hazards identified.</p>}
      {r.hazards.map((h, i) => (
        <div className="item" key={i}>
          <strong>{h.name}</strong> <Badge level={h.severity} />
          <p>{h.description}</p>
          <p><b>Fix:</b> {h.corrective_action}</p>
        </div>
      ))}
      <h4>PPE issues</h4>
      <List items={r.ppe_issues} />
      <h4>Recommendations</h4>
      <List items={r.recommendations} />
    </>
  );
}

export default function Safety() {
  return (
    <>
      <h2>Site safety check</h2>
      <p className="lede">Upload a photo from site. Get hazards, missing PPE and what to fix first.</p>
      <ImageAnalyzer endpoint="/api/safety/analyze" notesLabel="Site notes (optional)" button="Check safety" Result={Result} />
    </>
  );
}
