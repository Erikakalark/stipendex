"""Tolkar stiftelsernas ändamål till sökbara kriterier.

Regelbaserat (ingen AI behövs). Ger varje stiftelse:
  kat      stipendium | bidrag | ej_individ | intern | slakt | nominering | skola | ovrigt
  niva     student/doktorand/forskare/elev
  amnen    ämnesområden
  unis     lärosäten som nämns
  nationer studentnationer (Uppsala/Lund)
  orter    krav/företräde på ursprung
  flaggor  behov, man, kvinna, resa, bostad, meritkrav
  malgrupp bidragsmålgrupper (äldre, sjuka ...)
  route    hur man söker: lärosäteskod | nation | direkt
  vem      klarspråkssammanfattning

Körs: python pipeline/tag.py [--input data/raw/stiftelser.json] -> data/stiftelser.json
"""
import argparse
import json
import pathlib
import re
import unicodedata
from collections import Counter

from config import AID, DEMONYM, GAZ, LEVELS, LUND_SKANSKA, NATIONS, SUBJECTS, UNIS

UNI_CITIES = {"uppsala", "lund", "stockholm", "göteborg", "linköping", "umeå", "malmö"}
ROOT = pathlib.Path(__file__).resolve().parent.parent
PERSON_CO = re.compile(r"^[A-ZÅÄÖ][a-zåäöé\-]+(\s+[A-ZÅÄÖ]\.?)?(\s+[A-ZÅÄÖ][a-zåäöé\-]+){1,2}$")
ORG_WORDS = re.compile(r"nation|universitet|förvaltning|\bAB\b|kyrkan|stift|pastorat|region|landsting|kommun|förening|förbund|akademi|bank|SEB|advokat|byrå|stiftelse|institut|SLU|KTH|kår|tidning|förlag|riddarhus|museum|sällskap|revision|ekonomi|kansli|institution|samfund|högskola", re.I)


def low(s):
    return (s or "").lower().replace("\xad", "").replace("w", "v").replace("  ", " ")


def slugify(s):
    s = unicodedata.normalize("NFKD", s.lower().replace("å", "a").replace("ä", "a").replace("ö", "o"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70]


def is_person(co):
    c = (co or "").strip()
    return bool(c) and not ORG_WORDS.search(c) and bool(PERSON_CO.match(c))


def flags_of(t):
    f = set()
    if re.search(AID["ekonomiskt behov"], t): f.add("behov")
    if re.search(r"\bmanlig|\byngling|\bmän\b|gosse|pojk|söner", t) and not re.search(r"kvinn|flick|döttrar|manlig eller kvinnlig|manliga och kvinnliga|manlig och kvinnlig|män och kvinnor", t):
        f.add("man")
    if re.search(r"kvinnlig|kvinn|flick|döttrar|ogift", t) and not re.search(r"manlig|yngling|man eller kvinna|män och kvinnor", t):
        f.add("kvinna")
    if re.search(r"resa|resor|resestipend|utlandsvistelse|utrikes|utlandet|utomlands|studieresa", t): f.add("resa")
    if re.search(r"bostad|bostadsrum|lägenhet|hyreskostnad|elevhem|studentrum", t): f.add("bostad")
    if re.search(r"flit|förtjän|framstående|skicklig|begåv|goda studieresultat|lovande|duktig", t): f.add("meritkrav")
    if re.search(r"adlig|adel", t): f.add("foretrade_adel")
    elif re.search(r"släkt|ättling|avkomling", t): f.add("foretrade_slakt")
    return f


def category(t, levels, aid):
    if re.search(r"anställd|anställda|personal(?:en)? vid|befattningshavare|tjänstem[aä]n|medarbetare", t): return "intern"
    if re.search(r"släkt|ättling|avkomling|bröstarvinge|donatorns? barn|barnbarn", t) and not re.search(
            r"företräde|i första hand|främst|i andra hand|i brist på|i mån av|därefter|om sådan saknas|om ingen|såvida", t):
        return "slakt"
    stripped = t.replace("utan föregående ansökan", "").replace("utan ansökan", "")
    if re.search(r"utan (?:föregående )?ansökan|nominer|belöning|\bpris\b|\bpriset|prisbelön|medalj|premie", t) and not re.search(r"sökande|ansöka|ansökan", stripped):
        return "nominering"
    indiv = levels or re.search(r"stipend|bidrag till enskild|resebidrag|ungdom|person|enskilda|understöd", t) or aid
    if not indiv: return "ej_individ"
    if re.search(r"(?:elev|lärjung)(?:er)? (?:vid|i|inom|på) ", t) and not re.search(r"universitet|högskola|nation|student", t): return "skola"
    if re.search(r"^(?:till|för) (?:främjande|fromma|förmån för) (?:av )?(?:verksamhet|föreningen|museets|kyrkan|biblioteket|institutionen|nationens verksamhet)", t):
        return "ej_individ"
    if levels: return "stipendium"
    if aid: return "bidrag"
    return "ovrigt"


def origins(raw, t):
    tn = re.sub(r"[\wåäö\-]+\s+(?:och|eller|,)?\s*[\wåäö\-]*\s*nation(?:er|en|erna)?", " ", t)
    for u in UNIS.values():
        tn = re.sub(u["rx"], " ", tn)
    tn = re.sub(r"(?:vid|i|inom) (?:universitetet|högskolan|akademien) i \w+|\w+ (?:kommun|stift|landsting)s? (?:förvalt\w*)", " ", tn)
    out = set()
    if re.search(r"född|födda|uppvuxen|uppvuxna|bördig|härstamm|hemma|bosatt|mantalsskriv|kyrkobokför|folkbokför|från|infödd|landsm|ursprung|härkomst|verksam i|inom .{0,20}(?:län|kommun|socken|församling)", tn):
        for g in GAZ:
            gl = g.lower()
            if gl in UNI_CITIES:
                if re.search(r"(?:född|födda|uppvuxen|uppvuxna|bosatt|bosatta|hemma|från|infödd|mantalsskriv\w*|kyrkobokför\w*|folkbokför\w*)\s+(?:\w+\s+){0,3}" + gl, tn):
                    out.add(g)
            elif re.search(r"\b" + gl + r"(?:s|ländsk|länning)?\b", tn):
                out.add(g)
    for dk, land in DEMONYM.items():
        if dk in tn: out.add(land)
    return sorted(out)


def vem(r):
    L = {"student": "studenter", "doktorand": "doktorander", "forskare": "forskare", "elev": "elever"}
    parts = []
    if r["niva"]: parts.append(", ".join(L[l] for l in r["niva"]))
    if r["malgrupp"] and not r["niva"]: parts.append(", ".join(r["malgrupp"]))
    if r["unis"]: parts.append("vid " + " eller ".join(UNIS[u]["name"] for u in r["unis"]))
    if r["nationer"]: parts.append("medlem i " + " eller ".join(r["nationer"]))
    if r["amnen"]: parts.append("inom " + ", ".join(r["amnen"]))
    if r["orter"]: parts.append("med anknytning till " + ", ".join(r["orter"]))
    f = r["flaggor"]
    if "behov" in f and not (r["malgrupp"] == ["ekonomiskt behov"] and not r["niva"]): parts.append("med ekonomiskt behov")
    if "meritkrav" in f: parts.append("med goda studieresultat")
    if r["maxalder"]: parts.append(f"under ca {r['maxalder']} år")
    if "resa" in f: parts.append("för resa eller utlandsstudier")
    if "bostad" in f: parts.append("som stöd till boende")
    return ("För " + ", ".join(parts) + ".") if parts else "Ändamålet anger inga särskilda krav på mottagaren."


def tag(x):
    raw = (x.get("andamal") or "").strip()
    t = low(raw)
    co = (x.get("co") or "").strip()
    lc = low(co)
    levels = sorted(k for k, rx in LEVELS.items() if re.search(rx, t))
    aid = sorted(k for k, rx in AID.items() if re.search(rx, t))
    unis = [k for k, u in UNIS.items() if re.search(u["rx"], t) or re.search(u["rx"], lc)]
    route = next((k for k, u in UNIS.items() if re.search(u["rx"], lc)), None)
    nat = set()
    ctx = low(" ".join([t, lc, x.get("ort") or ""]))
    for city, nations in NATIONS.items():
        in_city = city in ctx or (city == "uppsala" and "upsala" in ctx) or any(UNIS[u]["city"] == city for u in unis)
        if not in_city: continue
        for n, rx in nations.items():
            if re.search(rx, t) or re.search(rx, lc): nat.add(n)
        if city == "lund" and re.search(r"skånska nation", t) and not re.search(r"sydskånsk", t):
            nat.update(LUND_SKANSKA)
    if not route and "nation" in lc: route = "nation"
    m = re.search(r"(?:inte|ej|icke)\s+(?:har\s+)?(?:fyllt|uppnått|passerat)\s+(\d\d)|(?:under|högst|max(?:imalt)?|upp till)\s+(\d\d)\s+år", t)
    maxage = int(next(g for g in m.groups() if g)) if m else None
    flags = flags_of(t)
    kat = category(t, levels, aid)
    hide = is_person(co)
    r = {
        "id": x["id"], "slug": f"{slugify(x['namn'] or 'stiftelse')}-{x['id']}", "namn": (x["namn"] or "").strip(),
        "orgnr": x.get("orgnr"), "kat": kat, "niva": levels, "amnen": sorted(k for k, rx in SUBJECTS.items() if re.search(rx, t)),
        "unis": unis, "nationer": sorted(nat), "orter": origins(raw, t), "flaggor": sorted(flags), "malgrupp": aid,
        "maxalder": maxage, "route": route or "direkt",
        "kontakt": {
            "co": "" if hide else co,
            "adress": "" if hide else " ".join(p for p in [(x.get("adr") or "").strip(), (x.get("postnr") or "").strip(), x.get("ort") or ""] if p),
            "telefon": "" if hide else (x.get("tel") or "").strip(),
        },
        "andamal": raw,
    }
    r["vem"] = vem(r)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(ROOT / "data" / "raw" / "stiftelser.json"))
    ap.add_argument("--output", default=str(ROOT / "data" / "stiftelser.json"))
    a = ap.parse_args()
    rows = [tag(x) for x in json.load(open(a.input, encoding="utf-8"))]
    pathlib.Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    json.dump(rows, open(a.output, "w", encoding="utf-8"), ensure_ascii=False)
    print(len(rows), Counter(r["kat"] for r in rows))


if __name__ == "__main__":
    main()
