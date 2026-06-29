# Web platform (backend + frontend)

A simple platform so bidders paste a JD and get a tailored resume + cover letter, while
your `LLM_API_KEY` stays server-side. Bidders sign in with a shared access token, submit
JDs, and download the generated files. Same pipeline as the CLI (`ats.pipeline.process_jd`).

## Run it (on your machine)

1. Set an access token in `.env` (any long random string):
   ```
   ACCESS_TOKEN=choose-a-long-random-string
   ```
   (Leave it blank only for local dev — that disables auth.)

2. Start the server from the project root:
   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
   ```

3. Open http://localhost:8000 , enter the token, paste a JD, click **Generate**.

## Deploy on your own server (VPS / container)

The code is deploy-ready; on a Linux host do the one-time setup, then start it:

```bash
pip install -e .
python -m playwright install chromium            # the browser
python -m playwright install-deps chromium        # Linux OS libs Chromium needs
# set env vars: LLM_API_KEY=...  ACCESS_TOKEN=...  (PORT optional)
python -m backend                                 # honors $HOST/$PORT, defaults 0.0.0.0:8000
```

- `python -m backend` reads `$PORT`/`$HOST`, so it works on hosts that inject a port.
- Chromium is launched with `--no-sandbox --disable-dev-shm-usage`, so PDF works in
  containers / as root without extra flags.
- Set env vars directly in your host's dashboard, or keep using `.env` — both work.
- It needs a writable disk (for `output/`) and Chromium, so a normal server/VPS/container
  is required (not Vercel/Netlify serverless).

## Let bidders reach it

The backend runs on your machine, so expose it to the internet with a tunnel:

- **Cloudflare Tunnel:** `cloudflared tunnel --url http://localhost:8000`
- **ngrok:** `ngrok http 8000`

Share the public URL + the access token with your bidder. They open the URL, sign in, and
bid. Everything (LLM calls, PDF rendering, the `output/` folder, `applications.csv`) stays
on your machine.

## What bidders can do
- Paste a JD and generate (auto-picks the best candidate, or pick one from the dropdown).
- See live activity ("Resume for <profile> -> <company> generated").
- Browse the applications table and download each Resume/Cover PDF.

Duplicate protection is built in: the same profile won't apply to the same company twice —
it auto-switches to the next-best candidate (tick **force** to override).

## API (token via `X-Access-Token` header)
- `POST /api/bid`            `{ "jd_text": "...", "profile_id": null, "force": false }`
- `GET  /api/applications`   the log (newest first)
- `GET  /api/profiles`       available candidates
- `GET  /api/files/<folder>/<filename>`   download a generated file

## Notes / limits (v1)
- Generation is serialized (one bid at a time) so Chromium/PDF and the CSV stay consistent.
- This backend needs a real filesystem + Chromium, so it can't run on Vercel serverless —
  host it yourself (your machine, or a small VPS). A static frontend could later live on
  Vercel pointing at this backend's URL.