/* Stipendex: matchning i webbläsaren mot /api/index.json. Inga uppgifter lämnar besökarens dator. */
(() => {
  const CFG = JSON.parse(document.getElementById("cfg").textContent);
  const ROOT = window.STIP_ROOT || "/";
  const SUFFIX = window.STIP_LINK_SUFFIX || "";
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const NORRLAND = ["Gästrikland", "Hälsingland", "Härjedalen", "Jämtland", "Medelpad", "Ångermanland", "Västerbotten", "Norrbotten", "Lappland"];
  const LEVELS = { student: ["student"], doktorand: ["doktorand", "student", "forskare"], forskare: ["forskare", "doktorand"], elev: ["elev"] };
  let DATA = [], mode = "stip";
  const shown = { hit: 15, gen: 10, chk: 10 };

  const opt = (v, t) => `<option value="${esc(v)}">${esc(t)}</option>`;
  const cap = s => s[0].toUpperCase() + s.slice(1);
  $("uni").innerHTML = Object.entries(CFG.unis).map(([k, u]) => opt(k, u.name)).join("") + opt("", "Annat eller inget lärosäte");
  $("amne").innerHTML = opt("", "Välj ämne") + CFG.subjects.map(s => opt(s, cap(s))).join("");
  $("land").innerHTML = opt("", "Välj") + CFG.lands.map(l => opt(l, l)).join("");
  $("aidboxes").innerHTML = CFG.aid.map((a, i) => `<label><input type="checkbox" class="aid" value="${esc(a)}" id="aid${i}"> ${esc(cap(a))}</label>`).join("");

  function setNations() {
    const u = CFG.unis[$("uni").value];
    const list = u ? (CFG.nations[u.city] || []) : [];
    const prev = $("nation").value;
    $("nation").innerHTML = opt("", "Ingen nation") + list.map(n => opt(n, n)).join("");
    if (list.includes(prev)) $("nation").value = prev;
    $("nationfield").hidden = !list.length;
  }

  // Exempelprofil
  $("uni").value = "UU"; setNations(); $("amne").value = "medicin"; $("nation").value = "Norrlands nation";
  $("land").value = "Norrbotten"; $("ort").value = "Luleå"; $("alder").value = 23; $("behov").checked = true;

  const profile = () => ({
    uni: $("uni").value, niva: $("niva").value, amne: $("amne").value, nation: $("nation").value, land: $("land").value,
    ort: $("ort").value.trim().toLowerCase(), alder: parseInt($("alder").value, 10) || null, kon: $("kon").value,
    behov: $("behov").checked, resa: $("resa").checked, bostad: $("bostad").checked,
    aid: [...document.querySelectorAll(".aid:checked")].map(e => e.value)
  });

  function originHit(x, p) {
    if (!x.o.length) return null;
    const o = x.o.map(s => s.toLowerCase());
    if (p.land && o.includes(p.land.toLowerCase())) return true;
    if (p.land && NORRLAND.includes(p.land) && o.includes("norrland")) return true;
    return !!(p.ort && o.includes(p.ort));
  }

  function common(x, p, hits, warns) {
    const oh = originHit(x, p);
    if (x.o.length) { if (oh) hits.push("Anknytning " + x.o.join(", ")); else return false; }
    if (x.f.includes("foretrade_adel")) warns.push("Företräde för adliga sökande");
    else if (x.f.includes("foretrade_slakt")) warns.push("Företräde för donatorns släkt");
    return true;
  }

  function matchStip(x, p) {
    if (x.k !== "s") return null;
    const hits = [], warns = [];
    if (x.l.length && !x.l.some(v => LEVELS[p.niva].includes(v))) return null;
    if (CFG.unis[x.r] && x.r !== p.uni) return null;
    if (x.u.length) { if (x.u.includes(p.uni)) hits.push(CFG.unis[p.uni].name); else return null; }
    if (x.na.length) {
      if (x.na.includes(p.nation)) hits.push(p.nation);
      else if (originHit(x, p)) warns.push("Kan kräva medlemskap i " + x.na.join(" eller "));
      else return null;
    } else if (x.r === "nation") return null;
    if (x.a.length) {
      if (p.amne && x.a.includes(p.amne)) hits.push(cap(p.amne));
      else if (!p.amne) warns.push("Gäller " + x.a.join(", "));
      else return null;
    }
    if (x.o.length && !originHit(x, p)) {
      if (x.na.length && x.na.includes(p.nation)) warns.push("Kan kräva anknytning till " + x.o.join(", "));
      else return null;
    } else if (!common(x, p, hits, warns)) return null;
    if (x.f.includes("man") && p.kon !== "man") warns.push("Ursprungligen bara för män");
    if (x.f.includes("kvinna") && p.kon !== "kvinna") warns.push("Ursprungligen bara för kvinnor");
    if (x.m && p.alder && p.alder > x.m) warns.push("Åldersgräns kring " + x.m + " år");
    if (x.f.includes("behov")) { if (p.behov) hits.push("Ekonomiskt behov"); else warns.push("Kräver ekonomiskt behov"); }
    if (x.f.includes("resa")) { if (p.resa) hits.push("Resa/utlandsstudier"); else warns.push("Främst för resor"); }
    if (x.f.includes("bostad")) { if (p.bostad) hits.push("Boende"); else warns.push("Gäller boende"); }
    const specific = x.u.length || x.na.length || x.a.length || x.o.length;
    return { x, hits, warns, score: hits.length * 2 - warns.length, group: warns.length ? "chk" : specific ? "hit" : "gen" };
  }

  function matchAid(x, p) {
    if (x.k !== "b") return null;
    const hits = [], warns = [];
    if (p.aid.length) { const h = x.g.filter(g => p.aid.includes(g)); if (!h.length) return null; hits.push(...h.map(cap)); }
    if (!common(x, p, hits, warns)) return null;
    return { x, hits, warns, score: hits.length * 2 - warns.length, group: warns.length ? "chk" : x.o.length ? "hit" : "gen" };
  }

  function how(x) {
    const u = CFG.unis[x.r];
    if (u) return `${esc(u.how)} <a href="${u.url}" rel="noopener">${esc(u.name)}</a>`;
    if (x.r === "nation" && x.na[0]) return `Söks via ${esc(x.na[0])}.` + (CFG.nationUrl[x.na[0]] ? ` <a href="${CFG.nationUrl[x.na[0]]}" rel="noopener">Nationens webbplats</a>` : "");
    return "Kontakta stiftelsen direkt, kontaktuppgifter finns på stiftelsens sida.";
  }

  function card(m) {
    const x = m.x;
    const chips = m.hits.map(h => `<li class="hit">${esc(h)}</li>`).join("") + m.warns.map(w => `<li class="w">${esc(w)}</li>`).join("");
    return `<article class="card ${m.group}">
      <h3><a href="${ROOT}stiftelse/${x.s}/${SUFFIX}">${esc(x.n)}</a></h3>
      ${chips ? `<ul class="chips">${chips}</ul>` : ""}
      <p>${esc(x.v)}</p><p class="how">${how(x)}</p></article>`;
  }

  function renderList(id, items, key) {
    const el = $(id);
    if (!items.length) { el.innerHTML = `<p class="note">Inga träffar här med din profil.</p>`; return; }
    const rest = items.length - shown[key];
    el.innerHTML = items.slice(0, shown[key]).map(card).join("") +
      (rest > 0 ? `<button type="button" class="more" data-k="${key}">Visa fler (${rest} kvar)</button>` : "");
  }

  function render() {
    const p = profile();
    const fn = mode === "stip" ? matchStip : matchAid;
    const res = DATA.map(x => fn(x, p)).filter(Boolean).sort((a, b) => b.score - a.score);
    const g = { hit: [], gen: [], chk: [] };
    res.forEach(m => g[m.group].push(m));
    $("summary").innerHTML = `<div class="tile"><b>${g.hit.length}</b><span>riktade till dig</span></div>
      <div class="tile"><b>${g.gen.length}</b><span>allmänna</span></div>
      <div class="tile"><b>${g.chk.length}</b><span>att kolla villkoren för</span></div>`;
    renderList("l-hit", g.hit, "hit"); renderList("l-gen", g.gen, "gen"); renderList("l-chk", g.chk, "chk");
  }

  function setMode(m) {
    mode = m;
    $("tab-stip").setAttribute("aria-selected", m === "stip"); $("tab-bidrag").setAttribute("aria-selected", m === "bidrag");
    document.querySelectorAll(".stip-only").forEach(e => e.hidden = m !== "stip");
    document.querySelectorAll(".bidrag-only").forEach(e => e.hidden = m === "stip");
    shown.hit = 15; shown.gen = 10; shown.chk = 10; render();
  }

  $("tab-stip").addEventListener("click", () => setMode("stip"));
  $("tab-bidrag").addEventListener("click", () => setMode("bidrag"));
  $("uni").addEventListener("change", setNations);
  $("profile").addEventListener("input", () => { $("exnote").hidden = true; shown.hit = 15; shown.gen = 10; shown.chk = 10; render(); });
  $("profile").addEventListener("submit", e => e.preventDefault());
  $("results").addEventListener("click", e => { const b = e.target.closest(".more"); if (b) { shown[b.dataset.k] += 20; render(); } });

  fetch(ROOT + "api/index.json").then(r => r.json()).then(d => { DATA = d; render(); })
    .catch(() => { $("summary").innerHTML = `<p class="note">Kunde inte läsa in stiftelserna. Ladda om sidan.</p>`; });
})();
