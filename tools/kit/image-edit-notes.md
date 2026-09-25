# Kit illustration sources and image-edit provenance

The assembly guide uses the actual kit supplied in `IMG_3895.jpg` (separate parts), `IMG_3898.jpg` (assembled mount), and `sensor_bracket_assy.MOV` (assembly sequence). The original uploads were not modified and are not duplicated in this website archive.

## Final photo assets

- `assets/kit-parts-clean-v2.png`: background removed and lighting/texture cleaned from IMG_3895.jpg.
- `assets/kit-assembled-clean-v2.png`: background removed and lighting/texture cleaned from IMG_3898.jpg; a second pass corrected the printed brand area and removed an invented trademark symbol.

Both use the built-in imagegen tool in edit mode, with transparent background enabled. No CLI/API fallback was used. The cutouts were inspected against the original photographs for component count, slots, housing openings, clip lips, saddle geometry and visible strap routing. The small letter annotations are HTML overlays with a readable key; they are not baked into the images. These cleaned product images are visual assembly references, not dimensional drawings.

## Prompts used

### Separate parts

Use case: background-extraction. Edit target: the supplied photograph of the disassembled RitmoForceCurve oar sensor kit. Create a clean, high-resolution product-reference cutout for an assembly guide. Remove ONLY the white paper, wood table, hard cast shadows and background. Keep every actual component, exact relative sizes, perspective, orientation and relative arrangement: the real sensor and printed face, black open housing with all its openings and ribs, two yellow slotted clips with their bent lips, curved yellow saddle with its side lips, yellow flexible ring, and black hook-and-loop strap. Preserve the true sensor button, printed logo, USB-C opening, all slots, curves, edges, and holes. Smooth print texture moderately and clean lighting to a polished product-photo finish without changing geometry. Retain enough fine material detail to show how pieces fit. No added screws, fasteners, parts, labels, arrows, text or watermark. Use genuine transparent background with clean anti-aliased edges; do not add fake drop shadows or checkerboard. Do not turn it into a cartoon or line drawing.

### Assembled mount

Use case: background-extraction. Edit target: the supplied photograph of the assembled RitmoForceCurve oar sensor in its real black housing, yellow clips and black hook-and-loop strap. Produce a clean product-reference cutout for a technical assembly guide. Remove the wooden table, wall, paper and their shadows only. Keep the assembled product exactly as photographed: same perspective and relative geometry, front rectangular opening, true sensor and printed face/button/logo, two real rectangular top ventilation openings with white sensor rear visible, black housing ribs and curves, both yellow clip plates with bent retaining lips, actual strap loop and exactly the visible strap routing. Clean and smooth print texture and lighting to a polished product photo while retaining mechanical detail. Preserve all genuine holes and slots, including openings that are partly obscured. Do not invent screws, fasteners, extra clip shapes, buttons or labels. Preserve the original text and logo placement as closely as possible. Keep the full strap and housing within frame with a little margin. Transparent background, clean edges, no synthetic shadow, no checkerboard, no cartoon.

### Printed-brand correction

Precise correction to edit target image 1, the clean transparent assembled-sensor cutout. Supporting original photo is image 2 and must only be used to check the small printed logo. Remove the invented registered-trademark symbol entirely. Restore the printed brand text exactly as in the original photo: "ritmoForceCurve" with a lowercase r, lowercase itmo, capital F and C. Keep it small and in the original understated yellow style. Do not add any trademark, copyright or other symbol. Change only that printed brand-text area. Preserve all component geometry, framing, real openings, strap and transparent background exactly as they currently are. No other changes.

## Mechanical drawings

`kit-clips.svg`, `kit-sensor.svg`, `kit-saddle.svg` and `kit-strap.svg` are hand-authored vector assembly references based on the supplied photos and movie. They add retaining lips, slot openings, housing depth, section views and fine leader lines. They carry no dimensional or manufacturing tolerances. Each drawing opens at full size when tapped.

The prior motion alignment procedure and the original sensor-direction photograph are unchanged.
