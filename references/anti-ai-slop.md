# Anti AI-Slop: Supaya Hasilnya Terasa Dibuat Developer Sungguhan

"AI slop" adalah hasil yang **tampak selesai tetapi generik, berlebihan, atau kosong**: UI yang mirip ribuan template, kode penuh komentar dan pengaman yang tidak perlu, serta teks yang terdengar seperti brosur. Penyebabnya, model cenderung kembali ke pola paling rata-rata dari data latihnya. Cara melawannya: **keputusan eksplisit, batasan tertulis, data nyata, dan review yang mencari pola ini dengan sengaja**.

Daftar di bawah adalah **sinyal, bukan hukum mutlak**. Pola yang dilarang boleh dipakai jika ada alasan produk yang tertulis (misalnya merek user memang ungu). Yang dilarang adalah memakainya **karena default**.

## 1. Prinsip

1. **Setiap pilihan punya alasan.** Jika tidak bisa menjelaskan kenapa warnanya itu, fontnya itu, atau abstraksinya itu, berarti itu default, bukan keputusan.
2. **Spesifik mengalahkan generik.** Data nyata, istilah domain user, angka nyata, dan nama fitur yang menggambarkan pekerjaan user.
3. **Lebih sedikit, lebih tajam.** Developer senior menghapus lebih banyak daripada yang ditambahkan AI.
4. **Konsisten di seluruh produk.** Slop sering terlihat dari ketidakkonsistenan: tiga gaya tombol, dua cara fetch data, empat istilah untuk hal yang sama.
5. **Jujur.** Tidak ada fitur, angka, testimoni, atau keberhasilan palsu, baik di UI maupun di laporan ke user.

## 2. Slop pada UI

| Pola slop | Gantinya |
|---|---|
| Gradasi ungu–biru/violet–indigo/pink sebagai latar atau tombol | Warna merek user, solid, dipakai hemat untuk aksi utama |
| Judul dengan teks bergradasi (`bg-clip-text text-transparent`) | Judul solid, hierarki lewat ukuran dan berat |
| Glassmorphism/`backdrop-blur` di mana-mana | Permukaan solid dengan border tipis; blur hanya untuk overlay yang memang melayang |
| Semua dibungkus kartu `rounded-2xl shadow-xl` | Baris dengan pemisah; kartu hanya untuk objek mandiri; radius dan shadow dari token |
| Tiga kartu fitur sejajar dengan ikon di lingkaran berwarna | Tunjukkan produk sebenarnya (screenshot/alur nyata); fitur dijelaskan dalam konteks pemakaian |
| Emoji sebagai ikon (🚀✨📊) | Satu set ikon konsisten |
| Ikon ✨ "sparkles" untuk semua fitur AI | Label yang menjelaskan hasilnya ("Ringkas catatan") |
| Hero "Welcome to [App]" + subjudul generik + "Get Started →" | Aplikasi langsung membuka layar kerja; marketing page menyebut masalah dan hasil secara spesifik |
| Dashboard penuh chart dan angka contoh | Angka nyata dari data user, atau empty state yang mengajak memulai |
| Statistik palsu ("10.000+ pengguna", "99,9% puas") | Hapus. Tampilkan hanya angka yang benar dan bisa dibuktikan |
| Testimoni/logo klien rekaan | Hapus sampai ada yang asli dengan izin |
| Lorem ipsum, "John Doe", "Acme Inc", `user@example.com` di layar produksi | Data contoh realistis di seed/dev saja; produksi memakai empty state |
| Spinner besar di tengah layar untuk setiap loading | Skeleton sesuai layout; loading lokal di tombol |
| Toast untuk setiap aksi + modal untuk setiap konfirmasi | Perubahan terlihat langsung; undo untuk aksi yang bisa dipulihkan; modal hanya untuk keputusan berisiko |
| Padding raksasa dan elemen yang terlalu besar di aplikasi kerja | Kepadatan sesuai pemakaian (§1 `sistem-ui.md`) |
| Semua teks rata tengah | Rata kiri untuk konten dan form; tengah hanya untuk empty state/hero pendek |
| Dark mode hasil membalik warna | Palet gelap yang disetel, atau tunda |
| Font Inter/default tanpa keputusan, ukuran acak | Font dipilih dengan alasan dan skala tipografi tetap |
| Warna, radius, dan jarak berbeda di tiap layar | Token desain dipakai di semua komponen |
| Animasi bounce/fade di setiap elemen | Gerak singkat yang menjelaskan perubahan |

## 3. Slop pada teks (copy & microcopy)

Hindari kata dan pola yang langsung terdengar "ditulis AI", terutama jika muncul bergerombol:

- **Inggris:** seamless, elevate, unlock, unleash, supercharge, empower, revolutionize, game-changer, cutting-edge, next-level, effortless, delve, harness, robust solution, "in today's fast-paced world", "Oops! Something went wrong".
- **Indonesia:** "mulus tanpa hambatan", "tingkatkan pengalaman Anda", "buka potensi", "revolusioner", "solusi terdepan/terbaik", "di era digital ini", "tak hanya … tetapi juga …", "kelas dunia", "Selamat datang di [Aplikasi]!", "Wujudkan impianmu bersama kami", "Ups! Terjadi kesalahan".
- **Pola:** daftar yang selalu berisi tiga hal, kalimat pendek dramatis berturut-turut, tanda seru di mana-mana, emoji di judul, dan klaim tanpa angka atau contoh.

Gantinya:

- Sebut **apa yang dilakukan produk untuk siapa**, dengan kata user sendiri: "Catat utang pelanggan warung dan kirim pengingat lewat WhatsApp."
- Label tombol = kata kerja + objek ("Catat utang"), bukan "Mulai Sekarang 🚀".
- Pesan error = apa yang terjadi + data aman/tidak + langkah berikutnya.
- Baca keras-keras. Jika terdengar seperti iklan TV, tulis ulang.

## 4. Slop pada kode

| Pola slop | Kenapa buruk | Gantinya |
|---|---|---|
| Komentar yang menceritakan kode (`// Increment counter`, `// Step 1: Import modules`, `// Fungsi ini untuk...`) | Bising, cepat basi, menandakan penulis tidak percaya kodenya terbaca | Nama yang jelas; komentar hanya untuk **kenapa** dan hal yang tidak terlihat |
| Docstring panjang di setiap fungsi trivial | Menambah baris tanpa informasi | Docstring untuk API publik/logika rumit saja |
| `try/catch` di setiap fungsi, `catch` yang hanya `console.log` lalu lanjut | Error tertelan, bug muncul jauh dari sumbernya | Tangkap di batas, tempat kamu bisa bertindak (`teknis-modern.md` §8) |
| Cek defensif untuk hal yang dijamin tipe (`if (user && user.id && typeof user.id === "string")`) | Kode membengkak, logika asli tersembunyi | Parse di batas sistem; di dalam, percayai tipe |
| Fallback diam-diam (`return []`, `?? "Unknown"`, nilai default palsu) saat data tidak ada | Menyembunyikan bug dan data rusak | Error yang jelas atau state "tidak ada" yang eksplisit |
| Helper/import/variabel yang tidak dipakai | Kode mati menyesatkan pembaca | Hapus |
| Abstraksi untuk satu pemakaian (`BaseService`, `Factory`, `Manager`, `GenericRepository<T>`) | Kompleksitas tanpa manfaat | Fungsi sederhana; abstraksi setelah ada dua pemakaian nyata |
| Opsi konfigurasi/flag untuk kebutuhan imajiner | Kombinasi yang tidak pernah dites | Bangun yang dibutuhkan sekarang |
| Duplikasi logika yang sedikit berbeda di beberapa tempat | Bug harus diperbaiki di banyak tempat | Satukan atau ekstrak setelah polanya jelas |
| Nama generik: `data`, `result`, `item`, `temp`, `handleClick2`, `utils.ts`, `helpers.ts` | Tidak menjelaskan domain | Nama domain: `unpaidDebts`, `sendReminder`, `format-rupiah.ts` |
| `any`, `as any`, `@ts-ignore`, `# type: ignore` | Mematikan jaring pengaman | Tipe yang benar; `unknown` + narrowing |
| `console.log`/`print` debug tertinggal | Bising dan bisa membocorkan data | Logger terstruktur, atau hapus |
| Emoji di log, kode, atau pesan commit | Tidak profesional, mengganggu grep/log | Teks polos |
| Implementasi palsu: `// TODO: implement`, return hardcoded sukses, mock data di jalur produksi | Fitur tampak jalan padahal tidak | Implementasi nyata, atau tandai jelas sebagai belum selesai di roadmap |
| Tes yang hanya mengetes mock, atau assertion lemah (`expect(result).toBeDefined()`) | Hijau palsu | Tes perilaku dengan assertion bermakna (`pengujian.md`) |
| `sleep`/`setTimeout` untuk "memperbaiki" race condition | Flaky dan menyembunyikan bug | Tunggu kondisi/event yang tepat |
| Menulis ulang fitur yang sudah ada di platform/library | Lebih banyak bug, lebih banyak kode | Pakai yang ada (`Intl`, `URLSearchParams`, `crypto.randomUUID`, komponen headless) |
| API usang dari ingatan, karena pengetahuan model punya tanggal batas (Pages Router untuk project baru, `getServerSideProps`, `tailwind.config.js` di v4, `moment`, `request`, Create React App) | Utang teknis sejak hari pertama | Cek dokumentasi resmi versi yang dipakai |
| File 1.000 baris berisi semuanya | Sulit dibaca, di-review, dan dites | Pecah per fitur/tanggung jawab |
| Gaya campur aduk (async/await + `.then`, dua cara fetch, dua library tanggal) | Terasa dikerjakan banyak "orang" tanpa arah | Satu konvensi, ditulis di README/ADR |

## 5. Slop pada arsitektur dan proses

- **Over-engineering untuk skala imajiner:** microservices, Kubernetes, event bus, Redis, atau GraphQL untuk aplikasi dengan 50 user. Ganti dengan monolith + Postgres + platform terkelola.
- **Diff membengkak:** tugas kecil menghasilkan perubahan di 15 file, refactor yang tidak diminta, dan file baru yang tidak perlu. Diff harus sebanding dengan tugasnya.
- **Tidak membaca kode yang ada:** membuat util baru padahal sudah ada, atau mengabaikan konvensi project.
- **Klaim tanpa bukti:** "sudah dites", "sudah aman", atau "production-ready" tanpa output perintah.
- **Laporan berlebihan ke user:** tabel, emoji, dan pujian pada diri sendiri. Laporan profesional: apa yang berubah, bukti, risiko, dan langkah berikutnya.

## 6. Slop pada dokumentasi dan git

- README dengan deretan badge, emoji di setiap heading, bagian "Features ✨" berisi janji, dan "Contributing" generik untuk project pribadi. README yang baik: apa ini, cara menjalankan (sudah diuji), cara deploy, struktur singkat, dan link ke `docs/`.
- Dokumen yang mengulang isi kode, atau menjelaskan hal yang tidak ada di produk.
- Commit "update", "fix bug", "final", "final2", atau satu commit raksasa "initial implementation". Commit yang baik kecil, Conventional Commits, dan menjelaskan kenapa.
- Pesan commit/PR penuh emoji atau poin berlebihan.

## 7. Tanda kerja developer sungguhan

Hasil yang terasa dikerjakan manusia berpengalaman biasanya punya ciri ini:

- **Konteks domain terasa:** istilah, contoh data, alur, dan prioritas sesuai bisnis user (warung, klinik, bengkel), bukan aplikasi generik.
- **Kasus tepi sudah dipikirkan:** data kosong, nama panjang, nominal besar, koneksi buruk, dan klik ganda.
- **Detail kecil konsisten:** format rupiah dan tanggal, istilah, jarak, fokus keyboard, judul tab browser, favicon, halaman 404.
- **Keputusan tercatat:** ADR singkat untuk pilihan penting, dan risiko yang diakui.
- **Kode membosankan dengan cara yang baik:** mudah ditebak, sedikit trik, nama jelas, dan diff kecil.
- **Ada hal yang sengaja tidak dibuat**, tercatat di non-goals.

## 8. Review anti-slop (bagian dari Gerbang G4)

1. Jalankan `python3 scripts/cek_slop.py <project>`. Tangani setiap temuan, atau catat alasan menerimanya.
2. Screenshot tiga layar terpenting di 390px dan 1280px. Untuk setiap layar, tanya: "Apakah layar ini bisa ditukar dengan aplikasi lain tanpa ada yang sadar?" Jika ya, berarti terlalu generik. Tambahkan konteks domain, data nyata, dan keputusan visual dari §1 `sistem-ui.md`.
3. Baca semua teks UI dalam satu kali duduk: satu suara? ada kata dari §3? istilah konsisten?
4. Baca diff akhir seperti reviewer senior: komentar narasi, catch kosong, abstraksi satu pemakaian, kode mati, dan API usang.
5. Pastikan tidak ada data, angka, atau konten palsu di build produksi.
