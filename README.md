# Stipendex

Hitta stipendier och bidrag från svenska stiftelser. Bygger på Länsstyrelsernas öppna stiftelseregister, tolkar varje stiftelses ändamål och gör det sökbart för både människor och AI-agenter.

## Kom igång (Erik)

1. Skapa ett gratis konto på github.com.
2. Öppna den här mappen i Claude Code och be den: *"Skapa ett publikt repo stipendex på mitt GitHub-konto, pusha koden och slå på GitHub Pages med GitHub Actions som källa."* (GitHub Pages är gratis för publika repon. Vill du ha koden privat går Cloudflare Pages också gratis, be Claude Code byta.)
3. Kör workflowen "Hämta data, bygg och publicera" en gång manuellt (fliken Actions → Run workflow). Den hämtar hela registret och publicerar sajten.
4. Köp stipendex.se (och gärna stipendex.eu, hittastipendium.se). Be Claude Code koppla domänen.

Sajten uppdateras sedan automatiskt varje natt. Driften kostar 0 kr, bara domänerna.

## Utveckla lokalt

```bash
pip install -r requirements.txt
python pipeline/tag.py --input data/sample/stiftelser_sample.json
python site/build.py --base-url http://localhost:8000
cd dist && python -m http.server 8000
```

Se CLAUDE.md för struktur, regler och backlog.

Källa: Länsstyrelsernas stiftelseregister (öppna data).
