"""Hämtar Länsstyrelsernas stiftelseregister (öppna data) och sparar det utan persondata.

Källa: https://stiftelser.lansstyrelsen.se/Öppendata/Json  (uppdateras dagligen)
Villkor: fri vidareanvändning, ange Länsstyrelsen som källa.

VIKTIGT: Källfilen innehåller ROLLER (styrelseledamöter med namn och födelsedatum).
Den delen kastas här och får aldrig sparas, committas eller publiceras.

Körs: python pipeline/fetch.py  -> data/raw/stiftelser.json
"""
import json
import pathlib
import sys
import urllib.request

URL = "https://stiftelser.lansstyrelsen.se/%C3%96ppendata/Json"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw" / "stiftelser.json"

KEEP = {
    "ID": "id", "NAMN": "namn", "ORGNR": "orgnr", "COADRESS": "co", "ADRESS": "adr",
    "POSTNR": "postnr", "ORT": "ort", "TELEFON": "tel", "TYP": "typ", "LANKOD": "lan",
    "KOMMUNKOD": "kom", "ANDAMAL": "andamal",
}


def main() -> int:
    req = urllib.request.Request(URL, headers={"User-Agent": "Stipendex/1.0 (+https://stipendex.se/om/)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = json.loads(r.read().decode("utf-8-sig"))
    rows = []
    for item in raw["STIFTELSER"]:
        s = item["STIFTELSE"]  # item["ROLLER"] ignoreras med flit (persondata)
        row = {new: s.get(old) for old, new in KEEP.items()}
        row["ort"] = (row["ort"] or "").strip()
        rows.append(row)
    if len(rows) < 10000:
        print(f"Misstänkt få stiftelser ({len(rows)}), avbryter utan att skriva över.", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    print(f"Sparade {len(rows)} stiftelser till {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
