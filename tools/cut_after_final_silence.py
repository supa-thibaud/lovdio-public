#!/usr/bin/env python3
"""
cut_after_final_silence.py

Trim an MP3 (or directory of MP3s) so the file ends right after the LAST
non-silent audio, removing the trailing silence at the end of the file.

Why this exists
---------------
When generating speech with ElevenLabs (and other TTS engines), the model
sometimes produces a long tail of silence after the actual speech ends.
This script removes that trailing silence so segments concatenate cleanly.

Usage
-----
    python cut_after_final_silence.py input.mp3
    python cut_after_final_silence.py input.mp3 -o output.mp3
    python cut_after_final_silence.py ./folder/                # batch
    python cut_after_final_silence.py input.mp3 --silence-thresh -40 --min-silence-len 800 --pad 200

Requires: pydub (pip install pydub) + ffmpeg in PATH.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from pydub import AudioSegment
    from pydub.silence import detect_nonsilent
except ImportError:
    sys.exit("Missing dependency: pip install pydub  (and install ffmpeg)")


def cut_after_final_silence(
    path: Path,
    out_path: Path,
    silence_thresh: int = -40,
    min_silence_len: int = 700,
    pad_ms: int = 150,
) -> None:
    audio = AudioSegment.from_file(path)
    nonsilent = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
    )
    if not nonsilent:
        print(f"[skip] {path.name}: file looks entirely silent")
        return

    last_end_ms = nonsilent[-1][1]
    end = min(last_end_ms + pad_ms, len(audio))
    trimmed = audio[:end]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    trimmed.export(out_path, format="mp3")
    print(f"[ok]   {path.name}: {len(audio)}ms -> {len(trimmed)}ms")


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
    p.add_argument("--min-silence-len", type=int, default=700, help="Min silence length to count, in ms (default 700)")
    p.add_argument("--pad", type=int, default=150, help="ms to keep after last non-silent sample (default 150)")
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
            dst = src.with_name(src.stem + ".trimmed.mp3")
        cut_after_final_silence(
            src, dst,
            silence_thresh=args.silence_thresh,
            min_silence_len=args.min_silence_len,
            pad_ms=args.pad,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
