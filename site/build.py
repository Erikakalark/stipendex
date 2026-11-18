"""Bygger den statiska sajten från data/stiftelser.json till dist/.

Körs: python site/build.py [--base-url https://stipendex.se] [--limit N]
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import shutil
import sys
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from config import AID, LANDS_UI, NATION_URL, NATIONS, SUBJECTS, UNIS  # noqa: E402
from tag import slugify  # noqa: E402

SITE = "Stipendex"
PUBLIC_KATS = ("stipendium", "bidrag")
PAGE = 150


def load(path):
    rows = json.load(open(path, encoding="utf-8"))
    return [r for r in rows if r["kat"] in PUBLIC_KATS]


def how_to_apply(r):
    """Returnerar (text, länk, länktext) för hur man söker."""
    if r["route"] in UNIS:
        u = UNIS[r["route"]]
        return u["how"], u["url"], f"{u['name']}s stipendiesida"
    if r["route"] == "nation" and r["nationer"]:
        n = r["nationer"][0]
        return (f"Söks via {n}. Nationen utlyser sina stipendier varje termin.", NATION_URL.get(n), n)
    return ("Kontakta stiftelsen direkt och fråga om ansökan och sista ansökningsdag. Många mindre stiftelser har ingen webbplats.",
            "https://stiftelser.lansstyrelsen.se/", "Länsstyrelsernas stiftelsesök")


def compact(r):
    """Kort post för matchningen i webbläsaren."""
    return {"i": r["id"], "s": r["slug"], "n": r["namn"], "k": r["kat"][0], "l": r["niva"], "a": r["amnen"], "u": r["unis"],
            "na": r["nationer"], "o": r["orter"], "f": r["flaggor"], "m": r["maxalder"], "r": r["route"], "g": r["malgrupp"], "v": r["vem"]}


def public(r, base):
    text, url, label = how_to_apply(r)
    return {**{k: r[k] for k in ("id", "namn", "orgnr", "kat", "niva", "amnen", "unis", "nationer", "orter", "flaggor", "malgrupp",
                                  "maxalder", "vem", "kontakt", "andamal")},
            "url": f"{base}/stiftelse/{r['slug']}/", "sa_soker_du": {"text": text, "lank": url},
            "kalla": "Länsstyrelsernas stiftelseregister"}


def jsonld(r, base, how):
    funder = {"@type": "Organization", "name": r["namn"], "identifier": r["orgnr"],
              "description": "Svensk stiftelse registrerad hos Länsstyrelsen"}
    if r["kontakt"]["adress"]:
        funder["address"] = {"@type": "PostalAddress", "streetAddress": r["kontakt"]["adress"], "addressCountry": "SE"}
    return {
        "@context": "https://schema.org", "@type": "MonetaryGrant", "name": r["namn"],
        "description": r["vem"] + " " + r["andamal"][:500], "url": f"{base}/stiftelse/{r['slug']}/",
        "funder": funder, "inLanguage": "sv", "isBasedOn": "https://stiftelser.lansstyrelsen.se/",
        "potentialAction": {"@type": "ApplyAction", "description": how[0], "target": how[1]},
    }


def paginate(items, size=PAGE):
    return [items[i:i + size] for i in range(0, len(items), size)] or [[]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "stiftelser.json"))
    ap.add_argument("--out", default=str(ROOT / "dist"))
    ap.add_argument("--base-url", default="https://stipendex.se")
    ap.add_argument("--preview", action="store_true", help="Relativa länkar med index.html, för förhandsvisning utan webbserver")
    a = ap.parse_args()
    base = a.base_url.rstrip("/")
    out = pathlib.Path(a.out)
    if out.exists(): shutil.rmtree(out)
    (out / "api" / "stiftelse").mkdir(parents=True)

    rows = sorted(load(a.data), key=lambda r: r["namn"].lower())
    today = dt.date.today().isoformat()
    env = Environment(loader=FileSystemLoader(str(ROOT / "site" / "templates")), autoescape=select_autoescape(["html"]))
    env.filters["tal"] = lambda n: f"{n:,}".replace(",", "\u202f")
    env.globals.update(SITE=SITE, BASE=base, TODAY=today, UNIS=UNIS, N_TOTAL=len(rows), slugify=slugify)
    urls = []

    def write(path, tpl, **ctx):
        depth = 0 if path == "/" else path.strip("/").count("/") + 1
        rel = "../" * depth

        def link(target):
            t = target.lstrip("/")
            if a.preview:
                return rel + (t + "index.html" if (t == "" or t.endswith("/")) else t)
            return "/" + t

        ctx.update(link=link, rel=rel if a.preview else "/")
        p = out / path.strip("/") / "index.html" if not path.endswith(".html") else out / path.strip("/")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(env.get_template(tpl).render(path=path, **ctx), encoding="utf-8")
        urls.append(base + path)

    # Hubbar
    by_uni, by_subj, by_nat = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in rows:
        for u in r["unis"]: by_uni[u].append(r)
        if r["route"] in UNIS and r["route"] not in r["unis"]: by_uni[r["route"]].append(r)
        for s in r["amnen"]: by_subj[s].append(r)
        for n in r["nationer"]: by_nat[n].append(r)

    # Stiftelsesidor
    for r in rows:
        how = how_to_apply(r)
        related = []
        for key, group in ([(u, by_uni[u]) for u in r["unis"][:1]] + [(s, by_subj[s]) for s in r["amnen"][:1]]):
            related += [x for x in group if x["id"] != r["id"]][:6]
        write(f"/stiftelse/{r['slug']}/", "stiftelse.html", r=r, how=how, ld=json.dumps(jsonld(r, base, how), ensure_ascii=False),
              related=related[:8], nation_url=NATION_URL)
        (out / "api" / "stiftelse" / f"{r['id']}.json").write_text(json.dumps(public(r, base), ensure_ascii=False), encoding="utf-8")

    def hub(prefix, title, intro, items, crumbs):
        pages = paginate(items)
        for i, chunk in enumerate(pages, 1):
            path = prefix if i == 1 else f"{prefix}sida/{i}/"
            write(path, "lista.html", title=title, intro=intro, items=chunk, page=i, pages=len(pages), prefix=prefix,
                  total=len(items), crumbs=crumbs)

    uni_list = []
    for code, u in UNIS.items():
        items = by_uni.get(code, [])
        uni_list.append((code, u, len(items)))
        hub(f"/larosate/{code.lower()}/", f"Stipendier vid {u['name']}",
            f"{len(items)} stiftelser i registret är knutna till {u['name']}. {u['how']}", items, [("Lärosäten", "/larosate/")])
    write("/larosate/", "larosaten.html", uni_list=uni_list, nations=sorted(by_nat.items()), nation_count={k: len(v) for k, v in by_nat.items()})
    for n, items in by_nat.items():
        hub(f"/nation/{slugify(n)}/", f"Stipendier för {n}", f"{len(items)} stiftelser nämner {n} i sitt ändamål.", items,
            [("Lärosäten", "/larosate/")])
    subj_list = []
    for s in SUBJECTS:
        items = by_subj.get(s, [])
        subj_list.append((s, slugify(s), len(items)))
        hub(f"/amne/{slugify(s)}/", f"Stipendier inom {s}", f"{len(items)} stiftelser delar ut stipendier eller bidrag inom {s}.", items,
            [("Ämnen", "/amne/")])
    write("/amne/", "amnen.html", subj_list=subj_list)
    bidrag = [r for r in rows if r["kat"] == "bidrag"]
    hub("/bidrag/", "Bidrag från stiftelser", f"{len(bidrag)} stiftelser ger ekonomiskt stöd till enskilda personer utanför studierna, till exempel vid sjukdom, ålder eller ekonomiskt behov.",
        bidrag, [])
    hub("/alla/", "Alla stiftelser", f"Alla {len(rows)} stiftelser som delar ut stipendier eller bidrag till enskilda.", rows, [])

    cfg = {"unis": {k: {"name": u["name"], "city": u["city"], "how": u["how"], "url": u["url"]} for k, u in UNIS.items()},
           "nations": {c: sorted(v) for c, v in NATIONS.items()}, "nationUrl": NATION_URL, "subjects": list(SUBJECTS),
           "aid": list(AID), "lands": LANDS_UI}
    write("/", "index.html", uni_list=uni_list, subj_list=subj_list, cfg=json.dumps(cfg, ensure_ascii=False),
          n_stip=len(rows) - len(bidrag), n_bidrag=len(bidrag))
    write("/404.html", "404.html")
    write("/om/", "om.html")
    write("/for-ai/", "for-ai.html", n=len(rows))

    # Agentlager
    (out / "api" / "index.json").write_text(json.dumps([compact(r) for r in rows], ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (out / "api" / "stiftelser.json").write_text(json.dumps({"kalla": "Länsstyrelsernas stiftelseregister, bearbetat av Stipendex",
                                                              "uppdaterad": today, "licens": "Fri att återanvända, ange Länsstyrelsen och Stipendex som källa",
                                                              "antal": len(rows), "stiftelser": [public(r, base) for r in rows]},
                                                             ensure_ascii=False), encoding="utf-8")
    (out / "llms.txt").write_text(env.get_template("llms.txt").render(uni_list=uni_list, subj_list=subj_list, n=len(rows), ex_id=rows[0]["id"] if rows else "",
                                                                    n_bidrag=len(bidrag)), encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    (out / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")
    shutil.copytree(ROOT / "site" / "static", out / "static")
    if base.endswith("stipendex.se"):
        (out / "CNAME").write_text("stipendex.se\n")
    (out / ".nojekyll").write_text("")
    print(f"Byggde {len(urls)} sidor och {len(rows)} API-poster till {out}")


if __name__ == "__main__":
    main()
