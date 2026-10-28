import { useState } from "react";
import Safety from "./pages/Safety.jsx";
import Cracks from "./pages/Cracks.jsx";
import Planning from "./pages/Planning.jsx";
import Valuation from "./pages/Valuation.jsx";
import Assistant from "./pages/Assistant.jsx";
import { useHealth } from "./components/ui.jsx";

const TABS = [
  ["safety", "Safety", Safety],
  ["cracks", "Cracks", Cracks],
  ["planning", "Planning", Planning],
  ["valuation", "Valuation", Valuation],
  ["assistant", "Site assistant", Assistant],
];

export default function App() {
  const [tab, setTab] = useState("safety");
  const health = useHealth();
  const Page = TABS.find((t) => t[0] === tab)[2];
  const status = !health ? "Connecting..." : health.status !== "ok" ? "Backend offline. Start it on port 8000." : health.ai_enabled ? "AI connected" : "Demo mode (no API key)";

  return (
    <div className="shell">
      <aside>
        <h1>Site<br />Intelligence</h1>
        <nav>
          {TABS.map(([id, label]) => (
            <button key={id} className={id === tab ? "nav on" : "nav"} aria-current={id === tab ? "page" : undefined} onClick={() => setTab(id)}>{label}</button>
          ))}
        </nav>
        <p className={`status ${health?.ai_enabled ? "ok" : ""}`}>{status}</p>
      </aside>
      <main><Page /></main>
    </div>
  );
}
