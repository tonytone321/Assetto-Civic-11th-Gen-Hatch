# Phase 2: dimensional reference model

Project: a high-fidelity Assetto Corsa (AC) car mod of the 2024 Honda Civic Hatchback Sport Touring, 1.5 L turbo, 6-speed manual, Canadian market, Sonic Grey Pearl. Phase 1, the research and sourced database, is finished and committed.

This run is Phase 2 only. Its job is to fix the car's proportions in Blender as a reference cage built from the database, and to measure how well that cage agrees with reference photos. It ends with numbers, not with a car body. No body surfaces, panels, interior, materials, AC physics files or sound. If you find yourself modeling the body, stop: that is Phase 3.

Do it as one thread from start to finish. If you are coordinating threads instead of working directly, give one working thread this message unchanged. Work through every step without pausing to ask whether to continue, except at the stops named below.

# Before anything else

1. Check that the Phase 1 files are on your branch: docs/SPEC.md, docs/PHASE1_SCORECARD.md and vehicle_data/_resolved.json. If they are not, stop and tell me the Phase 1 branch still needs merging.
2. Read docs/SPEC.md (the Phase 1 brief, whose rules still apply), docs/PHASE1_SCORECARD.md, docs/UNCERTAINTIES.md, docs/CONFLICTS.md and docs/PLATFORM_CONSTRAINTS.md.
3. Save this message unchanged as docs/SPEC_PHASE2.md and commit it. Re-read it whenever your context has been compacted.

# Rules

Carried over: exact identity; sources, not memory; unknown is a valid answer; derived numbers come from code; report only what happened; never work around access blocks; commit and push after each step.

New for this phase:
- Every script that produces a committed file lives in the repository and is run from the repository before its output is committed.
- Change data only through the builders or vehicle_data/user_measurements.json, never by editing generated JSON by hand.
- A published dimension is never adjusted to make a photo fit. If a photo disagrees with a published figure, that is a finding to report.

# Step 1. Prove Phase 1 is reproducible

The domain builders were moved into scripts/domains/ and most were never re-run from there. From a fresh clone in a temporary directory, run every builder, then resolve, derive and validate.

- If the regenerated files match what is committed (empty git diff), record that and go on.
- If the only differences are ordering, whitespace or timestamps, make the builders deterministic, commit, and go on.
- If any value differs or a builder fails, stop. Report each difference, which version you believe and why, and wait for my answer.

# Step 2. Settle the headline dimensions

For length, width, height, wheelbase, front track and rear track, open at least two Honda sources each and confirm the digits yourself. Overall length needs particular care: Honda Canada's 2024 hatchback sheet appears to read 4529 mm, Honda US press material lists 179.0 in, and Honda's US information-center page for 2024 prints 184.0 in, which is the sedan's figure. Keep every candidate with its source, select by the existing precedence rule (Canadian specification first), record disagreements in docs/CONFLICTS.md and re-run the pipeline.

# Step 3. Take in what I supplied

Look in user_supplied/ and list what is there and what is not. Everything in it is my own first-hand material (class B). Any item may be missing.

- measurements.txt: my notes in plain language, in any units. Transcribe each figure into vehicle_data/user_measurements.json, keeping my wording as the evidence and my original units beside the converted value. Expect ground-to-fender-lip and ground-to-wheel-center heights at each wheel, tire pressures, fuel level, engine rpm at 100 km/h in sixth, and the distance and camera height for each photo. If a note is ambiguous, ask me. Do not guess.
- photos/ files named side_left, side_right, front, rear, and possibly front_3q and rear_3q, as JPEG or HEIC. These are the Phase 2 references.
- photos/door_jamb and photos/tire_sidewall: read the GVWR, front and rear axle ratings, build date, tire size and pressures, paint code, and the tire make and model. Never copy the VIN into any file.
- ac_sdk/: the official AC pipeline documents. Use them to replace community-reported points in docs/PLATFORM_CONSTRAINTS.md with cited ones, starting with axis conventions and node naming.

Re-run resolve, derive and validate after entering anything, and run the gear-speed cross-check if I gave the rpm figure. If there are no photos, say so plainly, continue with the best items in references/manifest.json, and state how much that limits the result.

# Step 4. Blender

Blender is not preinstalled. Install the newest LTS release: try the official Linux build first, and if that download is blocked, use the bpy package from PyPI with a Python version it supports. Record the route and the exact version in docs/COORDINATES.md. Run it headless. Cycles on the CPU at low sample counts is enough. If neither route works, stop and tell me exactly what failed. Never describe a render that was not produced.

# Step 5. Coordinates

Write docs/COORDINATES.md and scripts/blender/coords.py, with one mapping function that every other script uses.

- Project coordinates, unchanged: origin on the ground at the centerline below the front axle; +X right, +Y forward, +Z up; meters.
- Blender: meters, scale 1.0, Z up, with the car facing Blender's -Y so that Blender's Front view shows the front of the car. That makes Blender (x, y, z) equal to project (-X, -Y, Z).
- AC: state the mapping only as far as the documents support it. Anything still community-reported, such as which side WHEEL_LF sits on, is marked unconfirmed and listed as a question for me.

Add tests/test_coords.py: the four wheel centers and the body extents must land where the mapping says.

# Step 6. Build the reference cage

scripts/blender/build_reference_cage.py reads vehicle_data/_resolved.json and builds everything from it. No dimension is typed into a script. Save the scene as blender/reference_cage.blend and commit it, since it is small and I want to open it. Larger build outputs go in blender/_build/, which git ignores.

Build these, naming each object with a REF_ prefix:
- the ground plane and the vehicle centerline plane;
- the body bounding box from overall length, width and height, positioned fore and aft by the front overhang. If the overhang is only photo-derived, say so and treat the box's fore-aft position as photo-derived;
- the front and rear axle lines, and the four wheel centers at half the track from the centerline and at the loaded tire radius above the ground, or at my measured wheel-center height if I gave one;
- four tire outlines from the tire's overall diameter and section width;
- the width over mirrors, if known;
- the estimated suspension hard points, as small markers;
- guide curves for the roofline, hood line, windshield base, hatch line, beltline, bumper extents and wheel arches, from the photo measurements.

Put each object in the collection that matches the class of its data: REF_published, REF_measured (my measurements), REF_photo (photo-derived) or REF_estimated. If the data for an item is missing, leave the item out and list it as missing. Do not invent it. Empties and bare curves do not render, so give markers and curves real thickness.

Add a script check that the cage's length, width, height, wheelbase and tracks equal the database values exactly.

# Step 7. Compare with the references

Do not treat a photo as a flat orthographic view. A photo taken from 20 m still shows the near side of the car a few percent larger than the centerline.

For each reference photo:
1. Take the focal length from EXIF, or estimate it and say so.
2. Find the camera position. Start from the distance and height in my notes if I gave them, then refine by fitting known points (wheel centers and tire contact points) and report the fit residual in pixels. If the fit is unstable, say so and use my stated figures.
3. Project the cage through that camera into the image.
4. Measure the difference at each key point, in millimeters at the car: roof peak, windshield base, hood leading edge, hatch line, front and rear bumper extents, wheel-arch tops, beltline, mirror position and ride height. State which plane each point is assumed to lie on, the centerline plane or the body-side plane.
5. Estimate the photo's own uncertainty at the car, from its resolution, the camera fit and lens distortion.

If my photos are present, re-derive the photo measurements from them with the same camera model, replacing the low-resolution render, then rebuild the cage and repeat the comparison.

Also render the cage alone: orthographic front, rear, left, right and top, plus front and rear three-quarter views.

Save renders and overlays under docs/phase2/. Commit overlays only for my own photos. For third-party images, commit the numbers and keep the images in the git-ignored cache.

# Step 8. Report

Write docs/MODEL_VALIDATION.md with:
- the reproducibility result from Step 1;
- the six headline dimensions with the sources that confirm each;
- what I supplied and what was missing;
- the Blender version and install route;
- one table per reference photo: each key point's difference, the photo's uncertainty, and a verdict of agrees (difference within uncertainty), disagrees, or not measurable with the reason;
- every unresolved item with what would resolve it;
- the open questions for me.

# Done means

- Step 1 passed, or I approved the differences.
- The cage matches the published dimensions exactly, checked by script.
- Every key point has a measured difference and a verdict, or is listed as not measurable.
- validate_db.py and the coordinate tests pass.

# Finish

Commit as "Phase 2: dimensional reference model" and push. If the push fails, say so and keep the local commits. End with a short message: what was built, the five largest differences, what is unresolved and what you need from me. Then stop. Do not begin Phase 3.
