# RitmoForceCurve public website update

This archive is the complete public website. Copy the contents of `rFCsite` into your existing website checkout and publish through your usual workflow. Keep the asset folders and the included `CNAME` together with the HTML files.

For a local preview, run this from the extracted `rFCsite` folder:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000`. The website needs no runtime server beyond static file hosting. This release does not change the app or Auto Analysis server.

## What changed

- The video uses a clean, aligned reed-bank background assembled from unobscured views in the original recording. The latest refinement separates the rower from the original recorded frames before interpolating the motion, addressing the doubled outline behind the head and back and the ghost reeds carried along that edge. The cap and hair are protected from holes in the foreground mask.

- The welcome page and Rowing Physics now explain **oar based vs oarlock based systems**, the changing sleeve/oarlock contact, and why shaft measurements give a direct view of the oar held by the rower and loaded by the water.

- Teal is the fixed detail colour, alongside canary yellow and cool slate. The accent chooser has been removed; old browser preferences no longer change the colour.
- The welcome title is directly below the tabs, with the iOS beta and kit buttons alongside it on wider screens.
- The latest Oar Bend Angle Recovery video has a subtle luminance adjustment to the rowing footage. The latest requested video edit adds motion-interpolated frames through the slowdown and widens the main descending part of the illustrative bend curve and shortens its low tail, with wash set to 5.2° and release travel near 3.2°. These video presentation changes do not change the example workout data. The sensor Y arrows now match the apparent length of X/Z; the middle shaft reference arrows retain their original length.
- The descriptive text is more prominent below the video and connects oar motion and force application with enjoyable rowing and team-boat swing.
- The kit guide combines retouched photographs of the actual parts with detailed mechanical drawings: clip fit, a curved housing that seats flush in the saddle, and inside-to-outside strap threading with the strap folding back onto itself on the same side.
- The sensor direction guide explicitly identifies +Y toward the handle and −Y toward the blade/button side.
- The welcome video starts automatically, loops at its built-in speed and exposes only a full-screen button. Browsers without element fullscreen use a full-window view with the same controls.
- The site wordmark now carries a superscript ™. Oar based and oarlock based measurement systems are described using their different measurement references.
- The new 10 September 2026 workout report replaces the previous example.
- The website consistently uses “oarlock” and “Moment/Bend Factor”. Ratio is in Oar based metrics. Rowing Physics has a visible tab with the starting-line explanation and the relationship between moment, inboard length and handle force.
- Stroke shading is explained as the variation and density of recorded strokes.

## Welcome video

The video keeps its original speed ramp and duration. The rower and stationary reed bank are processed as separate layers. The rower's colour and outline move together between original recorded frames, while the registered background keeps the reeds aligned. The sensor arrows, tracking and charts are rendered separately at the corresponding timestamps. Interpolation estimates the missing views between recorded frames.

The latest illustrative curve edit keeps a wider main curve and a short low tail. Wash begins within that tail at the displayed loading threshold; the small remaining bend reaches zero before release travel begins. The displayed angle segments are:

| Segment | Degrees |
| --- | ---: |
| Catch miss | 2.2 |
| Stroke length | 82.8 |
| Finish wash | 5.2 |
| Release travel | 3.2 |
| Total sweep arc | 93.4 |

The adjoining feather/release boundary follows that edit. These are video presentation edits; the original recording and supplied workout report retain their measured data. See `tools/video/README.md` for the reproduction method.

## Report factor display

The example report displays Moment/Bend Factor in N·m per degree. Its input converts at the display boundary into the existing internal convention. Default numerical data, curves and stroke metrics are preserved. Changing the factor still changes the derived moment/work/power quantities consistently, and Reset restores the original calibration.

## Later edits

Each guide is also a standalone HTML page. The main `index.html` contains copies for instant navigation. After changing a page, rebuild the combined index:

```bash
python3 -m pip install beautifulsoup4 tinycss2
python3 tools/rebuild_site.py
```

Replace `assets/rowing-welcome.mp4` and its matching poster to change the welcome video later. The player supports an HTTPS video URL on your own server as well. Use `video/mp4` and byte-range support for reliable playback. Bump the URL version in `welcome.html` after replacing a cached asset, then rebuild the index.

The long kit-assembly movie is not embedded on the assembly page; add its link to the existing Kit Videos table when ready.
