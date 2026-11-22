# Membangun Sistem UI Aplikasi

Panduan untuk **UI aplikasi**: dashboard, form, tabel, daftar, detail, pengaturan, dan alur kerja. Untuk landing page/website marketing, gunakan skill `design-taste-frontend` bila tersedia.

UI yang terasa dibuat profesional bukan soal efek atau gradasi. Ciri utamanya: **konsisten, padat informasi tapi tenang, jelas apa yang bisa dilakukan, dan tidak pernah membuat user bingung tentang keadaan aplikasi.** Rujukan kualitasnya produk seperti Linear, Stripe Dashboard, Vercel, Notion, GitHub, dan aplikasi bank/e-commerce lokal yang matang. Yang ditiru dari mereka adalah **polanya, bukan tampilannya**.

## 1. Mulai dari keputusan, bukan dari komponen

Sebelum menulis UI, tulis di `docs/01-rencana-produk.md` bagian desain:

1. **Siapa user dan di mana mereka memakainya?** Pemilik warung di HP Android kelas menengah, di bawah sinar matahari, satu tangan, berbeda kebutuhannya dengan admin kantor di laptop.
2. **Kepadatan:** *nyaman* (konsumen, jarang dipakai) atau *padat* (alat kerja harian, banyak data).
3. **Karakter (3 kata):** misalnya "tenang, tepercaya, cepat" atau "hangat, sederhana, lokal". Setiap keputusan visual harus bisa dijelaskan dengan tiga kata ini.
4. **Warna merek:** dari logo/identitas user. Jika belum ada, pilih satu hue dengan alasan (lihat §3). Jangan memakai default ungu/indigo hanya karena itu default.
5. **Tiga layar terpenting:** desain dan sempurnakan ini lebih dulu; layar lain mengikuti polanya.

## 2. Token desain: satu sumber kebenaran

Semua nilai visual berasal dari token, tidak ada angka acak di komponen.

```
primitif  →  semantik  →  komponen
blue-600     primary       button-bg
gray-50      surface       card-bg
red-600      danger        input-border-error
```

- **Primitif:** skala mentah (warna, ukuran, jarak).
- **Semantik:** makna (`--color-primary`, `--color-surface`, `--color-text-muted`, `--color-danger`). Komponen **hanya** memakai token semantik, sehingga ganti tema/dark mode cukup dengan memetakan ulang.
- Implementasi: CSS custom properties. Di Tailwind v4 lewat `@theme`; di shadcn/ui lewat variabel `:root`/`.dark` yang dipetakan dengan `@theme inline`. Jika token perlu dipertukarkan dengan tool desain, format **W3C Design Tokens (DTCG 2025.10)** adalah standar stabilnya.

Larangan: nilai hex/px langsung di komponen (`#6d28d9`, `mt-[13px]`), kecuali ada alasan tercatat.

## 3. Warna

- Ruang warna **OKLCH**: kecerahan konsisten antar-hue, sehingga skala lebih mudah dibuat seimbang.
- **Netral adalah 90% UI.** Buat skala abu-abu 11 tingkat (50–950), boleh sedikit diwarnai hue merek (chroma rendah) agar tidak terasa mati.
- **Satu warna merek** untuk aksi utama, fokus, dan elemen aktif. Bukan untuk dekorasi di mana-mana.
- **Warna status** dengan makna tetap: sukses (hijau), peringatan (kuning/amber), bahaya (merah), info (biru). Jangan memakai warna status untuk dekorasi.
- Kontras: teks ≥ 4,5:1, teks besar dan ikon/border penting ≥ 3:1. Cek setiap pasangan teks/latar.
- **Dark mode** adalah palet tersendiri yang disetel ulang (latar tidak hitam pekat, kurangi saturasi, elevasi lewat latar yang lebih terang, bukan bayangan). Dark mode bukan warna yang dibalik. Jika tidak ada waktu menyetelnya dengan benar, jangan rilis dark mode dulu.
- Jumlah warna di satu layar: netral + merek + status yang relevan. Jika ada warna keempat, harus ada alasannya.

## 4. Tipografi

- **Font:** untuk UI aplikasi, system font stack atau satu sans-serif yang dipilih dengan alasan (keterbacaan angka, dukungan huruf, karakter). Inter boleh dipakai jika memang dipilih, bukan karena default. Font display terpisah hanya untuk judul marketing.
- **Skala tetap**, misalnya 12 / 14 / 16 / 18 / 20 / 24 / 30 / 36 px. Aplikasi jarang butuh lebih dari 5 ukuran.
- Body 16px di mobile (mencegah zoom otomatis iOS pada input), 14–16px di desktop untuk UI padat.
- **Berat:** cukup 400 dan 500/600. Hierarki dibangun dengan ukuran, berat, dan warna (`text-muted`), bukan dengan memperbesar semuanya.
- Line-height: 1.4–1.6 untuk paragraf, 1.2–1.3 untuk judul. Panjang baris teks ≤ 70–75 karakter.
- **Angka:** `font-variant-numeric: tabular-nums` untuk tabel, saldo, dan statistik, agar digit sejajar.
- Judul halaman jelas dan pendek ("Pelanggan", "Utang belum lunas"), bukan slogan.

## 5. Jarak, layout, dan bentuk

- **Skala jarak berbasis 4px:** 4, 8, 12, 16, 20, 24, 32, 40, 48, 64. Tidak ada nilai di luar skala.
- **Kedekatan = hubungan.** Elemen yang berkaitan lebih rapat daripada antar-kelompok. Ini cara utama membuat UI terasa tertata.
- Lebar konten maksimum untuk halaman baca/form (±640–720px). Tabel/dashboard boleh selebar layar dengan padding konsisten.
- **Radius:** satu skala kecil (misalnya 6px kontrol, 8–12px kartu/dialog). Radius yang sama di seluruh aplikasi. Jangan `rounded-2xl` di semuanya.
- **Border lebih sering daripada shadow** untuk memisahkan area di UI aplikasi. Shadow untuk elemen yang benar-benar melayang (dropdown, dialog, toast).
- **Jangan semuanya dibungkus kartu.** Kartu untuk item yang bisa berdiri sendiri (dibuka, digeser, dipilih). Daftar dan pengaturan biasanya lebih baik sebagai baris dengan pemisah.

## 6. Ikon dan gambar

- **Satu set ikon** (misalnya Lucide) dengan ukuran tetap (16/20/24) dan stroke konsisten.
- Ikon mendampingi label, bukan menggantikannya. Tombol ikon saja wajib punya `aria-label` dan tooltip.
- **Emoji bukan ikon UI.**
- Ilustrasi hanya jika menambah makna (misalnya empty state pertama). Jangan memakai blob/ilustrasi stok generik untuk mengisi ruang.
- Avatar: inisial dengan warna turunan dari ID user jika tidak ada foto.

## 7. Komponen: gunakan primitif yang aksesibel, lalu jadikan milikmu

- Dialog, dropdown, popover, combobox, tabs, tooltip, dan date picker **jangan dibangun dari nol**. Fokus, keyboard, ARIA, dan posisinya sulit dibuat benar. Gunakan Radix/Base UI (lewat shadcn/ui) atau React Aria, lalu tata dengan token sendiri.
- Inventaris minimum: Button (primary, secondary, ghost, destructive; sm/md), Input, Textarea, Select/Combobox, Checkbox, Radio, Switch, Label + pesan bantuan/error, Dialog, Sheet/Drawer (mobile), Dropdown menu, Tabs, Toast, Tooltip, Badge, Avatar, Table, Skeleton, Empty state, Pagination, Breadcrumb/Page header.
- **Setiap komponen interaktif punya semua state:** default, hover, `focus-visible` (ring jelas), active/pressed, disabled, loading, error, dan selected bila relevan.
- Komponen dibuat sekali di `components/ui/` dan dipakai ulang. Jangan menyalin dan memodifikasi markup tombol di 12 tempat.

## 8. Pola layar aplikasi

### 8.1 App shell

- Desktop: sidebar kiri (navigasi utama ≤ 7 item, dikelompokkan) + area konten dengan **page header** (judul, deskripsi singkat opsional, satu aksi utama di kanan).
- Mobile: bottom navigation 3–5 tujuan utama, atau top bar + drawer. Aksi utama di zona jempol. Hormati safe area.
- Navigasi aktif terlihat jelas. Breadcrumb untuk hierarki dalam.

### 8.2 Hierarki aksi

- **Satu aksi utama per layar** (tombol primary). Aksi lain sekunder/ghost atau di menu "⋯".
- Aksi destruktif memakai warna bahaya dan konfirmasi. Untuk yang berdampak besar, minta user mengetik nama objeknya. Lebih baik lagi, sediakan **undo** ("Pelanggan dihapus. Urungkan") daripada dialog konfirmasi untuk aksi yang bisa dipulihkan.
- Label tombol = kata kerja + objek: "Simpan pelanggan", "Catat utang", "Kirim pengingat". Bukan "Submit", "OK", atau "Lanjutkan" yang ambigu.

### 8.3 Daftar dan tabel

- Kolom penting di kiri. Angka rata kanan dengan `tabular-nums`. Satuan di header, bukan diulang di setiap sel.
- Pencarian, filter, dan sort disimpan di URL.
- Pagination atau infinite scroll dengan posisi yang dipertahankan saat kembali.
- Aksi per baris di menu "⋯" atau saat hover. Aksi massal muncul saat ada baris terpilih.
- Mobile: tabel berubah menjadi daftar baris bertumpuk (judul, subjudul, nilai utama di kanan), bukan tabel yang di-scroll horizontal, kecuali memang data tabular yang lebar.
- Status sebagai badge dengan teks (bukan warna saja).

### 8.4 Form

- Satu kolom. Label **di atas** input (bukan placeholder sebagai label). Teks bantuan di bawah label/input bila perlu.
- Tandai yang **opsional**, bukan yang wajib, jika sebagian besar field wajib.
- Tipe input yang tepat: `type="email"`, `inputMode="numeric"` untuk nominal/OTP, `autocomplete` yang benar, dan format ribuan otomatis untuk rupiah.
- Validasi saat blur dan saat submit (bukan setiap ketikan). Pesan error spesifik di bawah field ("Nomor HP harus diawali 08 atau +62"), lalu fokus dipindah ke field error pertama.
- Tombol submit tetap aktif. Saat diklik dan ada error, tampilkan errornya. Saat diproses, tampilkan loading dan cegah klik ganda.
- Jangan menghapus isian user saat error. Form panjang: simpan draf atau pecah menjadi langkah.
- Nilai default yang masuk akal (tanggal hari ini, pilihan terakhir).

### 8.5 Detail dan edit

- Halaman detail menampilkan informasi paling penting di atas (nama, status, nilai utama), aksi di page header, dan riwayat/aktivitas di bawah.
- Edit inline untuk satu field sederhana; halaman/sheet edit untuk banyak field.

### 8.6 Dashboard

- Mulai dari pertanyaan user ("Berapa total utang yang belum dibayar? Siapa yang paling lama?"), bukan dari chart.
- 3–5 angka utama dengan konteks (perbandingan periode, bukan angka telanjang), lalu daftar yang bisa ditindaklanjuti. Chart hanya jika tren memang penting.
- **Tidak ada chart/angka palsu.** Jika belum ada data, tampilkan empty state yang mengajak membuat data pertama.

## 9. Keadaan aplikasi (yang membedakan amatir dan profesional)

| Keadaan | Pola yang benar |
|---|---|
| Loading awal | Skeleton berbentuk layout asli (bukan spinner di tengah layar). Tampilkan hanya jika > ~300ms agar tidak berkedip |
| Loading aksi | Tombol menampilkan spinner kecil + teks ("Menyimpan…"), tetap di tempat; elemen lain tidak melompat |
| Kosong (pertama kali) | Jelaskan apa yang akan muncul di sini + satu tombol aksi ("Belum ada pelanggan. Tambah pelanggan pertama") |
| Kosong (hasil filter) | "Tidak ada hasil untuk 'budi'" + tombol hapus filter |
| Error memuat | Pesan + tombol "Coba lagi"; data lama tetap tampil bila ada |
| Error aksi | Pesan spesifik di dekat aksi/field; input tidak hilang |
| Sukses | Perubahan terlihat langsung di UI; toast singkat hanya jika hasilnya tidak terlihat |
| Offline/lambat | Indikator koneksi; aksi diantrekan atau dicegah dengan penjelasan |
| Sebagian | Data parsial ditampilkan dengan penanda bagian mana yang belum siap |
| Tanpa izin | Jelaskan kenapa dan siapa yang bisa memberi akses, bukan halaman kosong |

## 10. Gerak (motion)

- Durasi 120–250ms, `ease-out` untuk masuk, lebih cepat untuk keluar. Hanya `transform` dan `opacity` (murah untuk GPU).
- Gerak harus menjelaskan sesuatu: dari mana panel datang, apa yang baru berubah, atau bahwa aksi diterima. Bukan dekorasi.
- Hormati `prefers-reduced-motion`.
- Jangan ada animasi masuk berulang pada setiap kartu/daftar saat navigasi biasa.

## 11. Mobile-first untuk pengguna Indonesia

- Mayoritas user memakai Android, sering kelas menengah, dengan koneksi tidak stabil. Uji di lebar **360–390px** dan dengan throttling jaringan "Fast 4G"/"Slow 4G".
- Target sentuh ≥ 44×44px untuk aksi utama, dengan jarak antar-target.
- Aksi utama dalam jangkauan jempol (bawah layar); hindari aksi penting hanya di pojok kanan atas.
- Input nominal dengan keyboard angka; tombol nominal cepat bila relevan (Rp10.000 / Rp50.000 / Rp100.000).
- Bagikan ke WhatsApp adalah fitur yang sering paling berguna: teks rapi, tautan dengan OG image.
- Bundle kecil dan gambar ringan, karena kuota data itu nyata.

## 12. Microcopy

- **Satu suara:** pilih "kamu" (santai) atau "Anda" (formal) dan konsisten di seluruh aplikasi, termasuk email dan pesan error.
- Kalimat pendek, kata sehari-hari, dan kata kerja aktif. "Utang dicatat" lebih baik daripada "Data utang telah berhasil disimpan ke dalam sistem".
- Istilah konsisten: jika menyebut "pelanggan", jangan berganti ke "customer", "klien", atau "kontak" di layar lain. Simpan glosarium di `docs/01-rencana-produk.md`.
- Pesan error: apa yang terjadi + apa yang bisa dilakukan. Tanpa menyalahkan user, tanpa "Oops!", tanpa kode error mentah (taruh ID referensi kecil di bawah bila perlu).
- Hindari tanda seru berlebihan, emoji di pesan sistem, dan kalimat basa-basi ("Selamat datang di aplikasi kami yang luar biasa!").
- Angka dan tanggal dengan format lokal (`Rp 1.250.000`, `22 Nov 2026`).

## 13. Proses kerja UI yang profesional

1. Tulis keputusan §1 dan token §2–§5 **sebelum** layar pertama.
2. Bangun komponen dasar + satu layar inti dengan **data realistis** (nama Indonesia, nominal nyata, teks panjang, daftar 3 item dan 300 item).
3. Screenshot di 390px, 768px, dan 1280px (browser automation bila tersedia). Review dengan mata desainer: apakah jaraknya konsisten, apakah ada satu fokus per layar, apakah keadaan kosong/loading/error sudah dirancang.
4. Uji keyboard penuh dan axe untuk aksesibilitas.
5. Bandingkan dengan produk rujukan untuk **pola** interaksi (bagaimana Linear membuat daftar, bagaimana Stripe membuat form pembayaran), bukan untuk menyalin tampilan.
6. Jalankan `scripts/cek_slop.py`, lalu periksa checklist `anti-ai-slop.md`.
7. Baru perluas ke layar lain dengan pola yang sama.

## 14. Checklist UI sebelum rilis

- [ ] Token semantik dipakai di semua komponen; tidak ada warna/jarak acak.
- [ ] Satu warna merek dengan alasan; kontras lolos AA; dark mode disetel atau belum dirilis.
- [ ] Skala tipografi ≤ 5–6 ukuran; angka memakai `tabular-nums`.
- [ ] Satu set ikon; tidak ada emoji sebagai ikon.
- [ ] Setiap layar punya satu aksi utama yang jelas.
- [ ] Semua komponen interaktif punya state hover/focus-visible/disabled/loading/error.
- [ ] Setiap daftar/halaman punya keadaan loading, kosong, error, dan tanpa izin.
- [ ] Form: label di atas, validasi blur/submit, pesan spesifik, tidak menghapus isian, anti klik ganda.
- [ ] Mobile 360px: tanpa scroll horizontal, target sentuh cukup, aksi utama terjangkau.
- [ ] Microcopy satu suara, istilah konsisten, label tombol kata kerja + objek.
- [ ] Tidak ada data/angka/testimoni palsu di produksi.
