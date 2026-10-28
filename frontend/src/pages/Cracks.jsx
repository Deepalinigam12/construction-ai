import ImageAnalyzer from "../components/ImageAnalyzer.jsx";
import { Badge, DemoNote, List } from "../components/ui.jsx";

function Result({ r }) {
  return (
    <>
      <h3>{r.crack_type} <Badge level={r.severity} /></h3>
      {r.urgent && <p className="error">Possible structural distress. Have a structural engineer inspect this soon.</p>}
      <p>{r.summary}</p>
      <DemoNote source={r.source} />
      <p><b>Estimated width:</b> {r.width_estimate}</p>
      <h4>Probable causes</h4>
      <List items={r.probable_causes} />
      <h4>Recommended actions</h4>
      <List items={r.recommended_actions} />
    </>
  );
}

export default function Cracks() {
  return (
    <>
      <h2>Crack analysis</h2>
      <p className="lede">Upload a close-up of a wall, slab or column. Include a coin or scale in the photo for a better width estimate.</p>
      <ImageAnalyzer endpoint="/api/cracks/analyze" notesLabel="Where is it, and when did you notice it?" button="Analyse crack" Result={Result} />
    </>
  );
}
