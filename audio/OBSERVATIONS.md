# Audio observations: when overrun burble really occurs

Domain 10, Phase 1. **No audio was analyzed in this phase.** Every clip in
`audio/reference_database.json` was catalogued from page text only (titles, descriptions,
comments, manufacturer pages). YouTube playback sits behind a "Sign in to confirm you're not
a bot" wall in this sandbox, later page loads returned HTTP 429 / Google "sorry" pages, and
downloading streaming media is against the site's terms, so nothing was downloaded. Nothing
below describes how any clip sounds.

Evidence levels used here:
- **[THIS CAR]**: a source about a 2022–2024 Civic 1.5T hatchback, with its class.
- **[GENERAL]**: general engine or exhaust physics or tuning practice, cited.
- **[INFERENCE]**: my reasoning from the two levels above. It is not evidence, and Phase 2
  should treat it as a tunable assumption.

## 1. Evidence about this car and engine

| # | Finding | Source (class) | Strength |
|---|---|---|---|
| 1.1 | Stock exhaust on the Sport Touring hatch (US EPC, 6MT and CVT share the parts): front pipe A with a flexible section, then **one converter assembly** shared by all 1.5T trims including the Si, then a centre pipe with **one in-line resonator** and a Y-split, then **two rear mufflers** (L 18305-T47-A51, R 18307-T47-A51) with finishers. | hondapartsnow catalog and diagram T404B0200 (A, as a reproduction of the Honda EPC) | Good for topology. Pipe diameters and catalyst-brick count are **unknown**. |
| 1.2 | The user's reference clip is a **muffler and resonator delete with the catalysts retained**, on the factory piping and finishers. It is *not* a bolt-on cat-back. Creator replies: "i still have cats. mine isn’t straight piped… only the mufflers and resonators"; "i didn’t touch my cats"; "stock exhaust". | YouTube comments, creator replies (C, unverified owner statement) | Documented: the exhaust. **Not documented:** gearbox (commenters claim CVT, e.g. "seeing the reverse light flash it’s cvt obviously"; others say manual), tune (several "is it tuned?" questions went unanswered), trim and intake/downpipe. |
| 1.3 | An owner reports: "I have a 23 Sport Touring 6 speed that sounds just like this. Has a Borla S Type exhaust on it. I was thinking it had a burble tune on it or something from previous owner." | Comment on the reference clip (C-, anecdote) | Weak. It suggests that audible overrun events can occur with a bolt-on cat-back on this exact car, possibly on a stock ECU, but the owner does not know whether the car is tuned. |
| 1.4 | "I got the magnaflow catback for the sport touring, sounds similar but doesn’t pop as much". | Comment on the reference clip (C-, anecdote) | Weak. It suggests that a silenced cat-back (MagnaFlow 19652: three straight-through mufflers) yields **fewer audible pops** than the muffler and resonator delete. |
| 1.5 | Rev hang: one review mentions "some rev hang" on a 2022 Sport Touring 6MT. An owner thread reports rev hang reduced by a KTuner calibration, which implies the hang is calibration-related. The car has a dual-mass flywheel (Honda Canada 2021 debut release). | Drivetrain and engine threads (`docs/research_log/05_drivetrain.md`, `04_engine.md`) | Qualitative only. Duration and rpm are **unknown**. |
| 1.6 | **Stock-ECU DFCO thresholds** for this engine (entry rpm, delay after pedal release, re-entry rpm, coolant or time conditions): **unknown**. The Hondata forum thread on "Fuel overrun cutoff" is disallowed by robots.txt. No Honda or tuner documentation for the 11th-gen 1.5T was found. | Recorded as `audio.overrun_fuel_cut_this_car` (unknown) | Gap. This matters most for gating the burble. |

## 2. General engine and exhaust physics (cited)

- **DFCO.** "Fuel injection engines generally do not use fuel while engine braking. This is known
  as deceleration fuel cut-off (DFCO)." When the pedal is released, "This causes fuel injection
  to cease and the throttle valve to close almost completely, greatly restricting forced airflow
  from, for example, a turbocharger." (Wikipedia, *Engine braking*.) During fully established
  DFCO, no fuel reaches the cylinders. Any post-combustion "pop" therefore needs fuel from
  *before* the cut or from the transition into it.
- **What burble or pop tunes change.** Tuners describe the method as: "disable the deceleration fuel
  cut off at the RPM limit you want the exhaust bangs to start, and then to also retard the
  timing so that the combustion happens while the exhaust valve is open". The retard sits in the
  "0-20kpa area of the map" (closed-throttle, very-low-load cells). Another post: "turn off
  deceleration fuel cut (overrun) and retard timing in low load area if you only want it to pop
  and bang off throttle". (HP Academy forum threads, C, tuner community.) **Implication:** sustained,
  repeating overrun crackle depends on *calibration* (fuel kept on plus heavy retard). A stock
  calibration with normal DFCO is not set up to produce it.
- **Catalysts.** The same thread notes that the effect "does not have a positive impact on cats.
  even the effect is greater without cats". Mufflers and resonators attenuate the pressure pulses
  further (see 1.4).
- **Mechanism of exhaust combustion.** In antilag systems, ignition is heavily retarded and extra
  fuel is added. "The excess fuel/air mixture escapes through the exhaust valves and combusts in
  the hot" exhaust manifold or turbine (Wikipedia, *Antilag system*). Overrun pops are the
  small-scale, unintended form of the same process: unburnt or late-burning mixture meets
  oxygen in hot exhaust.

## 3. Inferences for Phase 2 gating (marked; not evidence)

**[INFERENCE]** For a stock-ECU Sport Touring 6MT with a silenced, catalyst-retaining cat-back
(the user's target), burble should be **rare, short and soft**, never a continuous crackle:

1. **Trigger:** throttle closes quickly (tip-out) **after meaningful load**, with exhaust hot
   and boost present, at **mid-to-high rpm**. Typical cases are a lift at the end of a pull and the
   lift into an upshift, when the clutch goes in and the revs hang. A few events can
   occur in the short window between pedal release and full DFCO, while residual fuel and
   retarded torque-reduction spark pass into the exhaust.
2. **Then stop:** once DFCO is established, events should die out within a fraction of a second
   to about 1 s and **not continue through a long coast-down**. Sustained popping on a long
   overrun is tune behaviour (section 2) and should not be modelled for the stock car.
3. **Should NOT occur:** at steady cruise; during a slow, gentle lift (low preceding load, cool
   exhaust, little residual fuel); at idle; during cold start; under load; on a lift from low rpm
   near idle. Near idle, DFCO is normally inhibited to prevent stalling, which is general
   practice and not verified for this ECU.
4. **Variation:** the event probability should rise with preceding load, boost, exhaust
   temperature and rpm at lift. It should be lower with the stock mufflers (factory exhaust: near
   zero audibility) and higher with a muffler and resonator delete (the reference clip). The MagnaFlow
   or Borla cat-back sits between the two (anecdotes 1.3 and 1.4).
5. **Rev hang** (1.5) lengthens the clutch-in, closed-throttle window during upshifts.
   That window is the most plausible place for a manual car's upshift "blip-burble".

**What retires these inferences:** a synced recording and OBD log of the user's car (see below)
giving DFCO entry delay and rpm, re-entry rpm, and the onset times of pops relative to pedal
release.

## 4. What is needed from the user

- **A recording you have rights to:** ideally your own car (or the target cat-back on a 6MT ST),
  WAV or FLAC at 44.1 kHz or higher, microphone fixed about 0.5 m behind one tip and a second inside
  the cabin, no music. Include: idle; slow and fast lift-offs from 3000, 4500 and 6000 rpm in 3rd;
  clutch-in upshifts 2-3 and 3-4 at WOT; a long coast-down in 4th; a cold start.
- **A synced OBD log at 10 Hz or faster:** rpm, pedal and throttle, lambda or STFT or injector pulse,
  coolant, gear. This gives the DFCO thresholds (`audio.overrun_fuel_cut_this_car`).
- **For the reference clip:** the creator's statement of gearbox and tune, or the creator's
  permission to analyze the audio. Until then its pop count, spacing, duration, tone, level and
  delay after throttle close remain **unknown**.
