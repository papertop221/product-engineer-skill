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

Pipeline minimum:

1. Install dependency.
2. Lint/format check.
3. Type check (bila ada).
4. Test.
5. Build.
6. Deploy staging (opsional otomatis).
7. Deploy produksi (manual/approval).

Aturan:

- Jangan deploy dari laptop jika CI tersedia.
- Jangan menyimpan secret di file pipeline.
- Jangan melewati tes untuk "cepat".
- Catat versi/commit yang di-deploy.

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

## 8. Monitoring dan logging

Minimal pantau:

- Ketersediaan (uptime).
- Error aplikasi.
- Performa respons.
- Penggunaan resource.
- Biaya.
- Kegagalan job/webhook.

Praktik:

- Log terstruktur.
- Sertakan request ID/korelasi bila memungkinkan.
- Jangan log password, token, atau PII.
- Alert harus bisa ditindaklanjuti; hindari alert banjir.
- Siapkan jalur untuk melihat log dengan cepat saat insiden.

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
