# Panduan Memilih Stack

Tujuan panduan ini bukan membuat semua proyek memakai teknologi yang sama, tetapi membantu memilih **teknologi paling sederhana yang benar-benar cukup** untuk kebutuhan produk, lingkungan user, dan biaya yang tersedia.

## Prinsip

1. **Pilih yang paling mudah di-deploy dan dirawat.** Stack yang populer tetapi rumit untuk user adalah pilihan buruk.
2. **Satu bahasa bila memungkinkan.** Frontend dan backend dalam satu bahasa mengurangi konteks dan dependency.
3. **Monolith dulu.** Pisahkan komponen hanya jika ada alasan operasional atau skalabilitas yang nyata.
4. **Database relasional dulu.** PostgreSQL untuk hampir semua kasus; SQLite untuk aplikasi lokal/single-user.
5. **Auth terkelola dulu.** Jangan membangun sistem akun, reset password, dan verifikasi email sendiri kecuali ada kebutuhan khusus.
6. **Hindari infrastruktur yang belum dibutuhkan.** Kubernetes, microservices, message broker, dan cache terdistribusi bukan default untuk MVP.
7. **Perhatikan jalan keluar.** Data dan kode harus bisa dipindahkan tanpa terkunci total pada satu vendor.
8. **Manfaatkan yang sudah ada.** Jika user sudah punya akun cloud, domain, atau stack, gunakan itu bila aman dan cukup.

## Tabel pemilihan berdasarkan jenis produk

Tabel ini menjawab *bentuk* solusi. Untuk teknologi dan versi konkret yang direkomendasikan saat ini, lihat `teknis-modern.md` §2.

| Jenis produk | Default paling murah | Kapan naik level | Catatan |
|---|---|---|---|
| Web app / SaaS | Framework full-stack dengan server rendering + PostgreSQL + auth terkelola + hosting terkelola | Jika butuh realtime berat, tim besar, atau skala besar | Hindari memisahkan frontend/backend untuk MVP kecil |
| Landing page / katalog | Static site / SSG + form ke layanan email/DB | Jika butuh akun, pembayaran, dashboard | Jangan bangun backend hanya untuk halaman statis |
| API / backend | Satu service monolith + PostgreSQL + REST | Jika butuh event streaming, multi-tenant berat, atau tim terpisah | Dokumentasikan kontrak API |
| Mobile app | Cross-platform framework atau PWA | Jika butuh kamera/background/performance native yang tidak bisa dijembatani | Pertimbangkan biaya akun store dan proses review |
| Bot chat | Bahasa yang sama dengan backend + webhook + database | Jika butuh banyak worker, antrean, atau multi-platform | Amankan webhook, retry, dan idempotensi |
| Automasi / script | Script + scheduler (cron/GitHub Actions) + notifikasi | Jika butuh UI, monitoring, atau banyak job | Utamakan idempotensi dan dry-run |
| Desktop / CLI | CLI atau PWA/desktop wrapper sederhana | Jika butuh akses hardware, offline, atau distribusi installer | Pertimbangkan code signing dan auto-update |
| Tools internal | Web app sederhana + auth + audit log | Jika butuh SSO, izin granular, atau integrasi banyak sistem | Jangan remehkan backup dan akses |

**Catatan bot:** WhatsApp Business API memerlukan akun bisnis, verifikasi, dan biaya. Untuk MVP, Telegram/Discord atau web chat biasanya lebih cepat. Jangan menjanjikan bot WhatsApp sebelum memeriksa persyaratan platform.

**Catatan lokasi server:** pertimbangkan kedekatan server dengan user (latency) dan aturan/data residency jika produk menangani data sensitif.

## Database

| Kebutuhan | Pilihan default | Alasan |
|---|---|---|
| Data relasional, transaksi, query kompleks | PostgreSQL | Andal, kaya fitur, mudah dikelola |
| Aplikasi lokal/single-user | SQLite | Tanpa server, file tunggal, mudah backup |
| Dokumen/file besar | Object storage (S3-compatible) | Jangan simpan file besar di database |
| Cache/session | Redis atau cache bawaan platform | Hanya jika benar-benar perlu |
| Pencarian teks | PostgreSQL full-text search dulu | Elasticsearch hanya jika kebutuhan pencarian sudah kompleks |

**Aturan:** mulai dari satu database. Jangan menambahkan database kedua sebelum ada beban atau pola data yang benar-benar berbeda.

## Auth dan izin

Default: layanan auth terkelola yang mendukung email/password, verifikasi, reset, dan session aman. Jika produk internal dan user sudah punya identitas perusahaan, pertimbangkan SSO.

Bangun sendiri hanya jika:

- Ada kebutuhan kepatuhan yang tidak bisa dipenuhi penyedia.
- Integrasi auth sangat spesifik.
- Produk memang tentang identitas.

Jika membangun sendiri: hash password dengan Argon2id/bcrypt, jangan membuat crypto sendiri, dan uji alur reset/verifikasi dengan serius.

## Hosting

| Kebutuhan | Pilihan umum | Pertimbangan |
|---|---|---|
| Web full-stack kecil | Platform terkelola (Vercel/Netlify/Render/Railway/Fly.io) | Mudah, tetapi perhatikan cold start, batas fungsi, dan biaya saat naik |
| Kontrol penuh / worker | VPS kecil | Murah, tetapi user harus mengurus OS, update, backup, dan monitoring |
| Static | CDN/static hosting | Paling murah dan cepat |
| Mobile | Google Play / App Store | Perlu akun developer, signing key, review, dan biaya |
| Bot | VPS/serverless + webhook | Pastikan proses selalu hidup atau webhook tervalidasi |
| Automasi | GitHub Actions/cron | Perhatikan batas menit dan penyimpanan secret |

**Aturan:** pilih hosting yang meminimalkan jumlah komponen yang harus dirawat user. Jika memilih VPS, siapkan update keamanan, firewall, backup, dan monitoring sejak awal.

## Default "paling sedikit kode"

| Kebutuhan | Jangan langsung membangun | Pakai dulu |
|---|---|---|
| Login | Sistem akun sendiri | Auth terkelola |
| Pembayaran | Integrasi manual | Penyedia checkout/subscription |
| Email | SMTP server sendiri | Layanan email transaksional |
| File upload | Server file sendiri | Object storage + URL bertanda tangan |
| Search | Search engine sendiri | Query database/full-text search |
| Realtime | WebSocket custom | Layanan realtime atau polling bila cukup |
| Admin panel | UI admin dari nol | Generator admin/framework yang ada |
| Background job | Worker custom | Scheduler/queue terkelola |
| Form | Validasi dan state manual | Library form/validasi yang matang |
| PDF/Excel | Render dari nol | Library yang sudah teruji |

## Versi dan kematangan

- Pilih versi **LTS/stabil** runtime dan framework (misalnya Node LTS genap, Python yang masih didukung). Hindari versi beta/RC untuk produksi.
- Kunci versi runtime di repo (`.nvmrc`, `.python-version`, `rust-toolchain.toml`, `engines`) dan dependency lewat lockfile.
- Sebelum memilih library: cek bahwa package ada di registry resmi, dirilis dalam 12 bulan terakhir, punya pemakai yang luas, lisensinya cocok, dan tidak punya advisori keamanan terbuka yang serius.
- Ikuti dokumentasi resmi versi yang dipakai, bukan ingatan atau tutorial lama.

## Konteks Indonesia

| Kebutuhan | Default | Catatan |
|---|---|---|
| Pembayaran lokal | Payment gateway berizin BI (Midtrans, Xendit, DOKU, dan sejenisnya) untuk QRIS/VA/e-wallet | Lihat `siap-publik.md` §2; jangan memproses kartu sendiri |
| Notifikasi chat | Telegram bot (gratis, cepat) atau email | WhatsApp Business Platform perlu verifikasi bisnis dan biaya per percakapan |
| SMS/OTP | Hindari untuk MVP; gunakan email magic link/OAuth | SMS mahal dan rawan disalahgunakan |
| Lokasi server | Region Singapura/Jakarta untuk latency rendah | Hosting di luar negeri termasuk transfer data menurut UU PDP; catat di kebijakan privasi |
| Mobile | PWA dulu; jika perlu store, cross-platform (Flutter/React Native/Expo) | Play Store: closed test 12 tester × 14 hari untuk akun personal baru, target API terbaru, dan verifikasi developer |
| Bahasa & format | `id-ID`: Rp tanpa desimal, tanggal `DD/MM/YYYY`, zona WIB/WITA/WIT | Simpan waktu dalam UTC, tampilkan sesuai zona user |

## Kapan menaikkan kompleksitas

Naikkan hanya jika minimal satu benar:

- Ada kebutuhan nyata yang tidak bisa dipenuhi arsitektur sekarang.
- Beban sudah terukur dan menjadi bottleneck.
- Ada risiko keamanan/kepatuhan yang menuntut pemisahan.
- Tim/operasi sudah cukup besar untuk menanggung biaya tambahan.
- Ada bukti bahwa perubahan akan menghemat biaya total, bukan hanya terlihat modern.

## Jebakan yang harus dihindari

- Memilih stack karena tren, bukan karena kebutuhan.
- Memisahkan frontend/backend untuk aplikasi dengan satu alur sederhana.
- Memakai NoSQL untuk data yang jelas relasional.
- Membangun auth sendiri tanpa kebutuhan mendesak.
- Menambahkan Redis/cache sebelum ada masalah performa.
- Memakai Kubernetes untuk satu service kecil.
- Menaruh file besar di database.
- Mengandalkan free tier tanpa mencatat batasnya.
- Membuat dua repo untuk produk yang masih satu tim kecil.
- Menulis framework internal sebelum ada dua kasus nyata yang membutuhkannya.

## Contoh kombinasi yang sering cukup

Ini contoh, bukan keharusan. Pilih berdasarkan konteks.

- **Web app kecil:** framework full-stack + PostgreSQL + auth terkelola + hosting terkelola.
- **Tools internal:** framework full-stack + PostgreSQL + SSO/email + deploy ke platform yang sama.
- **Bot:** runtime yang sama dengan backend + database + webhook + scheduler.
- **Automasi:** Python/Node script + cron/GitHub Actions + notifikasi ke email/chat.
- **Mobile sederhana:** PWA dulu; naik ke cross-platform/native jika ada kebutuhan perangkat.
- **API:** satu service + PostgreSQL + dokumentasi OpenAPI + rate limit.

## Checklist keputusan stack

- [ ] Kebutuhan produk terpenuhi tanpa fitur spekulatif.
- [ ] Biaya bulanan diketahui dan ada batasnya.
- [ ] User bisa memiliki akun dan akses.
- [ ] Deploy bisa dilakukan dengan langkah yang jelas.
- [ ] Backup dan restore mungkin.
- [ ] Ada jalan keluar/migrasi data.
- [ ] Dependency sedikit dan terawat.
- [ ] Tim/user bisa merawatnya setelah serah terima.
- [ ] Versi stabil/LTS dipakai dan dikunci.
- [ ] Persyaratan platform/regulasi yang relevan sudah dicek (`siap-publik.md`).
