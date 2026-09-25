#!/usr/bin/env python3
"""Apply the welcome clip's subtle, luminance-only grade to its footage panel."""
import argparse
import json
from pathlib import Path
import subprocess

FILTER = (
    "[0:v]split=2[foot][chart];"
    "[foot]crop=2130:1440:0:0,"
    "lut=y='if(between(val,16,235),"
    "val+219*(((val-16)/219)*(1-(val-16)/219))"
    "*(0.50*((val-16)/219-0.5)+0.06),val)'[graded];"
    "[chart]crop=750:1440:2130:0[panel];"
    "[graded][panel]hstack=inputs=2[v]"
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Re-rendered 2880 × 1440 v7 master")
    parser.add_argument("output", type=Path, help="Website MP4 destination")
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error("Keep the source master and website output separate.")
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "json", str(args.source)
    ]))["streams"][0]
    if (info["width"], info["height"]) != (2880, 1440):
        parser.error("This panel boundary is specific to the 2880 × 1440 v7 master.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.stem + ".encoding.mp4")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(args.source),
        "-filter_complex", FILTER, "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
        "-color_range", "tv", "-colorspace", "bt709", "-color_trc", "bt709",
        "-color_primaries", "bt709", "-c:a", "copy", "-movflags", "+faststart",
        str(temporary)
    ], check=True)
    temporary.replace(args.output)
    poster = args.output.with_name(args.output.stem + "-poster.jpg")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "1.4",
        "-i", str(args.output), "-frames:v", "1", "-q:v", "2", str(poster)
    ], check=True)
    print(args.output)
    print(poster)


if __name__ == "__main__":
    main()
