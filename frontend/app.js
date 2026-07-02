"use strict";
const TOKEN_KEY = "ats_token";
let token = localStorage.getItem(TOKEN_KEY) || "";

const $ = (id) => document.getElementById(id);

function headers(extra) {
  return Object.assign({ "X-Access-Token": token }, extra || {});
}

async function api(path, opts) {
  const res = await fetch(path, Object.assign({ headers: headers(opts && opts.json ? { "Content-Type": "application/json" } : {}) }, opts || {}));
  if (res.status === 401) throw new Error("unauthorized");
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch (e) {}
    throw new Error(msg);
  }
  return res.json();
}

function log(msg, cls) {
  const el = document.createElement("div");
  el.className = "line " + (cls || "");
  const t = new Date().toLocaleTimeString();
  el.textContent = `[${t}] ${msg}`;
  $("log").prepend(el);
}

function showApp(connected) {
  $("login").classList.toggle("hidden", connected);
  $("app").classList.toggle("hidden", !connected);
  $("conn").textContent = connected ? "● connected" : "";
}

async function connect() {
  token = $("token").value.trim();
  $("loginError").textContent = "";
  if (!token) { $("loginError").textContent = "Enter a token."; return; }
  try {
    await api("/api/applications");
    localStorage.setItem(TOKEN_KEY, token);
    showApp(true);
    await loadProfiles();
    await loadApplications();
    log("Connected.", "dim");
  } catch (e) {
    $("loginError").textContent = e.message === "unauthorized" ? "Invalid token." : ("Error: " + e.message);
  }
}

async function loadProfiles() {
  try {
    const ps = await api("/api/profiles");
    const sel = $("profile");
    sel.innerHTML = '<option value="">Auto — best match</option>';
    ps.forEach((p) => {
      const o = document.createElement("option");
      o.value = p.id;
      o.textContent = `${p.name}${p.current_company ? " — " + p.current_company : ""}`;
      sel.appendChild(o);
    });
  } catch (e) { /* non-fatal */ }
}

// FIFO queue: paste JDs back-to-back without waiting; a single worker runs them in order
// (the server also serializes generation, so one-at-a-time keeps things predictable).
const queue = [];
let processing = false;
let seq = 0;

function updateQ() {
  const el = $("qstatus");
  if (!el) return;
  const waiting = queue.length;
  el.textContent = processing
    ? `⏳ generating…${waiting ? ` · ${waiting} queued` : ""}`
    : (waiting ? `${waiting} queued` : "");
}

function renderQueue() {
  updateQ();
  const box = $("queue");
  if (!box) return;
  box.innerHTML = queue.map((q, i) =>
    `<div class="qitem"><span class="qnum">${i + 1}</span>` +
    `<span class="qtext">${esc(q.preview)}</span>` +
    `<span class="qmeta">${esc(q.profileLabel)}${q.force ? " · force" : ""}</span>` +
    `<button class="qdel" data-id="${q.id}" title="Remove from queue">✕</button></div>`
  ).join("");
  box.querySelectorAll("button.qdel").forEach((b) =>
    b.addEventListener("click", () => removeQueued(Number(b.dataset.id)))
  );
}

function removeQueued(id) {
  const i = queue.findIndex((q) => q.id === id);
  if (i >= 0) { queue.splice(i, 1); renderQueue(); }
}

function enqueueBid() {
  const jd = $("jd").value.trim();
  if (!jd) { log("Paste a JD first.", "warn"); return; }
  // Snapshot the profile/force choices now, since they may change for the next JD.
  const sel = $("profile");
  queue.push({
    id: ++seq,
    jd_text: jd,
    jd_link: $("jdlink").value.trim(),
    profile_id: sel.value || null,
    force: $("force").checked,
    preview: jd.replace(/\s+/g, " ").slice(0, 70),
    profileLabel: sel.selectedIndex >= 0 ? sel.options[sel.selectedIndex].text : "Auto — best match",
  });
  $("jd").value = "";
  $("jdlink").value = "";
  $("jd").focus();
  log(`➕ Queued — ${queue.length + (processing ? 1 : 0)} in line.`, "dim");
  renderQueue();
  processQueue();
}

async function processQueue() {
  if (processing) return;        // a worker is already draining the queue
  processing = true;
  renderQueue();
  while (queue.length) {
    const item = queue.shift();
    renderQueue();
    log(`Matching candidate and generating…${queue.length ? ` (${queue.length} still queued)` : ""}`, "dim");
    try {
      const r = await api("/api/bid", { method: "POST", json: true,
        body: JSON.stringify({ jd_text: item.jd_text, jd_link: item.jd_link || null, profile_id: item.profile_id, force: item.force }) });
      const jd0 = r.jd || {};
      if (r.status === "generated") {
        if (r.switched_from) log(`${r.switched_from} already applied to ${jd0.company} — switched to next-best.`, "warn");
        log(`✓ Resume for ${r.profile} → ${jd0.role || "role"} @ ${jd0.company || "company"} generated.`, "ok");
        if (r.issues && r.issues.length) log(`(${r.issues.length} rule warning(s))`, "warn");
        await loadApplications();
      } else if (r.status === "skipped") {
        log("⚠ " + (r.message || "Skipped."), "warn");
      } else if (r.status === "blocked") {
        log(`⛔ JD skipped — ${r.message}`, "warn");
      } else {
        log("Error: " + (r.message || "unknown"), "err");
      }
    } catch (e) {
      if (e.message === "unauthorized") {
        queue.length = 0;        // drop the rest; the user must re-authenticate
        processing = false;
        renderQueue();
        showApp(false);
        return;
      }
      log("Error: " + e.message, "err");   // skip this one, keep draining the rest
    }
  }
  processing = false;
  renderQueue();
}

async function loadApplications() {
  const rows = await api("/api/applications");
  const tb = $("apps").querySelector("tbody");
  tb.innerHTML = "";
  rows.forEach((a) => {
    const tr = document.createElement("tr");
    const fileLinks = filesFor(a);
    tr.innerHTML = `<td>${a.number || ""}</td><td>${a.date || ""}</td><td>${esc(a.company)}</td>` +
      `<td>${esc(a.job_title)}</td><td>${esc(a.profile)}</td><td>${esc(a.salary)}</td>` +
      `<td>${jdLinkCell(a.jd_link)}</td><td>${fileLinks}</td>`;
    tb.appendChild(tr);
  });
  // wire up download links
  tb.querySelectorAll("a[data-folder]").forEach((a) => {
    a.addEventListener("click", (e) => { e.preventDefault(); download(a.dataset.folder, a.dataset.file, a.dataset.dlname); });
  });
}

function jdLinkCell(link) {
  link = (link || "").trim();
  // Only render an anchor for real http(s) URLs — guards against javascript:/data: URIs.
  if (!/^https?:\/\//i.test(link)) return "";
  return `<a href="${esc(link)}" target="_blank" rel="noopener noreferrer">link ↗</a>`;
}

function compact(name, fallback) { return (name || "").replace(/[^A-Za-z0-9]/g, "") || (fallback || "Resume"); }

function filesFor(a) {
  if (!a.folder) return "";
  const stem = compact(a.profile);            // matches the stored filename (fetch key)
  const co = compact(a.company, "Company");    // for the friendly save-as name
  // [label, stored filename to fetch, friendly download name]
  const items = [
    ["Resume PDF", `${stem}_Resume.pdf`, `Resume_${stem}_${co}.pdf`],
    ["Cover PDF", `${stem}_CoverLetter.pdf`, `CoverLetter_${stem}_${co}.pdf`],
  ];
  return items.map(([label, file, dlname]) =>
    `<a href="#" data-folder="${encodeURIComponent(a.folder)}" data-file="${encodeURIComponent(file)}" data-dlname="${encodeURIComponent(dlname)}">${label}</a>`
  ).join("");
}

async function download(folder, file, dlname) {
  try {
    const res = await fetch(`/api/files/${folder}/${file}`, { headers: headers() });
    if (!res.ok) { log(`Could not fetch ${decodeURIComponent(file)}.`, "err"); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = decodeURIComponent(dlname || file); a.click();
    URL.revokeObjectURL(url);
  } catch (e) { log("Download error: " + e.message, "err"); }
}

function esc(s) { return (s == null ? "" : String(s)).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

$("connect").addEventListener("click", connect);
$("token").addEventListener("keydown", (e) => { if (e.key === "Enter") connect(); });
$("submit").addEventListener("click", enqueueBid);
$("refresh").addEventListener("click", () => loadApplications().catch((e) => log(e.message, "err")));

// Auto-connect if we already have a token.
(async () => {
  if (token) {
    try { await api("/api/applications"); showApp(true); await loadProfiles(); await loadApplications(); }
    catch (e) { showApp(false); }
  } else { showApp(false); }
})();