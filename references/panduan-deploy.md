# Panduan Deploy dan Operasional

Tujuan deploy bukan sekadar "kode berjalan di server", tetapi **produk bisa dipakai dengan aman, bisa dipulihkan, dan bisa dirawat**.

## 1. Sebelum deploy

- [ ] Build produksi berhasil.
- [ ] Tes, lint, dan type check lulus.
- [ ] Environment variables lengkap.
- [ ] Secret tidak ada di git/log.
- [ ] Migrasi database diuji di staging.
- [ ] Backup sebelum migrasi berisiko.
- [ ] Smoke test staging lulus.
- [ ] Rollback plan jelas.
- [ ] Monitoring dan alert aktif.
- [ ] Biaya dan kepemilikan akun jelas.
- [ ] User tahu apa yang akan berubah.

## 2. Environment

Pisahkan minimal:

- **Lokal:** data contoh, aman untuk eksperimen.
- **Staging:** mirip produksi, untuk uji sebelum rilis.
- **Produksi:** data asli, akses terbatas.

Jangan memakai database produksi untuk pengujian. Jangan menyalin data pribadi produksi ke staging tanpa anonimisasi.

## 3. CI/CD

Pipeline minimum (urutan = urutan gagal tercepat):

1. Install dependency dari lockfile (`npm ci`, `uv sync --locked`, `cargo build --locked`).
2. Format check + lint.
3. Type check (bila ada).
4. Tes unit + integration.
5. Build artefak produksi.
6. Audit dependency + secret scan.
7. Deploy staging (otomatis dari `main`) → smoke test otomatis.
8. Deploy produksi (manual/approval untuk T2/T3) memakai **artefak yang sama** dengan staging.

Aturan:

- Jangan deploy dari laptop jika CI tersedia.
- Jangan menyimpan secret di file pipeline; gunakan secret store platform.
- Jangan melewati tes untuk "cepat".
- Token CI dengan izin minimum; versi action pihak ketiga di-pin.
- Catat versi/commit yang di-deploy; tag rilis produksi (`v1.2.0`).
- Lindungi branch `main`: CI wajib hijau sebelum merge.

Contoh GitHub Actions untuk project Node (sesuaikan untuk ekosistem lain; cek versi action terbaru, lalu pin ke commit SHA untuk T2/T3):

```yaml
name: ci
on:
  push: { branches: [main] }
  pull_request:
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with: { node-version-file: .nvmrc, cache: npm }
      - run: npm ci
      - run: npm run format:check
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test
      - run: npm run build
      - run: npm audit --omit=dev --audit-level=high
```

Untuk Python, ganti langkahnya dengan `uv sync --locked`, `ruff format --check`, `ruff check`, `mypy`, `pytest`, dan `pip-audit`. Untuk Rust: `cargo fmt --check`, `cargo clippy -- -D warnings`, `cargo test --locked`, dan `cargo audit`.

### Strategi rilis

- **Perubahan kecil dan sering** lebih aman daripada rilis besar yang jarang.
- **Feature flag** untuk fitur yang belum siap atau berisiko; bisa dimatikan tanpa deploy ulang.
- **Bertahap** bila platform mendukung: canary/persentase kecil → pantau error rate → naikkan.
- **Migrasi database expand/contract**: (1) tambah kolom/tabel baru yang kompatibel, (2) deploy kode yang menulis ke keduanya, (3) migrasi data, (4) deploy kode yang hanya membaca yang baru, (5) hapus yang lama di rilis berikutnya. Jangan pernah menghapus atau mengganti nama kolom dalam deploy yang sama dengan kode yang masih memakainya.

## 4. Secrets

- Simpan di secret manager platform, bukan di repo.
- `.env.example` hanya berisi nama variabel dan contoh nilai palsu.
- Jangan pernah menulis secret di chat, screenshot, log, atau pesan error.
- Batasi akses secret ke orang yang membutuhkan.
- Siapkan rotasi jika secret bocor.
- Hapus secret dari git history jika pernah ter-commit; mengganti nilainya saja tidak cukup.

## 5. Database dan migrasi

- Gunakan migrasi berversi.
- Uji migrasi di staging dengan data mirip produksi.
- Backup sebelum migrasi yang mengubah/menghapus data.
- Siapkan rollback atau migrasi maju (forward fix).
- Jangan mengedit skema produksi manual tanpa catatan.
- Untuk perubahan besar, pertimbangkan migrasi bertahap (expand/contract).

## 6. Backup dan restore

Backup belum berguna sampai pernah di-restore.

- Tentukan apa yang di-backup: database, file upload, konfigurasi.
- Tentukan frekuensi dan retensi.
- Enkripsi backup.
- Simpan di lokasi berbeda dari server produksi.
- Uji restore secara berkala.
- Catat siapa yang bisa mengakses backup.
- Dokumentasikan langkah restore.

## 7. Domain, DNS, dan SSL

- Pastikan domain dan akun registrar dimiliki user.
- Catat di mana DNS dikelola.
- Aktifkan HTTPS dan perpanjangan otomatis.
- Uji redirect HTTP → HTTPS.
- Catat masa berlaku domain/SSL.
- Jangan mengubah DNS tanpa memahami dampaknya.

## 8. Monitoring, logging, dan SLO

Minimal pantau empat sinyal emas: **traffic, error rate, latency, dan saturasi** (CPU/memori/koneksi DB/kuota). Tambahkan juga:

- Ketersediaan dari luar (uptime check ke health endpoint dan halaman utama).
- Error aplikasi dengan stack trace di server (misalnya Sentry), bukan di browser user.
- Kegagalan job/webhook/email.
- Biaya per layanan.

SLO sederhana untuk MVP (tulis di `docs/05-deploy.md`):

| SLO | Target contoh | Alert jika |
|---|---|---|
| Ketersediaan | 99,5% request sukses / 30 hari | Error rate 5xx > 2% selama 5 menit |
| Latency | p95 < 500 ms | p95 > 1 dtk selama 10 menit |
| Pembayaran (T3) | 100% webhook terverifikasi diproses | Ada webhook gagal > 3× berturut |
| Job terjadwal | Selesai sesuai jadwal | Job tidak berjalan > 2× interval |

Praktik:

- Log terstruktur (JSON) dengan level, waktu UTC, request ID, dan user ID (bukan email/nama).
- Jangan log password, token, OTP, nomor kartu, atau PII lengkap.
- Alert harus bisa ditindaklanjuti dan dikirim ke kanal yang benar-benar dibaca user/pengelola (email/Telegram/WhatsApp). Hindari alert banjir.
- Retensi log ditentukan, misalnya 14–30 hari untuk log aplikasi dan lebih lama untuk audit log.

## 9. Rollback

Siapkan sebelum deploy:

- Versi sebelumnya bisa di-deploy ulang.
- Migrasi database punya rencana rollback/forward fix.
- Feature flag bisa mematikan fitur bermasalah.
- Data yang berubah selama insiden bisa diidentifikasi.
- Siapa yang berwenang memutuskan rollback.

Setelah rollback, verifikasi alur utama dan catat penyebabnya.

## 10. Smoke test setelah deploy

- [ ] URL/resource bisa diakses.
- [ ] HTTPS valid.
- [ ] Halaman utama tampil.
- [ ] Login/logout bekerja (bila ada).
- [ ] Alur utama selesai.
- [ ] Data tersimpan dan terbaca.
- [ ] Error yang diharapkan tampil benar.
- [ ] Tidak ada error kritis di log.
- [ ] Monitoring menerima data.
- [ ] Job/webhook berjalan (bila ada).

## 11. Deploy per jenis produk

### Web app

- Periksa build, environment, domain, SSL, dan asset.
- Uji di browser dan ukuran layar berbeda.
- Pastikan redirect dan 404 benar.

### API/backend

- Uji health check.
- Uji auth dan rate limit.
- Uji error format.
- Pastikan migrasi sudah jalan.
- Pantau latency dan error rate.

### Mobile

- Build release, bukan debug.
- Tanda tangani dengan signing key yang aman.
- Uji instalasi di perangkat nyata.
- Siapkan proses review store.
- Siapkan crash reporting.
- Catat versi minimum OS.

### Bot

- Daftarkan webhook dengan URL HTTPS.
- Validasi secret/signature.
- Uji retry dan idempotensi.
- Pastikan proses selalu hidup atau platform retry.
- Pantau rate limit dan error platform.

### Automasi

- Uji `dry-run`.
- Pastikan idempotensi.
- Siapkan notifikasi gagal.
- Catat jadwal dan zona waktu.
- Simpan secret di scheduler, bukan di script.

### Desktop/CLI

- Build untuk platform target.
- Uji di mesin bersih.
- Siapkan installer/distribusi.
- Pertimbangkan code signing dan auto-update.
- Catat cara uninstall dan menghapus data.

## 12. Biaya

- Catat semua layanan berbayar dan batas free tier.
- Aktifkan budget alert.
- Pantau penggunaan mingguan pada awal launch.
- Hindari resource yang mudah membengkak tanpa batas (fungsi, storage, API AI).
- Siapkan rencana jika biaya naik.

## 13. Kepemilikan akun

- Akun layanan harus dimiliki user.
- Jangan membuat akun dengan identitas pribadi AI.
- Catat email pemilik, metode pembayaran, dan akses darurat.
- Simpan kredensial di password manager/secret manager.
- Berikan akses minimum yang diperlukan.

## 14. Runbook insiden

1. Tentukan dampak: siapa yang terdampak, fitur apa, data apa.
2. Cek perubahan terakhir dan monitoring.
3. Hentikan pendarahan: rollback, matikan fitur, atau batasi akses.
4. Beri tahu user dengan bahasa manusia.
   Jika data pribadi terdampak: siapkan pemberitahuan tertulis ke subjek data dan otoritas paling lambat 3 × 24 jam (UU PDP; lihat `siap-publik.md`). Keputusan dan pengirimannya dilakukan pemilik produk.
5. Perbaiki akar masalah.
6. Verifikasi pemulihan.
7. Catat penyebab, perbaikan, dan pencegahan.
8. Tambahkan tes/monitoring.

## 15. Serah terima operasional

- [ ] README berisi cara install, dev, test, build, deploy.
- [ ] Dokumen deploy berisi environment, secret, backup, rollback.
- [ ] User memegang akun dan kredensial.
- [ ] Operasi rutin dijelaskan.
- [ ] Batasan dan risiko dicatat.
- [ ] Kontak dukungan jelas.
- [ ] Langkah berikutnya disepakati.

## 16. Kalender perawatan

Produk yang tidak dirawat akan rusak sendiri: dependency usang, sertifikat/domain kedaluwarsa, dan aturan store berubah. Sepakati kalender ini dengan user dan tulis di `docs/06-serah-terima.md`:

| Frekuensi | Tugas |
|---|---|
| Harian (otomatis) | Backup, uptime check, alert error |
| Mingguan | Cek error baru dan biaya; proses PR update dependency keamanan |
| Bulanan | Update dependency minor; review akses akun; cek kuota/free tier |
| Triwulan | **Uji restore backup**; rotasi secret penting; review log audit; cek header keamanan dan skor performa |
| Tahunan | Perpanjangan domain; update runtime/framework mayor (LTS); naikkan target API Android (sekitar Agustus) dan SDK iOS (sekitar April); tinjau kebijakan privasi dan syarat; tinjau biaya hosting |
| Saat ada advisori | Dependency kritis ≤ 7 hari, tinggi ≤ 30 hari |

