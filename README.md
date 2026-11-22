# Product Engineer

Skill untuk agent AI yang mengubah ide mentah menjadi produk software nyata yang **siap dipakai publik**: rencana lengkap, arsitektur, kode yang aman, tes, review, kesiapan legal/rilis, deploy, dan serah terima.

Dibuat untuk orang yang **tidak mau mengurus hal teknis**. Kamu cukup membawa ide dan penilaian produk; agent yang mengurus sisanya.

```
Ide → Rencana → Fondasi → Bangun → Verifikasi → Siap publik → Deploy → Serah terima
 G0      G1        G2       G3        G4          G5          G6
```

## Masalah yang diselesaikan

Agent coding biasa langsung menulis kode. Hasilnya sering:

- fitur melebar tanpa batas karena tidak ada non-goals,
- keputusan teknologi diambil tanpa alasan yang bisa dipertanggungjawabkan,
- tidak ada tes, tidak ada rollback, tidak ada dokumentasi,
- user tidak tahu cara menjalankan atau merawat hasilnya,
- biaya bulanan baru ketahuan setelah tagihan datang,
- produk "jadi" tapi tidak siap publik: tanpa kebijakan privasi, webhook pembayaran tidak diverifikasi, ditolak store, atau secret bocor di repo.

Hasilnya harus terasa dikerjakan developer senior, bukan AI generik: teknologi terkini yang matang, sistem UI dengan token desain, teks yang spesifik, dan kode tanpa pola khas AI (lihat `references/anti-ai-slop.md`).

Skill ini memaksa urutan kerja developer profesional: **pahami → rencanakan → bangun sedikit → buktikan → siapkan rilis → deploy → serahkan**. Setiap fase punya gerbang (G0–G6) yang hanya lulus dengan bukti nyata, dan semua dokumennya bisa dibaca orang non-teknis.

Ketatnya pemeriksaan menyesuaikan **tingkat risiko** produk:

| Tingkat | Ciri | Contoh |
|---|---|---|
| T1 | Tanpa akun, data pribadi, atau uang | Landing page, kalkulator |
| T2 | Ada akun atau data pribadi | SaaS kecil, aplikasi pencatatan |
| T3 | Uang atau data sensitif | Pembayaran, e-commerce, klinik |

## Yang dilakukan skill

| Fase | Hasil | Gerbang |
|---|---|---|
| 0. Pahami ide | Tujuan, pengguna, batasan, tingkat risiko T1/T2/T3 | G0 |
| 1. Rencana lengkap | 8 dokumen di `docs/`, termasuk threat model, sebelum kode ditulis | G1 |
| 2. Fondasi | Repo, versi terkunci, CI dengan gerbang otomatis, konfigurasi aman | G2 |
| 3. Vertical slice | Fitur inti yang benar-benar bisa dipakai, dikerjakan dengan siklus test-first | G3 |
| 4. Verifikasi & hardening | Tes, OWASP Top 10:2025, performa (Core Web Vitals), WCAG 2.2 AA, uji restore | G4 |
| 5. Siap publik | Legal & privasi (UU PDP, PSE), pembayaran, email, SEO, store, anti-penyalahgunaan | G5 |
| 6. Deploy | CI/CD, secrets, backup, monitoring/SLO, rollback, smoke test di URL nyata | G6 |
| 7. Serah terima | User bisa memakai dan merawat produk, termasuk kalender perawatan | — |

Dokumen yang selalu dibuat:

```
docs/
├── README.md            ringkasan satu halaman: lingkup, stack, biaya, risiko
├── 01-rencana-produk.md masalah, pengguna, MVP, non-goals, acceptance criteria
├── 02-arsitektur.md     stack, diagram, data, API, keamanan, ADR
├── 03-roadmap.md        milestone, vertical slice, estimasi, progres
├── 04-kualitas.md       strategi tes, review, security baseline, performance budget
├── 05-deploy.md         hosting, CI/CD, secrets, backup, monitoring, rollback
├── 06-serah-terima.md   cara pakai, operasi rutin, kalender perawatan, batasan
├── 07-siap-rilis.md     production readiness review: legal, pembayaran, store, keputusan rilis
└── legal/               (dengan --publik) draft kebijakan privasi + syarat & ketentuan
```

## Instalasi

### Sekali perintah (semua CLI yang terdeteksi)

```bash
git clone https://github.com/papertop221/product-engineer-skill.git
cd product-engineer-skill
./install.sh
```

Pilih target tertentu atau uji dulu:

```bash
./install.sh --claude --opencode
./install.sh --dry-run
```

### Manual per CLI

| Agent | Lokasi skill |
|---|---|
| Claude Code | `~/.claude/skills/product-engineer/` |
| OpenCode | `~/.config/opencode/skills/product-engineer/` |
| Codex | `~/.codex/skills/product-engineer/` |
| Antigravity CLI | `~/.gemini/skills/product-engineer/` + daftar di `~/.gemini/config/skills.json` |

Contoh untuk satu agent:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/papertop221/product-engineer-skill.git \
  ~/.claude/skills/product-engineer
```

Untuk Antigravity, tambahkan entri berikut ke `~/.gemini/config/skills.json`:

```json
{
  "entries": [
    { "path": "~/.gemini/skills", "include_only": ["product-engineer"] }
  ]
}
```

### Verifikasi

- **Claude Code**: jalankan `/skills`, skill muncul sebagai `product-engineer`.
- **OpenCode**: mulai sesi baru, skill muncul di daftar available skills; bisa dipanggil dengan `@product-engineer`.
- **Codex**: mulai sesi baru dan minta "skill apa yang tersedia".
- **Antigravity**: mulai sesi baru; skill terdaftar dari `skills.json`.

## Cara memakai

Tidak ada perintah khusus. Bawa ide seperti bicara ke manusia:

```
Aku mau aplikasi catatan sederhana untuk tim kecil, bisa dipakai di HP,
dan datanya jangan hilang. Buatkan sampai bisa dipakai.
```

```
Ini ide bisnisku: warungku perlu sistem pesanan online. Aku tidak paham
teknis, tolong urus semuanya dari rencana sampai online.
```

```
Project-ku sudah jalan. Aku mau tambah fitur langganan bulanan.
Rencanakan dulu, jangan langsung koding.
```

Skill akan menggali sedikit, menulis rencana, meminta persetujuan pada hal yang berdampak bisnis (lingkup, biaya, jadwal), lalu bekerja.

## Batas otonomi

Agent **tidak** akan tanpa izin:

- menghapus data atau menjalankan migrasi yang merusak,
- mengubah DNS, domain, atau akun produksi,
- membelanjakan uang atau mengaktifkan layanan berbayar,
- mengirim kredensial ke layanan pihak ketiga,
- memaksa push, menimpa riwayat git, atau menghapus repo.

Keputusan bisnis tetap milikmu. Keputusan teknis diambil agent dan dicatat alasannya.

## Isi repo

```
product-engineer-skill/
├── SKILL.md                         alur kerja, gerbang, dan aturan skill
├── install.sh                       installer untuk Claude, OpenCode, Codex, Antigravity
├── assets/templates/
│   ├── docs/                        template 8 dokumen proyek
│   ├── legal/                       draft kebijakan privasi + syarat & ketentuan
│   └── README.md                    template README proyek
├── references/
│   ├── alur-kerja-profesional.md    cara kerja developer profesional secara runtut
│   ├── teknis-modern.md             stack terkini, arsitektur, data, API, React, error handling
│   ├── sistem-ui.md                 sistem UI aplikasi: token, komponen, pola layar, microcopy
│   ├── anti-ai-slop.md              larangan pola generik khas AI + gantinya
│   ├── keamanan.md                  OWASP Top 10:2025, ASVS 5.0, NIST 800-63B-4, LLM Top 10
│   ├── pengujian.md                 strategi tes, kasus tepi, smoke test, bukti
│   ├── standar-kualitas.md          review, aksesibilitas, performa, severity
│   ├── siap-publik.md               legal Indonesia, pembayaran, email, SEO, store
│   ├── panduan-stack.md             cara memilih stack dan layanan
│   └── panduan-deploy.md            CI/CD, backup, monitoring/SLO, rollback, perawatan
└── scripts/
    ├── scaffold_docs.py             pembuat docs/ otomatis
    ├── audit_rilis.py               pemeriksaan otomatis kesiapan rilis
    └── cek_slop.py                  deteksi sinyal AI slop di UI, teks, dan kode
```

### Scaffold dokumen

```bash
python3 scripts/scaffold_docs.py /path/ke/project --nama "Catatanku"
python3 scripts/scaffold_docs.py /path/ke/project --nama "Catatanku" --publik   # + draft legal
python3 scripts/scaffold_docs.py /path/ke/project --nama "Catatanku" --dry-run
python3 scripts/scaffold_docs.py /path/ke/project --nama "Catatanku" --force --no-readme
```

### Cek AI slop

Mendeteksi sinyal hasil yang "terasa dibuat AI": gradasi ungu, teks bergradasi, glassmorphism berlebihan, emoji sebagai ikon, frasa klise ("solusi terdepan", "seamless"), konten/angka palsu, komentar narasi, catch kosong, `any`, API usang (moment, CRA, `middleware.ts` di Next 16, `tailwind.config` di v4), library ganda, dan pesan commit tidak informatif. Hasilnya sinyal untuk ditinjau, bukan vonis.

```bash
python3 scripts/cek_slop.py /path/ke/project
python3 scripts/cek_slop.py /path/ke/project --ketat   # kode keluar 1 jika ada WARN (untuk CI)
```

### Audit kesiapan rilis

Memeriksa secret yang bocor, `.env`/kunci privat yang ikut ter-commit, lockfile, versi runtime, tes, CI, dan dokumen. Skrip ini tidak mengubah file apa pun dan memberi kode keluar 1 jika ada FAIL, sehingga bisa dipasang di CI.

```bash
python3 scripts/audit_rilis.py /path/ke/project
python3 scripts/audit_rilis.py /path/ke/project --publik          # + legal, siap-rilis, security.txt
python3 scripts/audit_rilis.py /path/ke/project --jalankan-audit  # + npm/pnpm audit, pip-audit, cargo audit, govulncheck, gitleaks bila terpasang
python3 scripts/audit_rilis.py /path/ke/project --json
```

## Uninstall

```bash
rm -rf ~/.claude/skills/product-engineer \
       ~/.config/opencode/skills/product-engineer \
       ~/.codex/skills/product-engineer \
       ~/.gemini/skills/product-engineer
```

Lalu hapus entri `~/.gemini/skills` dari `~/.gemini/config/skills.json` bila sudah tidak dipakai.

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
