# tools/

Small Python utilities we use around Lovdio audio production.

## Requirements

```bash
pip install pydub
# and install ffmpeg (https://ffmpeg.org/) so pydub can decode MP3s
```

## Scripts

### `cut_after_final_silence.py`

Trims trailing silence from an MP3 — useful because TTS engines (ElevenLabs in
particular) often leave a long silent tail at the end of a generation. Keeps
a small pad after the last spoken word so the cut doesn't feel abrupt.

```bash
python tools/cut_after_final_silence.py input.mp3
python tools/cut_after_final_silence.py ./folder/      # batch all *.mp3
```

### `cut_after_first_silence.py`

Removes everything **before** the first long silence. Why? With ElevenLabs the
voice needs a few words to calibrate — pitch, pacing, energy. A reliable trick
is to prepend a throwaway phrase (e.g. `"Hum, alors..."`) followed by a clear
pause, then say the real line. This script detects that first long silence
and chops off the priming words, leaving only the clean delivery.

Workflow:

1. In your TTS prompt: `"Hum, alors... [pause] <the real line>"`
2. Generate the MP3.
3. Run `cut_after_first_silence.py` — get the clean line back.

```bash
python tools/cut_after_first_silence.py input.mp3
python tools/cut_after_first_silence.py ./folder/      # batch
```

## Tuning silence detection

Both scripts expose the same three knobs:

| Flag | Default | What it does |
|---|---|---|
| `--silence-thresh` | `-40` dBFS | Anything quieter than this counts as silence. Lower (e.g. `-50`) = stricter. |
| `--min-silence-len` | `600`–`700` ms | Minimum silence duration to register as a real gap. |
| `--pad` | `80`–`150` ms | Breathing room kept around the cut, so it doesn't feel surgical. |

If a file is being chopped wrong, tweak `--silence-thresh` first (room noise),
then `--min-silence-len` (long natural pauses inside the line).
