#!/usr/bin/env python3
"""Builds vehicle_data/platform.json (domain 11). Every evidence string is asserted to be
present (whitespace-normalised) in the source's cache_file before it is recorded."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dbutil as db

d = {"domain": "platform", "title": "Platform constraints (Assetto Corsa + CSP)", "schema_version": 1,
     "updated": db.today(), "sources": {}, "parameters": {}}
d["class_note"] = ("Class mapping for platform facts: A = official documentation from the software's own developer "
                   "(Kunos for base AC, the Custom Shaders Patch project for CSP features); C = community reference "
                   "(modding forums, Content Manager source code, third-party exporters). Status 'confirmed' means the "
                   "value is stated verbatim in the cited source; class C confirmations still need a check against the "
                   "official AC SDK documents on the user's PC (not online, not supplied).")
R = "cache/repos/"
WIKI = "https://github.com/ac-custom-shaders-patch/acc-extension-config/wiki/"
W = R + "acc-extension-config.wiki/"
WIKI_C = "git clone of acc-extension-config.wiki @19048685 (2026-06-11)"
SDK_C = "git clone of acc-lua-sdk @7cf60f5a (2026-08-17)"
EX_C = "git clone of acc-lua-examples @51b25318 (2026-06-08)"
CM_C = "git clone of gro-ove/actools @e5e5c94b (2026-06-17)"

def src(sid, title, url, pub, cls, cache, method, notes=""):
    db.add_source(d, sid, title=title, url=url, publisher=pub, cls=cls, access_method=method,
                  applicability="Assetto Corsa (2014) car content pipeline; not vehicle-specific",
                  notes=notes, cache_file=cache)

src("csp-wiki-powertrain", "CSP wiki: Cars – Powertrain", WIKI + "Cars-%E2%80%93-Powertrain", "Custom Shaders Patch project (GitHub wiki)", "A", W + "Cars-–-Powertrain.md", WIKI_C)
src("csp-wiki-physics-scripts", "CSP wiki: Cars – Physics scripts", WIKI + "Cars-%E2%80%93-Physics-scripts", "Custom Shaders Patch project (GitHub wiki)", "A", W + "Cars-–-Physics-scripts.md", WIKI_C,
    "Same text mirrored at https://cup.acstuff.club/docs/csp/cars/physics-scripts (fetched 200, cache/pages/b780550ed8c6a124.txt).")
src("csp-wiki-extended-physics", "CSP wiki: Cars – Enabling extended physics", WIKI + "Cars-%E2%80%93-Enabling-extended-physics", "Custom Shaders Patch project (GitHub wiki)", "A", W + "Cars-–-Enabling-extended-physics.md", WIKI_C)
src("csp-wiki-audio", "CSP wiki: Cars – Audio options", WIKI + "Cars-%E2%80%93-Audio-options", "Custom Shaders Patch project (GitHub wiki)", "A", W + "Cars-–-Audio-options.md", WIKI_C)
src("csp-wiki-animations", "CSP wiki: Cars – Animations", WIKI + "Cars-%E2%80%93-Animations", "Custom Shaders Patch project (GitHub wiki)", "A", W + "Cars-–-Animations.md", WIKI_C)
src("csp-wiki-digital", "CSP wiki: Cars – Digital instruments", WIKI + "Cars-%E2%80%93-Digital-instruments", "Custom Shaders Patch project (GitHub wiki)", "A", W + "Cars-–-Digital-instruments.md", WIKI_C)
src("csp-wiki-inputs", "CSP wiki: Cars – Instruments inputs", WIKI + "Cars-%E2%80%93-Instruments-inputs", "Custom Shaders Patch project (GitHub wiki)", "A", W + "Cars-–-Instruments-inputs.md", WIKI_C)
src("csp-wiki-guessed", "CSP wiki: Cars – About guessed configs", WIKI + "Cars-%E2%80%93-About-guessed-configs", "Custom Shaders Patch project (GitHub wiki)", "A", W + "Cars-–-About-guessed-configs.md", WIKI_C)
src("csp-lua-audio", "CSP Lua SDK: common/ac_audio.d.lua (ac.AudioEvent)", "https://github.com/ac-custom-shaders-patch/acc-lua-sdk/blob/main/common/ac_audio.d.lua", "Custom Shaders Patch project", "A", R + "acc-lua-sdk/common/ac_audio.d.lua", SDK_C)
src("csp-lua-cphys", "CSP Lua SDK: ac_car_cphys.lua (car physics script library)", "https://github.com/ac-custom-shaders-patch/acc-lua-sdk/blob/main/ac_car_cphys.lua", "Custom Shaders Patch project", "A", R + "acc-lua-sdk/ac_car_cphys.lua", SDK_C)
src("csp-lua-readme", "CSP Lua SDK README", "https://github.com/ac-custom-shaders-patch/acc-lua-sdk/blob/main/README.md", "Custom Shaders Patch project", "A", R + "acc-lua-sdk/README.md", SDK_C)
src("csp-lua-ex-turbo", "CSP Lua examples: cars_physics/turbo_map/script.lua", "https://github.com/ac-custom-shaders-patch/acc-lua-examples/blob/main/cars_physics/turbo_map/script.lua", "Custom Shaders Patch project", "A", R + "acc-lua-examples/cars_physics/turbo_map/script.lua", EX_C)
src("csp-lua-ex-cars", "CSP Lua examples: cars/README.md (car script snippets)", "https://github.com/ac-custom-shaders-patch/acc-lua-examples/blob/main/cars/README.md", "Custom Shaders Patch project", "A", R + "acc-lua-examples/cars/README.md", EX_C)
src("csp-lua-ex-dash", "CSP Lua examples: cars/dash_display_8100/README.md (scriptable display)", "https://github.com/ac-custom-shaders-patch/acc-lua-examples/blob/main/cars/dash_display_8100/README.md", "Custom Shaders Patch project", "A", R + "acc-lua-examples/cars/dash_display_8100/README.md", EX_C)
src("acm-first-car", "TUTORIAL – Your FIRST car in Assetto Corsa – Basic Guide (luchian; edited with feedback from a Kunos 3D artist)", "https://www.assettocorsamods.net/threads/your-first-car-in-assetto-corsa-basic-guide.1019/", "assettocorsamods.net (community forum)", "C", "cache/pages/0916b7573fa9e6bf.txt", "static")
src("acm-sound-guide", "TUTORIAL – Start with Sound Modding – Quick Guide", "https://assettocorsamods.net/threads/start-with-sound-modding-quick-guide.1163/", "assettocorsamods.net (community forum)", "C", "cache/pages/bf7bb9e7f1524436.txt", "static",
    "Thread also suggests taking samples from other games/mods; that is excluded by project rule 6.")
src("acm-knsuseditor", "KnSusEditor – Values Compared to Real Life? (thread)", "https://assettocorsamods.net/threads/knsuseditor-values-compared-to-real-life.1122/", "assettocorsamods.net (community forum)", "C", "cache/pages/4157be37015b2e8a.txt", "static")
src("acm-fbx-anim", "FBX Animation (thread)", "https://www.assettocorsamods.net/threads/fbx-animation.2498/", "assettocorsamods.net (community forum)", "C", "cache/pages/543ffad1cdc945cd.txt", "static")
src("cm-turbo", "Content Manager source: AcTools/Utils/Physics/TurboDescription.cs", "https://github.com/gro-ove/actools/blob/master/AcTools/Utils/Physics/TurboDescription.cs", "Content Manager (open source community tool)", "C", R + "actools/AcTools/Utils/Physics/TurboDescription.cs", CM_C)
src("cm-torque", "Content Manager source: AcTools/Utils/Physics/TorquePhysicUtils.cs", "https://github.com/gro-ove/actools/blob/master/AcTools/Utils/Physics/TorquePhysicUtils.cs", "Content Manager (open source community tool)", "C", R + "actools/AcTools/Utils/Physics/TorquePhysicUtils.cs", CM_C)
src("cm-carobject", "Content Manager source: AcManager.Tools/Objects/CarObject.cs (car packing list)", "https://github.com/gro-ove/actools/blob/master/AcManager.Tools/Objects/CarObject.cs", "Content Manager (open source community tool)", "C", R + "actools/AcManager.Tools/Objects/CarObject.cs", CM_C)
src("cm-workshop", "Content Manager source: WorkshopCarValidator.cs (required files check)", "https://github.com/gro-ove/actools/blob/master/AcManager/Tools/WorkshopPublishTools/Validators/WorkshopCarValidator.cs", "Content Manager (open source community tool)", "C", R + "actools/AcManager/Tools/WorkshopPublishTools/Validators/WorkshopCarValidator.cs", CM_C)
src("cm-sfx", "Content Manager source: CarObject.Sfx.cs (GUIDs.txt handling)", "https://github.com/gro-ove/actools/blob/master/AcManager.Tools/Objects/CarObject.Sfx.cs", "Content Manager (open source community tool)", "C", R + "actools/AcManager.Tools/Objects/CarObject.Sfx.cs", CM_C)
src("cm-acd", "Content Manager source: AcTools/AcdFile/AcdEncryption.cs", "https://github.com/gro-ove/actools/blob/master/AcTools/AcdFile/AcdEncryption.cs", "Content Manager (open source community tool)", "C", R + "actools/AcTools/AcdFile/AcdEncryption.cs", CM_C)
src("cm-analyzer", "Content Manager source: CarAnalyzer.xaml.cs (LOD rating heuristics)", "https://github.com/gro-ove/actools/blob/master/AcManager/Pages/ContentTools/CarAnalyzer.xaml.cs", "Content Manager (open source community tool)", "C", R + "actools/AcManager/Pages/ContentTools/CarAnalyzer.xaml.cs", CM_C)
src("cm-wheels", "Content Manager source: Kn5RenderableCar.Wheels.cs (wheel node names)", "https://github.com/gro-ove/actools/blob/master/AcTools.Render/Kn5Specific/Objects/Kn5RenderableCar.Wheels.cs", "Content Manager (open source community tool)", "C", R + "actools/AcTools.Render/Kn5Specific/Objects/Kn5RenderableCar.Wheels.cs", CM_C)
src("cm-utils", "Content Manager source: Kn5RenderableCar.Utils.cs (cockpit LR/HR, seatbelt nodes)", "https://github.com/gro-ove/actools/blob/master/AcTools.Render/Kn5Specific/Objects/Kn5RenderableCar.Utils.cs", "Content Manager (open source community tool)", "C", R + "actools/AcTools.Render/Kn5Specific/Objects/Kn5RenderableCar.Utils.cs", CM_C)
src("blender-kn5", "moppius/blender-assetto-corsa-tools: exporter/exporter_utils.py", "https://github.com/moppius/blender-assetto-corsa-tools/blob/master/exporter/exporter_utils.py", "Community Blender KN5 exporter (MIT)", "C", R + "blender-assetto-corsa-tools/exporter/exporter_utils.py", "git clone @5f0c163c (2022-01-02)")
src("gtp-dds", "GTPlanet AC PC Mods General Discussion, post on DDS BC7/mipmaps/power-of-two", "https://www.gtplanet.net/forum/threads/assetto-corsa-pc-mods-general-discussion.307899/post-14358983", "GTPlanet forum (community)", "C", "cache/pages/9d01755bb6ac9e4d.txt", "static")

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def check(sid, ev):
    p = os.path.join(ROOT, d["sources"][sid]["cache_file"])
    txt = norm(open(p, encoding="utf-8", errors="ignore").read())
    for frag in ev.split(" … "):
        if norm(frag) not in txt:
            raise SystemExit(f"EVIDENCE NOT FOUND in {sid}: {frag!r}")

APP = {"year": "", "market": "", "trim": "", "body": "", "gearbox": "", "engine": "",
       "notes": "Platform documentation (Assetto Corsa / Custom Shaders Patch); not vehicle-specific."}

def add(key, desc, impact, value, sid, loc, ev, conf="high", notes="", status="confirmed", unit="text"):
    check(sid, ev)
    cls = d["sources"][sid]["class"]
    db.add_candidate(d, key, desc, unit, impact,
                     db.record(value=value, unit=unit, status=status, cls=cls, source_id=sid, locator=loc,
                               evidence=ev, as_printed=value if isinstance(value, str) else str(value),
                               applicability=APP, confidence=conf, notes=notes))

def unk(key, desc, impact, searches, how, notes=""):
    db.add_candidate(d, key, desc, "text", impact, db.unknown("text", searches, how, notes=notes, applicability=APP))

# ---------------- audio
add("platform.fmod_studio_version", "FMOD Studio version required to build AC car soundbanks", "critical", "1.08.12",
    "acm-sound-guide", "post #1 and #4 (Just Kauser, Jan/Feb 2018)",
    "Short tut.: Go to : Assetto Corsa\\sdk\\audio\\AC Audio Pipeline 1.9.pdf … In my case it is: v 1.08.12. … IMPORTANT: Download not the lastest FMOD version, download v.1.08.12!!!",
    conf="medium",
    notes="Community post quoting the official 'AC Audio Pipeline 1.9.pdf' shipped in the AC install (sdk/audio). Primary PDF is not online and was not supplied; the Kunos forum thread 'FMod official project v1.9' returned HTTP 403 (not worked around). Same poster notes newer cars might use another version. Verify on the user's PC: open sdk/audio/AC Audio Pipeline 1.9.pdf and read the 'FMod Studio version used' line.")
add("platform.audio_event_path_format", "FMOD event path convention for car sound events", "high", "event:/cars/<car_folder_id>/<event> (e.g. engine_ext, engine_int, door)",
    "csp-lua-audio", "ac.AudioEvent @param event",
    "Event name, for example, `'/cars/lada_revolution/door'` (leading “/” or “event:” prefix are optional). … For example, `'cars/:own/engine_ext'` or `'cars/:1/engine_int'`.",
    notes="Corroborated by Content Manager regex for sfx/GUIDs.txt lines: ^\\{(GUID)\\}\\s+event:/cars/(\\w+)/e (cm-sfx, line 27).")
add("platform.audio_engine_event_params", "Game-supplied parameters on engine/turbo/backfire/etc. events (as exposed by CSP's transform keys)", "critical",
    "engine_ext/engine_int: rpms, throttle; turbo: boost, bov, bov_decay; backfire_ext/int: throttle; limiter: decay; transmission: drivetrain_speed, throttle; gear_ext/int: state",
    "csp-wiki-audio", "Supported parameters list",
    "ENGINE_EXT: ENGINE_EXT_RPMS, ENGINE_EXT_THROTTLE; … ENGINE_INT: ENGINE_INT_RPMS, ENGINE_INT_THROTTLE; … BACKFIRE_EXT: BACKFIRE_EXT_THROTTLE; … LIMITER: LIMITER_DECAY; … TURBO: TURBO_BOOST, TURBO_BOV, TURBO_BOV_DECAY; … TRANSMISSION: TRANSMISSION_DRIVETRAIN_SPEED, TRANSMISSION_THROTTLE;",
    conf="medium",
    notes="CSP lists AC's existing event inputs by EVENT_PARAM key; lower-case FMOD parameter names are inferred from those keys (only 'drivetrain_speed', 'throttle', 'state', 'boost' appear lower-case in the text). No 'load' parameter is documented for base AC; CSP can add ENGINE_EXT_BOOST/ENGINE_INT_BOOST and TURBO_THROTTLE via [AUDIO_PROPERTIES]. Exact list must be confirmed against the Kunos FMOD template project (AC SDK, user's PC).")
add("platform.audio_sfx_files", "Files the car's sound needs", "high", "sfx/<car_folder_id>.bank + sfx/GUIDs.txt",
    "cm-workshop", "Validate(): ValidateFileExistance / ValidateAudioGuids",
    "var fileName = \"sfx/GUIDs.txt\"; … yield return ValidateFileExistance($\"sfx/{Target.Id}.bank\", 200e6);",
    notes="Content Manager's Steam Workshop validator treats GUIDs.txt as required for non-Kunos cars and the bank name must equal the car folder id.")

# ---------------- CSP Lua
add("platform.csp_min_version_physics_script", "Minimum CSP version for a car physics Lua script (data/script.lua)", "high", "0.1.77",
    "csp-wiki-physics-scripts", "first paragraph",
    "With 0.1.77 update it is now possible to use a Lua script to extend car physics. Simply create a “script.lua” in car data folder and it’ll work if extended physics is enabled.")
add("platform.csp_min_version_cphys_turbo_boost_read", "CSP build needed for carPh.turboBoost in physics scripts", "medium", "0.3.0-preview445",
    "csp-wiki-physics-scripts", "example 'Forcing more air into the engine'",
    "requires 0.3.0-preview445 or newer for `carPh.turboBoost` to work")
unk("platform.csp_min_version_visual_car_script", "Minimum CSP version for a visual (ext_config [SCRIPT_...]) car Lua script", "medium",
    ["CSP wiki clone (all Cars-* pages): grep 'SCRIPT', 'car script' - no version stated",
     "acc-lua-sdk clone: README, ac_car_scriptable_display.lua, common/ac_enums.lua (SharedNamespace CarScript) - no version",
     "acc-lua-examples cars/README.md - no version",
     "WebSearch: 'CSP lua sdk ac.StateCar fields ...' (no version)",
     "zgushonka/ac_scripts (linked from SDK README): shows [SCRIPT_...] SCRIPT='ext_script.lua' syntax, no version"],
    "Set [_EXTENSION] REQUIRED_VERSION / test on the CSP build the user runs; CSP changelog (acstuff.club/patch) could date it.",
    notes="Practical plan: target a current CSP (0.2.x/0.3.x) and declare REQUIRED_VERSION; do not rely on a minimum we could not cite.")
add("platform.extended_physics_switch", "How CSP extended physics is enabled for a car", "high", "car.ini [HEADER] VERSION=extended-2 (optionally [_EXTENSION] REQUIRED_VERSION=<build id>)",
    "csp-wiki-extended-physics", "main text",
    "open `car.ini`, find `[HEADER]` section and add `extended-` to `VERSION` value as prefix … original AC, if it would encounter that `VERSION` value, would crash",
    notes="Consequence: a car using CSP extended physics will not load in vanilla AC.")

# ---------------- engine / turbo model
add("platform.turbo_definition_location", "Where AC defines turbochargers", "critical", "engine.ini [TURBO_0..N] sections (keys MAX_BOOST, WASTEGATE, REFERENCE_RPM, GAMMA, LAG_UP, LAG_DN, DISPLAY_MAX_BOOST, COCKPIT_ADJUSTABLE); optional ctrl_turbo<N>.ini controllers; no turbo.ini",
    "csp-lua-ex-turbo", "DefaultTurbo()",
    "---Turbo acting similar to original Kunos turbo with CSP extensions. Only for illustrative purposes. … local section = 'TURBO_'..index … local gamma = engineINI:get(section, 'GAMMA', 2) … local rpmRef = engineINI:get(section, 'REFERENCE_RPM', 2000) … local lagDown = engineINI:get(section, 'LAG_DN', 0.99) … local lagUp = engineINI:get(section, 'LAG_UP', 0.99) … local wastegate = engineINI:get(section, 'WASTEGATE', 0) … local maxBoost = engineINI:get(section, 'MAX_BOOST', 1) … local controllerMaxBoost = ac.getDynamicController('ctrl_turbo'..index..'.ini')",
    notes="DISPLAY_MAX_BOOST and COCKPIT_ADJUSTABLE appear in the CSP Powertrain wiki [TURBO_0] example. No source anywhere mentions a turbo.ini; Content Manager also reads turbos only from engine.ini TURBO sections (cm-torque ReadTurbos). 'BOOST_THRESHOLD' as a turbo key was not found; the related key seen is [DAMAGE] TURBO_BOOST_THRESHOLD (community-reported, Automation forum) for engine damage.")
add("platform.turbo_torque_model", "How boost scales torque in AC (steady state, full throttle)", "critical",
    "T(rpm) = power.lut(rpm) * (1 + sum_i boost_i); boost_i = MAX_BOOST * min(1, (rpm*gas/REFERENCE_RPM)^GAMMA), clipped at WASTEGATE (if non-zero), approached through LAG_UP/LAG_DN",
    "cm-torque", "ConsiderTurbo()",
    "return torque * (1.0 + multiplier);",
    conf="medium",
    notes="Multiplier per turbo from cm-turbo CalculateMultiplier: 'var baseLevel = Math.Min(1, Math.Pow(rpm / ReferenceRpm, Gamma));' and wastegate clip 'Math.Min(Wastegate, result)'. Gas term and lag from CSP's illustrative re-implementation (csp-lua-ex-turbo: 'math.pow(math.saturateN(data.rpm * gas / rpmRef), gamma)'). Both are re-implementations; Kunos source is closed. Implication for Phase 4: power.lut is the NON-boosted torque curve if turbo sections are used, or the full curve with no turbo sections.")
add("platform.turbo_torque_model", "How boost scales torque in AC (steady state, full throttle)", "critical",
    "intensity = saturate(rpm*gas/REFERENCE_RPM)^GAMMA; spinning += (intensity - spinning)*(LAG_UP or LAG_DN)*dt; boost = MAX_BOOST*spinning (wastegate clip)",
    "csp-lua-ex-turbo", "DefaultTurbo() return function",
    "local intensity = math.pow(math.saturateN(data.rpm * gas / rpmRef), gamma) … spinning = spinning + (intensity - spinning) * (intensity > spinning and lagUp or lagDown) * dt",
    conf="medium", notes="CSP's own description: 'Turbo acting similar to original Kunos turbo with CSP extensions. Only for illustrative purposes.'")
add("platform.csp_turbo_v1", "CSP extended turbo model (TURBO_VERSION=1) availability", "medium", "CSP 0.2.8 (05/2025): engine.ini [HEADER] TURBO_VERSION=1, [TURBO_n] FLOW_ON_CUT",
    "csp-wiki-powertrain", "# Turbos / New for 0.2.8 (05/2025)",
    "## New for 0.2.8 (05/2025) … TURBO_VERSION=1 ;0 is AC, 1 is v1 CSP … FLOW_ON_CUT=0.6",
    notes="Fixes vanilla behaviour where ignition/fuel cuts act like a closed throttle and unspool the turbo. Relevant to rev-limiter/TC cuts on the Civic. Extended physics only.")
add("platform.power_curve_file", "Engine torque curve file", "critical", "engine.ini [HEADER] POWER_CURVE=power.lut (rpm|torque N*m), limiter at [ENGINE_DATA] LIMITER, idle at [ENGINE_DATA] MINIMUM",
    "cm-torque", "LoadCarTorque()",
    "var torque = engine[\"HEADER\"].GetLut(\"POWER_CURVE\", \"power.lut\"); … var limit = considerLimiter && engine.ContainsKey(\"ENGINE_DATA\") ? engine[\"ENGINE_DATA\"].GetDouble(\"LIMITER\", torque.MaxX) : torque.MaxX;",
    conf="medium", notes="MINIMUM key read in AcTools.Render/Data/CarData.cs line 1005. Wheel vs crank: not stated in any source opened; community convention is crank torque - unconfirmed. Coast/engine-brake keys ([COAST_REF] RPM/TORQUE/NON_LINEARITY) are believed but unconfirmed online; check formula_k engine.ini comments in the AC SDK.")

# ---------------- files / packaging
add("platform.required_data_files", "Data files without which the car will not load (per community guide)", "critical",
    "aero.ini (+wing LUTs), cameras.ini, car.ini, driver3d.ini, engine.ini (+power.lut), lods.ini, suspensions.ini, tyres.ini (+LUTs); brakes.ini, colliders.ini, drivetrain.ini, setup.ini needed for sane behaviour",
    "acm-first-car", "post #1, section 4: Edit \\DATA\\*.ini files",
    "MANDATORY … (without them, the car will not load and game will crash)",
    conf="medium", notes="List follows the guide's 'MANDATORY' and 'OPTIONAL, BUT MANDATORY' groups (2017; edited with Kunos 3D-artist feedback). Official car_pipeline*.pdf ships in sdk/dev on the user's PC.")
add("platform.data_packing", "Release packing of data folder", "high", "data/ folder packed to data.acd; encryption key derived from the car folder name",
    "cm-acd", "AcdEncryption.FromAcdFilename",
    "var id = name.StartsWith(\"data\", StringComparison.OrdinalIgnoreCase) ? Path.GetFileName(Path.GetDirectoryName(acdFilename)) : name;",
    conf="medium", notes="Guide: 'nowdays the entire folder is packed in one single file called data.acd'. Renaming the folder after packing breaks the data.acd (inference from key derivation). Unpacked data/ also loads (CSP: live reload of script.lua 'if data is unpacked').")
add("platform.car_folder_name_max_length", "Max length of the car folder name", "low", 32,
    "acm-first-car", "post #1, folder structure", "max length for car folder name: 32", unit="count",
    notes="From AC shared-memory definitions per guide; keep lower-case latin.")
add("platform.lod_structure", "LOD / collider structure", "high",
    "One KN5 per LOD listed in data/lods.ini ([LOD_0..n] FILE, IN, OUT; optional [LOD_HR]); [COCKPIT_HR] DISTANCE_SWITCH toggles COCKPIT_HR/COCKPIT_LR; physics collider is a separate collider.kn5 in the car root",
    "cm-carobject", "PackOverride()",
    "yield return Add(lods.GetSections(\"LOD\").Append(lods[\"LOD_HR\"]).Select(x => x.GetNonEmpty(\"FILE\")));",
    conf="medium",
    notes="IN/OUT keys: CarGenerateLodsDialog.xaml.cs lines 1291-1292; DISTANCE_SWITCH: cm-analyzer line ~413; collider.kn5 existence check: cm-workshop. The belief 'one KN5 per LOD plus a collider KN5' is consistent with all sources opened.")
add("platform.lod_triangle_targets", "LOD triangle/distance targets used by Content Manager's car analyzer (heuristic)", "low",
    "LOD_1 <= 45k tris (superb 22k), LOD_2 <= 11k (6k), LOD_3 <= 5k (3k); LOD_0 OUT ~15 m, LOD_1 OUT 25-60 m, LOD_2 OUT 60-250 m; 4 LODs; COCKPIT_HR < 20k tris or COCKPIT_LR with switch ~7 m",
    "cm-analyzer", "LOD rating block",
    "var correctLods = lodsTris[1] <= 45e3 && … (lods.Count < 3 || lodsTris[2] <= 11e3) && … (lods.Count < 4 || lodsTris[3] <= 5e3);",
    conf="low", notes="These are CM's quality heuristics, not engine limits.")
add("platform.collider_rules", "collider.kn5 construction", "high", "very low poly (40-60 tris) box-like shape, material named GL with GL shader in ksEditor, no vertex below car bottom, pivot at ground 0",
    "acm-first-car", "post #1, 3D: collider",
    "It is therefore required to use a VERY (40-60 triangles) low poly basic shape as collision box. … Note you need to set it with a material called GL, then assign the GL shader in KsEditor before exporting. … NO vertex under the car bottom (so DON'T go as low as the ground)",
    conf="medium")

# ---------------- 3D pipeline
add("platform.fbx_version", "FBX version accepted by ksEditor", "high", "FBX 2014/2015 (2016 unsupported)",
    "acm-first-car", "post #1, main steps 2c",
    "-c/ export to FBX up to 2014/2015 format (2016 is unsupported)", conf="medium",
    notes="2017 community statement; re-check with the ksEditor build on the user's PC.")
add("platform.model_units", "Model units", "high", "meters", "acm-first-car", "post #1, 2A", "Set scale to Meters.", conf="medium")
add("platform.ac_axis_up_forward", "AC/KN5 car-space up and forward axes", "critical", "+Y up, +Z forward (dummies Z forward, Y up)",
    "acm-first-car", "post #1, 2B important notes", "all dummies must have Z-axis pointing forward and Y-up.", conf="medium",
    notes="Consistent with suspension hard-point offsets (WBCAR_BOTTOM_FRONT z=+0.03 vs _REAR z=-0.33 in acm-knsuseditor) and the Blender exporter mapping (x, z, -y).")
add("platform.ac_vertical_origin", "Vertical origin of the car model", "high", "ground plane = 0 (wheels touching Y=0)",
    "acm-first-car", "post #1, 2B important notes",
    "car's body origin/pivot point : the model must be placed with the wheels touching the ground on the 0 coordinate (see below).", conf="medium")
add("platform.blender_to_kn5_mapping", "Axis mapping used by a community Blender->KN5 exporter", "medium", "kn5(x, y, z) = blender(x, z, -y)",
    "blender-kn5", "convert_vector3()", "return Vector((in_vec[0], in_vec[2], -in_vec[1]))", conf="medium",
    notes="With the car facing Blender -Y (Blender 'front' convention), KN5 +Z = forward and KN5 +X = Blender +X = the car's LEFT side. This sign is an inference, not stated by any source.")
unk("platform.ac_axis_x_sign", "Sign of AC car-space +X (car's left or right)", "critical",
    ["CSP wiki clone: grep 'left', 'axis', 'car space' (Lights: 'POSITION = 0, 0.7, 1.8 ; light position in car space'; Instruments inputs: 'X for left/right' - no sign)",
     "acc-lua-sdk clone: grep 'to the left', 'positive x', 'left-handed'",
     "WebSearch: 'assetto corsa kn5 coordinate system WHEEL_LF positive X ...'",
     "WebSearch: 'assetto corsa suspensions.ini WBCAR_TOP_FRONT coordinates x axis left right sign hub'",
     "overtake.gg suspension thread - bot challenge page, not worked around",
     "moppius Blender exporter: mapping (x, z, -y) implies +X = car left only under an assumed Blender orientation"],
    "In ksEditor or Content Manager showroom, open any stock Kunos car (structure only) and read the X translation of WHEEL_LF; positive => +X is the car's left. Then fix the project->AC mapping.",
    notes="Working hypothesis (unconfirmed): AC +X = car's left. Project frame is +X right, +Y forward, +Z up, origin on ground under the front axle; AC frame is +Y up, +Z forward, ground at Y=0; longitudinal origin of the KN5/physics body is not documented in sources opened (car.ini GRAPHICS_OFFSET exists per CM/zgushonka usage).")
add("platform.node_names_wheels", "Wheel/suspension node names", "critical", "WHEEL_LF/RF/LR/RR, SUSP_LF/RF/LR/RR, HUB_xx (optional), DISC_xx (or DISC_xx_ANIM)",
    "cm-wheels", "GetWheelNodesNames()",
    "var susp = $@\"SUSP_{namePostfix}\"; … var hub = $@\"HUB_{namePostfix}\"; … var animatedDisc = $@\"DISC_{namePostfix}_ANIM\"; … $@\"WHEEL_{namePostfix}\", susp, skipHub == true ? null : hub,",
    conf="medium", notes="WHEEL_LF/WHEEL_LR/WHEEL_RF/WHEEL_RR also in acm-first-car. CM's repair tool warns that missing SUSP_xx nodes 'Might cause crashes, especially in showroom.'")
add("platform.node_names_cockpit", "Cockpit/steering/shifter/seatbelt node names", "high", "COCKPIT_HR/COCKPIT_LR, STEER_HR/STEER_LR, SHIFT_HD/SHIFT_LD, CINTURE_ON/CINTURE_OFF",
    "cm-utils", "SetCockpitLrActive / SetSeatbeltActive",
    "case \"COCKPIT_LR\": … case \"STEER_LR\": … case \"SHIFT_LD\": … case \"COCKPIT_HR\": … case \"STEER_HR\": … case \"SHIFT_HD\": … var onNode = parent.GetDummyByName(\"CINTURE_ON\");",
    conf="medium", notes="Door/wiper/mirror/light node names are not covered by a source opened (DOOR_L/DOOR_R only appear in a CSP config template line). Lights/emissives are defined by mesh name in lights.ini / ext_config, so names are free but must match.")
add("platform.texture_rules", "Texture format constraints", "medium", "DDS; power-of-two sizes; BC7 allowed but must include mipmaps",
    "gtp-dds", "post #14358983 (page 4616)",
    "You should use this instead of \"BC3 (Linear, DXT5)\" … you must ALWAYS save the DDS with mipmaps as AC can't create the mipmaps for the new format and the game will crash otherwise. … you may run into issues if a track texture resolution isn't a power of 2",
    conf="low", notes="Forum post, not official; maximum texture size not found. Textures are embedded in the KN5 by ksEditor (acm-first-car).")

# ---------------- animations / instruments
add("platform.animation_pipeline", "How .ksanim animations are produced and used", "high",
    "animations/*.ksanim produced from baked FBX animation imported into ksEditor (or a Blender ksanim exporter); CSP [ANIMATION_...] binds a .ksanim to any instrument input",
    "csp-wiki-animations", "Syntax",
    "FILE = animation.ksanim     ; file name of new animation in “animations” folder",
    conf="medium", notes="FBX->ksEditor->ksanim and Blender ksanim/knh exporter routes: community-reported in acm-fbx-anim ('export as FBX (Selected objects only) and bake animation (then import into kseditor alongside the car and grab the ksanim)'). Steering wheel rotation itself is driven by the engine via STEER_HR (community).")
add("platform.digital_instrument_options", "Instrument options for the digital cluster", "high",
    "Kunos data/digital_instruments.ini + analog_instruments.ini; CSP can only re-format existing digital items ([DI_*] DIGITAL_ITEM=n) or draw full displays with [SCRIPTABLE_DISPLAY_...] Lua on a mesh",
    "csp-wiki-digital", "intro",
    "This is a temporary and somewhat hacky approach, doesn’t allow to define new digital instruments, but instead, only to replace text on original Kunos instruments defined in “data/digital_instruments.ini”.",
    notes="Scriptable display syntax (MESHES, RESOLUTION, DISPLAY_POS, DISPLAY_SIZE, SKIP_FRAMES, SCRIPT=*.lua) from csp-lua-ex-dash. For the Civic's 7-inch digital cluster a [SCRIPTABLE_DISPLAY_...] is the realistic route.")
add("platform.instrument_inputs", "Car-state inputs available to CSP instruments/emissives/animations", "high",
    "SPEED, RPM, GAS, BRAKE, CLUTCH, FUEL (l), WATER_TEMPERATURE (°C), TURBO, GEAR, ENGINE_TORQUE, TURNSIGNAL_LEFT/RIGHT, HAZARD, LOWBEAM/HIGHBEAM, SEATBELT, ABS_INACTION, TC_INACTION, CPHYS_SCRIPT_0..7, ...",
    "csp-wiki-inputs", "input list",
    "- `RPM`: engine RPM; … - `FUEL`: remaining fuel, in liters; … - `WATER_TEMPERATURE` (alias: `WATER_TEMP`): water temperature, in °C; … - `TURBO`: turbo boost; … - `GEAR`: current gear, with —1 for reverse and 0 for neutral",
    notes="Full list in the wiki page (lines 127-276 of the clone).")

db.save(d, os.path.join(ROOT, "vehicle_data", "platform.json"))
print("saved", len(d["parameters"]), "parameters,", len(d["sources"]), "sources")
