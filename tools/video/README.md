# Welcome video edit

The website includes the finished MP4 and poster. The scripts here reproduce
its changes from the separate **Oar Bend Edit Project, revision 7**. The source
movie and full editing project are intentionally not copied into the website.

## Current clip

- The original camera recording is 60 fps. At the slowest point, the previous
  clip held each native frame for about eight output frames. The base footage
  and moving water use bidirectional, adaptive overlapping-block motion
  compensation with variable block sizes. The rower uses the separate native
  foreground interpolation described below.
- Interpolation acts on the clean footage only, before sensor arrows, labels
  and plots are drawn. The original speed ramp, source start/end and total
  duration are retained. The output is still 60 fps; it is not slowed again by
  the browser. Intermediate frames are estimates, not additional measurements.
- The stationary reed bank uses a clean plate assembled from 26 registered
  frames of the original recording, excluding the rower. The person is masked
  in the real source frames, before interpolation. Navy-cap components and
  enclosed head interiors are protected, avoiding the old cutout artifacts.
  Premultiplied foreground colour and its alpha use the same motion field:
  tracked body/head motion controls the silhouette, while dense optical flow
  handles interior detail. This avoids pulling reeds into a second ghost edge.
- The observed bank plate follows the existing camera. Only reeds safely above
  the shoreline are replaced; the lower boat, oars and moving water retain their
  existing motion interpolation. No generated scenery is used. Registration
  fits translation, rotation and uniform scale; median bank alignment residual
  is 0.414 pixels in 1920×1080 analysis coordinates.
- Fractional sensor positions and the camera transform move smoothly between
  their original tracked positions. The sensor-local Y arrows remain `56 ×
  scale`, comparable to X (`50`) and Z (`61`). Both middle-of-shaft references
  remain `87 × scale`.
- A gentle luminance curve affects only the footage panel at x = 0–2129. It
  lowers some dark tones and lifts midtones while preserving black and white.
  No hue or saturation change is applied; the plot panel is ungraded.
- Export is H.264, CRF 17, slow preset, BT.709 and fast-start MP4, 2880 × 1440.

## Requested illustration change

This is a presentation edit to the short website video, not a recalculation of
recorded workout data. The example analysis report is unchanged by these tools.

The requested wider curve preserves the original amplitudes and all positions
through 55°. Its falling side moves right: the 0.5° bend crossing moves from 70°
to 80°, and the 0.1° crossing moves to 84.987°. That 0.1° point is the loaded-end /
wash-start boundary. A short positive tail continues to its actual zero at 86.5°.
These are separate events: Wash starts within the low tail rather than at zero.

The feather boundary remains at 90.187°, so Wash is 5.2° and Release travel is 3.2°.
The early curve, peak, small measured variations, original feather trace and total
sweep remain. Displayed intervals are:

| Metric | Displayed value |
| --- | ---: |
| Catch miss | 2.2° |
| Stroke length | 82.8° |
| Wash | 5.2° |
| Release travel | 3.2° |
| Total arc | 93.4° |

Unrounded components sum exactly to the total arc. Original measurements and
`recorded_*` entries remain in the original editing project. Physical raw roll and the original feather plot
are retained unchanged; the sensor-axis overlays keep their physical roll. See `presentation-change-validation.json`.

## Reproduce

Install Python with Pillow, NumPy, SciPy and OpenCV, and FFmpeg with `minterpolate`,
`zscale`, `tonemap`, `ffv1` and `libx264`. Extract the editing project. Paths below
are examples and should be replaced with your actual folders.

1. Enter the editing project and apply `sensor-y-axis.patch` once:
   `patch -p0 < /path/to/website/tools/video/sensor-y-axis.patch`
2. Prepare the source if necessary: `python3 work_v6/prepare_source.py`.
3. Create a separate copy of the requested presentation data:

```sh
python3 /path/to/website/tools/video/tweak_presentation_curve.py \
  /path/to/editing-project/work_v7/plot_data.json \
  /path/to/temporary/website_plot_data.json
```

4. Prepare the observed clean reed background (this reads the original source,
   not the already annotated website video):

```sh
python3 /path/to/website/tools/video/prepare_reed_background.py \
  /path/to/editing-project /path/to/temporary/reed-background
```

5. Render the finished clip:

```sh
python3 /path/to/website/tools/video/smooth_welcome_video.py \
  /path/to/editing-project \
  /path/to/temporary/rowing-welcome.mp4 \
  --plot-data /path/to/temporary/website_plot_data.json \
  --layered-background /path/to/temporary/reed-background \
  --validation /path/to/temporary/video-validation.json
```

The command creates a lossless, clean-footage intermediate beside the output,
then the final MP4 and `rowing-welcome-poster.jpg`. Copy only the MP4 and poster
into the website's `assets` folder. The intermediate can be deleted after
checking the result; it is not needed for website playback. A provided `--film`
path can reuse an already generated clean-footage intermediate, as was done
for the foreground/background correction. Layered interpolation is applied before
redrawing the graphs and sensor axes and before the existing luminance grade.

The source master remains intact. The selected recording has no audio stream.

For additional curve-only revisions, the renderer can also save
`--cache-restored-film /path/to/temporary/restored-clean-film.mkv`. This is a
lossless RGB copy after the native foreground/background composite but before overlays and the
luminance grade. Reuse it with `--film` and omit both `--layered-background` and `--background`; do not run the
composite twice. This large intermediate is not part of the website.

## Validation scope

The former post-interpolation matte retained duplicate shirt/head outlines and
could cut into the navy cap. It has been replaced by native-frame foreground
interpolation. Current edge checks cover every output frame 100–145, including
the former cap-hole interval 135–140, plus samples throughout the other slow
regions. See `background-validation.json` and `video-validation.json`. These are
visual/encoding checks, not claims of additional measured motion information.
