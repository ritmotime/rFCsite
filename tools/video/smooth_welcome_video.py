#!/usr/bin/env python3
"""Interpolate clean source footage, then redraw the v7 overlays at 60 fps.

Requires the separate Oar Bend Edit Project v7, prepared 4K SDR source, OpenCV,
NumPy, Pillow and FFmpeg. No text, plotted data or overlay is passed through
optical flow. The source movie and project data are not modified.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np


def make_interpolated_film(renderer, motion, output):
    """Interpolate source frames at the original output timeline's timestamps."""
    times = [float(np.interp(j, renderer._sf, renderer._ot))
             for j in range(renderer.START, renderer.LAST + 1)]
    # Look-ahead frames let minterpolate emit the actual final source frame.
    # They are trimmed from output and do not extend the published recording.
    for _ in range(3):
        times.append(times[-1] + 1 / renderer.FPS)
    terms = [f"if(gte(N,{j}),{times[j] - times[j - 1]:.12f},0)"
             for j in range(1, len(times))]
    expression = "+".join(terms)
    count = math.ceil(renderer.END * renderer.FPS) + 1
    filters = ("settb=1/1000000,setpts='(" + expression + ")/TB',"
               "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:"
               "me_mode=bidir:vsbmc=1:mb_size=8:search_param=64:scd=none,"
               f"trim=end_frame={count}")
    temporary = output.with_name(output.stem + ".interpolating.mkv")
    command = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "2130x1440", "-r", "60", "-i", "-", "-vf", filters,
               "-an", "-c:v", "ffv1", "-level", "3", "-threads", "4",
               "-pix_fmt", "yuv444p", str(temporary)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    for n in range(len(times)):
        j = min(renderer.LAST, renderer.START + n)
        process.stdin.write(motion.get_film(j, "follow")[0].tobytes())
        if n % 10 == 0:
            print(f"Interpolating source frame {n}/{len(times)}", flush=True)
    process.stdin.close()
    if process.wait():
        raise RuntimeError("Footage interpolation failed")
    temporary.replace(output)


def install_renderer(project, plot_data=None, film=None, background=None, film_hook=None, layered_background=None):
    sys.path.insert(0, str(project / "work_v7"))
    renderer = importlib.import_module("render_v7")
    motion = importlib.import_module("motion_v6")
    if plot_data is not None:
        renderer.DATA = json.loads(Path(plot_data).read_text())
        renderer.T = np.asarray(renderer.DATA["time"], float)
        renderer.ARC = np.asarray(renderer.DATA["angle"], float)
        renderer.CURVES = [np.asarray(renderer.DATA[k], float) for k in renderer.KEYS]
        renderer.STATIC = renderer.static_plots()
    native_sensor_data = renderer.sensor_data
    bank = None
    if background is not None:
        from reed_background import ReedBank
        bank = ReedBank(project, background, motion)

    person = None
    if layered_background is not None:
        from layered_person import LayeredPerson
        person = LayeredPerson(project, layered_background, motion, renderer.LAST)

    capture = None
    if film is not None:
        capture = cv2.VideoCapture(str(film))
        if not capture.isOpened():
            raise RuntimeError(f"Cannot open interpolated footage: {film}")

    def smooth_film(f, view):
        f = float(np.clip(f, renderer.START, renderer.LAST))
        j = min(int(math.floor(f)), renderer.LAST - 1)
        t = f - j
        ma = motion.camera_matrix(j, view)
        mb = motion.camera_matrix(j + 1, view)
        if capture is None:
            raise RuntimeError("Prepare interpolated footage before rendering")
        ok, bgr = capture.read()
        if not ok:
            raise RuntimeError("Interpolated footage ended before final output frame")
        pixels = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        if bank is not None:
            pixels, _, _, _ = bank.frame(pixels, f)
        if person is not None:
            pixels, _, _ = person.frame(pixels, f)
        if film_hook is not None:
            film_hook(pixels)
        return pixels, (1 - t) * ma + t * mb

    def fractional_sensor_data(f):
        j = min(int(math.floor(f)), renderer.LAST - 1)
        t = f - j
        data = []
        for (pa, va), (pb, vb) in zip(native_sensor_data(j), native_sensor_data(j + 1)):
            v = (1 - t) * va + t * vb
            data.append(((1 - t) * pa + t * pb, v / np.linalg.norm(v)))
        return data

    # Source frame values and plotted paths retain their original calculation.
    # Change only footage/anchor sampling from nearest to fractional frames.
    renderer.get_film = smooth_film
    renderer.source_index = lambda f: float(f)
    renderer.sensor_data = fractional_sensor_data
    return renderer, motion


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--validation", type=Path)
    parser.add_argument("--background", type=Path, help="Registered reed plate directory from prepare_reed_background.py")
    parser.add_argument("--cache-restored-film", type=Path, help="Optionally retain lossless RGB footage before overlays/grade for future plot-only edits")
    parser.add_argument("--film", type=Path, help="Existing interpolated clean-film intermediate")
    parser.add_argument("--plot-data", type=Path, help="Optional edited presentation copy; original data left intact")
    parser.add_argument("--layered-background", type=Path, help="Interpolate real native foreground masks separately over this registered reed bank (preferred)")
    args = parser.parse_args()
    if args.background and args.layered_background:
        parser.error("Use --layered-background or legacy --background, not both")
    cv2.setNumThreads(2)
    project, output = args.project.resolve(), args.output.resolve()
    source_script = (project / "work_v7/render_v7.py").read_text()
    if "vy,56*scale" not in source_script:
        parser.error("Apply sensor-y-axis.patch to v7 first (sensor Y length 56).")
    # Prepare clean footage first; text and charts never enter interpolation.
    film = args.film or output.with_name(output.stem + ".film.mkv")
    if not film.exists():
        sys.path.insert(0, str(project / "work_v7"))
        r0 = importlib.import_module("render_v7")
        m0 = importlib.import_module("motion_v6")
        make_interpolated_film(r0, m0, film)
    cache_process = None
    cache_temporary = None
    if args.cache_restored_film:
        cache_temporary = args.cache_restored_film.with_name(args.cache_restored_film.stem + ".encoding.mkv")
        cache_process = subprocess.Popen([
            "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", "2130x1440", "-r", "60", "-i", "-", "-an", "-c:v", "ffv1",
            "-level", "3", "-threads", "2", "-pix_fmt", "bgr0", str(cache_temporary)
        ], stdin=subprocess.PIPE)
    hook = (lambda pixels: cache_process.stdin.write(pixels.tobytes())) if cache_process else None
    r, motion = install_renderer(project, args.plot_data, film, args.background, hook, args.layered_background)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from grade_welcome_video import FILTER
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_name(output.stem + ".rendering.mp4")
    command = [
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{r.W}x{r.H}", "-r", str(r.FPS), "-i", "-", "-an",
        "-filter_complex", FILTER, "-map", "[v]", "-c:v", "libx264",
        "-preset", "slow", "-threads", "4", "-crf", "17", "-pix_fmt", "yuv420p",
        "-color_range", "tv", "-colorspace", "bt709", "-color_trc", "bt709",
        "-color_primaries", "bt709", "-movflags", "+faststart", str(temp)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    count = math.ceil(r.END * r.FPS) + 1
    for i in range(count):
        f = r.source_frame(i / r.FPS)
        process.stdin.write(r.render_frame(f, "follow").tobytes())
        if i % 30 == 0:
            print(f"Rendered {i}/{count}", flush=True)
    process.stdin.close()
    if process.wait():
        raise RuntimeError("FFmpeg encoding failed")
    if cache_process:
        cache_process.stdin.close()
        if cache_process.wait():
            raise RuntimeError("Restored film cache encoding failed")
        cache_temporary.replace(args.cache_restored_film)
    temp.replace(output)
    poster = output.with_name(output.stem + "-poster.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.4", "-i", str(output),
                    "-frames:v", "1", "-q:v", "2", str(poster)], check=True)
    if args.validation:
        recorded = [project / p for p in ["work_v7/plot_data.json",
                    "work_v5/video_alignment.json", "work_v4/sensor_tracking.json",
                    "work_v4/boat_tracking.json"]]
        args.validation.write_text(json.dumps({
            "method": ("Source-native foreground masks; premultiplied RGB/alpha shared motion; feature-constrained silhouette and dense interior; existing motion-compensated water" if args.layered_background else "FFmpeg bidirectional adaptive overlapping block motion compensation; variable-size8pxblocks; clean footage only"),
            "background_restoration": "Registered observed reed-bank plate with separately interpolated native foreground; water remains dynamic" if args.layered_background else ("registered observed reed-bank plate; foreground and water preserved" if args.background else None),
            "overlay_sampling": "fractional source positions; redrawn vector/text overlays",
            "output_frames": count, "output_fps": r.FPS,
            "duration_seconds": count / r.FPS, "bytes": output.stat().st_size,
            "source_range": [r.START, r.LAST], "speed_ramp_changed": False,
            "sensor_y_length": 56, "middle_y_length": 87,
            "presentation_data_sha256": hashlib.sha256(args.plot_data.read_bytes()).hexdigest() if args.plot_data else None,
            "display_metrics": r.DATA["metrics"],
            "inputs_sha256": {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest() for p in recorded}
        }, indent=2))
    print(output, flush=True)


if __name__ == "__main__":
    main()
