import { useEffect, useState } from "react";
import { postImage } from "../api.js";
import { ErrorBox, Field, useAsync } from "./ui.jsx";

export default function ImageAnalyzer({ endpoint, notesLabel, button, Result }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [notes, setNotes] = useState("");
  const [{ loading, error, data }, run] = useAsync();

  useEffect(() => {
    if (!file) return setPreview("");
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  return (
    <div className="split">
      <section className="panel">
        <label className={`drop ${preview ? "has" : ""}`}>
          {preview ? <img src={preview} alt="Selected upload" /> : <span>Choose a site photo (JPG, PNG, WEBP, up to 8 MB)</span>}
          <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={(e) => setFile(e.target.files[0] || null)} />
        </label>
        <Field label={notesLabel}>
          <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </Field>
        <button className="primary" disabled={!file || loading} onClick={() => run(() => postImage(endpoint, file, notes))}>
          {loading ? "Analysing..." : button}
        </button>
        <ErrorBox message={error} />
      </section>
      <section className="panel result">
        {data ? <Result r={data} /> : <p className="muted">Results appear here after you run an analysis.</p>}
      </section>
    </div>
  );
}
