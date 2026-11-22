# Strategi Pengujian

Tes ada untuk satu tujuan: **memberi keyakinan bahwa produk bekerja dan perubahan berikutnya tidak merusaknya**, dengan biaya serendah mungkin. Tes bukan untuk mengejar angka coverage.

## 1. Bentuk portofolio tes

```
        ▲  sedikit   E2E — alur user utama di browser/perangkat nyata
       ▲▲▲           Integration — API + database + auth, tanpa mock untuk DB
     ▲▲▲▲▲▲▲  banyak  Unit — logika murni: perhitungan, validasi, transformasi
```

- **Unit:** cepat (ms), tanpa jaringan/DB. Untuk aturan bisnis, perhitungan uang, parsing, dan validasi.
- **Integration:** menguji kode bersama dependensi nyatanya. Gunakan database sungguhan (SQLite in-memory atau Postgres lokal/container) daripada mock, karena mock database sering "lulus" untuk query yang salah.
- **E2E:** sedikit tetapi bernilai tinggi. Daftar/login, alur inti, dan pembayaran. Gunakan Playwright atau sejenisnya; jika tidak tersedia, klik-tes manual terdokumentasi atau skill `agent-browser`/`replica-test`.
- **Manual eksploratif:** sebelum rilis, 15–30 menit mencoba merusak produk dengan sengaja.

Untuk produk dengan banyak integrasi (API/backend), integration test boleh menjadi mayoritas.

## 2. Apa yang wajib diuji (berdasarkan risiko)

Prioritaskan dari atas:

1. **Uang:** total, pajak, diskon, pembulatan, mata uang, refund, dan idempotensi pembayaran.
2. **Akses:** user A tidak bisa membaca/mengubah data user B; non-admin tidak bisa melakukan aksi admin; user yang logout tidak bisa mengakses apa pun.
3. **Integritas data:** create/update/delete benar, constraint ditegakkan, transaksi atomik, dan migrasi tidak merusak data lama.
4. **Alur utama:** satu alasan utama produk ini ada harus berjalan end-to-end.
5. **Bug yang pernah terjadi:** setiap bug yang diperbaiki mendapat tes regresi.
6. **Jalur error:** layanan luar timeout/500, input tidak valid, dan data tidak ditemukan.

Yang **tidak** perlu diuji: getter/setter trivial, kode library pihak ketiga, dan detail implementasi yang sering berubah.

## 3. Kasus tepi yang sering terlupa

| Kategori | Contoh |
|---|---|
| Kosong | string kosong, list kosong, `null`, field hilang |
| Batas | 0, -1, maksimum, maksimum+1, tanggal 29 Feb, akhir bulan, pergantian tahun |
| Ukuran | teks 10.000 karakter, file 0 byte, file melebihi batas, 10.000 baris data |
| Format | emoji, huruf non-Latin, spasi di awal/akhir, huruf besar/kecil pada email |
| Waktu | zona waktu berbeda (WIB/WITA/WIT/UTC), jam bergeser, jam server vs client |
| Uang | Rp0, nominal sangat besar, pembulatan (selalu integer satuan terkecil) |
| Konkurensi | dua request bersamaan mengubah data yang sama, klik ganda tombol bayar |
| Pengulangan | webhook dikirim dua kali, job dijalankan ulang, refresh setelah submit |
| Akses | token kedaluwarsa, user dihapus saat session aktif, ID milik orang lain |
| Jaringan | offline, lambat, putus di tengah upload |

## 4. Menulis tes yang baik

- Nama tes menjelaskan perilaku: `menolak_pembayaran_jika_total_tidak_cocok`, bukan `test1`.
- Pola **Arrange–Act–Assert**; satu perilaku per tes.
- Tes harus **deterministik**: jangan bergantung pada waktu nyata, urutan eksekusi, data acak tanpa seed, atau internet. Bekukan jam dan seed generator acak.
- Setiap tes menyiapkan dan membersihkan datanya sendiri (transaksi rollback atau DB baru per tes).
- Data uji dibuat dengan factory/fixture yang jelas, **tidak pernah** dari data produksi asli.
- Assertion memeriksa hasil yang bermakna (nilai, status, efek di DB), bukan sekadar "tidak error".
- Mock hanya untuk batas yang tidak bisa dikendalikan (API pembayaran, email, waktu). Untuk layanan luar, uji juga kontraknya dengan contoh respons asli dari dokumentasi.

## 5. Test-first untuk bug

1. Reproduksi bug dalam tes → tes **gagal**.
2. Perbaiki akar masalahnya (lihat skill `bedah-akar`), bukan gejalanya.
3. Tes lulus, dan seluruh suite tetap lulus.
4. Tanya: di mana lagi pola bug yang sama mungkin ada?

## 6. Tes flaky

Tes yang kadang lulus kadang gagal lebih berbahaya daripada tidak ada tes, karena mengajarkan tim untuk mengabaikan merah.

- Jangan menambal dengan `retry` atau `sleep`. Cari penyebabnya: waktu, urutan, state bersama, jaringan, atau race condition.
- Jika belum bisa diperbaiki segera: karantina dengan catatan dan tenggat. Jangan dihapus diam-diam.

## 7. Pengujian non-fungsional

| Jenis | Cara murah | Kapan |
|---|---|---|
| Performa web | Lighthouse/PageSpeed (lab) + data lapangan Core Web Vitals setelah live | Sebelum rilis + pasca-launch |
| Beban API | `k6`/`autocannon`/`hey` dengan skenario realistis ke staging | T2/T3 sebelum rilis |
| Aksesibilitas | axe (DevTools/Playwright), navigasi keyboard penuh, zoom 200% | Setiap layar baru |
| Kompatibilitas | Chrome Android, Safari iOS, Chrome desktop; layar 360px dan 1280px | Sebelum rilis |
| Keamanan | Lihat §9 `keamanan.md` | Setiap rilis |
| Backup | Restore ke database terpisah, lalu cek jumlah baris dan sampel data | Sebelum launch + berkala |

## 8. Smoke test (setelah setiap deploy)

Checklist 5 menit, dijalankan di URL nyata:

- [ ] Halaman/endpoint utama merespons 200 dengan HTTPS valid.
- [ ] Health check OK.
- [ ] Login/logout bekerja.
- [ ] Alur utama selesai dan datanya tersimpan.
- [ ] Satu aksi yang seharusnya ditolak memang ditolak.
- [ ] Tidak ada error baru di log/monitoring.

Otomatiskan jika memungkinkan (skrip `curl` atau satu tes Playwright `@smoke`).

## 9. Coverage

- Coverage adalah **alat untuk menemukan bagian yang belum diuji**, bukan target.
- Targetkan coverage tinggi pada modul logika bisnis dan keamanan. Abaikan kode glue/UI sederhana.
- Coverage 100% dengan assertion lemah lebih buruk daripada 60% dengan assertion tajam.

## 10. Bukti yang dicatat

Setiap gerbang mencatat ke log verifikasi di `docs/04-kualitas.md`:

| Tanggal | Gerbang | Perintah | Hasil | Catatan |
|---|---|---|---|---|
| 2026-01-10 | G4 | `npm test` | 84 lulus, 0 gagal | — |
| 2026-01-10 | G4 | `npm audit --omit=dev` | 0 tinggi/kritis | 1 sedang diterima: … |
| 2026-01-11 | G6 | smoke test produksi | 6/6 lulus | URL: … |

Tanpa baris di log ini, gerbangnya dianggap belum lulus.
