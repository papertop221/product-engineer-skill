# Standar Kualitas — {{NAMA_PRODUK}}

> **Status:** draft · **Pemilik:** {{PEMILIK}} · **Terakhir diperbarui:** {{TANGGAL}}

## 1. Strategi tes

| Jenis | Cakupan | Alat | Kapan dijalankan |
|---|---|---|---|
| Unit | Logika murni, validasi, perhitungan |  | Setiap perubahan |
| Integration | API + database, alur antar komponen |  | Sebelum merge |
| End-to-end | Alur user utama |  | Sebelum deploy |
| Manual | UX, perangkat, kasus sulit diotomasi |  | Sebelum launch |

**Prinsip:** tes pada jalur yang kalau rusak membuat user kehilangan data, uang, atau akses. Jangan mengejar angka coverage.

## 2. Critical paths yang wajib diuji

- [ ] Daftar/login/logout (bila ada).
- [ ] Alur utama produk dari awal sampai akhir.
- [ ] Membuat, membaca, mengubah, menghapus data inti.
- [ ] Pembayaran/transaksi (bila ada).
- [ ] Izin: user biasa vs admin.
- [ ] Input kosong, salah, terlalu besar, dan berulang.
- [ ] Jaringan putus/timeout.
- [ ] Data kosong dan data sangat banyak.
- [ ] Backup dan restore.

## 3. Checklist review

### Correctness
- [ ] Kode melakukan apa yang diminta, termasuk kasus gagal.
- [ ] Tidak ada logika yang hanya benar di happy path.
- [ ] Batas nilai (0, negatif, kosong, maksimum) ditangani.
- [ ] Tidak ada race condition pada operasi penting.

### Keamanan
- [ ] Input divalidasi; output di-encode.
- [ ] Query berparameter; tidak ada string concat untuk SQL/shell/path.
- [ ] Otorisasi diperiksa di server.
- [ ] Secret tidak ada di repo/log/chat.
- [ ] Rate limit untuk login dan endpoint publik.
- [ ] File upload dibatasi.
- [ ] Dependency diaudit.

### Data
- [ ] Constraint database sesuai aturan bisnis.
- [ ] Migrasi aman dan bisa diulang.
- [ ] Transaksi dipakai untuk operasi yang harus atomik.
- [ ] Backup tersedia dan restore pernah diuji.
- [ ] Data pribadi diminimalkan dan tidak di-log.

### UX dan aksesibilitas
- [ ] Keadaan loading, kosong, error, dan sukses jelas.
- [ ] Bisa dipakai dengan keyboard.
- [ ] Label, kontras, dan teks alternatif memadai.
- [ ] Responsif di layar kecil.
- [ ] Pesan error membantu, bukan menyalahkan user.

### Performa
- [ ] Tidak ada N+1 query yang jelas.
- [ ] Index ada untuk query penting.
- [ ] Aset besar di-lazy-load/kompresi.
- [ ] Waktu respons masuk budget.

### Maintainability
- [ ] Nama jelas dan konsisten.
- [ ] Tidak ada kode mati atau duplikasi besar.
- [ ] Tidak ada abstraksi untuk kebutuhan imajiner.
- [ ] Dependency yang tidak dipakai dihapus.
- [ ] Dokumentasi diperbarui.

## 4. Security baseline

**Tingkat risiko:** T1 / T2 / T3 — kontrol lengkap per tingkat ada di `references/keamanan.md` skill product-engineer.

| OWASP Top 10:2025 | Kontrol utama di produk ini | Diuji dengan | Status |
|---|---|---|---|
| A01 Broken Access Control | Cek kepemilikan objek di server | Tes lintas user |  |
| A02 Security Misconfiguration | Debug mati, header keamanan, CORS allowlist | `curl -sI` |  |
| A03 Supply Chain | Lockfile, audit dependency | `npm audit` / `pip-audit` / … |  |
| A04 Cryptographic Failures | HTTPS, hash password, enkripsi backup |  |  |
| A05 Injection | Query berparameter, validasi skema, auto-escape |  |  |
| A06 Insecure Design | Aturan bisnis di server, rate limit |  |  |
| A07 Authentication Failures | Auth terkelola / NIST 800-63B-4 |  |  |
| A08 Integrity Failures | Verifikasi webhook, SRI |  |  |
| A09 Logging & Alerting | Log event keamanan tanpa PII, alert |  |  |
| A10 Exceptional Conditions | Fail closed, error handler global, timeout |  |  |

Checklist umum:

- [ ] HTTPS di produksi.
- [ ] Password di-hash dengan Argon2id/bcrypt atau auth terkelola.
- [ ] Session/cookie aman (HttpOnly, Secure, SameSite).
- [ ] CSRF protection untuk aksi yang mengubah data.
- [ ] CORS allowlist, bukan `*` untuk endpoint ber-auth.
- [ ] Validasi dan batas ukuran request.
- [ ] Error produksi tidak membocorkan stack trace.
- [ ] Least privilege untuk database dan cloud.
- [ ] Log tidak berisi password, token, atau PII.
- [ ] Backup terenkripsi.
- [ ] Rencana rotasi secret.

## 5. Aksesibilitas baseline

- [ ] HTML semantik dan heading berurutan.
- [ ] Semua input punya label.
- [ ] Fokus keyboard terlihat.
- [ ] Kontras teks memadai.
- [ ] Gambar bermakna punya teks alternatif.
- [ ] Tombol/target sentuh cukup besar.
- [ ] Tidak ada ketergantungan pada warna saja.
- [ ] Animasi bisa dikurangi.

## 6. Performance budget

| Metrik | Target | Cara ukur |
|---|---|---|
| Waktu muat awal |  |  |
| Waktu respons API |  |  |
| Ukuran bundle |  |  |
| Query database |  |  |

Hanya isi yang relevan. Untuk produk internal sederhana, budget bisa berupa "halaman terasa instan di perangkat user".

## 7. Bug severity dan kebijakan

| Severity | Contoh | Kebijakan |
|---|---|---|
| Kritis | Kehilangan data, kebocoran data, pembayaran salah | Perbaiki sebelum deploy |
| Tinggi | Alur utama gagal, akses tidak sah | Perbaiki sebelum deploy |
| Sedang | Fitur sekunder rusak, workaround ada | Perbaiki di milestone berikutnya |
| Rendah | Kosmetik, teks, edge case jarang | Backlog |

## 8. Release checklist

- [ ] Semua tes lulus.
- [ ] Build produksi berhasil.
- [ ] Migrasi database diuji.
- [ ] Backup sebelum migrasi.
- [ ] Environment variables lengkap.
- [ ] Smoke test staging lulus.
- [ ] Rollback plan jelas.
- [ ] Monitoring aktif.
- [ ] Dokumentasi diperbarui.
- [ ] User diberi tahu apa yang berubah.

## 9. Risiko yang diterima

| Risiko | Alasan diterima | Dampak | Rencana |
|---|---|---|---|
|  |  |  |  |

## 10. Catatan review terakhir

| Tanggal | Reviewer | Temuan | Status |
|---|---|---|---|
|  |  |  |  |

## 11. Log verifikasi

Setiap gerbang dianggap lulus hanya jika ada barisnya di sini. Tulis perintah yang benar-benar dijalankan dan hasilnya.

| Tanggal | Gerbang | Perintah / pemeriksaan | Hasil | Catatan |
|---|---|---|---|---|
|  | G2 | `python3 scripts/audit_rilis.py .` |  |  |
|  | G4 | `python3 scripts/cek_slop.py .` + screenshot review 390/1280px |  |  |
|  |  |  |  |  |

