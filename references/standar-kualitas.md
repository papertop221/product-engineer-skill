# Standar Kualitas

Dokumen ini adalah panduan kerja untuk review, pengujian, keamanan, aksesibilitas, dan performa. Gunakan bagian yang relevan dengan jenis produk; tidak semua poin berlaku untuk semua proyek.

## 1. Cara berpikir tentang kualitas

Kualitas bukan "semua fitur ada". Kualitas berarti:

- Produk melakukan hal yang dijanjikan, termasuk saat ada input aneh dan jaringan buruk.
- Data user tidak hilang, bocor, atau berubah tanpa izin.
- User bisa memahami keadaan aplikasi: loading, kosong, error, sukses.
- Perubahan bisa dirawat tanpa takut merusak sesuatu.
- Biaya operasional dan performa masuk akal untuk kebutuhan.

Fokuskan pengujian pada **jalur yang mahal jika rusak**: uang, data pribadi, akses, dan alur utama.

## 2. Strategi tes per jenis produk

### Web app

- Unit: validasi, perhitungan, transformasi data.
- Integration: route/API + database.
- End-to-end: daftar/login, alur utama, pembayaran bila ada.
- Manual: responsivitas, keyboard, browser umum, keadaan jaringan lambat.

### API/backend

- Unit: aturan bisnis.
- Integration: endpoint + database + auth.
- Contract: skema request/response.
- Manual: rate limit, timeout, error format, idempotensi.

### Mobile

- Unit dan integration seperti web.
- Manual di perangkat nyata: izin, kamera, offline, background, ukuran layar, versi OS.
- Uji instalasi dari build release, bukan hanya debug.

### Bot

- Unit: parsing pesan dan aturan.
- Integration: webhook + database.
- Manual: pesan berulang, pesan sangat panjang, user diblokir, timeout, rate limit.
- Pastikan webhook tervalidasi dan proses bisa retry tanpa menggandakan aksi.

### Automasi

- Uji dengan data contoh dan `dry-run`.
- Pastikan idempotensi: dijalankan dua kali tidak merusak data.
- Siapkan notifikasi jika gagal.
- Catat input, output, dan waktu eksekusi tanpa menyimpan secret.

## 3. Metode review yang efektif

1. **Baca diff, bukan seluruh repo.** Fokus pada perubahan dan efek sampingnya.
2. **Telusuri satu alur dari awal sampai akhir.** Jangan hanya membaca fungsi per fungsi.
3. **Cari kasus yang tidak diuji:** input kosong, negatif, duplikat, sangat besar, akses tanpa izin.
4. **Periksa batas sistem:** validasi input, error dari API luar, timeout, file.
5. **Periksa data:** constraint, transaksi, migrasi, backup.
6. **Periksa keamanan:** auth, otorisasi, secret, query, upload, dependency.
7. **Periksa UX:** loading, kosong, error, sukses, mobile, keyboard.
8. **Simplify pass:** hapus yang tidak perlu, satukan duplikasi, jelaskan yang membingungkan.
9. **Verifikasi ulang** setelah perbaikan.

Review bukan pengganti tes. Tes bukan pengganti review.

## 4. Security baseline

### Input dan output

- Validasi tipe, panjang, format, dan rentang di server.
- Encode output sesuai konteks (HTML, URL, JS, SQL).
- Jangan percaya nama file, header, atau data dari client.
- Batasi ukuran request dan upload.

### Database

- Query berparameter.
- Constraint untuk aturan bisnis penting.
- Least privilege untuk user database.
- Jangan simpan password/token dalam plaintext.
- Backup terenkripsi dan uji restore.

### Auth dan session

- Hash password dengan Argon2id/bcrypt.
- Session/cookie: HttpOnly, Secure, SameSite.
- CSRF protection untuk aksi yang mengubah data.
- Rate limit login, reset password, dan endpoint publik.
- Otorisasi di server, bukan hanya menyembunyikan UI.
- Logout benar-benar menghapus session.

### Web

- HTTPS.
- CORS allowlist.
- Content Security Policy bila memungkinkan.
- Jangan menaruh secret di frontend.
- Lindungi dari XSS, clickjacking, dan open redirect.

### File upload

- Batasi tipe dan ukuran.
- Simpan di luar webroot/object storage.
- Nama file di-generate, bukan dari user.
- Pindai bila file publik.
- Jangan eksekusi file upload.

### Dependency dan supply chain

- Audit dependency berkala.
- Hapus dependency yang tidak dipakai.
- Pin versi di lockfile.
- Hati-hati dengan package populer yang mencurigakan.
- Jangan menjalankan script install dari sumber tidak tepercaya.

### AI/LLM

- Perlakukan output model sebagai input tidak tepercaya.
- Jangan taruh secret, kredensial, atau data pribadi di prompt.
- Batasi token, biaya, dan waktu.
- Siapkan fallback saat model gagal/timeout.
- Minta konfirmasi manusia untuk aksi berisiko.
- Uji dengan prompt berbahaya dan input yang mencoba membocorkan instruksi.

## 5. Aksesibilitas

- HTML semantik: heading, button, label, table.
- Semua input punya label yang terhubung.
- Fokus keyboard terlihat dan urutannya masuk akal.
- Kontras teks memadai.
- Gambar bermakna punya teks alternatif; gambar dekoratif `alt=""`.
- Jangan mengandalkan warna saja untuk status.
- Target sentuh cukup besar.
- Animasi bisa dikurangi (`prefers-reduced-motion`).
- Pesan error dekat dengan input dan mudah dibaca screen reader.

## 6. Performa

- Ukur dulu: waktu muat, waktu respons, query lambat, ukuran bundle.
- Cari N+1 query.
- Tambahkan index untuk query penting.
- Lazy-load aset besar.
- Kompresi gambar dan file.
- Cache hanya jika ada bukti kebutuhan dan strategi invalidasi.
- Tetapkan budget yang relevan; jangan optimasi spekulatif.

## 7. Data dan integritas

- Gunakan transaksi untuk operasi yang harus atomik.
- Idempotensi untuk aksi yang bisa diulang (pembayaran, webhook, job).
- Constraint database untuk aturan yang tidak boleh dilanggar.
- Migrasi aman: backup, uji di staging, rencana rollback.
- Jangan edit data produksi manual tanpa backup.
- Uji restore, bukan hanya backup.

## 8. UX dan penanganan error

Setiap layar/fitur sebaiknya punya:

- Keadaan loading.
- Keadaan kosong yang menjelaskan langkah berikutnya.
- Keadaan error yang memberi tahu apa yang bisa dilakukan.
- Keadaan sukses yang jelas.
- Konfirmasi untuk aksi destruktif.
- Pencegahan double-submit.

Pesan error yang baik: apa yang terjadi, apakah data aman, dan apa langkah berikutnya. Jangan menampilkan stack trace ke user.

## 9. Bug severity dan keputusan rilis

| Severity | Contoh | Tindakan |
|---|---|---|
| Kritis | Kehilangan data, kebocoran, pembayaran salah, akses tidak sah | Blokir rilis |
| Tinggi | Alur utama gagal, data salah, error umum | Blokir rilis |
| Sedang | Fitur sekunder rusak, workaround ada | Boleh rilis dengan catatan |
| Rendah | Kosmetik, teks, edge case jarang | Backlog |

Risiko yang diterima harus dicatat, bukan diabaikan.

## 10. Definisi "cukup baik untuk dirilis"

- Tidak ada bug kritis/tinggi.
- Alur utama teruji di lingkungan yang mirip produksi.
- Backup dan rollback tersedia.
- Error penting terpantau.
- User tahu cara memakai dan melaporkan masalah.
- Batasan diketahui dan didokumentasikan.
