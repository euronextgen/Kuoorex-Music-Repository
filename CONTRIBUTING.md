# Contributing to the Kuoorex Beat Catalog

This document describes the internal workflow for adding beats to the catalog. It is written for David (and any future team members).

---

## Overview

```
Suno → beats/_inbox/ → [process] → beats/<slug>/ → [review] → commit → auto-publish
```

---

## Step 1 — Generate and download from Suno

1. Generate your beat in Suno (Pro plan ensures commercial rights).
2. Save the Suno prompt you used — you'll need it for metadata.
3. Download as **WAV** (not MP3 — we generate the MP3s ourselves).
4. Name the file descriptively: `dark-trap-piano-149bpm.wav` (doesn't need to be the final title).

---

## Step 2 — Drop in _inbox

Place the WAV file(s) in `beats/_inbox/`.

```
beats/
  _inbox/
    dark-trap-piano-149bpm.wav   ← drop here
    another-beat.wav
```

WAV files are excluded from git (see `.gitignore`). The folder is just a local working area.

---

## Step 3 — Ingest / empaquetar

### Opción rápida (CLI)

Usá `scripts/package_beat.py` para crear/refrescar la carpeta de un beat desde un WAV exportado:

```bash
python scripts/package_beat.py \
  --wav "C:/path/to/your/exported-beat.wav" \
  --title "Tickin" \
  --slug "tickin" \
  --bpm 140 \
  --key "F minor" \
  --mood "dark_trap"
```

Esto crea/refresca `beats/<slug>/` con:
- `info.json` (schema v2)
- `README.md` desde template
- placeholders `cover.jpg`, `waveform.png`, `preview_30s.mp3`

### Opción manual (editar info.json)

Copiá el template:

```bash
cp resources/templates/beat-info.json beats/<slug>/info.json
```

Editá los campos: `title`, `audio.bpm`, `audio.key`, `audio.mood`, `date_created`, etc.

---

## Step 4 — Review and approve

Check each generated folder in `beats/`:

```json
// beats/dark-trap-piano-149/info.json
{
  "title": "Dark Trap Piano",
  "audio": { "bpm": 149, "mood": "dark_trap", ... },
  "distribution": { "ready_youtube": false }  ← change to true when ready
}
```

Adjust any wrong title, mood, tags, or instruments. When satisfied:

```json
"distribution": {
  "ready_youtube": true
}
```

---

## Step 5 — Commit

```bash
git add beats/<slug>/
git commit -m "feat(beat): add <slug>"
```

GitHub Actions will automatically:
- Rebuild `catalog/catalog.json`
- Queue the YouTube upload if `ready_youtube: true`
- Deploy the updated catalog page

---

## File structure per beat

```
beats/<slug>/
  info.json         ← metadata (all fields, v2 schema)
  README.md         ← human-readable description + license
  cover.jpg         ← 1080×1080 cover (cyberpunk Y2K style)
  cover_yt.jpg      ← 1280×720 for YouTube video
  waveform.png      ← waveform visualization
  preview_30s.mp3   ← 30-second preview clip (committed to git)
```

Full WAV and tagged MP3 live in Cloudflare R2 — not in git.

---

## Validating info.json

To validate against the JSON Schema before committing:

```bash
# Install once
pip install jsonschema

# Validate
python scripts/validate_beat.py beats/<slug>/info.json
```

---

## Mood reference

| Mood | Sound |
|---|---|
| `dark_trap` | Hard 808s, minor keys, dark atmosphere |
| `melodic_trap` | Melodic elements, emotional, trap drums |
| `drill` | Fast hi-hats, UK or NY drill patterns |
| `rnb` | Smooth, soulful, groovy |
| `lofi` | Chill, lo-fi textures, relaxed |
| `hyperpop` | Distorted, experimental, high energy |
| `ambient` | Atmospheric, no traditional drums or minimal |
| `experimental` | Doesn't fit any other category |

---

## Questions?

Contact: kuoorexcontact@gmail.com
