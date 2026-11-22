#!/usr/bin/env python3
"""Ambil versi stabil TERBARU suatu paket langsung dari registry resmi, saat skrip dijalankan.

Dipakai agent sebelum memilih/memasang teknologi, supaya keputusan memakai versi saat ini,
bukan daftar yang ditulis di dokumen. Hanya standard library; butuh jaringan.

Contoh:
    python3 scripts/cek_versi.py next react tailwindcss               # npm (default)
    python3 scripts/cek_versi.py --pypi fastapi pydantic ruff
    python3 scripts/cek_versi.py --crates axum tokio
    python3 scripts/cek_versi.py --proyek ~/proyek-saya               # bandingkan package.json/pyproject dengan terbaru
    python3 scripts/cek_versi.py --node                               # rilis Node.js LTS aktif saat ini
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = {"User-Agent": "product-engineer-cek-versi/1.0"}
PRERELEASE = re.compile(r"(?i)(alpha|beta|rc|canary|next|dev|preview|nightly|pre|\bexperimental)")


def get_json(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def npm_latest(name: str) -> tuple[str, str]:
    d = get_json(f"https://registry.npmjs.org/{name.replace('/', '%2F')}")
    latest = d.get("dist-tags", {}).get("latest", "?")
    t = d.get("time", {}).get(latest, "")[:10]
    dep = d.get("versions", {}).get(latest, {}).get("deprecated")
    return latest, t + (f"  DEPRECATED: {dep}" if dep else "")


def pypi_latest(name: str) -> tuple[str, str]:
    d = get_json(f"https://pypi.org/pypi/{name}/json")
    v = d["info"]["version"]
    files = d["releases"].get(v, [])
    t = (files[0].get("upload_time", "")[:10]) if files else ""
    yanked = " YANKED" if files and files[0].get("yanked") else ""
    return v, t + yanked


def crates_latest(name: str) -> tuple[str, str]:
    d = get_json(f"https://crates.io/api/v1/crates/{name}")
    c = d["crate"]
    return c.get("max_stable_version") or c["max_version"], (c.get("updated_at") or "")[:10]


def node_lts() -> list[tuple[str, str]]:
    rows = get_json("https://nodejs.org/dist/index.json")
    seen: dict[str, tuple[str, str]] = {}
    for r in rows:
        if r.get("lts"):
            seen.setdefault(r["lts"], (r["version"], r["date"]))
    cur = next(r for r in rows if not PRERELEASE.search(r["version"]))
    out = [(f"current {cur['version']}", cur["date"])]
    out += [(f"LTS {k} {v[0]}", v[1]) for k, v in list(seen.items())[:3]]
    return out


def lookup(fn, name: str) -> str:
    try:
        v, extra = fn(name)
        return f"{name:<28} {v:<14} {extra}"
    except urllib.error.HTTPError as e:
        return f"{name:<28} TIDAK DITEMUKAN (HTTP {e.code}) — periksa ejaan; jangan install paket yang tidak ada"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return f"{name:<28} gagal terhubung: {e}"


def project_report(root: Path) -> None:
    pkg = root / "package.json"
    if pkg.is_file():
        data = json.loads(pkg.read_text())
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        print(f"package.json ({len(deps)} dependency): terpasang → terbaru")
        for name, spec in sorted(deps.items()):
            try:
                latest, extra = npm_latest(name)
            except Exception as e:  # jaringan/registry: laporkan, jangan berhenti
                print(f"  {name:<30} ? ({e})")
                continue
            cur = re.search(r"\d+", spec)
            lat = re.search(r"\d+", latest)
            flag = "  <-- MAJOR lebih baru" if cur and lat and int(lat.group()) > int(cur.group()) else ""
            print(f"  {name:<30} {spec:<14} → {latest:<12}{flag}")
    for req in (root / "requirements.txt", ):
        if req.is_file():
            print("requirements.txt: terpasang → terbaru")
            for line in req.read_text().splitlines():
                m = re.match(r"([A-Za-z0-9_.\-]+)\s*(?:==\s*([\w.]+))?", line.strip())
                if not m or line.strip().startswith(("#", "-")):
                    continue
                print("  " + lookup(pypi_latest, m.group(1)) + (f"  (terpasang {m.group(2)})" if m.group(2) else ""))
    if not pkg.is_file() and not (root / "requirements.txt").is_file():
        print("Tidak ada package.json atau requirements.txt di folder ini.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Versi stabil terbaru dari registry resmi (saat dijalankan).")
    ap.add_argument("paket", nargs="*")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--pypi", action="store_true", help="cari di PyPI")
    g.add_argument("--crates", action="store_true", help="cari di crates.io")
    ap.add_argument("--node", action="store_true", help="tampilkan rilis Node.js current & LTS")
    ap.add_argument("--proyek", metavar="DIR", help="bandingkan dependency project dengan versi terbaru")
    args = ap.parse_args()

    if not (args.paket or args.node or args.proyek):
        ap.print_help()
        return 2
    if args.node:
        try:
            for label, date in node_lts():
                print(f"Node.js {label:<26} {date}")
        except Exception as e:
            print(f"Node.js: gagal terhubung: {e}")
    if args.proyek:
        project_report(Path(args.proyek).expanduser())
    fn = pypi_latest if args.pypi else crates_latest if args.crates else npm_latest
    for name in args.paket:
        print(lookup(fn, name))
    print("\nVersi di atas adalah rilis stabil terbaru saat ini. Tetap baca changelog/migration guide mayor sebelum memakainya,")
    print("dan pastikan kompatibel dengan dependency lain. Untuk memilih teknologi, cari juga perbandingan terbaru (lihat references/teknis-modern.md §0).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
