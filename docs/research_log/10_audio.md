# 10 Audio: research log

Files: `audio/reference_database.json` (built by `scripts/domains/audio_build.py`),
`audio/OBSERVATIONS.md`, `scripts/domains/audio_yt_comments.py` (text-only comment reader:
it expands reply threads and blocks media requests). The thread was interrupted twice by usage
limits, and the work was rebuilt from the on-disk state.

## Sources opened
- Reference clip `youtube.com/shorts/BDuJz3FTOpU`: oEmbed JSON; rendered watch page; comments with
  reply threads expanded (`cache/pages/a189ed58f517a54d.txt`). Channel shorts and videos pages,
  plus the companion "cold start" short and the "35k mile walk around and cosmetic mod list" video.
- hondapartsnow.com: 2024 Civic exhaust-pipe and muffler listings; part pages 18307-T47-A51,
  18305-T47-A51, 18150-64A-L00, 18200-T20-A01; diagram T404B0200 (image in the git-ignored cache).
- MagnaFlow 19652 (manufacturer), Borla 140966 (manufacturer, rendered), Remark ST Link Loop
  (PRL and Kami Speed retailers), PLM muffler delete (Redline360), Borla and Remark YouTube
  pages (descriptions and comments).
- Wikipedia *Engine braking* (DFCO) and *Antilag system*; two HP Academy forum threads on
  pop-and-bang tuning.

## Found
- Stock ST hatch exhaust: one converter assembly (shared with all 1.5T trims and the Si), one
  centre in-line resonator, a Y-split and two rear mufflers (L and R, ST-specific part numbers,
  shared 6MT and CVT). Pipe diameter is **unknown**.
- Reference clip: muffler and resonator delete with **cats retained** and factory finishers (creator
  replies). Gearbox is **not documented**: commenters claim CVT, which is unverified. Tune, trim and
  intake are not documented. **Audio not accessed or analyzed.**
- Catalogued: 4 products (MagnaFlow, Borla, Remark, and PLM, which does not fit the ST) and
  13 clips by text only (5 manufacturer, 7 owner or shop, 1 stock POV). Weights: 1 high,
  3 medium, 6 low, 3 excluded. No stock-exhaust sound clip of a 6MT ST was confirmed as stock.
- The Borla page contradicts itself: 2.5 in in the description, "2.25\" Diameter System" in the
  feature list.

## Blocked or not done
- YouTube playback is behind a bot wall. Later watch-page loads returned **HTTP 429 / Google
  "sorry"** (not worked around); the MBRP clip description could not be read. A static re-fetch
  overwrote two rendered caches, so the reference clip's view and subscriber counts rely on the
  first render and `docs/PREFLIGHT.md`.
- YouTube search results are disallowed by robots.txt, so clips were found through WebSearch and
  related-video lists.
- honda.oempartsonline.com and hondapartsconnection.com: Cloudflare challenge (403).
- hondata.mobi forum: robots.txt disallows.
- borla.com static fetch: 403; the rendered fetch returned 200.
- The MagnaFlow-hosted mp4 sound clip states no licence, so it was catalogued by link only and
  not analyzed.

## Open questions
- Stock DFCO thresholds and timing on this ECU (`audio.overrun_fuel_cut_this_car`, unknown).
- Stock pipe diameter; catalyst count and position (a commenter's "secondary cat" is unverified).
- Gearbox and tune of the reference clip car.

## Leads for other domains
- Identity: a Remark-video commenter says the Canadian-spec Sport Hatchback has "the 1.5 T and
  the same diffuser and plastic exhaust tips as the Touring" (unverified). The PLM page says ST
  finishers are longer ("extended length of the exhaust tips"). Both affect which trims share the
  ST exhaust and rear valance.
- Visual (09): the HPD spoiler appears on the reference-clip car ("oem hpd spoiler from honda").
  It is not a factory ST feature, so that clip is not a clean visual reference.
- Engine and drivetrain: overrun fuel cut is unknown here too. "Some rev hang" is reported and is
  reduced by aftermarket calibration.
