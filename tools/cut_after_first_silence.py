#!/usr/bin/env python3
"""
cut_after_first_silence.py

Trim an MP3 (or directory of MP3s) so the file STARTS just after the first
long silence, removing the calibration "throwaway" words at the beginning.

Why this exists
---------------
With ElevenLabs (and similar TTS), the voice often needs a few priming words
at the very start of a prompt before it stabilises. A common trick is to
prepend a short throwaway phrase (e.g. "Hum, alors,") and a pause, then say
the real line. This script detects the first long silence and discards
everything before it, leaving only the clean line.

Workflow
--------
1. In your TTS prompt, prepend something like:  "Hum... [PAUSE] <real text>"
2. Generate the MP3.
3. Run this script: it removes the "Hum..." + pause and keeps the real text.

Usage
-----
    python cut_after_first_silence.py input.mp3
    python cut_after_first_silence.py input.mp3 -o output.mp3
    python cut_after_first_silence.py ./folder/                # batch
    python cut_after_first_silence.py input.mp3 --silence-thresh -40 --min-silence-len 600 --pad 80

Requires: pydub (pip install pydub) + ffmpeg in PATH.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from pydub import AudioSegment
    from pydub.silence import detect_silence
except ImportError:
    sys.exit("Missing dependency: pip install pydub  (and install ffmpeg)")


def cut_after_first_silence(
    path: Path,
    out_path: Path,
    silence_thresh: int = -40,
    min_silence_len: int = 600,
    pad_ms: int = 80,
) -> None:
    audio = AudioSegment.from_file(path)
    silences = detect_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
    )
    if not silences:
        print(f"[skip] {path.name}: no silence >= {min_silence_len}ms found")
        return

    first_silence_end_ms = silences[0][1]
    start = max(first_silence_end_ms - pad_ms, 0)
    trimmed = audio[start:]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    trimmed.export(out_path, format="mp3")
    print(f"[ok]   {path.name}: cut first {start}ms -> kept {len(trimmed)}ms")


def iter_inputs(target: Path):
    if target.is_dir():
        yield from sorted(target.glob("*.mp3"))
    else:
        yield target


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path, help="MP3 file or directory of MP3 files")
    p.add_argument("-o", "--output", type=Path, default=None, help="Output file (single-file mode) or directory")
    p.add_argument("--silence-thresh", type=int, default=-40, help="dBFS below which audio is silence (default -40)")
    p.add_argument("--min-silence-len", type=int, default=600, help="Min silence length to detect, in ms (default 600)")
    p.add_argument("--pad", type=int, default=80, help="ms of audio to keep BEFORE the silence end, as breathing room (default 80)")
    args = p.parse_args()

    target: Path = args.input
    if not target.exists():
        sys.exit(f"Not found: {target}")

    for src in iter_inputs(target):
        if args.output and target.is_file():
            dst = args.output
        elif args.output:
            dst = args.output / src.name
        else:
            dst = src.with_name(src.stem + ".cut.mp3")
        cut_after_first_silence(
            src, dst,
            silence_thresh=args.silence_thresh,
            min_silence_len=args.min_silence_len,
            pad_ms=args.pad,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
