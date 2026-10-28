// All calls go through Vite's /api proxy (see vite.config.js).
async function handle(res) {
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const j = await res.json();
      msg = typeof j.detail === "string" ? j.detail : "Check the values you entered and try again.";
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const getJSON = (url) => fetch(url).then(handle);
export const postJSON = (url, body) =>
  fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).then(handle);
export const postImage = (url, file, notes) => {
  const fd = new FormData();
  fd.append("image", file);
  fd.append("notes", notes || "");
  return fetch(url, { method: "POST", body: fd }).then(handle);
};

export const inr = (n) => "Rs " + Math.round(n).toLocaleString("en-IN");
