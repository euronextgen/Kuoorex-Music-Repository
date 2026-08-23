#!/usr/bin/env python3
"""
build_catalog.py — Rebuild catalog/catalog.json and README.md from beat info.json files.
Run this after adding or changing a beat.
"""
import json
from pathlib import Path
from datetime import date

REPO = Path(__file__).resolve().parent.parent
BEATS = REPO / "beats"
CATALOG_DIR = REPO / "catalog"
README = REPO / "README.md"

CATALOG_DIR.mkdir(exist_ok=True)


def load_beat(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_catalog():
    beats = []
    for info_path in sorted(BEATS.glob("*/info.json")):
        parent = info_path.parent
        if parent.name.startswith("_"):
            continue
        try:
            data = load_beat(info_path)
        except Exception as exc:
            raise RuntimeError(f"Failed to parse {info_path}: {exc}") from exc

        slug = data.get("slug") or parent.name
        audio = data.get("audio", {}) or {}
        distribution = data.get("distribution", {}) or {}
        license_info = data.get("license", {}) or {}
        tiers = license_info.get("tiers", {}) or {}
        license_tier = license_info.get("default")
        license_price = None
        if license_tier == "free_for_profit_40_60":
            license_price = 0
        elif license_tier == "lease_mp3":
            license_price = tiers.get("lease_mp3", {}).get("price_eur")
        elif license_tier == "lease_wav":
            license_price = tiers.get("lease_wav", {}).get("price_eur")
        elif license_tier == "exclusive_only":
            license_price = tiers.get("exclusive", {}).get("price_eur")

        beats.append({
            "slug": slug,
            "title": data.get("title") or slug,
            "producer": data.get("producer") or "Kuoorex",
            "bpm": audio.get("bpm"),
            "key": audio.get("key"),
            "mood": audio.get("mood"),
            "license": license_tier,
            "license_price_eur": license_price,
            "youtube_url": distribution.get("youtube_url"),
            "ready_youtube": distribution.get("ready_youtube") is True,
        })

    catalog = {
        "generated_at": date.today().isoformat(),
        "schema_version": "beats.catalog/1.0",
        "count": len(beats),
        "beats": beats,
    }
    target = CATALOG_DIR / "catalog.json"
    target.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK  Wrote {len(beats)} beat(s) to {target}")


def update_readme():
    lines = []
    beats = []
    for info_path in sorted(BEATS.glob("*/info.json")):
        parent = info_path.parent
        if parent.name.startswith("_"):
            continue
        data = json.loads(info_path.read_text(encoding="utf-8"))
        beats.append(data)
        slug = data.get("slug") or parent.name
        title = data.get("title") or slug
        audio = data.get("audio", {}) or {}
        dist = data.get("distribution", {}) or {}
        bpm = audio.get("bpm") or ""
        key = audio.get("key") or ""
        mood = (audio.get("mood") or "").replace("_", " ").title() or ""
        yt = dist.get("youtube_url") or ""
        label = f"[▶]({yt})" if yt else "—"
        lines.append(f"| [{title}](beats/{slug}/) | {bpm} | {key} | {mood} | {label} |")

    catalog_md = "\n".join(lines)
    readme = README.read_text(encoding="utf-8")
    marker = "## Catalog"
    start = readme.index(marker)
    end = readme.index("---", start + len(marker))
    before = readme[:start]
    after = readme[end:]
    new_catalog = (
        before
        + "## Catalog\n\n| Beat | BPM | Key | Mood | YouTube |\n"
        + "|---|---|---|---|---|\n"
        + catalog_md
        + "\n\n*Updated automatically on each release.*\n\n"
        + after.split("---", 2)[2]
    )
    README.write_text(new_catalog, encoding="utf-8")
    print(f"OK  Updated catalog table in {README}")


def main() -> int:
    build_catalog()
    update_readme()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
