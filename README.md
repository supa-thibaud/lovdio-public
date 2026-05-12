# lovdio_public

Public home for small open tools we use around [Lovdio](https://lovdio.com) —
the romantic audio stories site — plus related projects from
[Neverending](https://neverending.ai), the company behind Lovdio
(including [Supafriends](https://supafriends.com), a romance chatbot platform).

The repo also serves a tiny landing page via GitHub Pages
(see [`index.html`](./index.html)).

## What's inside

- [`tools/`](./tools) — small Python utilities. Currently focused on
  cleaning up MP3s produced by ElevenLabs:
  - [`cut_after_final_silence.py`](./tools/cut_after_final_silence.py) — trim trailing silence.
  - [`cut_after_first_silence.py`](./tools/cut_after_first_silence.py) — drop the priming "calibration" words at the start.

See [`tools/README.md`](./tools/README.md) for usage and the trick of prepending
a throwaway phrase to stabilise the ElevenLabs voice.

## Install

```bash
pip install pydub
# + install ffmpeg in your PATH
```

## Links

- Main site → https://lovdio.com
- Parent company → https://neverending.ai
- Related project → https://supafriends.com
