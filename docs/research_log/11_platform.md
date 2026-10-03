# Research log: Domain 11, Platform (2026-10-03)

* No `user_supplied/` material, so there are no official AC pipeline documents (car_pipeline PDF, AC Audio Pipeline PDF, FMOD template, formula_k sample data). All Kunos-side facts are community-reported until they are checked against the AC SDK on the user's PC.
* `gh api` to the CSP repos was refused (repo access not enabled for this session). A public `git clone --depth 1` into the git-ignored `cache/repos/` worked:
  * acc-extension-config @7084c197 and its wiki @19048685
  * acc-lua-sdk @7cf60f5a and its wiki
  * acc-lua-examples @51b25318
  * gro-ove/actools (Content Manager) @e5e5c94b
  * moppius/blender-assetto-corsa-tools @5f0c163c
  * zgushonka/ac_scripts @f43aa876
  
  These are the `cache_file`s in `vehicle_data/platform.json`.
* Fetched with `scripts/fetch_page.py` (200): cup.acstuff.club docs (a mirror of the CSP wiki); assettocorsamods.net threads 1019 (first car guide), 1163 (sound guide, pages 1–3), 1122 (KnSusEditor) and 2498 (FBX animation); GTPlanet posts 14358983 and 14359573; Automation forum p=80311; Steam discussion 494632768627956990 (no useful content); the Kunos official forum index and the sounds, physics and 3D modding subforums.
* Blocked, not worked around:
  * Kunos forum thread "FMod official project v1.9" (37827): **HTTP 403**.
  * overtake.gg suspension thread: **bot challenge**.
  * raw.githubusercontent.com for zgushonka README: 404 at the guessed path (cloned instead).
* Searches (WebSearch, 10): CSP StateCar fields; Kunos SDK engine.ini turbo docs; FMOD 1.08.12 (×2); Kunos SDK docs/ksEditor; COAST_REF/BOOST_THRESHOLD; REFERENCE_RPM comment text; WBCAR coordinates/axis sign; KN5 axis/WHEEL_LF sign; ksanim pipeline; DDS formats.
* `vehicle_data/platform.json` has 30 parameters (2 unknown: `ac_axis_x_sign` and `csp_min_version_visual_car_script`). It was built by a one-off builder (`scratchpad/build_platform.py`, outside the repo because Domain 11 owns no script path) that asserts every evidence fragment is present, whitespace-normalised, in its `cache_file` before recording it. `dbutil.py check`: OK.
* Main open items for the user's PC:
  1. The sign of AC +X: read WHEEL_LF's X in ksEditor or the CM showroom.
  2. The FMOD version line and the event/parameter list in `AC Audio Pipeline 1.9.pdf` and the template project.
  3. The `engine.ini` coast, limiter and inertia keys in the formula_k comments.
  4. Whether power.lut is crank torque.
