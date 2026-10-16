# Website validation — 16 October 2026, v11

## Guides and navigation

- The current public metric reference covers the Core and Advanced catalog. Definitions were checked against the completed iOS v97-sync1 and server v96-view2 sources.
- Independent review checked current metric definitions, subject grouping, app workflows and report-control wording.
- The combined index was rebuilt from the standalone guides. All 19 navigation entries match their embedded panels.
- All non-example HTML pages were scanned for excluded visible content and obsolete special check controls; none remain.
- Local page, image and section links pass validation. Shared JavaScript files pass syntax checks.
- The welcome video, poster and custom-domain file match the previous package byte-for-byte. Existing colors and useful setup illustrations are retained.

## Fresh example

The example was regenerated on 16 October 2026 using the server v96-view2 pipeline and the original 29 September 2026 DAT workout, with its matching GPS, phone motion and processing settings:

- `rFC202609291245.dat`: oar recording.
- `acgy202609291245.dat`: phone motion.
- `gps202609291245.dat`: GPS.
- Captured processing sidecar: calibration and setup, including the applied scale factor.

The generated workout contains 634 strokes, four groups and two pieces. The GPS route has 2,707 points. GPS speed and distance are available for 629 strokes; fused boat speed and the IMU speed/distance ranges for 626; the V² energy estimate for 624. Missing support remains unavailable.

The public report uses these newly computed values. Public presentation filtering removes excluded fields and special check controls without changing the calculations. Check metrics use the normal Boat category and catalog order.

Final report verification details and the file hash are retained in `WEB-RELEASE.json` and the example's provenance notes.

## Verification limit

No visual browser QA was performed in this environment. Static checks and report data/DOM checks do not establish a fresh desktop/mobile visual inspection. The website package has not been published to the live domain.
