# Preflight — 2026-10-03

Kept short, per spec. Each line is what actually happened in this sandbox.

## Network and tools

| Check | Target | Result |
|---|---|---|
| Honda Canada | `https://www.honda.ca/en/civic_hatchback/specs` (rendered, headless Chromium) | **200, reachable.** The live page now shows the *current* Civic Hatchback line (Sport, Sport Hybrid, Sport Touring Hybrid, 2.0 L), not the 2024 car. 2024 data must come from Honda Canada's newsroom (`hondanews.ca`, 200), other Honda Canada pages, owner's manuals and press kits. |
| Honda US | `automobiles.honda.com/2024/civic-hatchback/specs-features-trim-comparison` | **403 (Akamai "Access Denied")**, both plain and rendered. Site-side block; not worked around. `hondanews.com` (US press site) returns **200**. |
| NHTSA | `www.nhtsa.gov/vehicle/2024/HONDA/CIVIC/5%2520HB/FWD` | **403 (Akamai edge "Access Denied")**, plain and rendered. Not worked around. |
| NHTSA API | `api.nhtsa.gov/SafetyRatings/...civic hatchback` and `vpic.nhtsa.dot.gov` | **200.** Returns `2024 Honda CIVIC HATCHBACK 5 HB FWD`, VehicleId 19595. vPIC VIN decoding works. |
| Other government | `tc.canada.ca`, `nrcan.gc.ca`, `fcr-ccc.nrcan-rncan.gc.ca`, `fueleconomy.gov` | **200** each. |
| Tire maker | `goodyear.com/en-ca`, `michelin.ca/en` | **200** each. |
| Car magazine | `motortrend.com` (200), `caranddriver.com` (serves pages; two URLs I guessed returned 404 and were not used) | Reachable by direct fetch. **The built-in WebSearch tool refuses `caranddriver.com`, `motortrend.com`, `roadandtrack.com` as search domains** (publisher opt-out of Anthropic's search agent). Their `robots.txt` does not name Anthropic agents; direct fetches honor `robots.txt` (`scripts/fetch_page.py` checks it before every request). |
| Forum | `civicxi.com/forum/` | **200.** |
| YouTube | `youtube.com/shorts/BDuJz3FTOpU`, oEmbed API | **200.** Metadata readable: title "11th Gen Civic 1.5L muffler and resonator delete. Burbles.", channel `nycivic`, no description. The rendered watch page shows **"Sign in to confirm you're not a bot"** — playback is gated; not worked around. |
| Wayback Machine | `web.archive.org` | **Blocked**: egress proxy closes the tunnel (connection reset); the WebFetch tool also refuses it. Archived 2024 Honda pages are therefore unavailable. |
| Autotrader.ca editorial | `editorialsui.autotrader.ca` | **Blocked** by egress proxy (502 to CONNECT). `www.autotrader.ca` returns 200. |
| Web search | WebSearch tool | **Works.** |
| git push | `origin claude/zen-gates-3y0ani` | **Works** (spec commit pushed). |
| Headless browser | Playwright + pre-installed Chromium 1194 | Works after adding the egress proxy CA to the browser NSS store (`scripts/setup_env.sh`). TLS verification is not disabled anywhere. |
| PDF text | PyMuPDF, `pdftotext` | Installed. |
| Image/audio analysis | numpy, scipy, OpenCV, Pillow, soundfile, ffmpeg | Installed. |

## Verdict

Honda Canada and government sources (NHTSA API, Transport Canada, NRCan, EPA) are reachable, so per the spec the run continues without waiting. Blocked hosts are listed above and are not worked around; where they would have been the primary source, the affected records say so.

## user_supplied/

**Not present.** The repository contained no `user_supplied/` directory at the start of this run, so there are no first-hand notes, photos, measurements or recordings yet. `vehicle_data/user_measurements.json` is the template for adding them; the resolver gives them top precedence.
