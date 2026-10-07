## 8. Unresolved items

Each item says what would settle it. Numbers are in the tables above. No data value was changed to make an image fit.

1. **Ride height (wheel-centre height).**
   - The cage puts every wheel centre at `tires.loaded_radius`. That is an estimate (class E), used because no measured wheel-centre height was supplied.
   - The render (R1) puts both axles slightly higher. This agrees within U, but R1 is the only image whose camera fit was accepted, and it is a CGI render, not a photograph.
   - Settled by: ground-to-hub-centre height measured at each wheel, entered in `vehicle_data/user_measurements.json`.
2. **Windshield header.**
   - Phase 1 (3-segment fit to the front of the top profile) and Phase 2 (4-segment fit to the whole profile) place the windshield-to-roof break at different points on the same render. The difference in Y is larger than U.
   - The transition is curved. A "header" defined as the breakpoint of a piecewise-linear fit therefore moves with the number of segments.
   - Consequence: Phase 1's uncertainty for `proportions.windshield_header_y` is too small, and so is the uncertainty of the cage's windshield and roofline guides built from it.
   - Settled by: defining the header as a physical edge (top of the glass, or the roof-panel seam) and measuring it on a long-lens side photo of the car. That would change the Phase 1 builder `scripts/domains/photo_measure_side.py`, which was not done in Phase 2.
3. **Overall length and the fore-aft position of the body box.**
   - Honda Canada prints 4529 mm, which its 2022/2023 sheets give as the length without the front licence-plate bracket. hondanews.com prints 179.0 in (4546.6 mm), the with-bracket length.
   - The cage uses 4529 mm.
   - The box's fore-aft position comes from the overhang split measured on the Phase 1 render (`REF_photo`).
   - No image here locates the bumper extremes closely enough to separate the two lengths: R1's U on the bumper extents is far larger than the 18 mm between them.
   - Settled by: a tape measurement bumper to bumper, and knowing whether the bracket is fitted.
4. **Cage items left out for lack of data** (§5):
   - mirror position;
   - eight suspension hard points;
   - hood leading edge;
   - hatch line;
   - beltline;
   - wheel-arch curves.

   Phase 2 measured a hatch-top point and a beltline height on R1, but the cage has nothing to compare them with. Adding them would mean new Phase 1 keys from a builder.
5. **Not checked against any image:**
   - body width;
   - both tracks;
   - mirror width;
   - anything else seen only from the front or rear.

   None of the references is a straight front or rear view.
6. **Images that gave no verdicts:**
   - **R2 (press photo):** an isotropic pinhole camera does not explain its two wheels, so the camera fit was rejected (§6).
   - **R4 and R5 (Canadian Commons photos):** both are steep three-quarter views of black wheels on black tyres, and their cameras were not fitted.
     - R4: both tyre contacts were found, but no rim-lip ellipse met the acceptance rules.
     - R5: only one of the two tyre contacts was found on the car silhouette.
     - Fitting them would need a tyre-silhouette model (a torus outline) instead of the rim-lip circle. That was not built.
   - **R3 (Queens, EXIF focal length):** the best independent image, a real Sport Touring shot with a long lens. Its camera fit was nevertheless rejected (§6).
     - On both wheels the rim detector fitted the inner ring where the spokes meet the dark barrel. It missed the rim lip, which on this wheel is a thin bright machined line between a dark barrel and a black tyre. As a result, the rim and contact residuals are far above the acceptance limits.
     - Two other detectors were tried and discarded because they also failed on this image: a whole-loop edge integral and a Hessian ridge integral. Getting a fit would have needed tuning to this one photo.
7. **Assetto Corsa frame.**
   - Neither the sign of X for `WHEEL_LF` nor the longitudinal origin is confirmed, because no `user_supplied/ac_sdk/` documents were supplied.
   - `scripts/blender/coords.py:project_to_ac` refuses to convert until both are given.
8. **The target car itself was not photographed.**
   - Every image shows a 2022 car in another colour, from the US or Canada.
   - Honda Canada's 2022, 2023 and 2024 hatchback sheets print the same length, height, wheelbase and tracks (§2). That is the only evidence here that the body is unchanged up to 2024.

## 9. Open questions

1. **Photos of your car.** Could you add these to `user_supplied/photos/`?
   - straight left and right side views, taken from 10 m or more with a long lens, with the camera at wheel-centre height;
   - straight front and rear views;
   - the camera's distance and height for each.

   With those, the camera distance becomes known, and the image measures length, height, overhangs, arch tops and the windshield break directly.
2. **Measurements.** For `user_supplied/measurements.txt`:
   - ground-to-fender-lip height and ground-to-wheel-centre height at all four wheels;
   - tyre pressures and fuel level at the time;
   - engine rpm at 100 km/h in 6th gear (for the gear-speed check left open in Phase 1).
3. **Door-jamb placard and tyre sidewall.** Photos of both would confirm tyre size, pressures, axle ratings and paint code. **Please crop out the VIN.**
4. **AC frame.** The `sdk/dev/car_pipeline*.pdf` from your Assetto Corsa install, or the X sign of `WHEEL_LF` read from any Kunos car in ksEditor, plus where AC puts the model origin along the car. See `docs/COORDINATES.md`.
5. **Front licence-plate bracket.** Is one fitted to your car? It decides whether the in-game length should be 4529 mm or about 4547 mm.
6. **Press photo R2.** Is its anisotropy real? Its two wheels look different in size and shape in a way a single pinhole camera cannot explain. If Honda publishes the original-resolution file, its EXIF focal length would let the fit be retried. Otherwise R2 stays a reference for colour and details only.
