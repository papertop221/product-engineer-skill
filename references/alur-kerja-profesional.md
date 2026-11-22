# Alur Kerja Developer Profesional

Rangkuman cara kerja tim engineering profesional, disusun dari praktik umum industri: NIST SSDF (SP 800-218), OWASP SAMM/ASVS, Google SRE, riset DORA, trunk-based development, Conventional Commits, dan Semantic Versioning. Pakai sebagai "cara kerja default"; sesuaikan kedalamannya dengan tingkat risiko produk (T1/T2/T3).

## 1. Prinsip yang membedakan profesional dari amatir

| Amatir | Profesional |
|---|---|
| Langsung menulis kode | Memahami masalah, menulis kriteria sukses, baru menulis kode |
| "Di laptopku jalan" | Bisa dibangun ulang dari nol dengan satu perintah, dan CI membuktikannya |
| Tes ditulis kalau sempat | Tes adalah bagian dari definisi selesai |
| Keamanan di akhir | Keamanan dirancang sejak awal (*shift left*) dan diverifikasi di setiap gerbang |
| Perubahan besar sekaligus | Perubahan kecil, sering, dan bisa dibatalkan |
| Deploy = selesai | Selesai = terverifikasi di produksi, terpantau, dan bisa di-rollback |
| Mengandalkan ingatan | Mengandalkan dokumen, checklist, dan otomasi |
| Menyembunyikan masalah | Mencatat risiko dan utang teknis secara terbuka |

Riset DORA 2025 menemukan bahwa AI bekerja sebagai **penguat**: tim dengan umpan balik cepat, perubahan kecil, dan pengujian kuat menjadi makin baik, sedangkan tim tanpa itu justru makin tidak stabil. Karena itu, makin banyak kode yang ditulis AI, makin penting gerbang kualitas otomatis.

## 2. Siklus hidup pengembangan (SDLC) singkat

```
Pahami → Spesifikasi → Rancang → Bangun (test-first) → Verifikasi → Rilis → Operasi → Belajar
   ↑                                                                               │
   └──────────────────────────── umpan balik ──────────────────────────────────────┘
```

Pemetaan ke kelompok praktik NIST SSDF:

| Kelompok SSDF | Artinya untuk proyek ini | Di mana dilakukan |
|---|---|---|
| **PO** — Siapkan organisasi | Tetapkan tingkat risiko, standar, tooling, dan gerbang | Fase 0–2 |
| **PS** — Lindungi software | Repo, secret, signing key, dan integritas build terlindungi | Fase 2, 6 |
| **PW** — Hasilkan software yang aman | Threat model, kode aman, review, tes, konfigurasi aman | Fase 1–4 |
| **RV** — Tanggapi kerentanan | Audit dependency rutin, triase temuan, perbaikan, dan pencegahan | Fase 4, 7 |

## 3. Sebelum menulis kode

### 3.1 Pahami masalahnya

- Siapa penggunanya, apa yang mereka coba capai, dan bagaimana mereka melakukannya sekarang.
- Apa hasil minimal yang sudah berguna.
- Apa yang **mahal jika salah**: uang, data, akses, reputasi.

### 3.2 Tulis kriteria yang bisa diuji

Format: **Diberikan** [kondisi] **Ketika** [aksi] **Maka** [hasil yang bisa diamati].

Setiap user story minimal punya:

- 1 kriteria happy path,
- 1 kriteria gagal (input salah, tidak berizin, layanan luar mati),
- kasus tepi yang relevan (kosong, duplikat, batas maksimum, bersamaan).

### 3.3 Kebutuhan non-fungsional (NFR)

Tulis secara eksplisit, walau singkat:

| NFR | Contoh target MVP |
|---|---|
| Ketersediaan | 99,5% per bulan (≈3,6 jam gangguan) cukup untuk MVP |
| Performa | Halaman utama LCP ≤ 2,5 dtk di HP kelas menengah; API p95 ≤ 500 ms |
| Keamanan | Sesuai tingkat risiko di `keamanan.md` |
| Privasi | Hanya kumpulkan data yang benar-benar dipakai |
| Aksesibilitas | WCAG 2.2 AA untuk UI publik |
| Pemulihan | RPO (data yang boleh hilang) ≤ 24 jam; RTO (waktu pulih) ≤ 4 jam |
| Biaya | ≤ Rp X/bulan pada Y user |

### 3.4 Rancang dan catat keputusan

- Untuk keputusan yang sulit dibatalkan (database, auth, hosting, struktur data inti), tulis **ADR**: konteks → keputusan → alasan → konsekuensi → alternatif yang ditolak.
- Buat threat model ringan (lihat `keamanan.md`) sebelum membangun fitur yang menyentuh auth, uang, upload, atau data pribadi.
- Rancang kontrak lebih dulu: skema data, endpoint, format error. Kontrak yang jelas mencegah kerja ulang.

## 4. Saat menulis kode

### 4.1 Urutan kerja untuk satu perubahan

1. Buat branch pendek dari `main` (atau langsung di `main` untuk proyek solo kecil, asalkan gerbang lokal dijalankan).
2. Tulis tes yang gagal untuk perilaku baru atau bug.
3. Tulis kode minimal sampai tes lulus.
4. Refactor selagi tes hijau.
5. Jalankan seluruh gerbang lokal.
6. Review diff sendiri dengan checklist.
7. Commit dengan pesan yang jelas.
8. Push → CI → review → merge → deploy.

Satu perubahan sebaiknya bisa di-review dalam ≤ 30 menit (sekitar < 400 baris diff). Pecah perubahan yang lebih besar.

### 4.2 Gerbang lokal (sebelum commit/push)

Jalankan dalam urutan ini; berhenti saat ada yang gagal:

```text
format --check → lint → type check → unit test → integration test → build → audit dependency → secret scan
```

Contoh per ekosistem (pakai yang sesuai project):

| Ekosistem | Format | Lint | Type | Test | Audit |
|---|---|---|---|---|---|
| Node/TS | `prettier --check .` | `eslint .` | `tsc --noEmit` | `vitest run` / `node --test` | `npm audit --omit=dev` |
| Python | `ruff format --check` | `ruff check` | `mypy` / `pyright` | `pytest` | `pip-audit` |
| Rust | `cargo fmt --check` | `cargo clippy -- -D warnings` | (compiler) | `cargo test` | `cargo audit` |
| Go | `gofmt -l .` | `go vet ./...` / `staticcheck` | (compiler) | `go test ./...` | `govulncheck ./...` |

Secret scan: `gitleaks detect` bila tersedia; jika tidak, `scripts/audit_rilis.py` menyediakan pemeriksaan dasar.

### 4.3 Git dan commit

- **Trunk-based:** `main` selalu hijau dan bisa di-deploy. Branch fitur berumur pendek (jam sampai beberapa hari).
- **Conventional Commits:** `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `perf:`, `security:`. Baris pertama ≤ 72 karakter; isi menjelaskan **kenapa**.
- Satu commit = satu perubahan logis. Jangan mencampur refactor besar dengan fitur.
- Jangan pernah meng-commit secret, `.env`, data user, atau file build. Jika terlanjur, **rotasi secret-nya**; menghapus dari history saja tidak cukup.
- Jangan `force-push` ke branch bersama.

### 4.4 Versi dan rilis

- **Semantic Versioning:** `MAJOR.MINOR.PATCH`. Naikkan MAJOR untuk perubahan yang merusak kompatibilitas, MINOR untuk fitur baru, dan PATCH untuk perbaikan.
- Tag setiap rilis produksi (`v1.2.0`) dan simpan `CHANGELOG.md` yang ditulis untuk manusia.
- Rilis harus **reproducible**: commit + lockfile + versi runtime menghasilkan build yang sama.

## 5. Review kode

Review mencari masalah yang tidak tertangkap tes. Urutan prioritas:

1. **Kebenaran:** apakah kode melakukan yang diminta, termasuk saat gagal?
2. **Keamanan:** akses, input, secret, injeksi, dan data pribadi.
3. **Data:** integritas, transaksi, migrasi, dan kemungkinan kehilangan data.
4. **Desain:** apakah ada cara yang lebih sederhana? Apakah ada abstraksi prematur?
5. **Tes:** apakah tes benar-benar membuktikan perilakunya, bukan sekadar menaikkan coverage?
6. **Keterbacaan:** nama, struktur, dan komentar "kenapa".
7. Gaya: serahkan ke formatter/linter, jangan diperdebatkan manual.

Untuk produk T2/T3, review dilakukan oleh pihak **terpisah** dari penulis, misalnya subagent reviewer atau skill `code-review`/`security-review`. Jika tidak tersedia, beri jeda lalu review dengan sikap "aku mencari kesalahan".

## 6. Integrasi dan pengiriman berkelanjutan (CI/CD)

- Setiap push menjalankan gerbang otomatis yang sama dengan gerbang lokal.
- Build artefak sekali, lalu promosikan artefak yang sama dari staging ke produksi. Jangan build ulang untuk produksi.
- Deploy produksi lewat pipeline, dengan persetujuan manual untuk T2/T3.
- Secret CI di secret store platform; izin token CI seminimal mungkin (`permissions: contents: read`).
- Versi action/plugin pihak ketiga di-pin (idealnya ke commit SHA).

## 7. Operasi (setelah rilis)

- **Observability:** log terstruktur, metrik (traffic, error rate, latency, saturasi), dan health check.
- **SLO sederhana:** misalnya "99,5% request sukses per 30 hari" dan "p95 < 500 ms". Alert hanya untuk hal yang perlu tindakan.
- **Insiden:** hentikan dampaknya dulu (rollback/feature flag), komunikasikan, perbaiki akar masalah, lalu tulis postmortem tanpa menyalahkan.
- **Perawatan:** update dependency berkala, tanggapi advisori keamanan, uji restore, dan rotasi secret.

## 8. Metrik kesehatan pengiriman (DORA)

Ukur secara kasar sekalipun proyeknya kecil. Metrik ini menunjukkan apakah proses kerja sehat:

| Metrik | Arti | Arah yang baik |
|---|---|---|
| Deployment frequency | Seberapa sering rilis ke produksi | Sering (harian/mingguan) |
| Lead time for changes | Commit → produksi | Pendek (jam/hari) |
| Change failure rate | % deploy yang menyebabkan masalah | Rendah |
| Failed deployment recovery time | Waktu pulih dari deploy gagal | Pendek (menit/jam) |

Perubahan kecil + gerbang otomatis + rollback cepat memperbaiki keempatnya sekaligus.

## 9. Bekerja sebagai agent AI: aturan tambahan

- **Verifikasi keberadaan.** Sebelum `install`, pastikan package ada di registry resmi, namanya benar, terawat, dan dipakai luas. Sebelum memanggil API library, pastikan fungsinya ada di versi yang terpasang.
- **Baca, jangan menebak.** Untuk konfigurasi platform (hosting, auth, payment), ikuti dokumentasi resmi terbaru, karena perilakunya sering berubah.
- **Jalankan, jangan berasumsi.** Setiap klaim "berhasil" harus didukung output perintah yang benar-benar dijalankan di sesi ini.
- **Lingkungan terbatas** (misalnya Termux/Android): cek tool yang tersedia lebih dulu. Jika gerbang tertentu tidak bisa dijalankan lokal (Docker, browser), jalankan di CI dan katakan dengan jujur bahwa gerbang itu hanya dibuktikan di CI.
- **Jangan menyentuh di luar lingkup.** Perubahan yang tidak diminta = risiko yang tidak diminta.
- **Tinggalkan jejak.** Keputusan → ADR, bukti → log verifikasi, risiko → daftar risiko.
