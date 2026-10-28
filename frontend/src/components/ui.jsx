import { useEffect, useState } from "react";

export function Badge({ level, children }) {
  return <span className={`badge b-${level}`}>{children ?? level}</span>;
}

export function DemoNote({ source }) {
  if (source !== "demo") return null;
  return <p className="demo-note">Demo mode: results come from built-in rules. Add an API key to the backend for AI analysis.</p>;
}

export function Field({ label, children }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  );
}

export function useAsync() {
  const [state, set] = useState({ loading: false, error: "", data: null });
  const run = async (fn) => {
    set({ loading: true, error: "", data: null });
    try {
      set({ loading: false, error: "", data: await fn() });
    } catch (e) {
      set({ loading: false, error: e.message || "Something went wrong.", data: null });
    }
  };
  return [state, run];
}

export function ErrorBox({ message }) {
  return message ? <p className="error" role="alert">{message}</p> : null;
}

export function List({ items }) {
  if (!items?.length) return <p className="muted">None found.</p>;
  return <ul className="plain">{items.map((x, i) => <li key={i}>{x}</li>)}</ul>;
}

export function useHealth() {
  const [h, setH] = useState(null);
  useEffect(() => {
    fetch("/api/health").then((r) => r.json()).then(setH).catch(() => setH({ status: "down" }));
  }, []);
  return h;
}
