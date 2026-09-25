# Public website validation — head and back interpolation cleanup

- The prior movie's doubled silhouette behind the head and torso was traced to interpolation of the person together with the reeds. A separate mask defect briefly replaced part of the navy cap with background pixels.
- The revised method separates the person in original recorded frames and interpolates foreground colour and transparency together over the registered reed bank. Original-frame cap and hair shapes were compared with the repaired masks.
- Every frame from 100–145 was inspected in native-detail closeups, along with later positions at frames 155, 175, 195, 216, 226 and 231. The former trailing outline is absent in these checks, and the cap remains solid through the previous failure interval. These are visual checks of the inspected sequence, not a claim that estimated intermediate frames reproduce an unavailable high-frame-rate recording exactly.
- The welcome page and combined index differ from the previous release only in cache-version references. Their existing responsive layout, teal styling and full-screen-only playback control are retained. The previous responsive checks at 1440 px and 390 px remain applicable.
- The supplied example workout report is byte-identical to the previous release. Curve presentation, metric boundaries and recorded data have not changed in this cleanup. Catch miss, stroke length, wash and release travel remain 2.2°, 82.8°, 5.2° and 3.2°, adding to the 93.4° total arc.

- The finished MP4 passed a full decode: 2880 × 1440 pixels, 232 frames at 60 fps, 3.866667 seconds, 29,184,779 bytes. The presentation-data hash matches the previous approved curve. All 232 lower-water regions (y ≥ 900 in the clean footage) were unchanged before video compression.

- The installed cache-versioned video loaded in the browser, automatically played with muted audio and looping, and advanced its playhead without errors. Native playback controls remain disabled; the full-screen control is retained.

This archive contains no app or analysis-server changes and has not been deployed to the live website.
