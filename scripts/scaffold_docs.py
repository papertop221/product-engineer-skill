#!/usr/bin/env python3
"""Membuat kerangka dokumen proyek dari template product-engineer.

Contoh:
    python3 scripts/scaffold_docs.py ~/proyek-saya \
        --nama "Kasir Warung" \
        --pemilik "Budi" \
        --ringkasan "Aplikasi kasir sederhana untuk warung makan." \
        --publik
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "templates"
DOCS_TEMPLATE_DIR = TEMPLATE_ROOT / "docs"
ROOT_README_TEMPLATE = TEMPLATE_ROOT / "README.md"
LEGAL_TEMPLATE_DIR = TEMPLATE_ROOT / "legal"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Membuat docs/ lengkap dan README dari template product-engineer."
    )
    parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="Folder proyek tujuan (default: folder saat ini).",
    )
    parser.add_argument(
        "--nama",
        required=True,
        help="Nama produk, misalnya 'Kasir Warung'.",
    )
    parser.add_argument(
        "--pemilik",
        default="Pemilik produk",
        help="Nama pemilik produk (default: 'Pemilik produk').",
    )
    parser.add_argument(
        "--ringkasan",
        default="TODO: ringkas produk dalam 1-2 kalimat.",
        help="Ringkasan produk untuk README dan docs/README.md.",
    )
    parser.add_argument(
        "--tanggal",
        default=None,
        help="Tanggal dokumen dalam format YYYY-MM-DD (default: hari ini).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Timpa file yang sudah ada (hati-hati).",
    )
    parser.add_argument(
        "--no-readme",
        action="store_true",
        help="Jangan buat README.md di root proyek.",
    )
    parser.add_argument(
        "--publik",
        action="store_true",
        help="Tambahkan draft dokumen legal (kebijakan privasi, syarat & ketentuan) ke docs/legal/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tampilkan file yang akan dibuat tanpa menulis apa pun.",
    )
    return parser.parse_args()


def render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main() -> int:
    args = parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists():
        print(f"Folder proyek tidak ditemukan: {project}", file=sys.stderr)
        return 2
    if not project.is_dir():
        print(f"Path proyek bukan folder: {project}", file=sys.stderr)
        return 2

    if not args.nama.strip():
        print("--nama tidak boleh kosong.", file=sys.stderr)
        return 2

    if not DOCS_TEMPLATE_DIR.is_dir():
        print(f"Folder template tidak ditemukan: {DOCS_TEMPLATE_DIR}", file=sys.stderr)
        return 2

    if args.tanggal:
        try:
            dt.date.fromisoformat(args.tanggal)
        except ValueError:
            print("--tanggal harus berformat YYYY-MM-DD.", file=sys.stderr)
            return 2

    tanggal = args.tanggal or dt.date.today().isoformat()
    ringkasan = args.ringkasan.strip() or "TODO: ringkas produk dalam 1-2 kalimat."
    values = {
        "NAMA_PRODUK": args.nama.strip(),
        "PEMILIK": args.pemilik.strip() or "Pemilik produk",
        "TANGGAL": tanggal,
        "RINGKASAN": ringkasan,
    }

    targets: list[tuple[Path, Path]] = []
    for template in sorted(DOCS_TEMPLATE_DIR.glob("*.md")):
        targets.append((template, project / "docs" / template.name))

    if args.publik:
        if not LEGAL_TEMPLATE_DIR.is_dir():
            print(f"Folder template legal tidak ditemukan: {LEGAL_TEMPLATE_DIR}", file=sys.stderr)
            return 2
        for template in sorted(LEGAL_TEMPLATE_DIR.glob("*.md")):
            targets.append((template, project / "docs" / "legal" / template.name))

    if not args.no_readme and ROOT_README_TEMPLATE.is_file():
        targets.append((ROOT_README_TEMPLATE, project / "README.md"))

    if not targets:
        print("Tidak ada template yang ditemukan.", file=sys.stderr)
        return 2

    created: list[Path] = []
    skipped: list[Path] = []

    for source, destination in targets:
        if destination.exists() and not args.force:
            skipped.append(destination)
            continue

        try:
            content = render(source.read_text(encoding="utf-8"), values)
        except OSError as exc:
            print(f"Gagal membaca template {source}: {exc}", file=sys.stderr)
            return 2

        if args.dry_run:
            print(f"Akan dibuat: {destination}")
            created.append(destination)
            continue

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        except OSError as exc:
            print(f"Gagal menulis {destination}: {exc}", file=sys.stderr)
            return 2

        print(f"Dibuat: {destination}")
        created.append(destination)

    if skipped:
        print("\nDilewati karena sudah ada (--force akan menimpa; hati-hati):")
        for path in skipped:
            print(f"  - {path}")

    if args.dry_run:
        print(f"\nDry run: {len(created)} file akan dibuat, {len(skipped)} dilewati.")
        return 0

    if created:
        print(f"\nSelesai: {len(created)} file dibuat, {len(skipped)} dilewati.")
        print("Langkah berikutnya: isi docs/ dengan keputusan nyata, lalu tunjukkan docs/README.md ke user.")
        if args.publik:
            print("Dokumen legal di docs/legal/ adalah DRAFT: isi sesuai produk nyata dan minta pemilik meninjaunya.")
    elif skipped:
        print("\nTidak ada file baru. Semua target sudah ada.")
    else:
        print("\nTidak ada file yang dibuat.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
