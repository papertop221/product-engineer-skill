# Siap Dipakai Publik — Production Readiness

Kode yang benar belum tentu berarti produk siap dipakai orang lain. Dokumen ini berisi semua hal **di luar kode** yang biasanya membuat produk gagal, diblokir, ditolak store, atau menimbulkan masalah hukum setelah rilis. Isi hasilnya di `docs/07-siap-rilis.md`.

> **Penting — fakta yang cepat berubah.** Aturan platform dan regulasi di bawah dicatat per **November 2026** dan akan berubah (target API, syarat testing, regulasi PDP, tarif). Jangan menjadikannya acuan final: **cari aturan yang berlaku pada tanggal sesi ini** lewat web search ke sumber resmi. Sebelum rilis, selalu cek ulang ke sumber resmi yang disebut, lalu catat tanggal pengecekannya di `docs/07-siap-rilis.md`. Hal legal disampaikan ke user sebagai **draft dan informasi, bukan nasihat hukum**. Untuk produk T3, sarankan konsultasi dengan konsultan hukum.

## 1. Legal dan privasi (Indonesia)

### 1.1 UU 27/2022 tentang Pelindungan Data Pribadi (UU PDP)

UU PDP berlaku penuh sejak Oktober 2024. Peraturan pelaksananya, **PP 33/2026**, ditetapkan Juli 2026 dan berlaku enam bulan setelah diundangkan. Lembaga pengawas PDP masih dalam proses pembentukan; sementara fungsinya dijalankan Komdigi. Sanksi administratif bisa mencapai **2% dari pendapatan tahunan**, dan ada juga ancaman pidana untuk pelanggaran tertentu.

Kewajiban praktis untuk produk yang memproses data pribadi (T2/T3):

- [ ] **Dasar pemrosesan** yang jelas untuk setiap jenis data. Untuk aplikasi konsumen, biasanya persetujuan eksplisit atau pelaksanaan perjanjian (layanan yang diminta user).
- [ ] **Persetujuan** yang spesifik, bisa dibuktikan (simpan waktu, versi kebijakan, dan apa yang disetujui), dan bisa ditarik kembali. Jangan memakai checkbox yang sudah tercentang.
- [ ] **Pemberitahuan privasi** (kebijakan privasi) yang mudah dipahami: data apa, untuk apa, berapa lama, dibagikan ke siapa (termasuk layanan pihak ketiga seperti hosting, analytics, email, dan AI), serta hak user.
- [ ] **Hak subjek data** yang bisa dijalankan: akses/salinan, koreksi, penghapusan, penarikan persetujuan, dan keberatan. Sediakan fitur di aplikasi atau minimal jalur email dengan SLA respons.
- [ ] **Minimisasi dan retensi:** kumpulkan seperlunya, hapus saat tidak diperlukan.
- [ ] **Keamanan data:** kontrol di `keamanan.md` adalah bentuk teknis kewajiban ini.
- [ ] **Pemberitahuan kebocoran:** jika terjadi kegagalan pelindungan data, pemberitahuan tertulis ke subjek data dan lembaga paling lambat **3 × 24 jam**. Siapkan template dan runbook-nya sebelum launch.
- [ ] **Transfer ke luar negeri:** hosting/layanan di luar Indonesia termasuk transfer data. Catat di kebijakan privasi dan pilih penyedia dengan perlindungan memadai.
- [ ] **Data spesifik** (kesehatan, biometrik, genetika, catatan kejahatan, data anak, keuangan pribadi) → otomatis T3: perlu penilaian dampak (DPIA), perlindungan lebih ketat, dan untuk anak, persetujuan orang tua/wali.
- [ ] **Pejabat PDP (DPO)** wajib untuk pemrosesan skala besar, data spesifik, atau pemantauan sistematis. Beri tahu user jika produknya mendekati kriteria ini.

Sumber resmi: JDIH Komdigi / peraturan.go.id (UU 27/2022, PP 33/2026).

### 1.2 Pendaftaran PSE Lingkup Privat (Komdigi)

Berdasarkan PM Kominfo 5/2020, penyelenggara sistem elektronik privat yang melayani pengguna di Indonesia (misalnya platform jual beli, layanan keuangan, layanan komunikasi, media sosial, mesin pencari, dan pemrosesan data pribadi untuk transaksi) wajib **mendaftar sebelum layanan digunakan**. Pendaftaran dilakukan melalui OSS (oss.go.id). Platform yang tidak terdaftar bisa ditegur lalu diputus aksesnya, dan penegakan aktif masih berlangsung pada 2026.

- [ ] Nilai apakah produk masuk kriteria. Tool pribadi/internal kecil umumnya tidak; aplikasi publik yang bertransaksi atau memproses data pribadi pengguna Indonesia umumnya ya.
- [ ] Jika ya: user (pemilik usaha/badan hukum) mendaftar lewat OSS. Pendaftaran perlu NIB, jadi ini keputusan dan tindakan user, bukan agent.
- [ ] Panduan: s.komdigi.go.id/pendaftaranpseprivat.

### 1.3 Dokumen legal minimum untuk produk publik

| Dokumen | Kapan wajib | Template |
|---|---|---|
| Kebijakan privasi | Ada data pribadi apa pun (termasuk email, analytics, cookie) | `assets/templates/legal/kebijakan-privasi.md` |
| Syarat & ketentuan | Ada akun, transaksi, atau konten user | `assets/templates/legal/syarat-ketentuan.md` |
| Kebijakan refund/pembatalan | Ada pembayaran | Bagian di syarat & ketentuan |
| Pemberitahuan cookie/consent | Ada cookie non-esensial (analytics/iklan), terutama jika ada user dari UE | Banner consent sederhana |
| Identitas penyelenggara + kontak | Selalu untuk produk publik | Halaman "Tentang/Kontak" |

Aturan:

- Template harus diisi sesuai produk nyata, bukan disalin generik. Kebijakan yang menjanjikan hal yang tidak dilakukan justru menimbulkan risiko.
- Tautkan dari footer, halaman daftar, dan checkout. Simpan versi + tanggal berlaku.
- Jika target pengguna mencakup UE, AS (California), atau anak-anak di bawah 13 tahun, ada regulasi tambahan (GDPR, CCPA, COPPA). Tandai sebagai risiko dan sarankan konsultasi.

### 1.4 Hak kekayaan intelektual dan lisensi

- [ ] Semua font, ikon, gambar, dan audio punya lisensi yang mengizinkan pemakaian komersial.
- [ ] Lisensi dependency kompatibel dengan model distribusi (waspadai GPL/AGPL untuk software tertutup).
- [ ] Nama produk dan logo sudah dicek: tidak ada merek terdaftar yang sama di kelas yang sama (PDKI: pdki-indonesia.dgip.go.id), dan domain/handle media sosial tersedia. Skill `replica-brand` bisa membantu.
- [ ] Konten buatan AI tidak meniru merek atau karya orang lain.

## 2. Pembayaran (bila ada) — otomatis T3

### 2.1 Pilih penyedia berizin

- Indonesia: payment gateway berizin Bank Indonesia (misalnya Midtrans, Xendit, DOKU, iPaymu) untuk QRIS, virtual account, e-wallet, dan kartu.
- Internasional: Stripe, Paddle, atau Lemon Squeezy (merchant of record yang mengurus pajak).
- Produk digital di dalam aplikasi mobile: aturan store mewajibkan billing store untuk barang digital tertentu. Cek kebijakan Google Play Billing / Apple IAP sebelum merancang alur bayar.
- **Jangan pernah menyimpan atau memproses nomor kartu sendiri.** Gunakan checkout/hosted fields penyedia agar tetap di luar lingkup PCI DSS yang berat.
- Biaya: MDR QRIS sejak 1 Oktober 2026 berjenjang per kategori merchant dan nominal transaksi (cek pengumuman Bank Indonesia). Biaya VA/e-wallet/kartu berbeda per penyedia. Masukkan ke perhitungan harga.

### 2.2 Alur pembayaran yang benar

1. Server membuat pesanan dengan **harga dari server**, status `menunggu_pembayaran`, dan ID unik.
2. Server membuat transaksi di penyedia (dengan idempotency key = ID pesanan) dan mengirim token/URL checkout ke client.
3. User membayar di halaman/komponen penyedia.
4. Penyedia mengirim **webhook** ke server.
5. Server **memverifikasi signature/token webhook** sesuai dokumentasi resmi penyedia. Tolak jika tidak valid.
6. Server mengecek ulang status ke API penyedia (atau mempercayai webhook yang sudah terverifikasi), mencocokkan **nominal dan mata uang** dengan pesanan, lalu memperbarui status **secara idempoten** dalam transaksi DB. Webhook yang sama datang dua kali harus tetap menghasilkan satu perubahan.
7. Redirect sukses di client **bukan bukti pembayaran**. Status hanya berubah lewat langkah 5–6.

Checklist:

- [ ] Mode sandbox diuji untuk semua skenario: sukses, gagal, kedaluwarsa, dibatalkan, webhook ganda, webhook terlambat, dan refund.
- [ ] Kunci produksi hanya di secret manager; kunci sandbox ≠ produksi.
- [ ] Rekonsiliasi harian/mingguan: jumlah di sistem = laporan settlement penyedia.
- [ ] Email/notifikasi bukti pembayaran ke user.
- [ ] Kebijakan refund tertulis dan prosesnya diuji.
- [ ] Alert jika webhook gagal berulang.
- [ ] Pajak: tanyakan ke user apakah usahanya PKP (PPN) dan apakah ada kewajiban pajak digital. Ini keputusan user/akuntan.

## 3. Email

- [ ] Kirim lewat layanan email transaksional (Resend, Postmark, Amazon SES, Mailgun, Brevo, dan sejenisnya), bukan SMTP server sendiri.
- [ ] Domain pengirim punya **SPF**, **DKIM**, dan **DMARC** (mulai `p=none` lalu naik ke `quarantine`) yang sejalan dengan domain di alamat From. Gmail, Yahoo, dan Microsoft menolak email massal yang tidak memenuhi ini.
- [ ] Email pemasaran/massal: header **List-Unsubscribe + List-Unsubscribe-Post** (unsubscribe satu klik, RFC 8058), permintaan berhenti diproses ≤ 2 hari, dan tingkat spam dijaga jauh di bawah 0,3%.
- [ ] Email transaksional (reset password, bukti bayar) dipisah dari pemasaran, idealnya di subdomain berbeda.
- [ ] Template punya versi teks biasa, alamat fisik/identitas pengirim, dan tidak memuat data sensitif.
- [ ] Uji: email masuk inbox (bukan spam) di Gmail dan Outlook.

## 4. Web publik: ditemukan, dipercaya, dan nyaman

- [ ] `<title>` dan meta description unik per halaman; `lang="id"` (atau sesuai bahasa).
- [ ] Open Graph + Twitter card (judul, deskripsi, gambar 1200×630) agar tautan tampil baik di WhatsApp/media sosial.
- [ ] Favicon + `apple-touch-icon`; `manifest.webmanifest` jika PWA.
- [ ] `robots.txt` dan `sitemap.xml`. Staging **di-noindex** agar tidak muncul di Google.
- [ ] URL kanonis; redirect `www` ↔ apex dan HTTP → HTTPS konsisten.
- [ ] Halaman 404 dan 500 yang ramah, dengan jalan kembali.
- [ ] Performa: Core Web Vitals "baik" (LCP ≤ 2,5 dtk, INP ≤ 200 ms, CLS ≤ 0,1) di HP kelas menengah dengan koneksi 4G.
- [ ] Aksesibilitas WCAG 2.2 AA (lihat `standar-kualitas.md`).
- [ ] Analytics yang menghormati privasi (misalnya Plausible, Umami, atau Cloudflare Web Analytics). Jika memakai analytics berbasis cookie, minta consent lebih dulu.
- [ ] Daftarkan ke Google Search Console (dilakukan user dengan akunnya sendiri).

## 5. Anti-penyalahgunaan

Produk publik pasti didatangi bot dan orang iseng. Siapkan sebelum launch:

- [ ] Rate limit: login, signup, reset password, OTP, form kontak, endpoint AI, dan pencarian.
- [ ] CAPTCHA/anti-bot yang ramah (Cloudflare Turnstile, hCaptcha) pada form publik yang sering diserang, jika rate limit saja tidak cukup.
- [ ] Batas sumber daya per user: ukuran upload, jumlah item, dan kuota AI.
- [ ] Konten buatan user (UGC): fitur laporkan, kemampuan admin menghapus/memblokir, dan syarat penggunaan yang melarang konten ilegal.
- [ ] Verifikasi email/nomor sebelum fitur yang bisa disalahgunakan (kirim pesan ke orang lain, undang, dan sejenisnya).
- [ ] Budget alert di setiap layanan berbayar per pemakaian (hosting, database, AI, SMS, email), untuk mencegah tagihan kejutan.

## 6. Distribusi aplikasi mobile

### 6.1 Google Play (cek ulang di Play Console Help)

- [ ] Akun developer atas nama user (biaya satu kali USD 25). Pilih akun organisasi jika ada badan usaha.
- [ ] **Akun personal baru** (dibuat setelah 13 Nov 2023) wajib menjalankan **closed testing minimal 12 tester yang ikut terus-menerus selama 14 hari** sebelum bisa mengajukan akses produksi. Tester harus benar-benar memakai aplikasinya. Masukkan dua minggu ini ke jadwal.
- [ ] **Target API level:** aplikasi baru dan update wajib menargetkan **Android 16 (API 36)** sejak 31 Agustus 2026. Persyaratan ini naik setiap tahun sekitar Agustus; masukkan ke kalender perawatan.
- [ ] **Verifikasi developer Android:** sejak 30 September 2026, di Indonesia (juga Brasil, Singapura, Thailand), aplikasi yang dipasang di perangkat Android bersertifikat harus terdaftar atas nama developer terverifikasi, **termasuk APK yang dibagikan di luar Play**. Rencana Google: berlaku global pada 2027. Daftarkan identitas developer dan package name melalui Android Developer Console / Play Console.
- [ ] Format AAB, Play App Signing aktif, dan upload key di-backup aman.
- [ ] Data safety form diisi jujur sesuai data yang benar-benar dikumpulkan (termasuk oleh SDK pihak ketiga).
- [ ] Kebijakan privasi berupa URL publik.
- [ ] Rating konten, target audiens, dan deklarasi izin sensitif (lokasi latar belakang, SMS, dan sejenisnya).
- [ ] Uji di perangkat nyata dari build **release**.

### 6.2 Apple App Store (cek ulang di developer.apple.com/news/upcoming-requirements)

- [ ] Apple Developer Program atas nama user (USD 99/tahun). Build iOS memerlukan macOS/Xcode atau layanan build cloud (misalnya EAS Build, Codemagic).
- [ ] Sejak 28 April 2026, upload wajib dibangun dengan **Xcode 26+ dan SDK 26**. Persyaratan SDK naik setiap tahun.
- [ ] Kuesioner **age rating** versi baru dijawab.
- [ ] App Privacy ("nutrition label") dan privacy manifest SDK diisi sesuai kenyataan.
- [ ] Jika ada login pihak ketiga, perhatikan aturan Sign in with Apple. Jika ada pembuatan akun, wajib ada fitur **hapus akun di dalam aplikasi**.
- [ ] Uji via TestFlight sebelum submit, dan siapkan akun demo untuk reviewer.

### 6.3 Alternatif lebih murah untuk MVP

- **PWA** (web yang bisa di-install): tanpa biaya store dan tanpa review, update instan. Cocok untuk banyak MVP; bisa dibungkus ke Play Store nanti (TWA).
- Pertimbangkan ini terlebih dahulu jika fitur perangkat (background, Bluetooth, dan sejenisnya) tidak diperlukan.

## 7. Dukungan dan komunikasi

- [ ] Kanal dukungan yang jelas (email/WhatsApp bisnis/form) dengan target waktu respons.
- [ ] FAQ singkat untuk 5 pertanyaan yang paling mungkin.
- [ ] Kontak keamanan: `/.well-known/security.txt` atau `security@`.
- [ ] Cara memberi tahu user saat gangguan: halaman status sederhana, banner, atau kanal sosial.
- [ ] Changelog/"Apa yang baru" untuk user.

## 8. Operasi dan keberlanjutan

- [ ] Monitoring uptime eksternal (misalnya UptimeRobot, Better Stack) + error tracking (misalnya Sentry) aktif.
- [ ] SLO dan alert didefinisikan (lihat `panduan-deploy.md`).
- [ ] Backup otomatis + **restore sudah diuji** + lokasi terpisah.
- [ ] Runbook insiden + template pemberitahuan kebocoran data (UU PDP 3 × 24 jam).
- [ ] Budget alert biaya aktif; proyeksi biaya pada 10× user dihitung.
- [ ] Kalender perawatan disepakati (lihat `docs/06-serah-terima.md`).
- [ ] Semua akun layanan dimiliki user, dengan MFA aktif pada akun penting (registrar domain, hosting, payment, email, store).

## 9. Keputusan rilis

Sebelum rilis publik, tunjukkan ringkasan ini ke user:

```
Siap rilis: Ya / Ya dengan catatan / Belum
Tingkat risiko: T1 / T2 / T3
Gerbang: G0 ✔ G1 ✔ G2 ✔ G3 ✔ G4 ✔ G5 ✔ G6 –
Risiko yang diterima: …
Yang perlu kamu lakukan: (daftar tindakan user: daftar PSE, isi data legal, buat akun store, …)
```

Rilis publik adalah tindakan yang sulit dibatalkan. **Minta konfirmasi eksplisit user** sebelum membuka akses ke publik.
