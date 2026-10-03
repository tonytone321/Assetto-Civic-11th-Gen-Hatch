# Platform constraints — Assetto Corsa + Custom Shaders Patch (Domain 11)

Researched 2026-10-03. Machine-readable records: `vehicle_data/platform.json` (30 `platform.*` parameters, every quote checked by script against the cached text). Log: `docs/research_log/11_platform.md`.

**Status legend**

* **confirmed**: stated verbatim in official documentation from the software's own developer (Custom Shaders Patch GitHub wiki or Lua SDK for CSP features; nothing official from Kunos was reachable online, see below).
* **community-reported**: stated verbatim in a community source (assettocorsamods.net guides, Content Manager source code, community exporters, forum posts). Usually reliable, but check it against the official AC SDK documents on your PC.
* **unconfirmed**: believed or inferred but not found stated in any source opened. It needs checking on your Windows PC.

**The key gap: no official Kunos documentation was available.** Nothing was in `user_supplied/`. The Kunos documents (`sdk/dev/car_pipeline*.pdf`, `sdk/audio/AC Audio Pipeline 1.9.pdf`, the FMOD template project and the commented `formula_k` sample car in `sdk/dev/content/cars/`) ship only inside your AC install. The Kunos forum thread "FMod official project v1.9" returned **HTTP 403** and was not worked around. Every Kunos-side fact below is therefore at best community-reported until you check it against those files.

## Sources used

| id | what | class |
|---|---|---|
| csp-wiki-* | CSP wiki, https://github.com/ac-custom-shaders-patch/acc-extension-config/wiki (git clone @19048685, 2026-06-11; mirrored at cup.acstuff.club/docs/csp) | A (CSP) |
| csp-lua-* | CSP Lua SDK https://github.com/ac-custom-shaders-patch/acc-lua-sdk (@7cf60f5a) and examples https://github.com/ac-custom-shaders-patch/acc-lua-examples (@51b25318) | A (CSP) |
| acm-first-car | "Your FIRST car in Assetto Corsa – Basic Guide", assettocorsamods.net thread 1019 (edited with feedback from a Kunos 3D artist) | C |
| acm-sound-guide | "Start with Sound Modding – Quick Guide", assettocorsamods.net thread 1163 | C |
| acm-knsuseditor, acm-fbx-anim | assettocorsamods.net threads 1122, 2498 | C |
| cm-* | Content Manager source, https://github.com/gro-ove/actools (@e5e5c94b) | C |
| blender-kn5 | https://github.com/moppius/blender-assetto-corsa-tools exporter (@5f0c163c) | C |
| gtp-dds | GTPlanet AC mods thread, post 14358983 | C (low) |

---

## 1. Files a loadable car needs

| Point | Status | Source and quote |
|---|---|---|
| Car folder `content/cars/<id>/` holding `<id>.kn5` (name identical to the folder, lower case), `collider.kn5`, `data/` (or `data.acd`), `sfx/`, `skins/<skin>/`, `ui/ui_car.json` + `ui/badge.png`, `animations/`, `texture/`; plus `driver_base_pos.knh`, `body_shadow.png`, `tyre_0..3_shadow.png` | community-reported | acm-first-car: "the name of the exported file must be identical to the name of car folder"; cm-workshop checks `collider.kn5`, `driver_base_pos.knh`, `body_shadow.png`, `tyre_?_shadow.png`, `ui/badge.png`, `sfx/{Id}.bank` |
| Data files without which the car will not load: `aero.ini` (+ wing `_CL`/`_CD` LUTs), `cameras.ini`, `car.ini`, `driver3d.ini`, `engine.ini` + `power.lut`, `lods.ini`, `suspensions.ini`, `tyres.ini` (+ LUTs). Needed for sane behaviour: `brakes.ini`, `colliders.ini`, `drivetrain.ini`, `setup.ini`. Optional: `analog_instruments.ini`, `digital_instruments.ini`, `lights.ini`, `mirrors.ini`, `sounds.ini`, `electronics.ini`, `ai.ini`, `damage.ini`, `flames.ini`, `throttle.lut`, `blurred_objects.ini`, `wing_animations.ini` | community-reported | acm-first-car: "MANDATORY (without them, the car will not load and game will crash)" |
| `data/` is packed into `data.acd` for release, with the encryption key taken from the car folder name. An unpacked `data/` also loads. | community-reported | cm-acd: `Path.GetFileName(Path.GetDirectoryName(acdFilename))`; acm-first-car: "the entire folder is packed in one single file called data.acd" |
| Car folder name at most 32 characters, lower-case latin | community-reported | acm-first-car: "max length for car folder name: 32" |
| Sound: `sfx/<id>.bank` + `sfx/GUIDs.txt` (the GUID lines name `event:/cars/<id>/...`) | community-reported | cm-workshop, cm-sfx regex `event:/cars/(\w+)/e` |
| CSP per-car config lives at `content/cars/<id>/extension/ext_config.ini` | confirmed | csp-wiki-guessed: "if you’re working on a new car, use “assettocorsa/content/cars/\<carfolder\>/extension/ext_config.ini”" |
| Exact official required-file list | **unconfirmed** | Read `sdk/dev/car_pipeline*.pdf` on your PC |

## 2. Node naming

| Nodes | Status | Source |
|---|---|---|
| `WHEEL_LF`, `WHEEL_RF`, `WHEEL_LR`, `WHEEL_RR` dummies, each visual wheel parented to its dummy, never scaled | community-reported | acm-first-car: "Make every mesh a child to its respective dummy !" |
| `SUSP_xx` (missing ones "Might cause crashes, especially in showroom"), optional `HUB_xx`, `DISC_xx` or `DISC_xx_ANIM` | community-reported | cm-wheels `GetWheelNodesNames()`; CarModelRepair.cs |
| `COCKPIT_HR` / `COCKPIT_LR`, `STEER_HR` / `STEER_LR`, `SHIFT_HD` / `SHIFT_LD` (high/low-res switch), `CINTURE_ON` / `CINTURE_OFF` (seatbelt) | community-reported | cm-utils `SetCockpitLrActive`, `SetSeatbeltActive` |
| `DAMAGE_GLASS*` | community-reported (weak) | cm Kn5RenderableList.cs line 23 |
| Doors (`DOOR_L` / `DOOR_R`), wipers, mirrors, fuel cap, the driver-arm/hand nodes and blurred-rim names (`blurred_objects.ini`) | **unconfirmed** | `DOOR_L, DOOR_R` appear only in a CSP config template line (ks_audi_r8_plus.ini). Check the pipeline PDF. |
| Lights and emissives are not fixed names: `lights.ini` / CSP `ext_config` reference meshes by name | community-reported | CSP Lights/Emissive wiki pages use `MESHES = ...` |

## 3. LOD and collider structure

| Point | Status | Source |
|---|---|---|
| **"One KN5 per LOD plus a collider KN5": consistent with every source.** `data/lods.ini` has `[LOD_0..n]` with `FILE`, `IN`, `OUT` (optional `[LOD_HR]`); `[COCKPIT_HR] DISTANCE_SWITCH` swaps the HR/LR cockpit; `collider.kn5` sits separately in the car root | community-reported | cm-carobject: `lods.GetSections("LOD").Append(lods["LOD_HR"]).Select(x => x.GetNonEmpty("FILE"))`; CarGenerateLodsDialog `section.Set("IN", …)`/`("OUT", …)`; cm-analyzer `["COCKPIT_HR"].GetFloat("DISTANCE_SWITCH", 0f)` |
| Collider: very low poly ("40-60 triangles"), material named `GL` with GL shader, no vertex below the car floor, pivot at ground 0 | community-reported | acm-first-car (quoted in platform.json) |
| CM quality heuristics (not engine limits): 4 LODs; LOD_1 ≤ 45k tris, LOD_2 ≤ 11k, LOD_3 ≤ 5k; LOD_0 OUT ≈ 15 m, LOD_1 OUT 25–60 m, LOD_2 OUT 60–250 m; COCKPIT_LR switch ≈ 7 m | community-reported | cm-analyzer |
| Hard polygon or texture limits per LOD | **unconfirmed** | not found |

## 4. FBX and texture requirements

| Point | Status | Source |
|---|---|---|
| FBX "up to 2014/2015 format (2016 is unsupported)" for ksEditor | community-reported (2017) | acm-first-car |
| Scene units in meters; Blender export "scale" toggle off | community-reported | acm-first-car: "Set scale to Meters." |
| Every object needs a material/texture; ksEditor assigns shaders and embeds textures in the KN5 | community-reported | acm-first-car |
| DDS textures, power-of-two sizes; BC7 works but must carry mipmaps or AC crashes | community-reported (low) | gtp-dds |
| Maximum texture size, required DDS format per shader slot | **unconfirmed** | not found |

## 5. Instrument options (digital cluster)

| Point | Status | Source |
|---|---|---|
| Kunos `data/digital_instruments.ini` and `analog_instruments.ini` | community-reported | acm-first-car (FOR_LATER_USE list) |
| CSP `[DI_*]` sections can only re-format existing Kunos digital items ("doesn’t allow to define new digital instruments") | confirmed | csp-wiki-digital |
| CSP `[SCRIPTABLE_DISPLAY_...]` draws a whole display on a mesh with Lua (`MESHES`, `RESOLUTION`, `DISPLAY_POS`, `DISPLAY_SIZE`, `SKIP_FRAMES`, `SCRIPT = x.lua`). **This is the realistic route for the Civic's digital cluster.** | confirmed | csp-lua-ex-dash; CSP config ks_alfa_giulia_qv.ini |
| Inputs for instruments, emissives and animations: `SPEED`, `RPM`, `GAS`, `FUEL` (litres), `WATER_TEMPERATURE` (°C), `TURBO`, `GEAR` (−1 R, 0 N), `ENGINE_TORQUE`, `TURNSIGNAL_LEFT/RIGHT`, `HAZARD`, `LOWBEAM`/`HIGHBEAM`, `SEATBELT`, `ABS_INACTION`, `TC_INACTION`, `CPHYS_SCRIPT_0..7`, among others | confirmed | csp-wiki-inputs |
| Also available: CSP analog-instrument extensions, analog odometers with trip counters, LED panels | confirmed (feature pages exist) | CSP wiki Cars – Analog instruments / Analog odometers / LED panels |

## 6. Animation pipeline

| Point | Status | Source |
|---|---|---|
| `animations/*.ksanim` hold gear-shift, steering and similar animations | community-reported | acm-first-car |
| ksanim is made by baking an FBX animation, importing it into ksEditor alongside the car and taking the ksanim from there, or by using a Blender ksanim/knh exporter; animate empties rather than meshes; the first frame is the rest state | community-reported | acm-fbx-anim |
| CSP `[ANIMATION_...] INPUT=… FILE=x.ksanim TIME=… INPUT_AS_PROGRESS / LOOP_WHILE_ACTIVE / HOLD_STATE` binds any ksanim to any instrument input (doors, wipers, pedals) | confirmed | csp-wiki-animations: "FILE = animation.ksanim ; file name of new animation in “animations” folder" |
| CSP car scripts can drive animations: `root:setAnimation(__dirname..'/my_anim.ksanim', progress)` | confirmed | csp-lua-ex-cars |
| Steering-wheel rotation is driven by the engine (STEER_HR), not by a custom ksanim | community-reported (search snippet only) | needs checking against the pipeline PDF |

## 7. Audio pipeline

| Point | Status | Source |
|---|---|---|
| **FMOD Studio 1.08.12**, the version named in `sdk/audio/AC Audio Pipeline 1.9.pdf`; later versions cause problems | community-reported | acm-sound-guide: "In my case it is: v 1.08.12." / "download v.1.08.12!!!". The same poster suspected newer cars use another version, and the official thread returned 403. **Check the PDF.** |
| An SDK template FMOD project exists ("you can use the example project") | community-reported | acm-sound-guide; Kunos forum thread "FMod official project v1.9" (403, unread) |
| Event path `event:/cars/<car_id>/<event>`, e.g. `engine_ext`, `engine_int`, `door` | confirmed | csp-lua-audio: "`'/cars/lada_revolution/door'` (leading “/” or “event:” prefix are optional)… `'cars/:own/engine_ext'`" |
| Car events known through CSP's volume keys: engine_ext/int, gear_ext/int, bodywork, wind, dirt, down_shift, horn, gear_grind, backfire_ext/int, traction_control_ext/int, transmission, limiter, turbo (+ hit, scrape, wheel, skid_ext/int). CSP adds `/transmission_ext`, `/wiper_ext`, `/wiper_int` | confirmed (key names); FMOD event spelling inferred | csp-wiki-audio |
| Game-supplied parameters: engine: `rpms`, `throttle`; turbo: `boost`, `bov`, `bov_decay`; backfire: `throttle`; limiter: `decay`; transmission: `drivetrain_speed`, `throttle`; gear: `state`; wind: `speed`, `air_pressure` | confirmed as CSP keys (`ENGINE_EXT_RPMS`, …); lower-case FMOD names **inferred** | csp-wiki-audio |
| **A game-supplied "load" parameter was not found in any source.** CSP can add `boost` to the engine events and `throttle` to turbo (`[AUDIO_PROPERTIES]`), remap inputs with LUTs (`[AUDIO_PARAMETER_TRANSFORM]`) and scale volume/pitch per event | confirmed (CSP); base-AC list unconfirmed | csp-wiki-audio |
| For state-driven burble: CSP car scripts can create `ac.AudioEvent('cars/:own/<event>')`, set parameters (`setParam`), position the event and start or stop it from any logic (throttle closed, rpm, gear, time since lift) | confirmed | csp-lua-audio, lib_audio.lua |
| A physics script can override the gas value the audio sees (`ac.overrideCarState('gasForAudio', …)`) | confirmed | csp-lua-cphys line 79 |
| Bank and GUIDs are built on Windows in FMOD Studio 1.08.12; bank name = car id | community-reported | cm-sfx, acm-first-car |
| Project rule: no samples from other games or mods (the community guide suggests extracting them; **we will not**) | rule | SPEC rule 6 |

## 8. CSP Lua car scripts

| Point | Status | Source |
|---|---|---|
| Physics script `data/script.lua` from **CSP 0.1.77**; requires extended physics; reloads live when data is unpacked | confirmed | csp-wiki-physics-scripts |
| Physics script can read the car state and detailed physics state (`ac.accessCarPhysics()`: `rpm`, `gas`, `gForces`, `requestedGearIndex`, …), modify engine RPM, damage, stalling, controls (`gas`, gear), override engine torque (`ac.overrideEngineTorque`), turbo boost (`ac.overrideTurboBoost`), gas input (`ac.overrideGasInput`), add forces, set 8 (CSP 0.2.1: 256) controller values (`SCRIPT_n` / `CPHYS_SCRIPT_n`) | confirmed | csp-wiki-physics-scripts, csp-lua-ex-turbo, CSP wiki New inputs for dynamic controllers |
| `carPh.turboBoost` readable from CSP 0.3.0-preview445 | confirmed | csp-wiki-physics-scripts |
| Visual car script in `ext_config.ini` `[SCRIPT_...] SCRIPT = x.lua`: reads `car.*` (e.g. `car.rpm`, `car.speedKmh`, `car.extraA`, `car.waterTemperature`, `car.ballast`), finds nodes/meshes (`ac.findNodes`, `ac.findMeshes`), sets materials and animations, plays audio | confirmed (API in SDK/examples); `[SCRIPT_...]` syntax community-reported (zgushonka/ac_scripts, linked from the SDK README) | csp-lua-ex-cars, csp-lua-readme |
| Visual and physics scripts exchange data via `ac.connect(..., ac.SharedNamespace.CarScript)` or shared events | confirmed | csp-lua-ex-cars |
| Full field list of `ac.StateCar` | **unconfirmed**: generated definitions ship only with CSP builds (`extension/internal/lua-sdk`), not in the public repo | csp-lua-readme |
| Minimum CSP version for visual car scripts / scriptable displays | **unconfirmed** | not stated anywhere opened |

## 9. How AC models torque and boost

| Point | Status | Source |
|---|---|---|
| Torque curve: `engine.ini [HEADER] POWER_CURVE=power.lut` (rpm, N·m); `[ENGINE_DATA] LIMITER`, `MINIMUM` (idle) | community-reported | cm-torque, CarData.cs |
| **Turbos are `[TURBO_0..n]` sections in `engine.ini`; no `turbo.ini` exists in any source.** Keys: `MAX_BOOST`, `WASTEGATE`, `REFERENCE_RPM`, `GAMMA`, `LAG_UP`, `LAG_DN`, `DISPLAY_MAX_BOOST`, `COCKPIT_ADJUSTABLE`; optional controllers `ctrl_turbo<n>.ini`, `ctrl_wastegate<n>.ini` | confirmed (CSP re-implementation of the "original Kunos turbo") + community-reported (CM) | csp-lua-ex-turbo, csp-wiki-powertrain, cm-torque |
| `BOOST_THRESHOLD` is **not** a turbo key in any source. The related key is `[DAMAGE] TURBO_BOOST_THRESHOLD` (engine damage) | community-reported | Automation forum post (cache/pages/568bfc4a861a1ef8.txt) |
| Model: T = power.lut(rpm) × (1 + Σ boostᵢ); boostᵢ → MAX_BOOST × min(1, (rpm·gas/REFERENCE_RPM)^GAMMA), clipped at WASTEGATE, approached at rates LAG_UP/LAG_DN. **Consequence: with turbo sections, `power.lut` must be the boost-free base curve.** | community-reported (CM) + confirmed as CSP's illustrative re-implementation | cm-turbo `Math.Min(1, Math.Pow(rpm / ReferenceRpm, Gamma))`, cm-torque `torque * (1.0 + multiplier)`; csp-lua-ex-turbo |
| CSP extended turbo: `EXT_GAS_CURVE`, `EXT_SPIN_DELAY` (2019); `TURBO_VERSION=1` + `FLOW_ON_CUT` (CSP 0.2.8, 05/2025) keeps boost through ignition cuts (limiter and TC cuts); extended physics only | confirmed | csp-wiki-powertrain |
| CSP `RESPONSE_TIME` (engine response delay), engine maps `[MAP]`, `[FUEL_CONSUMPTION]` | confirmed | csp-wiki-powertrain |
| Coast/engine-brake: `[COAST_REF]` (RPM, TORQUE, NON_LINEARITY) believed; "no coast.lut … Must keep the section in engine.ini" | section: community-reported; keys **unconfirmed** | acm-first-car; check `formula_k/data/engine.ini` comments |
| Limiter behaviour keys (e.g. `LIMITER_HZ`), engine `INERTIA` key, whether power.lut is crank or wheel torque | **unconfirmed** | check SDK sample data |

## 10. Axis conventions and mapping to the project frame

| Point | Status | Source |
|---|---|---|
| AC/KN5 car space: **+Y up, +Z forward**; dummies Z forward and Y up | community-reported | acm-first-car: "all dummies must have Z-axis pointing forward and Y-up." Consistent with acm-knsuseditor hard points (front z = +0.03, rear z = −0.33) |
| Ground plane at Y = 0 (wheels touching 0) | community-reported | acm-first-car |
| Suspension hard points in `suspensions.ini` are offsets relative to the wheel, mirrored left/right (no asymmetry except solid axles) | community-reported | acm-knsuseditor: "Its all used as mirrored" |
| Community Blender exporter maps kn5 (x, y, z) = blender (x, z, −y) | community-reported (code) | blender-kn5 |
| **Sign of AC +X (car's left or right): unconfirmed.** Working hypothesis: +X = car's left (inferred from the exporter with the car facing Blender −Y) | unconfirmed | see `platform.ac_axis_x_sign` |
| KN5/physics longitudinal origin (CG? wheelbase centre? `car.ini GRAPHICS_OFFSET`) | **unconfirmed** | not documented in sources opened |

**Project → AC mapping (provisional, to verify):** project frame +X right, +Y forward, +Z up, origin on the ground below the front axle. If AC +X is the car's left: `x_ac = −X`, `y_ac = Z`, `z_ac = Y − y0`, where `y0` is the project Y of the AC origin (unknown until checked). If AC +X is the car's right, `x_ac = +X`. **Check:** open any stock car in ksEditor or the CM showroom and read the X of `WHEEL_LF`.

## 11. Steps that need your Windows PC

| Step | Why | Status |
|---|---|---|
| Read `sdk/dev/car_pipeline*.pdf`, `sdk/audio/AC Audio Pipeline 1.9.pdf`, `formula_k` sample data comments | official docs exist only in the install | community-reported location |
| ksEditor: FBX import, shaders, KN5 export (car, LODs, collider), ksanim extraction | Windows tool in the AC SDK | community-reported |
| FMOD Studio 1.08.12: build `<id>.bank` + `GUIDs.txt` from the SDK template | Kunos pipeline | community-reported |
| `data.acd` packing (Content Manager or ksEditor) | key tied to folder name | community-reported |
| In-game testing, CSP Lua debugging (live reload with unpacked data), CSP Object Inspector, CM showroom | needs AC + CSP | confirmed (CSP live reload) |

## What could not be confirmed or was blocked

* Official Kunos documents (car pipeline PDF, audio pipeline PDF, FMOD template, `formula_k` comments): **not online, not supplied**.
* Kunos forum "FMod official project v1.9" (`assettocorsa.net/forum/index.php?threads/fmod-official-project-v1-9.37827/`): **HTTP 403**, not worked around.
* overtake.gg suspension thread: **bot challenge**, not worked around.
* `gh api` to the CSP repos is not enabled in this session; public `git clone` worked and was used instead.
* Not confirmed: the sign of AC +X; the longitudinal origin; the complete list of FMOD event parameters (and whether a `load` parameter exists); the coast/limiter/inertia keys in engine.ini; whether power.lut is crank or wheel torque; texture size limits; the minimum CSP version for visual car scripts; the full `ac.StateCar` field list; door, wiper and mirror node names.
