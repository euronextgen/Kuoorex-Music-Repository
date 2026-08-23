#!/usr/bin/env python3
"""
package_beat.py — Ingest a beat into the Kuoorex catalog.

Usage:
    python scripts/package_beat.py --wav <path> --title <title> --slug <slug> --bpm <bpm> --key <key> --mood <mood>
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BEATS = REPO / "beats"
TEMPLATE = REPO / "resources" / "templates" / "beat-info.json"
README_TMPL = """# {title}

**Producer:** Kuoorex  
**BPM:** {bpm}  
**Key:** {key}  
**Mood:** {mood_human}  
**License:** Free For Profit (40/60) — credit required

## Description

_{notes}_

## License summary

- **Free for Profit:** MP3 with tag, credit required, 40/60 split.
- **Lease MP3:** €25 — no tag, 5K streams, 2K units.
- **Lease WAV:** €50 — no tag, 10K streams, 5K units.
- **Exclusive:** €300+ — full rights, removed from catalog.

Full terms → [LICENSE_TIERS.md](../LICENSE_TIERS.md)

Contact for beats, collabs or custom work → kuoorexcontact@gmail.com
"""

MOOD_MAP = {
    "dark_trap": "Dark Trap",
    "melodic_trap": "Melodic Trap",
    "drill": "Drill",
    "rnb": "R&B",
    "lofi": "Lo-Fi",
    "hyperpop": "Hyperpop",
    "ambient": "Ambient",
    "experimental": "Experimental",
}


def slugify(value: str) -> str:
    out = []
    for ch in value.lower().replace(" ", "-"):
        if ch.isalnum() or ch == "-":
            out.append(ch)
    return "".join(out)


def make_info(args: argparse.Namespace) -> dict:
    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    data["slug"] = args.slug
    data["title"] = args.title
    data["date_created"] = args.date or "2026-06-20"
    data["audio"]["bpm"] = int(args.bpm)
    data["audio"]["key"] = args.key
    data["audio"]["mood"] = args.mood
    data["audio"]["energy"] = args.energy or "medium"
    if args.notes:
        data["notes"] = args.notes
    data["license"]["tiers"]["free_for_profit"]["enabled"] = args.free_for_profit
    data["license"]["default"] = "free_for_profit_40_60" if args.free_for_profit else "lease_only"
    return data


def write_beat(slug: str, title: str, bpm: int, key: str, mood: str, notes: str | None) -> Path:
    out = BEATS / slug
    out.mkdir(parents=True, exist_ok=True)
    info = out / "info.json"
    if info.exists():
        raise FileExistsError(f"{info} already exists. Remove it first if you want to overwrite.")
    data = make_info(
        argparse.Namespace(
            slug=slug,
            title=title,
            date="2026-06-20",
            bpm=bpm,
            key=key,
            mood=mood,
            energy="medium",
            notes=notes,
            free_for_profit=True,
        )
    )
    info.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readme = out / "README.md"
    readme.write_text(
        README_TMPL.format(
            title=title,
            bpm=bpm,
            key=key,
            mood_human=MOOD_MAP.get(mood, mood),
            notes=notes or "No description yet.",
        ),
        encoding="utf-8",
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a beat into the Kuoorex catalog.")
    parser.add_argument("--wav", help="Source WAV path")
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug", default=None)
    parser.add_argument("--bpm", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--mood", default="dark_trap")
    parser.add_argument("--energy", default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    args.slug = args.slug or slugify(args.title)
    if args.slug != slugify(args.slug):
        raise SystemExit(f"Invalid slug: {args.slug!r}")

    out = BEATS / args.slug
    if out.exists() and not args.overwrite:
        raise SystemExit(f"{out} exists. Use --overwrite to replace.")

    created = write_beat(args.slug, args.title, args.bpm, args.key, args.mood, args.notes)
    print(f"OK  packaged -> {created}")
    print(f"    info.json -> {created / 'info.json'}")
    print(f"    README.md -> {created / 'README.md'}")
    if args.wav:
        wav = Path(args.wav)
        if not wav.exists():
            raise SystemExit(f"WAV not found: {wav}")
        dest = created / "source.wav"
        shutil.copy2(wav, dest)
        print(f"    source.wav -> {dest} (copy)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
