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

Ringkasan per jenis produk. Prinsip, kasus tepi, data uji, dan bukti ada di `pengujian.md`.

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

Detail lengkap per tingkat risiko (T1/T2/T3) ada di `keamanan.md`: OWASP Top 10:2025, auth (NIST SP 800-63B-4), secrets, upload, API, mobile, dan AI/LLM. Saat review, minimal pastikan:

- Otorisasi per objek dicek di server (user A tidak bisa mengakses data user B).
- Input divalidasi dengan skema di server; query berparameter; output di-encode.
- Tidak ada secret di repo, frontend, log, atau prompt.
- Error tidak membocorkan detail internal dan gagal secara aman (*fail closed*).
- Dependency baru benar-benar ada, resmi, terawat, dan lolos audit.
- Webhook diverifikasi dan diproses idempoten.

## 5. Aksesibilitas (target WCAG 2.2 AA untuk UI publik)

- HTML semantik: heading berurutan, `button` untuk aksi, `a` untuk navigasi, `label` untuk input, tabel untuk data tabular.
- Semua input punya label yang terhubung; pesan error dekat dengan input dan diumumkan ke screen reader (`aria-live`/`aria-describedby`).
- Semua fungsi bisa dipakai dengan keyboard; fokus terlihat jelas dan tidak tertutup elemen lengket (sticky header/banner).
- Kontras teks minimal 4,5:1 (teks besar 3:1); komponen UI dan ikon penting 3:1.
- Target sentuh minimal 24×24 px CSS (disarankan 44×44 untuk tombol utama).
- Aksi drag punya alternatif klik/tap.
- Form tidak meminta user mengetik ulang informasi yang sudah diberikan; login tidak mengandalkan tes kognitif (izinkan paste password dan password manager).
- Gambar bermakna punya teks alternatif; gambar dekoratif `alt=""`.
- Jangan mengandalkan warna saja untuk status.
- Tetap bisa dipakai saat zoom 200% dan di lebar 320 px tanpa scroll horizontal.
- Animasi menghormati `prefers-reduced-motion`.
- Cek otomatis dengan axe, lalu cek manual dengan keyboard. Alat otomatis hanya menangkap sebagian masalah.

## 6. Performa

Ukur dulu, baru optimasi. Budget default untuk web publik (persentil ke-75 kunjungan nyata, HP kelas menengah):

| Metrik | Baik | Perlu perbaikan | Buruk |
|---|---|---|---|
| LCP (konten utama tampil) | ≤ 2,5 dtk | ≤ 4 dtk | > 4 dtk |
| INP (respons interaksi) | ≤ 200 ms | ≤ 500 ms | > 500 ms |
| CLS (layout bergeser) | ≤ 0,1 | ≤ 0,25 | > 0,25 |

Budget default lain (sesuaikan di `docs/04-kualitas.md`):

- JavaScript awal ≤ ~200 KB terkompresi untuk halaman utama.
- API p95 ≤ 500 ms untuk endpoint interaktif; query DB utama ≤ 100 ms.
- Gambar dalam format modern (WebP/AVIF) dengan ukuran sesuai tampilan, punya `width`/`height` (mencegah CLS), dan di-lazy-load di bawah lipatan.

Praktik:

- Cari N+1 query; tambahkan index untuk kolom yang dipakai di `WHERE`/`JOIN`/`ORDER BY` query utama.
- Pagination untuk semua daftar yang bisa tumbuh.
- Kompresi (gzip/brotli) dan cache header untuk aset statis berversi.
- Pekerjaan berat (email, laporan, pemrosesan gambar) dipindah ke background job.
- Cache aplikasi hanya jika ada bukti kebutuhan dan strategi invalidasinya jelas.
- Jangan optimasi spekulatif.

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

- Tidak ada bug kritis/tinggi; risiko yang diterima tercatat.
- Gerbang G0–G5 lulus dengan bukti di log verifikasi.
- Alur utama teruji di lingkungan yang mirip produksi.
- Backup dan rollback tersedia.
- Error penting terpantau.
- User tahu cara memakai dan melaporkan masalah.
- Batasan diketahui dan didokumentasikan.
