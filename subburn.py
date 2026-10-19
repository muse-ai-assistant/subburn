#!/usr/bin/env python3
"""subburn - burn subtitles into video (hardsub) or mux as a track (softsub).

Usage:
    subburn video.mp4 sub.srt -o out.mp4            # hard burn (default)
    subburn video.mp4 sub.srt --soft -o out.mkv     # soft subtitle track, no re-encode
    subburn video.mp4 sub.srt --fontsize 32 --style top -o out.mp4
    subburn video.mp4 sub.srt --font /path/to/font.ttf -o out.mp4
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

FFMPEG_INSTALL_HINT = """\
ffmpeg not found. Install it first:

  Windows : winget install Gyan.FFmpeg        (or download from https://www.gyan.dev/ffmpeg/builds/)
  macOS   : brew install ffmpeg
  Ubuntu/Debian : sudo apt install ffmpeg
  Fedora  : sudo dnf install ffmpeg
"""

# libass alignment numbers: 2 = bottom-center, 8 = top-center
ALIGNMENTS = {"bottom": 2, "top": 8}

# subtitle codec to use per container for soft mux
SOFT_CODECS = {".mp4": "mov_text", ".m4v": "mov_text", ".mkv": "srt", ".webm": "webvtt"}


def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        sys.exit("Error: " + FFMPEG_INSTALL_HINT)


def escape_filter_path(path):
    """Escape a file path for use inside an ffmpeg filtergraph argument."""
    return re.sub(r"([\\':;\[\],])", r"\\\1", path)


def font_family_from_file(font_path):
    """Get the family name of a font file via fontconfig (fc-scan)."""
    fc_scan = shutil.which("fc-scan")
    if not fc_scan:
        return None
    try:
        out = subprocess.run(
            [fc_scan, "--format", "%{family}\n", font_path],
            capture_output=True, text=True, timeout=15,
        )
        name = out.stdout.strip().split("\n")[0].strip()
        return name or None
    except Exception:
        return None


def build_subtitles_filter(sub_path, font=None, fontsize=None, style="bottom"):
    """Build the ffmpeg -vf subtitles=... argument."""
    parts = [f"subtitles='{escape_filter_path(sub_path)}'"]

    force = []
    fontsdir = None
    if font:
        font = os.path.abspath(font)
        if not os.path.isfile(font):
            sys.exit(f"Error: font file not found: {font}")
        fontsdir = os.path.dirname(font)
        family = font_family_from_file(font)
        if family:
            force.append(f"FontName={family}")
        else:
            print("Warning: could not detect font family name "
                  "(fontconfig not available); using fontsdir only, "
                  "the exact font may not be picked.", flush=True)
    if fontsdir:
        parts.append(f"fontsdir='{escape_filter_path(fontsdir)}'")
    if fontsize:
        force.append(f"FontSize={fontsize}")
    if style in ALIGNMENTS:
        force.append(f"Alignment={ALIGNMENTS[style]}")
    # readable defaults: white text, black outline, a bit of bottom margin
    force.append("PrimaryColour=&H00FFFFFF")
    force.append("OutlineColour=&H80000000")
    force.append("BorderStyle=1")
    force.append("Outline=2")
    force.append("Shadow=0")
    force.append("MarginV=28")
    parts.append(f"force_style='{','.join(force)}'")
    return ":".join(parts)


def hard_burn(video, sub, out, font, fontsize, style, crf):
    # Copy the subtitle to a temp file with a safe ASCII name so the
    # subtitles filter never chokes on exotic characters in the path.
    ext = os.path.splitext(sub)[1].lower() or ".srt"
    tmpdir = tempfile.mkdtemp(prefix="subburn_")
    safe_sub = os.path.join(tmpdir, "sub" + ext)
    shutil.copyfile(sub, safe_sub)
    try:
        vf = build_subtitles_filter(safe_sub, font, fontsize, style)
        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
            "-c:a", "copy",
            out,
        ]
        print("Running: " + " ".join(cmd), flush=True)
        r = subprocess.run(cmd)
        if r.returncode != 0:
            sys.exit(f"Error: ffmpeg failed (exit {r.returncode})")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def soft_mux(video, sub, out):
    ext = os.path.splitext(out)[1].lower()
    codec = SOFT_CODECS.get(ext)
    if codec is None:
        sys.exit(
            f"Error: --soft muxing into '{ext}' is not supported. "
            "Use .mp4/.m4v (mov_text) or .mkv (srt)."
        )
    cmd = [
        "ffmpeg", "-y",
        "-i", video,
        "-i", sub,
        "-map", "0", "-map", "1",
        "-c", "copy",
        "-c:s", codec,
        "-disposition:s:0", "default",
        out,
    ]
    print("Running: " + " ".join(cmd), flush=True)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"Error: ffmpeg failed (exit {r.returncode})")


def main():
    ap = argparse.ArgumentParser(
        description="Burn subtitles into video (hardsub) or mux as a subtitle track (softsub).",
    )
    ap.add_argument("video", help="input video file")
    ap.add_argument("subtitle", help="subtitle file (.srt / .ass)")
    ap.add_argument("-o", "--output", required=True, help="output video file")
    ap.add_argument("--soft", action="store_true",
                    help="mux subtitle as a separate track instead of burning in "
                         "(no re-encode, much faster)")
    ap.add_argument("--font", default=None,
                    help="font file (.ttf/.otf/.ttc) for hard-burned subtitles")
    ap.add_argument("--fontsize", type=int, default=None,
                    help="font size for hard-burned subtitles (default: style default)")
    ap.add_argument("--style", choices=["bottom", "top"], default="bottom",
                    help="subtitle position for hard burn (default: bottom)")
    ap.add_argument("--crf", type=int, default=23,
                    help="quality for hard-burn re-encode, lower = better (default: 23)")
    args = ap.parse_args()

    check_ffmpeg()

    if not os.path.isfile(args.video):
        sys.exit(f"Error: video not found: {args.video}")
    if not os.path.isfile(args.subtitle):
        sys.exit(f"Error: subtitle not found: {args.subtitle}")
    sub_ext = os.path.splitext(args.subtitle)[1].lower()
    if sub_ext not in (".srt", ".ass", ".ssa", ".vtt"):
        sys.exit(f"Error: unsupported subtitle format '{sub_ext}' (use .srt/.ass/.ssa/.vtt)")

    if args.soft:
        if args.font or args.fontsize or args.style != "bottom":
            print("Note: --font/--fontsize/--style only apply to hard burn; "
                  "ignored for --soft mux.", flush=True)
        soft_mux(args.video, args.subtitle, args.output)
    else:
        hard_burn(args.video, args.subtitle, args.output,
                  args.font, args.fontsize, args.style, args.crf)

    print(f"Done: {args.output}", flush=True)


if __name__ == "__main__":
    main()
