# ritmoForceCurve complete website — 7 October 2026, v10

This is a complete replacement website, including all previous website changes and the v58 example report. No earlier ZIP is needed.

## Install

Copy the contents of `rFCsite/` into your existing website checkout, replacing matching website files. Preserve the repository history and deployment configuration, then publish through your normal workflow. `CNAME` keeps `www.ritmoforcecurve.com`.

This folder installs the website. Install the matching iOS and server updates separately using the consolidated package’s top-level instructions. Updating website files does not update an app already installed on a phone or an existing analysis server.

For a local preview, run `python3 -m http.server 8000` inside `rFCsite`, then open `http://localhost:8000/`. Interactive curves, replay and CSV downloads require JavaScript. The static report preview also shows the stroke checks and summary averages. Optional map backgrounds need internet access.

## Changes in v10 / v58

- Distance check, Speed check and Energy-loss check are visible in workout, group, piece, selected-group and individual-stroke views. Summary labels begin with **Average**.
- All three summary checks are the arithmetic means of valid individual stroke values. Each valid stroke contributes equally, including valid zero values. Missing values are excluded. Checks are never summed; the energy summary averages stroke percentages rather than reconstructing a ratio from summed energy integrals.
- Workout and individual values wrap on narrow screens. The three checks appear near the start of All Strokes. **Show stroke checks** in Session Overview and All Strokes provides direct access.
- The complete reference documents all **81 shared catalog metrics**, including Peak work per degree, plus the four separately identified iOS magnetic metrics and the available curve families.
- Six guides explain the saved iOS path **Workout Metrics → Recalculate boat checks**, which uses the workout’s original native phone/GPS files and saved settings. Missing source data stays unavailable; other stroke metrics are preserved.
- The no-JavaScript report preview now includes workout, group and piece check averages and individual checks in its first-20-stroke table. The visible **Example report v58** label distinguishes this report from older downloads.

## Separate recording instructions

- **iOS App:** connection, active-oar setup, six-step alignment, live views, recording and whole-workout upload. Alignment keeps four required core movements, optional square swoop and optional squared float. Hold the square blade floating steadily for 12 seconds; its saved reference remains with the oar.
- **Android:** WitMotion connection, five-block TXT alignment ending with the floating square blade, a separate rowing recording, and export/upload. The final block is retained; the importer does not automatically turn it into a calibrated waterline.
- **Android Phone Motion & GPS:** Sensor Logger streams, background-recording checks, separate-CSV ZIP export and timezone matching.
- **Cloud Analysis:** common settings and reports after either platform’s data has been uploaded.

Hardware assembly and sensor-direction guides lead to the appropriate platform. Historical iOS links in the former combined guide still resolve to the iOS guide.

## Example provenance

The example uses the 29 September 2026 workout and preserves the native scalar values, averaged curves and packed individual samples supplied in the 5 October gravity-parity v54 report. The v57 update added three check estimates from its retained, reduced fused-speed profiles; v58 preserves those individual estimates and changes their summary aggregation and presentation.

Checks are available for **620 of 634 strokes**. Their arithmetic means are **55.81 cm distance check**, **1.49 m/s speed check** and **2.21% energy-loss check**. These are visibly labelled retained-profile estimates, not a fresh full-resolution analysis. New server/iOS analyses use original supported native fused-speed samples before display reduction. The energy check follows the requested V² model; it is not measured rowing energy loss.

Saved squared-float references remain distinct from an explicitly applied physical report waterline.

## Earlier work preserved

The corrected welcome video and poster, mounting photographs and drawings, pricing and guarantees, TestFlight link, domain configuration, navigation fixes, calibration units and override priority, full-rate recording guidance, frozen per-oar settings, sharing guidance and shared after-upload settings workflow remain included.

Source history: v54 complete iOS/server sources and report; cumulative v56 recording/alignment changes; v57 native checks and report restoration; v58 metric availability and summary consistency fixes. This history identifies the supplied code; it does not imply the new app or server is already deployed.

## Future edits

Individual guide HTML files are the content sources. Update `WEB-RELEASE.json`, then run:

```bash
python3 -m pip install beautifulsoup4 tinycss2
python3 tools/rebuild_site.py
python3 tools/validate_site.py
```

The build combines guides into `index.html`, scopes their styles and adds the current cache version to local assets. It leaves `example_workout.html` untouched. After replacing the example, update its SHA-256 in `WEB-RELEASE.json`.

After publishing, check both `/` and `/index.html`, plus the example link. They should show the v10 site and v58 report. Refresh the host’s HTML cache if it retains an older entry page. Updating a website cannot change an older HTML file already downloaded by a reader.
