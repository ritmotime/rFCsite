#!/usr/bin/env python3
"""Rebuild the observed reed-bank plate for the supplied oar-video project.

Usage:
    python prepare_reed_background.py /path/to/Oar_Bend_Edit_Project /path/to/output

Requires Python 3, numpy and opencv-python. The original project is read only.
This is deliberately a recipe for this particular 191-frame recording, not a
general background-removal tool. Reference frame 90, the bank tracking region,
and the subject masks have been checked against this recording. Do not reuse
them for another video without reviewing the masks and resulting plate.

Coordinates: tracking uses 1920 x 1080; original footage is 3840 x 2160. The
saved 3 x 3 transforms map each source frame into reference frame 90 in tracking
coordinates. Native-coordinate transforms are D @ H @ inverse(D), where
D = diag(2, 2, 1). Only the observed reed bank is suitable for replacement;
moving water and boat fragments below the shoreline must be kept out of the
composite. The plate has no invented or reflected pixels.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import warnings


REFERENCE_FRAME = 90
FRAME_COUNT = 191
ANALYSIS_SIZE = (1920, 1080)
NATIVE_SIZE = (3840, 2160)
PLATE_SIZE = (3840, 1000)


def read_frame(cap, frame_index):
    import cv2

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, image = cap.read()
    if not ok:
        raise RuntimeError(f"Cannot decode source frame {frame_index}")
    return image


def register_bank(cap):
    """Fit similarity transforms from bidirectionally verified bank tracks."""
    import cv2
    import numpy as np

    reference = cv2.cvtColor(
        cv2.resize(read_frame(cap, REFERENCE_FRAME), ANALYSIS_SIZE),
        cv2.COLOR_BGR2GRAY,
    )
    mask = np.zeros_like(reference)
    mask[8:385, 8:-8] = 255
    mask[130:450, 690:1090] = 0  # Reference-frame head, torso and arms.
    points = cv2.goodFeaturesToTrack(
        reference, 2500, 0.015, 9, mask=mask, blockSize=5
    )
    if points is None or len(points) < 30:
        raise RuntimeError("Not enough reed-bank features in reference frame 90")
    lk_options = dict(winSize=(25, 25), maxLevel=4, criteria=(3, 40, 0.001))
    transforms, diagnostics = [], []
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    for frame_index in range(FRAME_COUNT):
        ok, image = cap.read()
        if not ok:
            raise RuntimeError(f"Cannot decode source frame {frame_index}")
        gray = cv2.cvtColor(cv2.resize(image, ANALYSIS_SIZE), cv2.COLOR_BGR2GRAY)
        forward, status, error = cv2.calcOpticalFlowPyrLK(
            reference, gray, points, None, **lk_options
        )
        backward, back_status, _ = cv2.calcOpticalFlowPyrLK(
            gray, reference, forward, None, **lk_options
        )
        valid = (
            (status[:, 0] > 0)
            & (back_status[:, 0] > 0)
            & (np.linalg.norm(backward[:, 0] - points[:, 0], axis=1) < 0.8)
            & (error[:, 0] < 22)
        )
        source, target = forward[valid, 0], points[valid, 0]
        if len(source) < 30:
            raise RuntimeError(f"Insufficient bank tracks in frame {frame_index}")
        affine, inliers = cv2.estimateAffinePartial2D(
            source, target, method=cv2.RANSAC, ransacReprojThreshold=1.5,
            maxIters=2000, confidence=0.999, refineIters=20,
        )
        if affine is None or inliers is None or int(inliers.sum()) < 30:
            raise RuntimeError(f"Bank registration failed in frame {frame_index}")
        transform = np.vstack([affine, [0.0, 0.0, 1.0]])
        predicted = cv2.perspectiveTransform(source[None], transform)[0]
        residual = np.linalg.norm(predicted - target, axis=1)[inliers[:, 0] > 0]
        transforms.append(transform)
        diagnostics.append({
            "frame": frame_index, "tracked": len(source),
            "inliers": int(inliers.sum()),
            "median_residual_analysis_px": float(np.median(residual)),
            "p95_residual_analysis_px": float(np.percentile(residual, 95)),
        })
        if frame_index % 30 == 0:
            print(f"Registered {frame_index + 1}/{FRAME_COUNT} frames", flush=True)
    return np.asarray(transforms), diagnostics


def build_plate(cap, tracking, transforms):
    """Use a masked median of 26 observed frames, in native pixel coordinates."""
    import cv2
    import numpy as np

    frames = sorted(set(range(0, FRAME_COUNT, 8)) | {REFERENCE_FRAME, 190})
    double = np.diag([2.0, 2.0, 1.0])
    half = np.diag([0.5, 0.5, 1.0])
    images, masks, provenance = [], [], []
    for frame_index in frames:
        image = read_frame(cap, frame_index)
        mask = np.full(image.shape[:2], 255, np.uint8)
        mask[:5] = mask[-5:] = 0
        mask[:, :5] = mask[:, -5:] = 0
        bbox = tracking[frame_index].get("red_shirt_bbox")
        if bbox:
            x, y, width, height = bbox
            cv2.rectangle(
                mask, (int(2 * (x - 75)), int(2 * (y - 105))),
                (int(2 * (x + width + 110)), int(2 * (y + height + 140))),
                0, -1,
            )
        elif frame_index < 8:
            mask[200:1100, 3740:] = 0  # Person approaching the right edge.
        elif 128 <= frame_index <= 144:
            mask[200:1100, :220] = 0  # Person leaving the left edge.
        native_transform = double @ transforms[frame_index] @ half
        images.append(cv2.warpPerspective(
            image, native_transform, PLATE_SIZE, flags=cv2.INTER_LANCZOS4,
            borderMode=cv2.BORDER_CONSTANT,
        ))
        valid = cv2.warpPerspective(
            mask, native_transform, PLATE_SIZE, flags=cv2.INTER_NEAREST,
            borderMode=cv2.BORDER_CONSTANT,
        )
        masks.append(cv2.erode(valid, np.ones((5, 5), np.uint8)) > 0)
        provenance.append({
            "frame": frame_index, "person_bbox_analysis": bbox,
            "person_mask_expansion_analysis": [-75, -105, 110, 140] if bbox else None,
        })
        print(f"Prepared plate observation {frame_index}", flush=True)
    images, masks = np.stack(images), np.stack(masks)
    counts = masks.sum(axis=0).astype(np.uint8)
    plate = np.empty((PLATE_SIZE[1], PLATE_SIZE[0], 3), np.uint8)
    # Small row blocks keep float working memory modest. Missing outer-border
    # pixels remain black and are explicitly marked by zero observation count.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="All-NaN slice encountered")
        for y in range(0, PLATE_SIZE[1], 40):
            chunk = images[:, y:y + 40].astype(np.float32)
            chunk[~masks[:, y:y + 40]] = np.nan
            plate[y:y + 40] = np.nan_to_num(
                np.nanmedian(chunk, axis=0), nan=0.0
            ).astype(np.uint8)
    return plate, counts, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", type=Path, help="Edit-project directory containing work_v4 and work_v6")
    parser.add_argument("output", type=Path, help="Directory for the regenerated plate and registration files")
    args = parser.parse_args()
    # Import after argument parsing so --help works before dependencies install.
    import cv2
    import numpy as np

    project, output = args.project.expanduser().resolve(), args.output.expanduser().resolve()
    source_path = project / "work_v6" / "source_color_4k.mp4"
    tracking_path = project / "work_v4" / "boat_tracking.json"
    if not source_path.is_file() or not tracking_path.is_file():
        parser.error("Project must contain work_v6/source_color_4k.mp4 and work_v4/boat_tracking.json")
    tracking = {int(row["frame"]): row for row in json.loads(tracking_path.read_text())["rows"]}
    if not all(index in tracking for index in range(FRAME_COUNT)):
        parser.error("Expected tracking rows for all source frames 0 through 190")
    cv2.setNumThreads(2)
    cap = cv2.VideoCapture(str(source_path))
    try:
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open {source_path}")
        size = (round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        if size != NATIVE_SIZE or round(cap.get(cv2.CAP_PROP_FRAME_COUNT)) != FRAME_COUNT:
            raise ValueError("This recipe expects the supplied 3840×2160, 191-frame source")
        transforms, diagnostics = register_bank(cap)
        plate, counts, observations = build_plate(cap, tracking, transforms)
    finally:
        cap.release()
    output.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output / "background_plate_native.png"), plate):
        raise RuntimeError("Cannot write background_plate_native.png")
    np.savez(output / "registration_transforms.npz", similarity=transforms)
    np.save(output / "observation_count.npy", counts)
    metadata = {
        "reference_frame": REFERENCE_FRAME,
        "size_native": list(PLATE_SIZE),
        "analysis_size": list(ANALYSIS_SIZE),
        "source_video": str(source_path), "source_tracking": str(tracking_path),
        "matrix_direction": "source frame j -> reference frame 90, analysis coordinates",
        "native_conversion": "diag(2,2,1) @ Hanalysis @ diag(.5,.5,1)",
        "shoreline_analysis_approximation": "y = 428 - 0.0094 * x",
        "clean_bank_use_native_y": [0, 820], "bank_water_blend_native_y": [810, 860],
        "caution": "Use the reed bank only. Water/boat remnants below the shoreline are not a valid replacement. Unobserved border pixels are black; consult observation_count.npy.",
        "method": "26 registered source frames; broad observed shirt/head/arm exclusion; masked RGB temporal median; similarity transforms from bidirectional bank feature tracks. No generated imagery.",
        "frame_count": len(observations), "sources": observations,
        "coverage_bank_y0_810": {
            "min": int(counts[:810].min()), "median": float(np.median(counts[:810])),
            "percent_ge5": float(np.mean(counts[:810] >= 5) * 100),
            "percent_zero": float(np.mean(counts[:810] == 0) * 100),
        },
        "registration_diagnostics": diagnostics,
    }
    (output / "registration_plate_provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Saved plate, transforms, observation counts and provenance to {output}")


if __name__ == "__main__":
    main()
