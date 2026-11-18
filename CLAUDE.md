# Stipendex – instruktioner för Claude Code

Stipendex (stipendex.se) är ett gratis, oberoende register över svenska stiftelser som delar ut **stipendier** och **bidrag** till enskilda. Målet är trafik från både människor (Google) och AI-agenter (ChatGPT, Claude, Perplexity), och sajten ska kännas trovärdig för båda.

Ägare: Erik. Han skriver informellt på svenska och vill ha praktiska, färdiga lösningar. All text på sajten är på svenska.

## Hur det fungerar

```
pipeline/fetch.py   hämtar Länsstyrelsens register (JSON, ~22 MB) -> data/raw/stiftelser.json (UTAN persondata)
pipeline/tag.py     tolkar ändamål till villkor (regelbaserat)     -> data/stiftelser.json
pipeline/config.py  ALLA regler och listor: lärosäten, nationer, ämnen, orter, målgrupper
site/build.py       statisk sajtgenerator (Jinja2)                 -> dist/
site/templates/     sidmallar
site/static/        style.css, app.js (matchningen sker i besökarens webbläsare)
tests/              pytest
.github/workflows/build.yml  varje natt: fetch -> tag -> test -> build -> GitHub Pages
```

Lokalt:
```bash
pip install -r requirements.txt
python pipeline/fetch.py          # kräver nätåtkomst till stiftelser.lansstyrelsen.se
python pipeline/tag.py            # eller: --input data/sample/stiftelser_sample.json (2 945 stiftelser, för utveckling)
python -m pytest -q tests
python site/build.py --base-url http://localhost:8000 && (cd dist && python -m http.server 8000)
```

## Absoluta regler

1. **Ingen persondata.** Källfilen har `ROLLER` (styrelseledamöter med namn och födelsedatum). Den kastas i fetch.py och får aldrig sparas, committas, visas eller exporteras. Privatpersoner som står som c/o döljs (`is_person` i tag.py). Testet `test_no_personal_data_fields` ska alltid passera.
2. **Ange källa.** Villkoret för öppna data är att Länsstyrelsen anges som källa. Gör det i sidfot, API och llms.txt.
3. **Originaltexten gäller.** Visa alltid stiftelsens ändamål ordagrant bredvid tolkningen, och skriv att tolkningen kan vara fel.
4. **Låtsas inte vara myndighet.** Inget som liknar Länsstyrelsens "Stiftelsesök" i namn eller utseende.
5. **Hitta inte på deadlines.** Registret saknar datum. Visa bara datum vi har en källa för (lärosätenas sidor), med källan.

## Datan

- 17 357 aktiva stiftelser (pensions-, personal- och kollektivavtalsstiftelser ingår inte i registret).
- `kat`: stipendium | bidrag | ej_individ | intern | slakt | nominering | skola | ovrigt. Sajten visar bara stipendium och bidrag.
- `route`: lärosäteskod (UU, LU, SU …) om stiftelsen förvaltas av lärosätet, `nation`, annars `direkt` (kontakta stiftelsen).
- Uppsala och Lund har studentnationer; nationsregler finns i config.NATIONS.
- Tolkningen är regelbaserad och ungefärlig (mätt ca 50–70 % precision på riktade träffar i prototypen). Förbättra hellre reglerna i config.py med tester än att lägga till specialfall i tag.py.

## Agentlagret (viktigt för trafiken)

- `/api/stiftelser.json` hela registret, `/api/stiftelse/<id>.json` per stiftelse, `/api/index.json` för matchningen.
- `/llms.txt`, `/sitemap.xml`, `robots.txt` (tillåter alla, även AI-crawlers).
- JSON-LD `MonetaryGrant` på varje stiftelsesida.
- Fasta adresser: `/stiftelse/<namn-slug>-<id>/`. Id kommer från Länsstyrelsen och ändras inte. Byt aldrig URL-format utan redirects.

## Nästa steg (backlog)

1. Koppla domänen stipendex.se (GitHub Pages: Settings → Pages → Custom domain; DNS: A-poster mot GitHub Pages + `www` CNAME).
2. Deadlinedatabas: `data/deadlines.yaml` per stiftelse-id/lärosäte med källa, visa på stiftelsesidan.
3. Fler lärosäten i config.UNIS (Örebro, Karlstad, Luleå, Handelshögskolan …) med ansökningsinfo.
4. Bättre tolkning: utvärdera mot ett handgranskat urval (`data/sample/`), mät precision per fält.
5. Engelsk version (`/en/`) när svenska fungerar.
6. Intäkter senare: sponsrade stipendier (tydligt märkta), B2B till skolor/kommuner, deadline-bevakning. Aldrig lån till studenter med ekonomiskt behov.

## Stil

Lugn, saklig, akademisk design (Newsreader + IBM Plex Sans, mörkgrönt på ljus botten, mörkt läge). Inga emojis, inga kryptoliknande effekter. Svenska utan anglicismer i UI-text.
