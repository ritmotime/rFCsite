# Ritmo website help update — 19 November 2026

This is the complete trimmed website, with its existing content and required media preserved. It is prepared for your current hosting workflow; it has not been published to the live domain.

## Added

- Your Chatling agent 6638573337, loaded once on top-level HTML pages. The bottom-right floating launcher stays visible when scrolling. It does not create a second chat inside an embedded example-report frame.
- `workout-report-overview.html`: a short report guide with lightweight HTML examples of navigation/buttons.
- `recording-troubleshooting.html`: connections, missing/gapped recordings, setup/calibration, units and reference planes, boat motion and GPS. It excludes historical software-bug workarounds.
- Links from Help, report overview and report controls, including the index page's built-in panels.

## Install

Unzip, then copy the CONTENTS of `rFCsite` into your existing website folder/repository and publish using your normal process. Preserve any existing `.git` directory. The domain CNAME is retained. Keep `ritmo-help.js`, the two guide pages and their CSS alongside the HTML pages. Do not upload this ZIP as Chatling knowledge.

The loader uses your supplied public chatbot ID; no private API key is included. Widget title, position and auto-open behavior are controlled in your Chatling widget settings. Bottom right and closed-on-load were observed in the preview; the current header reads “Support Agent”. Set Header Title to “Ritmo Help” in Chatling if desired.

## Verification

The widget opened and closed in the browser preview, remained at bottom right after scrolling, and loaded once on the tested pages. The new guide links and section navigation were exercised. All 31 top-level HTML documents include one shared loader. A frame guard prevents loading inside an embedded report. Source links, required assets, archive integrity and text conversions were checked separately. The live domain is not changed by downloading this package.

Replace the old Chatling knowledge using the corrected starter kit. The website embed does not automatically replace uploaded documents. Test the bot after the five new documents are Processed.
