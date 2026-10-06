# ritmoForceCurve complete website — 6 October 2026, v8

This is a complete replacement website. You do not need to install or download the previous v7 package first. It contains the earlier website updates plus the cross-thread instruction review described below.

## Install

Copy the contents of `rFCsite/` into your existing website checkout, replacing matching website files. Preserve your existing repository history and deployment configuration, then publish through your normal workflow. The included `CNAME` keeps `www.ritmoforcecurve.com`.

This package updates the website. It does not install an iOS app or update the analysis server. App controls and upload features require the corresponding app/server build.

For a local preview, open a terminal in `rFCsite` and run:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/`. Use a browser with JavaScript enabled for the report and replay. Optional map backgrounds need internet access.

## Separate recording paths

- **iOS App:** connection, active-oar setup, alignment, live views, recording and whole-workout upload.
- **Android:** WitMotion connection, its four-block TXT alignment recording, a separate rowing recording, and export/upload.
- **Android Phone Motion & GPS:** Sensor Logger streams, background-recording test, separate-CSV ZIP export and timezone matching.
- **Cloud Analysis:** common settings and results after either platform's data has been uploaded.

The physical kit-assembly and sensor-direction guides are common to the hardware and lead to the correct platform guide. Old links to the iOS section of the former combined guide open the new iOS guide.

## New instruction review

- Added the latest six-step iOS alignment sequence: four core movements, optional square swoop and optional squared float in the same series.
- Simplified squared-float guidance: square the blade, let it float, and keep it steady for 12 seconds. Its saved reference stays with the oar and travels with the workout upload.
- Kept the Android TXT alignment procedure separate; the iOS-only float capture is not presented as an Android importer feature.
- Updated recording guidance for new full-rate acceleration, separate fresh magnetic samples and the frozen per-oar dimensions/calibration snapshot, including manual-factor setups.
- Distinguished stored/uploaded inputs from server magnetic catch-angle reconstruction, which is not added by the recording update.
- Corrected active-oar versus managed-collection guidance and sharing instructions after reviewing the current Swift source.
- Updated Moment/Bend Factor terminology, units, override priority and geometry guidance.
- Reconciled metric and curve choices with the report's current Core/Advanced/Diagnostics controls, including the unified choices and hidden internal geometry fields.
- Updated the shared settings, calibration, source/reference and report-control explanations.

## Preserved from the previous complete update

The corrected welcome movie and poster, mounting photographs and drawings, pricing and guarantees, TestFlight link, domain configuration, navigation fixes, and latest available self-contained example report are included.

The example remains the delivered **5 October gravity-parity v54** report for the 29 September workout. Its bytes and numerical data are unchanged. It demonstrates the plots, boat/oar replay and inner blade/shaft contact model; it predates the 6 October additions to recording metadata. A saved squared-float reference and a physically applied report waterline are documented as separate concepts, rather than silently assumed equivalent.

## Source review

The review used the current v54 complete iOS source, the v54 server/report, the v55 sensor-recording/import update and the subsequent delivered six-step iOS alignment instructions. Previously packaged controls are documented as beta controls; the website does not imply that an uninstalled app/server update is already running on your devices or hosted server.

## Future edits

Individual guide HTML files are the content sources. Update the release in `WEB-RELEASE.json`, then rebuild and check:

```bash
python3 -m pip install beautifulsoup4 tinycss2
python3 tools/rebuild_site.py
python3 tools/validate_site.py
```

The build combines the guides into `index.html` and gives local assets the current cache version. It leaves `example_workout.html` untouched. Replace that file with a newly generated complete report when a newer example is ready.

After publishing, check both `/` and `/index.html`. They should load the same v8 site. If your host retains an old entry page, refresh its HTML cache through your normal deployment process.

Validation details are in `WEB-VALIDATION.md`.
