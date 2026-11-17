# Deploy dan Operasional — {{NAMA_PRODUK}}

> **Status:** draft · **Pemilik:** {{PEMILIK}} · **Terakhir diperbarui:** {{TANGGAL}}

## 1. Environment

| Environment | URL / lokasi | Tujuan | Data yang dipakai |
|---|---|---|---|
| Lokal |  | Pengembangan | Data contoh |
| Staging |  | Uji sebelum rilis | Data uji |
| Produksi |  | User nyata | Data asli |

## 2. Hosting dan biaya

| Layanan | Fungsi | Paket | Biaya bulanan | Batas |
|---|---|---|---|---|
|  |  |  |  |  |
| **Total** |  |  |  |  |

- **Alasan memilih hosting ini:**
- **Cara keluar/migrasi:**
- **Batas free tier yang perlu diawasi:**

## 3. CI/CD

| Tahap | Perintah | Kapan |
|---|---|---|
| Install |  |  |
| Lint |  |  |
| Type check |  |  |
| Test |  |  |
| Build |  |  |
| Deploy staging |  |  |
| Deploy produksi |  |  |

- **Branch strategi:**
- **Siapa yang bisa deploy:**
- **Approval yang diperlukan:**

## 4. Secrets dan environment variables

| Nama | Fungsi | Disimpan di | Pemilik | Rotasi |
|---|---|---|---|---|
|  |  |  |  |  |

**Aturan:** secret asli tidak boleh masuk git, log, screenshot, atau chat. `.env.example` hanya berisi nama variabel.

## 5. Database dan migrasi

- **Jenis database:**
- **Lokasi:**
- **Cara menjalankan migrasi:**
- **Cara rollback migrasi:**
- **Aturan:** backup sebelum migrasi berisiko; jangan edit data produksi manual tanpa backup.

## 6. Backup dan restore

- **Apa yang di-backup:**
- **Frekuensi:**
- **Retensi:**
- **Lokasi:**
- **Enkripsi:**
- **Cara restore:**
- **Terakhir diuji restore:**
- **Pemilik proses:**

## 7. Domain, DNS, dan SSL

- **Domain:**
- **Registrar dan pemilik akun:**
- **DNS:**
- **SSL:** otomatis / manual
- **Masa berlaku:**
- **Cara memperbarui:**

## 8. Monitoring, logging, dan alert

| Yang dipantau | Alat | Ambang alert | Penerima |
|---|---|---|---|
| Error aplikasi |  |  |  |
| Ketersediaan |  |  |  |
| Performa |  |  |  |
| Biaya |  |  |  |

- **Health check:**
- **Log disimpan di:**
- **Data yang tidak boleh di-log:**

## 9. Rollback

- **Kapan rollback:**
- **Langkah rollback aplikasi:**
- **Langkah rollback database:**
- **Verifikasi setelah rollback:**
- **Siapa yang memutuskan:**

## 10. Smoke test setelah deploy

- [ ] URL bisa dibuka dan HTTPS valid.
- [ ] Halaman utama tampil.
- [ ] Login/logout bekerja (bila ada).
- [ ] Alur utama bisa diselesaikan.
- [ ] Data tersimpan dan terbaca kembali.
- [ ] Error yang diharapkan tampil dengan benar.
- [ ] Tidak ada error kritis di log.
- [ ] Monitoring menerima data.

## 11. Runbook insiden

1. Pastikan dampak dan cakupan masalah.
2. Cek monitoring, log, dan perubahan terakhir.
3. Jika perlu, rollback.
4. Beri tahu user dengan bahasa manusia: apa yang terjadi, dampaknya, dan tindakan berikutnya.
5. Catat penyebab dan perbaikan.
6. Tambahkan tes/monitoring agar tidak terulang.

## 12. Akun dan kepemilikan

| Layanan | Akun/email | Pemilik | Akses diberikan ke | Catatan |
|---|---|---|---|---|
|  |  |  |  |  |

**Aturan:** akun layanan harus dimiliki user, bukan identitas pribadi AI. Kredensial disimpan di password manager/secret manager, bukan hanya di percakapan.

## 13. Batas biaya dan pengawasan

- **Budget bulanan:**
- **Ambang peringatan:**
- **Cara memantau:**
- **Tindakan jika melewati budget:**

## 14. Catatan operasional lain

-
