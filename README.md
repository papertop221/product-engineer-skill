# Product Engineer

Skill untuk agent AI yang mengubah ide mentah menjadi produk software nyata: rencana lengkap, arsitektur, kode, tes, review, deploy, dan serah terima.

Dibuat untuk orang yang **tidak mau mengurus hal teknis**. Kamu cukup membawa ide dan penilaian produk; agent yang mengurus sisanya.

```
Ide  →  Rencana  →  Fondasi  →  Bangun  →  Review  →  Deploy  →  Serah terima
```

## Masalah yang diselesaikan

Agent coding biasa langsung menulis kode. Hasilnya sering:

- fitur melebar tanpa batas karena tidak ada non-goals,
- keputusan teknologi diambil tanpa alasan yang bisa dipertanggungjawabkan,
- tidak ada tes, tidak ada rollback, tidak ada dokumentasi,
- user tidak tahu cara menjalankan atau merawat hasilnya,
- biaya bulanan baru ketahuan setelah tagihan datang.

Skill ini memaksa urutan yang benar: **pahami → rencanakan → bangun sedikit → buktikan → deploy → serahkan**, dengan dokumen yang bisa dibaca manusia non-teknis.

## Yang dilakukan skill

| Fase | Hasil |
|---|---|
| 0. Terima ide | Tujuan, pengguna, batasan, dan asumsi yang eksplisit |
| 1. Rencana lengkap | 7 dokumen proyek di `docs/` sebelum satu baris kode ditulis |
| 2. Fondasi | Repo, stack paling sederhana yang cukup, konfigurasi aman |
| 3. Vertical slice | Fitur inti yang benar-benar bisa dipakai, bukan mockup |
| 4. Review & hardening | Tes, security check, performa, aksesibilitas |
| 5. Deploy | CI/CD, secrets, backup, monitoring, rollback, smoke test |
| 6. Serah terima | User bisa memakai dan merawat produk tanpa agent |

Dokumen yang selalu dibuat:

```
docs/
├── README.md            ringkasan satu halaman: lingkup, stack, biaya, risiko
├── 01-rencana-produk.md masalah, pengguna, MVP, non-goals, acceptance criteria
├── 02-arsitektur.md     stack, diagram, data, API, keamanan, ADR
├── 03-roadmap.md        milestone, vertical slice, estimasi, progres
├── 04-kualitas.md       strategi tes, review, security baseline, performance budget
├── 05-deploy.md         hosting, CI/CD, secrets, backup, monitoring, rollback
└── 06-serah-terima.md   cara pakai, operasi rutin, kredensial, batasan
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
├── SKILL.md                    definisi dan alur kerja skill
├── install.sh                  installer untuk Claude, OpenCode, Codex, Antigravity
├── assets/templates/           template 7 dokumen proyek + README proyek
├── references/
│   ├── panduan-stack.md        cara memilih stack dan layanan
│   ├── standar-kualitas.md     standar kode, tes, dan review
│   └── panduan-deploy.md       pola deploy, backup, dan rollback
└── scripts/scaffold_docs.py    pembuat docs/ otomatis
```

### Scaffold dokumen

```bash
python3 scripts/scaffold_docs.py /path/ke/project --name "Catatanku"
python3 scripts/scaffold_docs.py /path/ke/project --dry-run
python3 scripts/scaffold_docs.py /path/ke/project --force --no-readme
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
