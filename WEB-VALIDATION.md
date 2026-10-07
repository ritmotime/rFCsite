# Website validation — 7 October 2026, v10 / v58

## Guides and navigation

- The complete shared reference covers all 81 catalog metrics; four additional iOS magnetic metrics are identified separately.
- iOS and Android recording paths remain separate. Android lists five alignment blocks; iOS retains four required steps and two optional steps.
- Six updated guides document **Workout Metrics → Recalculate boat checks** and the report’s **Show stroke checks** controls.
- The combined index and scoped styles were rebuilt from the guide sources. The site validator checked 27 HTML pages, 19 navigation panels and 474 local references, including anchors, duplicate IDs and release cache parameters; no errors were found.
- Chromium checks passed at 1440, 390 and 320 pixels: 18 standalone-guide checks and 57 combined-panel checks, with no document overflow. All 18 historical/navigation route checks passed. There were no JavaScript, HTTP or resource-load errors; the welcome video loaded and decoded.

## Example report

- Actual displayed values were checked in workout, group, piece and selected-group summaries and their detail dialogs against arithmetic means recomputed from individual strokes. They survive calibration apply/reset and course-reference changes.
- Example averages are **55.81 cm**, **1.49 m/s** and **2.21%**, with **620 / 634** valid strokes. Per-stroke values remain explicitly labelled estimates from retained reduced profiles; no native raw-data reanalysis was performed.
- Workout and individual values were checked against their viewport and overflow ancestors at 1440 and 390 pixels. All three remain horizontally visible.
- The All Strokes table has 81 columns and 634 rows. Its first columns include the three checks. All 44,362 populated numeric cells were compared with their source values and display-unit conversion; no mismatches were found.
- Stroke, group, piece and selected-group CSV values match the underlying strokes or their arithmetic means. Summary CSV headers identify the stroke-mean convention and units.
- Fresh reports, older saved table visibility, unavailable checks, selected groups, animation averages, reloads and direct Show stroke checks actions were exercised without JavaScript errors.
- With JavaScript disabled, the static preview displays the same check averages, updated group/piece tables and the first 20 individual stroke values.
- Original native metrics, averaged curves and packed individual samples are preserved. The current report assets are embedded exactly; the example SHA-256 is recorded in `WEB-RELEASE.json`.

The corrected welcome video/poster, kit images, pricing and domain configuration remain included. No website publication was performed. Website checks do not compile the iOS app or deploy the analysis server; see the consolidated package’s validation notes for code checks.

Run `python3 tools/validate_site.py` after future guide rebuilds.
