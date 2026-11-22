#!/usr/bin/env python3
"""Pendeteksi sinyal "AI slop" pada project: UI generik, teks klise, kode berlebihan, dan teknologi usang.

Ini heuristik: setiap temuan adalah SINYAL untuk dicek manusia, bukan vonis. Pola yang
dipakai dengan alasan produk yang tertulis boleh dipertahankan. Hanya memakai standard
library dan tidak mengubah file apa pun. Detail dan gantinya: references/anti-ai-slop.md.

Contoh:
    python3 scripts/cek_slop.py ~/proyek-saya
    python3 scripts/cek_slop.py ~/proyek-saya --ketat   # kode keluar 1 jika ada WARN
    python3 scripts/cek_slop.py ~/proyek-saya --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build", "out",
    "target", ".next", ".nuxt", ".svelte-kit", ".turbo", ".cache", "coverage", ".expo",
    ".gradle", ".idea", ".vscode", "vendor", ".dart_tool", "Pods",
}
CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".vue", ".svelte", ".astro", ".dart", ".go", ".rs", ".kt", ".swift", ".php", ".rb"}
UI_EXT = {".jsx", ".tsx", ".vue", ".svelte", ".astro", ".html", ".css", ".scss"}
COPY_EXT = CODE_EXT | {".html", ".md", ".mdx", ".json", ".yaml", ".yml", ".txt"}
SKIP_FILES = re.compile(r"(\.min\.(js|css)$|\.d\.ts$|(^|/)(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|bun\.lock|uv\.lock|poetry\.lock|Cargo\.lock|composer\.lock)$|\.map$)")
TEST_OR_FIXTURE = re.compile(r"(^|/)(tests?|__tests__|spec|e2e|fixtures?|mocks?|__mocks__|seeds?|stories|storybook)/|\.(test|spec|stories)\.[jt]sx?$|(^|/)test_[^/]+\.py$|_test\.(py|go)$|(^|/)seed[^/]*\.(ts|js|py|sql)$")
MIGRATION = re.compile(r"(^|/)(migrations?|drizzle|prisma/migrations|alembic/versions)/")
MAX_BYTES = 1024 * 1024

EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF☀-⛿✀-✒✗-➿]")

COPY_SLOP = [
    r"seamless(?:ly)?", r"elevate", r"unlock(?:s|ing)? (?:the |your )?(?:power|potential|full)", r"unleash", r"supercharge",
    r"empower(?:s|ing)?", r"revolutioni[sz]e", r"game[- ]changer", r"cutting[- ]edge", r"next[- ]level",
    r"effortless(?:ly)?", r"\bdelve\b", r"in today'?s (?:fast[- ]paced|digital)", r"\boops\b",
    r"mulus tanpa", r"tingkatkan pengalaman", r"buka potensi", r"revolusioner", r"solusi (?:terdepan|terbaik|inovatif)",
    r"era digital", r"kelas dunia", r"selamat datang di", r"wujudkan impian", r"\bups[!,]",
]
COPY_SLOP_RX = re.compile(r"(?i)(" + "|".join(COPY_SLOP) + r")")
STRING_SEGMENT = re.compile(r"\"([^\"\\\n]{3,})\"|'([^'\\\n]{3,})'|`([^`\\]{3,})`|>([^<>{}\n]{3,})<")

PLACEHOLDER = re.compile(r"(?i)\blorem ipsum\b|\b(?:john|jane) doe\b|\bacme(?: inc| corp)?\b|\bfoo@bar\b")
FAKE_STAT = re.compile(r"(?i)\b\d[\d.,]*\s*[kKrbjt]?\+\s*(?:happy\s+)?(?:users|customers|clients|pengguna|pelanggan|klien|bisnis|businesses)\b")

PURPLE = r"(?:purple|violet|indigo|fuchsia)"
TW_GRADIENT = re.compile(r"\bbg-(?:gradient-to|linear-to|linear|radial|conic)-?\w*")
TW_PURPLE_STOP = re.compile(r"\b(?:from|via|to)-" + PURPLE + r"-\d{2,3}")
CSS_PURPLE_GRADIENT = re.compile(r"(?i)(?:linear|radial|conic)-gradient\([^;]*(?:" + PURPLE + r"|#(?:6d28d9|7c3aed|8b5cf6|a855f7|9333ea|6366f1|4f46e5|4338ca|c026d3|d946ef))")
GRADIENT_TEXT = re.compile(r"bg-clip-text[^\"'`]*text-transparent|text-transparent[^\"'`]*bg-clip-text|background-clip:\s*text")
TW_ARBITRARY = re.compile(r"\b[a-z-]+-\[(?:#[0-9a-fA-F]{3,8}|\d+(?:\.\d+)?px)\]")

TS_ANY = re.compile(r":\s*any\b|\bas any\b|<any>|any\[\]")
TS_IGNORE = re.compile(r"@ts-ignore|@ts-nocheck")
PY_IGNORE = re.compile(r"#\s*type:\s*ignore(?!\[)")
CONSOLE = re.compile(r"\bconsole\.(?:log|debug)\(")
EMPTY_CATCH_JS = re.compile(r"catch\s*(?:\([^)]*\))?\s*\{\s*\}")
CATCH_LOG_ONLY = re.compile(r"catch\s*\((\w+)\)\s*\{\s*console\.(?:log|error)\(\s*\1\s*\)\s*;?\s*\}")
EMPTY_EXCEPT_PY = re.compile(r"except[^:\n]*:\s*\n\s*pass\b|except[^:\n]*:\s*pass\b")
NARRATION = re.compile(
    r"^\s*(?:step\s*\d+|langkah\s*\d+|import(?:ing)?\b|define\s|initiali[sz]e\s|create\s(?:a|an|the)\s|"
    r"returns?\s(?:the|a)\s|this\s(?:function|component|method|class|hook|file)\b|set\s?up\s|handle\s(?:the\s)?|"
    r"fungsi ini|komponen ini|inisialisasi\s|buat\s(?:variabel|fungsi|state)|definisikan\s|impor\s)",
    re.I,
)
COMMENT_C = re.compile(r"^\s*(?://|/\*|\*(?!\*?/))\s?(.*)")
COMMENT_HASH = re.compile(r"^\s*#(?![!\[])\s?(.*)")
HASH_COMMENT_EXT = {".py", ".rb"}


def comment_body(line: str, ext: str) -> str | None:
    m = (COMMENT_HASH if ext in HASH_COMMENT_EXT else COMMENT_C).match(line)
    return m.group(1) if m else None
FAKE_IMPL = re.compile(r"(?i)TODO:?\s*implement|not implemented(?! error)|implement (?:this|later)|placeholder implementation|mock(?:ed)? (?:data|response) for now")
TODO = re.compile(r"\b(?:TODO|FIXME|HACK|XXX)\b")
USE_EFFECT_FETCH = re.compile(r"useEffect\(\s*(?:async\s*)?\(\)\s*=>\s*\{.{0,300}?\bfetch\(", re.S)
GENERIC_FILE = re.compile(r"(^|/)(utils?|helpers?|misc|common|functions)\.(ts|js|tsx|jsx|py)$")
BAD_COMMIT = re.compile(r"(?i)^(update|updates|fix|fixes|wip|changes|final\d*|test|asdf|commit|misc|stuff|done|minor|edit)[.!]*$")


class Report:
    def __init__(self) -> None:
        self.items: dict[tuple[str, str, str], list[str]] = defaultdict(list)

    def add(self, level: str, rule: str, message: str, where: str | None = None) -> None:
        bucket = self.items[(level, rule, message)]
        if where is not None and where not in bucket:
            bucket.append(where)

    def counts(self) -> dict[str, int]:
        c = {"WARN": 0, "INFO": 0}
        for (level, _, _) in self.items:
            c[level] += 1
        return c


def collect_files(root: Path) -> tuple[list[str], bool]:
    if (root / ".git").exists() and shutil.which("git"):
        try:
            out = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                capture_output=True, check=True, timeout=60,
            ).stdout.decode("utf-8", "replace")
            return sorted({f for f in out.split("\0") if f and (root / f).is_file()}), True
        except (subprocess.SubprocessError, OSError):
            pass
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            files.append(Path(dirpath, name).relative_to(root).as_posix())
    return sorted(files), False


def read(root: Path, rel: str) -> str | None:
    p = root / rel
    try:
        if p.stat().st_size > MAX_BYTES:
            return None
        data = p.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data.decode("utf-8", "replace")


def scan(root: Path) -> Report:
    r = Report()
    files, is_git = collect_files(root)
    files = [f for f in files if not SKIP_FILES.search(f) and not any(part in SKIP_DIRS for part in Path(f).parts)]
    glass_hits: list[str] = []
    arbitrary_hits: list[str] = []
    pkg_deps: dict[str, str] = {}

    for rel in files:
        ext = Path(rel).suffix.lower()
        if ext not in COPY_EXT and ext not in UI_EXT:
            continue
        text = read(root, rel)
        if text is None:
            continue
        lines = text.splitlines()
        is_test = bool(TEST_OR_FIXTURE.search(rel))
        is_code = ext in CODE_EXT
        is_ui = ext in UI_EXT

        if Path(rel).name == "package.json" and "/" not in rel:
            try:
                pkg = json.loads(text)
                for key in ("dependencies", "devDependencies"):
                    pkg_deps.update(pkg.get(key, {}) or {})
            except json.JSONDecodeError:
                pass

        # ---- UI visual
        if is_ui or ext in {".js", ".ts"}:
            for i, line in enumerate(lines, 1):
                if (TW_GRADIENT.search(line) and TW_PURPLE_STOP.search(line)) or CSS_PURPLE_GRADIENT.search(line):
                    r.add("WARN", "ui-gradasi-ungu", "Gradasi ungu/violet/indigo (pola AI paling dikenali). Pakai warna merek solid kecuali ada alasan merek tertulis.", f"{rel}:{i}")
                if GRADIENT_TEXT.search(line):
                    r.add("WARN", "ui-teks-gradasi", "Judul/teks bergradasi. Gunakan teks solid; hierarki lewat ukuran dan berat.", f"{rel}:{i}")
                if "backdrop-blur" in line or "backdrop-filter" in line:
                    glass_hits.append(f"{rel}:{i}")
                for _ in TW_ARBITRARY.finditer(line):
                    arbitrary_hits.append(f"{rel}:{i}")
                if ext in {".jsx", ".tsx", ".vue", ".svelte", ".astro", ".html"} and EMOJI.search(line) and comment_body(line, ext) is None:
                    r.add("WARN", "ui-emoji", "Emoji di markup UI. Pastikan bukan pengganti ikon/dekorasi; gunakan satu set ikon.", f"{rel}:{i}")

        # ---- copy & konten palsu
        if not is_test:
            for i, line in enumerate(lines, 1):
                segments = [line] if not is_code else [g for m in STRING_SEGMENT.finditer(line) for g in m.groups() if g]
                for seg in segments:
                    m = COPY_SLOP_RX.search(seg)
                    if m:
                        r.add("WARN", "teks-klise", "Frasa klise khas AI. Tulis spesifik: apa yang dilakukan produk untuk siapa.", f"{rel}:{i} — \"{m.group(1)}\"")
                    if PLACEHOLDER.search(seg):
                        r.add("WARN", "konten-placeholder", "Konten placeholder (Lorem ipsum/John Doe/Acme) di luar tes/seed.", f"{rel}:{i}")
                    if FAKE_STAT.search(seg):
                        r.add("WARN", "statistik", "Klaim angka pengguna. Pastikan nyata dan bisa dibuktikan; jika tidak, hapus.", f"{rel}:{i}")

        if not is_code:
            continue

        # ---- kode
        code_lines = [ln for ln in lines if ln.strip()]
        comment_lines = [ln for ln in code_lines if comment_body(ln, ext) is not None]
        if len(code_lines) >= 40 and len(comment_lines) / len(code_lines) > 0.35 and not MIGRATION.search(rel):
            r.add("WARN", "komentar-padat", f"Rasio komentar tinggi (>35%). Komentar hanya untuk 'kenapa'; nama yang jelas untuk 'apa'.", f"{rel} ({len(comment_lines)}/{len(code_lines)} baris)")
        for i, line in enumerate(lines, 1):
            body = comment_body(line, ext)
            if body is not None and NARRATION.match(body):
                r.add("WARN", "komentar-narasi", "Komentar yang menceritakan kode (Step 1, Import..., This function...). Hapus atau ganti dengan alasan.", f"{rel}:{i}")
            if body is not None and EMOJI.search(body):
                r.add("WARN", "emoji-kode", "Emoji di komentar kode.", f"{rel}:{i}")
            if FAKE_IMPL.search(line):
                r.add("WARN", "implementasi-palsu", "Implementasi belum ada/palsu. Selesaikan atau tandai di roadmap, jangan dirilis diam-diam.", f"{rel}:{i}")
            elif TODO.search(line):
                r.add("INFO", "todo", "TODO/FIXME tersisa. Pindahkan ke backlog atau selesaikan.", f"{rel}:{i}")
            if ext in {".ts", ".tsx"}:
                if TS_ANY.search(line) and body is None:
                    r.add("WARN", "ts-any", "Tipe `any` mematikan pemeriksaan tipe. Gunakan tipe nyata atau `unknown` + narrowing.", f"{rel}:{i}")
                if TS_IGNORE.search(line):
                    r.add("WARN", "ts-ignore", "@ts-ignore/@ts-nocheck. Perbaiki tipenya, atau pakai @ts-expect-error dengan alasan.", f"{rel}:{i}")
            if ext == ".py" and PY_IGNORE.search(line):
                r.add("INFO", "py-ignore", "`# type: ignore` tanpa kode error spesifik.", f"{rel}:{i}")
            if ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"} and not is_test and CONSOLE.search(line) and body is None:
                r.add("WARN", "console-log", "console.log/debug tertinggal. Gunakan logger terstruktur atau hapus.", f"{rel}:{i}")
        if ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
            for m in EMPTY_CATCH_JS.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                r.add("WARN", "catch-kosong", "catch kosong menelan error. Tangani di batas sistem atau lempar ulang.", f"{rel}:{line_no}")
            for m in CATCH_LOG_ONLY.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                r.add("WARN", "catch-log-saja", "catch yang hanya mencetak error lalu lanjut seolah sukses.", f"{rel}:{line_no}")
            if ext in {".jsx", ".tsx"}:
                for m in USE_EFFECT_FETCH.finditer(text):
                    line_no = text.count("\n", 0, m.start()) + 1
                    r.add("INFO", "useeffect-fetch", "Fetch data di useEffect. Pertimbangkan Server Component/loader atau TanStack Query.", f"{rel}:{line_no}")
        if ext == ".py":
            for m in EMPTY_EXCEPT_PY.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                r.add("WARN", "except-pass", "`except: pass` menelan error.", f"{rel}:{line_no}")
        if not MIGRATION.search(rel) and not is_test:
            if len(lines) > 600:
                r.add("WARN", "file-besar", "File kode > 600 baris. Pecah per tanggung jawab.", f"{rel} ({len(lines)} baris)")
            if GENERIC_FILE.search(rel) and len(lines) > 250:
                r.add("WARN", "file-generik", "File utils/helpers besar menjadi tempat sampah. Pecah dan beri nama sesuai isi.", f"{rel} ({len(lines)} baris)")

    if len(glass_hits) > 3:
        msg = f"backdrop-blur/glassmorphism dipakai {len(glass_hits)}×. Pakai hanya untuk overlay yang melayang."
        for h in glass_hits:
            r.add("WARN", "ui-glass", msg, h)
    if len(arbitrary_hits) > 5:
        msg = f"{len(arbitrary_hits)} nilai arbitrer Tailwind (hex/px langsung). Pindahkan ke token desain."
        for h in arbitrary_hits:
            r.add("WARN", "token", msg, h)

    # ---- teknologi usang / campuran generasi
    # CATATAN: daftar di bawah adalah potret (Nov 2026) dan akan menua. Jangan jadikan acuan tunggal:
    # teknologi terkini ditentukan lewat protokol riset (references/teknis-modern.md §0 + cek_versi.py).
    def major(name: str) -> int | None:
        m = re.search(r"(\d+)", pkg_deps.get(name, ""))
        return int(m.group(1)) if m else None

    fileset = set(files)
    for dep, why in {
        "react-scripts": "Create React App sudah tidak direkomendasikan. Gunakan Vite atau framework (Next.js, React Router).",
        "moment": "moment.js dalam mode maintenance. Gunakan Intl + date-fns/Day.js/Temporal.",
        "request": "Paket `request` sudah deprecated. Gunakan fetch bawaan.",
        "tailwindcss-animate": "Untuk Tailwind v4/shadcn terbaru, gunakan tw-animate-css.",
    }.items():
        if dep in pkg_deps:
            r.add("WARN", "usang", why, f"package.json: {dep}")
    tw = major("tailwindcss")
    tw_config = [f for f in fileset if re.fullmatch(r"tailwind\.config\.(js|ts|cjs|mjs)", f)]
    if tw is not None and tw >= 4 and tw_config:
        r.add("WARN", "campur-generasi", "Tailwind v4 memakai konfigurasi CSS-first (@theme). tailwind.config.* gaya v3 kemungkinan sisa/terabaikan.", tw_config[0])
    nx = major("next")
    if nx is not None and nx >= 16:
        for mw in ("middleware.ts", "middleware.js", "src/middleware.ts", "src/middleware.js"):
            if mw in fileset:
                r.add("WARN", "usang", "Next.js 16 mengganti middleware menjadi proxy (proxy.ts).", mw)
    has_app_dir = any(f.startswith(("app/", "src/app/")) for f in fileset)
    if has_app_dir:
        for f in files:
            if Path(f).suffix in {".tsx", ".jsx", ".ts", ".js"} and re.search(r"\b(getServerSideProps|getStaticProps)\b", read(root, f) or ""):
                r.add("INFO", "campur-generasi", "API Pages Router di project yang punya App Router. Pastikan ini migrasi yang disengaja.", f)
    icon_libs = [d for d in pkg_deps if d in {"lucide-react", "react-icons", "@heroicons/react", "@phosphor-icons/react", "@tabler/icons-react", "@fortawesome/react-fontawesome", "react-feather"}]
    if len(icon_libs) > 1:
        r.add("WARN", "ikon-campur", "Lebih dari satu library ikon. Pilih satu set agar konsisten.", ", ".join(icon_libs))
    date_libs = [d for d in pkg_deps if d in {"moment", "dayjs", "date-fns", "luxon"}]
    if len(date_libs) > 1:
        r.add("WARN", "dua-cara", "Lebih dari satu library tanggal.", ", ".join(date_libs))
    fetch_libs = [d for d in pkg_deps if d in {"axios", "@tanstack/react-query", "swr", "ky"}]
    if {"@tanstack/react-query", "swr"} <= set(fetch_libs):
        r.add("WARN", "dua-cara", "TanStack Query dan SWR sekaligus. Pilih satu.", ", ".join(fetch_libs))

    # ---- riwayat commit
    if is_git:
        try:
            log = subprocess.run(["git", "-C", str(root), "log", "-50", "--format=%s"], capture_output=True, text=True, timeout=30).stdout
        except (subprocess.SubprocessError, OSError):
            log = ""
        for subject in log.splitlines():
            if BAD_COMMIT.match(subject.strip()) or EMOJI.search(subject):
                r.add("WARN", "commit", "Pesan commit tidak informatif atau berisi emoji. Gunakan Conventional Commits yang menjelaskan alasan.", subject.strip()[:80])
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description="Deteksi sinyal AI slop (heuristik, tanpa mengubah file).")
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--ketat", action="store_true", help="Kode keluar 1 jika ada WARN (untuk CI).")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--maks", type=int, default=10, help="Maksimum lokasi yang ditampilkan per temuan (default 10).")
    args = ap.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"Folder project tidak ditemukan: {root}", file=sys.stderr)
        return 2
    rep = scan(root)
    counts = rep.counts()
    ordered = sorted(rep.items.items(), key=lambda kv: (kv[0][0] != "WARN", kv[0][1]))

    if args.json:
        out = [{"level": l, "rule": ru, "message": m, "locations": locs} for (l, ru, m), locs in ordered]
        print(json.dumps({"project": str(root), "counts": counts, "findings": out}, ensure_ascii=False, indent=2))
    else:
        print(f"Cek AI slop: {root}\n")
        if not ordered:
            print("Tidak ada sinyal slop yang terdeteksi. Tetap lakukan review visual dan baca teks UI (references/anti-ai-slop.md §8).")
        for (level, rule, msg), locs in ordered:
            mark = "! WARN" if level == "WARN" else "· INFO"
            extra = f" ({len(locs)} lokasi)" if len(locs) > 1 else ""
            print(f"{mark}  [{rule}] {msg}{extra}")
            for loc in locs[: args.maks]:
                print(f"           - {loc}")
            if len(locs) > args.maks:
                print(f"           … dan {len(locs) - args.maks} lainnya")
        print(f"\nRingkasan: {counts['WARN']} jenis WARN, {counts['INFO']} jenis INFO.")
        print("Ini sinyal, bukan vonis: perbaiki, atau catat alasan mempertahankannya di docs/04-kualitas.md.")
    return 1 if args.ketat and counts["WARN"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
