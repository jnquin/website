#!/usr/bin/env python3
"""
Sync taxonomy slugs (artist_slugs, staff_slugs) from artists and staff arrays.
"""
import re
from pathlib import Path

DISC_DIR = Path("content/discography")


def parse_frontmatter(fm_str: str) -> dict:
    """Parse frontmatter for role, artists, label, artist_credits."""
    params = {}
    # role
    m = re.search(r"^role:\s*(.+)$", fm_str, re.M)
    if m:
        v = m.group(1).strip().strip('"\'')
        params["role"] = v
    # artists_display
    m = re.search(r"^artists_display:\s*(.+)$", fm_str, re.M)
    if m:
        v = m.group(1).strip()
        if v.startswith('"'):
            v = re.search(r'"((?:[^"\\]|\\.)*)"', v)
            params["artists_display"] = v.group(1) if v else ""
        else:
            params["artists_display"] = v.strip('"\'')
    # label (plaintext)
    m = re.search(r"^label:\s*(.+)$", fm_str, re.M)
    if m:
        v = m.group(1).strip().strip('"\'')
        params["label"] = v
    # artists (new format: array of {slug, role, display, mode}) or artist_credits
    m = re.search(r"(?:artists|artist_credits):\s*\n((?:\s+-\s+slug:.*?\n(?:\s+(?:display|role|mode):.*?\n)*)*)", fm_str, re.M | re.DOTALL)
    if m:
        credits = []
        for block in re.finditer(r"-\s+slug:\s*[\"']([^\"']+)[\"']\s*\n((?:\s+\w+:\s*[^\n]*\n?)*)", m.group(1)):
            slug, rest = block.group(1), block.group(2)
            mode_m = re.search(r"mode:\s*[\"']([^\"']+)[\"']", rest)
            mode = (mode_m.group(1) or "").strip().lower() if mode_m else None
            display_m = re.search(r"display:\s*[\"']([^\"']*)[\"']", rest)
            display = (display_m.group(1) or "").strip() if display_m else ""
            role_m = re.search(r"role:\s*[\"']([^\"']*)[\"']", rest)
            role = (role_m.group(1) or "").strip() if role_m else ""
            cred = {"slug": slug, "display": display, "role": role, "mode": mode}
            credits.append(cred)
        if credits:
            params["artists"] = credits
    # artist_slugs (for taxonomy - simple string array)
    m = re.search(r"^artist_slugs:\s*\[(.*?)\]", fm_str, re.M | re.DOTALL)
    if m:
        params["artist_slugs"] = re.findall(r'"([^"]+)"', m.group(0))
    # staff (new format: array of {slug, role, display, mode})
    m = re.search(r"staff:\s*\n((?:\s+-\s+slug:.*?\n(?:\s+(?:display|role|mode):.*?\n)*)*)", fm_str, re.M | re.DOTALL)
    if m:
        credits = []
        for block in re.finditer(r"-\s+slug:\s*[\"']([^\"']+)[\"']\s*\n((?:\s+\w+:\s*[^\n]*\n?)*)", m.group(1)):
            slug, rest = block.group(1), block.group(2)
            mode_m = re.search(r"mode:\s*[\"']([^\"']+)[\"']", rest)
            mode = (mode_m.group(1) or "").strip().lower() if mode_m else None
            display_m = re.search(r"display:\s*[\"']([^\"']*)[\"']", rest)
            display = (display_m.group(1) or "").strip() if display_m else ""
            role_m = re.search(r"role:\s*[\"']([^\"']*)[\"']", rest)
            role = (role_m.group(1) or "").strip() if role_m else ""
            cred = {"slug": slug, "display": display, "role": role, "mode": mode}
            credits.append(cred)
        if credits:
            params["staff"] = credits
    # staff_slugs
    m = re.search(r"^staff_slugs:\s*\[(.*?)\]", fm_str, re.M | re.DOTALL)
    if m:
        params["staff_slugs"] = re.findall(r'"([^"]+)"', m.group(0))
    return params


def ensure_taxonomy_slugs(fm_str: str, params: dict) -> str:
    """Ensure artist_slugs and staff_slugs are derived from artists and staff."""
    result = fm_str

    # artist_slugs: from artists (default mode), plus staff with mode "artist" (if not already present)
    artists = params.get("artists") or []
    staff = params.get("staff") or []
    artist_slugs = []
    artist_seen = set()
    if isinstance(artists, list):
        for a in artists:
            if not (isinstance(a, dict) and a.get("slug") and a.get("slug", "").lower() != "none"):
                continue
            mode = (a.get("mode") or "").lower()
            if mode != "staff":  # default artist, or explicit mode "artist"
                slug = a.get("slug")
                if slug not in artist_seen:
                    artist_slugs.append(slug)
                    artist_seen.add(slug)
    if isinstance(staff, list):
        for s in staff:
            if not (isinstance(s, dict) and s.get("slug") and s.get("slug", "").lower() != "none"):
                continue
            if (s.get("mode") or "").lower() == "artist":
                slug = s.get("slug")
                if slug not in artist_seen:
                    artist_slugs.append(slug)
                    artist_seen.add(slug)
    if artist_slugs:
        slugs_str = "[" + ", ".join(f'"{s}"' for s in artist_slugs) + "]"
        if re.search(r"^artist_slugs\s*:", result, re.M):
            result = re.sub(
                r"^artist_slugs\s*:\s*\[[^\]]*\]",
                f"artist_slugs: {slugs_str}",
                result,
                flags=re.M,
            )
        else:
            result = result.rstrip() + f"\nartist_slugs: {slugs_str}\n"

    # staff_slugs: from staff (default mode), plus artists with mode "staff" (if not already present)
    staff_slugs = []
    staff_seen = set()
    if isinstance(staff, list):
        for s in staff:
            if not (isinstance(s, dict) and s.get("slug") and s.get("slug", "").lower() != "none"):
                continue
            mode = (s.get("mode") or "").lower()
            if mode != "artist":  # default staff, or explicit mode "staff"
                slug = s.get("slug")
                if slug not in staff_seen:
                    staff_slugs.append(slug)
                    staff_seen.add(slug)
    if isinstance(artists, list):
        for a in artists:
            if not (isinstance(a, dict) and a.get("slug") and a.get("slug", "").lower() != "none"):
                continue
            if (a.get("mode") or "").lower() == "staff":
                slug = a.get("slug")
                if slug not in staff_seen:
                    staff_slugs.append(slug)
                    staff_seen.add(slug)
    if staff_slugs:
        slugs_str = "[" + ", ".join(f'"{s}"' for s in staff_slugs) + "]"
        if re.search(r"^staff_slugs\s*:", result, re.M):
            result = re.sub(
                r"^staff_slugs\s*:\s*\[[^\]]*\]",
                f"staff_slugs: {slugs_str}",
                result,
                flags=re.M,
            )
        else:
            result = result.rstrip() + f"\nstaff_slugs: {slugs_str}\n"

    return result


def main():
    for d in sorted(DISC_DIR.iterdir()):
        if not d.is_dir():
            continue
        idx = d / "index.md"
        if not idx.exists():
            continue
        text = idx.read_text(encoding="utf-8")
        if "---" not in text:
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        before, fm_str, content = parts
        fm_str = fm_str.strip()
        params = parse_frontmatter(fm_str)
        new_fm = ensure_taxonomy_slugs(fm_str, params)
        if new_fm != fm_str:
            new_text = "---\n" + new_fm.strip() + "\n---\n\n" + content.lstrip()
            idx.write_text(new_text, encoding="utf-8")
            print(f"Updated: {d.name}")


if __name__ == "__main__":
    main()
