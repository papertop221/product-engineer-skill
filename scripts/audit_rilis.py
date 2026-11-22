#!/usr/bin/env python3
"""Pemeriksaan otomatis kesiapan rilis untuk project yang dibangun dengan product-engineer.

Memeriksa hal yang sering terlewat sebelum rilis: secret yang bocor, file .env atau
kunci privat yang ikut ter-commit, lockfile, versi runtime, tes, CI, dan dokumen.
Hanya memakai standard library. Tidak mengubah file apa pun.

Contoh:
    python3 scripts/audit_rilis.py ~/proyek-saya
    python3 scripts/audit_rilis.py ~/proyek-saya --publik
    python3 scripts/audit_rilis.py ~/proyek-saya --jalankan-audit   # npm audit, pip-audit, dst. bila terpasang
    python3 scripts/audit_rilis.py ~/proyek-saya --json

Kode keluar: 0 = tidak ada FAIL, 1 = ada FAIL, 2 = kesalahan pemakaian.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
    "target", ".next", ".nuxt", ".svelte-kit", ".turbo", ".cache", "coverage",
    ".gradle", ".idea", ".vscode", "vendor", ".dart_tool", "Pods", ".expo",
}
MAX_SCAN_BYTES = 2 * 1024 * 1024
LARGE_FILE_BYTES = 5 * 1024 * 1024

# (label, regex) — pola yang hampir pasti secret asli.
STRONG_SECRETS = [
    ("Kunci privat", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY(?: BLOCK)?-----"),
    ("AWS access key", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("GitHub token", r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b"),
    ("GitLab token", r"\bglpat-[A-Za-z0-9_\-]{20,}\b"),
    ("Slack token", r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    ("Stripe live key", r"\b[sr]k_live_[A-Za-z0-9]{20,}\b"),
    ("Anthropic API key", r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b"),
    ("OpenAI API key", r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_\-]{32,}\b"),
    ("Telegram bot token", r"\b\d{8,10}:AA[A-Za-z0-9_\-]{33}\b"),
    ("Midtrans server key", r"\b(?:SB-)?Mid-server-[A-Za-z0-9_\-]{16,}\b"),
    ("Xendit secret key", r"\bxnd_(?:production|development)_[A-Za-z0-9]{20,}\b"),
    ("SendGrid key", r"\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b"),
]
# Pola yang perlu dicek manusia (bisa jadi kunci publik/contoh).
WEAK_SECRETS = [
    ("Google API key (cek: kunci publik Firebase wajar, kunci server tidak)", r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    ("Kredensial di URL koneksi", r"\b[a-z][a-z0-9+.\-]*://[^\s:/@'\"]+:[^\s@'\"]{6,}@[^\s'\"]+"),
]
ASSIGNMENT_SECRET = re.compile(
    r"""(?ix)
    \b(password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|private[_-]?key)\b
    ["']?\s*[:=]\s*
    ["']([^"'\s]{8,})["']
    """
)
# Placeholder jelas di dalam token yang mirip secret kuat.
STRONG_PLACEHOLDER = re.compile(r"(?i)(x{6,}|\*{3,}|\.{3}|<[^>]*>|example|your[_-]|placeholder|redacted)")
# Placeholder untuk nilai assignment/pola lemah (lebih longgar karena pola itu sendiri lebih lemah).
PLACEHOLDER = re.compile(
    r"(?i)(x{4,}|\*{3,}|\.{3}|<[^>]*>|\$\{|\{\{|example|contoh|sample|dummy|changeme|change_me|your[_-]|placeholder|test|fake|palsu|redacted|isi[_-]|todo)"
)

ENV_FILE = re.compile(r"(^|/)\.env(\.[A-Za-z0-9_-]+)?$")
ENV_TEMPLATE_SUFFIX = (".example", ".sample", ".template", ".dist", ".defaults")
KEY_FILE = re.compile(r"(?i)(\.(pem|key|p12|pfx|jks|keystore)|(^|/)id_(rsa|ed25519|ecdsa|dsa))$")
ENV_USAGE = re.compile(r"process\.env\b|import\.meta\.env\b|os\.environ|os\.getenv|env::var|os\.Getenv|Deno\.env|System\.getenv|ENV\[")
CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rs", ".go", ".rb", ".php", ".java", ".kt", ".dart", ".svelte", ".vue"}
TEST_NAME = re.compile(r"(^|/)(tests?|__tests__|spec|e2e)/|(_test\.(go|py|rs)|\.test\.[jt]sx?|\.spec\.[jt]sx?|(^|/)test_[^/]+\.py)$")

LOCKFILES = {
    "package.json": ["package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock"],
    "pyproject.toml": ["uv.lock", "poetry.lock", "pdm.lock", "Pipfile.lock", "requirements.txt", "requirements.lock"],
    "Pipfile": ["Pipfile.lock"],
    "Cargo.toml": ["Cargo.lock"],
    "go.mod": ["go.sum"],
    "Gemfile": ["Gemfile.lock"],
    "composer.json": ["composer.lock"],
    "pubspec.yaml": ["pubspec.lock"],
}
DOCS_REQUIRED = [
    "README.md", "01-rencana-produk.md", "02-arsitektur.md", "03-roadmap.md",
    "04-kualitas.md", "05-deploy.md", "06-serah-terima.md",
]


@dataclass
class Finding:
    level: str  # FAIL | WARN | OK | INFO
    check: str
    message: str
    details: list[str] = field(default_factory=list)


class Audit:
    def __init__(self, root: Path, publik: bool, run_tools: bool) -> None:
        self.root = root
        self.publik = publik
        self.run_tools = run_tools
        self.findings: list[Finding] = []
        self.is_git = False
        self.files: list[str] = []  # path relatif dengan "/"

    # ------------------------------------------------------------------ util
    def add(self, level: str, check: str, message: str, details: list[str] | None = None) -> None:
        self.findings.append(Finding(level, check, message, details or []))

    def exists(self, rel: str) -> bool:
        return (self.root / rel).exists()

    def read(self, rel: str) -> str | None:
        path = self.root / rel
        try:
            if not path.is_file() or path.stat().st_size > MAX_SCAN_BYTES:
                return None
            data = path.read_bytes()
        except OSError:
            return None
        if b"\0" in data[:8192]:
            return None
        return data.decode("utf-8", errors="replace")

    # ------------------------------------------------------------ file list
    def collect_files(self) -> None:
        if (self.root / ".git").exists() and shutil.which("git"):
            try:
                out = subprocess.run(
                    ["git", "-C", str(self.root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                    capture_output=True, check=True, timeout=60,
                ).stdout
                self.files = sorted({f for f in out.decode("utf-8", "replace").split("\0") if f and (self.root / f).is_file()})
                self.is_git = True
                return
            except (subprocess.SubprocessError, OSError):
                pass
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                rel = Path(dirpath, name).relative_to(self.root).as_posix()
                self.files.append(rel)
        self.files.sort()

    # --------------------------------------------------------------- checks
    def check_git(self) -> None:
        if self.is_git:
            self.add("OK", "git", "Repo git terdeteksi; yang dipindai = file ter-commit + file baru yang tidak di-ignore.")
        else:
            self.add("WARN", "git", "Bukan repo git (atau git tidak tersedia). Semua file dipindai; inisialisasi git di Fase 2.")
        if not self.exists(".gitignore"):
            self.add("WARN", "gitignore", "Tidak ada .gitignore. Tambahkan minimal: .env, build output, dependency, dan data lokal.")

    def check_sensitive_files(self) -> None:
        env_files = [
            f for f in self.files
            if ENV_FILE.search(f) and not f.endswith(ENV_TEMPLATE_SUFFIX)
        ]
        if env_files:
            where = "akan/sudah ikut ter-commit" if self.is_git else "ada di folder project"
            self.add("FAIL", "env-file", f"File environment berisi nilai asli {where}. Masukkan ke .gitignore; jika pernah ter-commit, rotasi semua secret di dalamnya.", env_files)
        elif not self.is_git:
            gi = self.read(".gitignore") or ""
            if not re.search(r"(?m)^\s*\.env", gi):
                self.add("WARN", "env-file", ".gitignore tidak mengabaikan .env.")
        key_files = [f for f in self.files if KEY_FILE.search(f)]
        if key_files:
            self.add("FAIL", "key-file", "File kunci/sertifikat privat ada di project (signing key, SSH key, keystore). Pindahkan ke secret manager atau simpan di luar repo.", key_files)
        if not env_files and not key_files:
            self.add("OK", "sensitive-files", "Tidak ada file .env asli atau file kunci privat di daftar file.")

    def check_secrets(self) -> None:
        strong = [(label, re.compile(rx)) for label, rx in STRONG_SECRETS]
        weak = [(label, re.compile(rx)) for label, rx in WEAK_SECRETS]
        hits_fail: list[str] = []
        hits_warn: list[str] = []
        for rel in self.files:
            text = self.read(rel)
            if text is None:
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if len(line) > 2000:
                    line = line[:2000]
                for label, rx in strong:
                    m = rx.search(line)
                    if m and not STRONG_PLACEHOLDER.search(m.group(0)):
                        hits_fail.append(f"{rel}:{lineno} — {label}")
                for label, rx in weak:
                    m = rx.search(line)
                    if m and not PLACEHOLDER.search(m.group(0)):
                        hits_warn.append(f"{rel}:{lineno} — {label}")
                m = ASSIGNMENT_SECRET.search(line)
                if m and not PLACEHOLDER.search(m.group(2)):
                    hits_warn.append(f"{rel}:{lineno} — nilai '{m.group(1)}' ditulis langsung di kode")
        if hits_fail:
            self.add("FAIL", "secrets", "Kemungkinan secret asli ditemukan. Hapus dari kode, pindahkan ke environment/secret manager, dan ROTASI secret-nya (anggap sudah bocor).", hits_fail[:50])
        if hits_warn:
            self.add("WARN", "secrets-review", "Pola mirip secret yang perlu dicek manual.", hits_warn[:50])
        if not hits_fail and not hits_warn:
            self.add("OK", "secrets", "Tidak ada pola secret yang dikenali. (Pemindaian dasar; gunakan gitleaks untuk pemeriksaan menyeluruh.)")

    def check_lockfiles(self) -> None:
        manifests = [f for f in self.files if Path(f).name in LOCKFILES]
        if not manifests:
            self.add("INFO", "lockfile", "Tidak ada manifest dependency yang dikenali (package.json, pyproject.toml, Cargo.toml, go.mod, …).")
            return
        missing_fail: list[str] = []
        missing_warn: list[str] = []
        fileset = set(self.files)
        for manifest in manifests:
            name = Path(manifest).name
            if name == "pyproject.toml" and not self._pyproject_has_deps(manifest):
                continue
            if name == "go.mod" and "require" not in (self.read(manifest) or ""):
                continue
            if self._has_lock_upwards(manifest, LOCKFILES[name], fileset):
                continue
            if name in ("pyproject.toml", "Pipfile"):
                missing_warn.append(manifest)
            elif name == "Cargo.toml" and not (Path(manifest).parent / "src" / "main.rs").as_posix() in fileset:
                missing_warn.append(manifest + " (library: lockfile opsional)")
            else:
                missing_fail.append(manifest)
        if missing_fail:
            self.add("FAIL", "lockfile", "Manifest tanpa lockfile yang di-commit. Build tidak reproducible dan rawan serangan supply chain.", missing_fail)
        if missing_warn:
            self.add("WARN", "lockfile", "Manifest Python/Rust tanpa lockfile. Gunakan uv.lock/poetry.lock atau requirements dengan versi terkunci.", missing_warn)
        for req in [f for f in self.files if re.search(r"(^|/)requirements[^/]*\.txt$", f)]:
            loose = []
            for line in (self.read(req) or "").splitlines():
                s = line.split("#", 1)[0].strip()
                if not s or s.startswith(("-", "--")):
                    continue
                if "==" not in s and "@" not in s:
                    loose.append(s)
            if loose:
                self.add("WARN", "pinning", f"{req}: {len(loose)} dependency tanpa versi terkunci (==).", loose[:20])
        if not missing_fail and not missing_warn:
            self.add("OK", "lockfile", "Semua manifest dependency punya lockfile.")

    def _pyproject_has_deps(self, rel: str) -> bool:
        text = self.read(rel) or ""
        return bool(re.search(r"(?m)^\s*dependencies\s*=\s*\[\s*[\"']", text) or "[tool.poetry.dependencies]" in text)

    def _has_lock_upwards(self, manifest: str, locks: list[str], fileset: set[str]) -> bool:
        parent = Path(manifest).parent
        while True:
            for lock in locks:
                candidate = (parent / lock).as_posix()
                if candidate.startswith("./"):
                    candidate = candidate[2:]
                if candidate in fileset:
                    return True
            if parent == Path(".") or parent == Path(""):
                return False
            parent = parent.parent

    def check_runtime_pinned(self) -> None:
        fileset = set(self.files)
        problems = []
        if "package.json" in fileset:
            pkg = self.read("package.json") or ""
            if '"engines"' not in pkg and not ({".nvmrc", ".node-version", ".tool-versions"} & fileset):
                problems.append("Node: tambahkan .nvmrc atau \"engines\" di package.json")
        if "pyproject.toml" in fileset or any(re.search(r"(^|/)requirements[^/]*\.txt$", f) for f in fileset):
            py = self.read("pyproject.toml") or ""
            if "requires-python" not in py and not ({".python-version", ".tool-versions", "runtime.txt"} & fileset):
                problems.append("Python: tambahkan .python-version atau requires-python")
        if "Cargo.toml" in fileset:
            cargo = self.read("Cargo.toml") or ""
            if "rust-version" not in cargo and not ({"rust-toolchain.toml", "rust-toolchain"} & fileset):
                problems.append("Rust: tambahkan rust-toolchain.toml atau rust-version")
        if problems:
            self.add("WARN", "runtime", "Versi runtime belum dikunci.", problems)

    def check_tests_ci_docs(self) -> None:
        tests = [f for f in self.files if TEST_NAME.search(f)]
        if tests:
            self.add("OK", "tests", f"{len(tests)} file tes ditemukan.")
        else:
            self.add("WARN", "tests", "Tidak ada file tes yang dikenali. Jalur kritis wajib punya tes (lihat references/pengujian.md).")

        ci = [f for f in self.files if f.startswith(".github/workflows/") or f in (".gitlab-ci.yml", "bitbucket-pipelines.yml", ".circleci/config.yml", "azure-pipelines.yml") or f.startswith(".woodpecker")]
        if ci:
            self.add("OK", "ci", "Konfigurasi CI ditemukan.", ci[:10])
            for wf in ci:
                text = self.read(wf) or ""
                if wf.startswith(".github/workflows/") and "permissions:" not in text:
                    self.add("WARN", "ci-permissions", f"{wf}: tidak ada blok 'permissions:'. Batasi izin token (mis. contents: read).")
        else:
            self.add("WARN", "ci", "Tidak ada konfigurasi CI. Gerbang otomatis (lint, tes, build, audit) belum berjalan di setiap push.")

        if not self.exists("README.md"):
            self.add("WARN", "readme", "Tidak ada README.md di root.")
        missing_docs = [d for d in DOCS_REQUIRED if not self.exists(f"docs/{d}")]
        if self.publik and not self.exists("docs/07-siap-rilis.md"):
            missing_docs.append("07-siap-rilis.md")
        if missing_docs:
            self.add("WARN", "docs", "Dokumen proyek belum lengkap (buat dengan scripts/scaffold_docs.py).", [f"docs/{d}" for d in missing_docs])
        else:
            self.add("OK", "docs", "Dokumen proyek lengkap.")

        uses_env = any(
            Path(f).suffix in CODE_EXT and ENV_USAGE.search(self.read(f) or "")
            for f in self.files if not TEST_NAME.search(f)
        )
        has_example = any(Path(f).name.startswith(".env") and f.endswith(ENV_TEMPLATE_SUFFIX) for f in self.files)
        if uses_env and not has_example:
            self.add("WARN", "env-example", "Kode membaca environment variable tetapi tidak ada .env.example yang mendokumentasikannya.")

    def check_misc(self) -> None:
        large = []
        for f in self.files:
            try:
                size = (self.root / f).stat().st_size
            except OSError:
                continue
            if size > LARGE_FILE_BYTES:
                large.append(f"{f} ({size // (1024 * 1024)} MB)")
        if large:
            self.add("WARN", "large-files", "File besar di repo. Pindahkan ke object storage/Git LFS bila bukan bagian dari kode.", large[:20])
        debug = []
        for f in self.files:
            name = Path(f).name
            if re.fullmatch(r"settings[^/]*\.py", name) and re.search(r"(?m)^\s*DEBUG\s*=\s*True\b", self.read(f) or ""):
                debug.append(f)
        if debug:
            self.add("WARN", "debug", "DEBUG = True ditulis langsung. Pastikan diambil dari environment dan mati di produksi.", debug)

    def check_publik(self) -> None:
        names = [f.lower() for f in self.files]
        has_privacy = any(re.search(r"priva(cy|si)", n) for n in names)
        has_terms = any(re.search(r"(terms|syarat|ketentuan|(^|[/_-])tos\b)", n) for n in names)
        if not has_privacy:
            self.add("WARN", "legal", "Kebijakan privasi tidak ditemukan. Wajib jika produk mengumpulkan data pribadi apa pun (lihat references/siap-publik.md).")
        if not has_terms:
            self.add("WARN", "legal", "Syarat & ketentuan tidak ditemukan. Diperlukan jika ada akun, transaksi, atau konten user.")
        drafts = [f for f in self.files if f.startswith("docs/legal/") and "DRAFT TEMPLATE" in (self.read(f) or "")]
        if drafts:
            self.add("WARN", "legal-draft", "Dokumen legal masih berupa template draft. Isi sesuai produk nyata lalu minta pemilik meninjaunya.", drafts)
        if not any(f.endswith(".well-known/security.txt") for f in self.files):
            self.add("INFO", "security-txt", "Tidak ada .well-known/security.txt (disarankan sebagai kontak laporan keamanan).")
        siap = self.read("docs/07-siap-rilis.md")
        if siap is not None and re.search(r"Keputusan rilis \|\s*Belum / Ya dengan catatan / Ya", siap):
            self.add("WARN", "siap-rilis", "docs/07-siap-rilis.md belum diisi (keputusan rilis masih kosong).")
        if has_privacy and has_terms and not drafts:
            self.add("OK", "legal", "Dokumen privasi dan syarat ditemukan.")

    def run_external_tools(self) -> None:
        fileset = set(self.files)
        plans: list[tuple[str, list[str], bool]] = [
            ("npm audit", ["npm", "audit", "--omit=dev", "--audit-level=high"], "package-lock.json" in fileset),
            ("pnpm audit", ["pnpm", "audit", "--prod", "--audit-level", "high"], "pnpm-lock.yaml" in fileset),
            ("pip-audit", ["pip-audit", "-r", "requirements.txt"], "requirements.txt" in fileset),
            ("cargo audit", ["cargo", "audit"], "Cargo.lock" in fileset),
            ("govulncheck", ["govulncheck", "./..."], "go.mod" in fileset),
            ("gitleaks", ["gitleaks", "detect", "--no-banner", "--redact", "--source", "."] if self.is_git else ["gitleaks", "detect", "--no-banner", "--redact", "--no-git", "--source", "."], True),
        ]
        for label, cmd, applicable in plans:
            if not applicable:
                continue
            if not shutil.which(cmd[0]):
                self.add("INFO", "tool", f"{label} tidak terpasang; dilewati.")
                continue
            try:
                proc = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, timeout=300)
            except subprocess.TimeoutExpired:
                self.add("WARN", "tool", f"{label} timeout (> 5 menit).")
                continue
            except OSError as exc:
                self.add("WARN", "tool", f"{label} gagal dijalankan: {exc}")
                continue
            tail = [line for line in (proc.stdout + proc.stderr).strip().splitlines()[-15:]]
            if proc.returncode == 0:
                self.add("OK", "tool", f"{label} lulus.")
            else:
                self.add("FAIL", "tool", f"{label} melaporkan masalah (kode {proc.returncode}). Periksa outputnya; butuh jaringan untuk database advisori.", tail)

    # ----------------------------------------------------------------- run
    def run(self) -> list[Finding]:
        self.collect_files()
        self.check_git()
        self.check_sensitive_files()
        self.check_secrets()
        self.check_lockfiles()
        self.check_runtime_pinned()
        self.check_tests_ci_docs()
        self.check_misc()
        if self.publik:
            self.check_publik()
        if self.run_tools:
            self.run_external_tools()
        return self.findings


SYMBOL = {"FAIL": "✖ FAIL", "WARN": "! WARN", "OK": "✔ OK  ", "INFO": "· INFO"}
ORDER = {"FAIL": 0, "WARN": 1, "INFO": 2, "OK": 3}


def main() -> int:
    parser = argparse.ArgumentParser(description="Pemeriksaan otomatis kesiapan rilis (tanpa mengubah file).")
    parser.add_argument("project", nargs="?", default=".", help="Folder project (default: folder saat ini).")
    parser.add_argument("--publik", action="store_true", help="Tambahkan pemeriksaan untuk rilis publik (legal, siap-rilis, security.txt).")
    parser.add_argument("--jalankan-audit", action="store_true", help="Jalankan alat audit yang terpasang (npm/pnpm audit, pip-audit, cargo audit, govulncheck, gitleaks).")
    parser.add_argument("--json", action="store_true", help="Keluarkan hasil dalam format JSON.")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"Folder project tidak ditemukan: {root}", file=sys.stderr)
        return 2

    findings = Audit(root, args.publik, args.jalankan_audit).run()
    findings.sort(key=lambda f: ORDER[f.level])
    counts = {lvl: sum(1 for f in findings if f.level == lvl) for lvl in ORDER}

    if args.json:
        print(json.dumps({"project": str(root), "counts": counts, "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=2))
    else:
        print(f"Audit rilis: {root}\n")
        for f in findings:
            print(f"{SYMBOL[f.level]}  [{f.check}] {f.message}")
            for d in f.details:
                print(f"           - {d}")
        print(f"\nRingkasan: {counts['FAIL']} FAIL, {counts['WARN']} WARN, {counts['OK']} OK, {counts['INFO']} INFO")
        if counts["FAIL"]:
            print("Gerbang BELUM lulus: perbaiki semua FAIL terlebih dahulu.")
        elif counts["WARN"]:
            print("Tidak ada FAIL. Tinjau setiap WARN: perbaiki, atau catat alasan menerimanya di docs/04-kualitas.md.")
        else:
            print("Semua pemeriksaan otomatis lulus. Ini bukan pengganti review manual dan tes.")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
