# Website validation — 6 October 2026, v8

## This release

- 27 HTML pages, 19 combined-site panels and 456 local page/asset/section references checked; no missing targets or duplicate HTML IDs.
- Shared navigation JavaScript and 12 executable inline scripts pass syntax checks.
- Rebuilding is stable: repeated generation produces identical combined index and scoped stylesheet output.
- Browser layout checks covered all 19 panels at 1440, 390 and 320 pixels (57 cases). Two unwrapped tables were fixed; 8 targeted rechecks of their embedded and standalone views at 320 and 390 pixels all pass. No remaining document horizontal overflow was found.
- All 18 browser routing checks passed, including separate iOS/Android categories, canonical section links, refresh, Back and legacy iOS links from the former combined guide.
- No JavaScript, HTTP or failed-resource errors were found during the guide browser checks. The welcome video loads and decodes with muted looping playback.
- New iOS alignment and Android phone-recording mobile screenshots were visually reviewed. The iOS sequence has four required and two optional steps; Android retains its separate supported TXT procedure.
- Checked removal of stale combined-guide labels and visible placeholders.
- ZIP integrity and completeness checked before delivery.

## Preserved and previously verified

The example report is byte-for-byte the delivered v54 report. Its successful plot/animation/Next-stroke, CSV and PNG checks from v7 remain applicable; no report data or code was changed for this release. The corrected welcome movie and poster, kit/calibration/connection images, pricing and domain configuration are preserved.

Website browser checks do not establish the scientific accuracy of estimated metrics or test an iPhone app build. This package was not deployed to the public site. Optional external services and background map providers were not exercised.

For future local reference checks, run `python3 tools/validate_site.py` after the rebuild.
