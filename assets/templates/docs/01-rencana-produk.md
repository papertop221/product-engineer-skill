# Rencana Produk — {{NAMA_PRODUK}}

> **Status:** draft · **Pemilik:** {{PEMILIK}} · **Terakhir diperbarui:** {{TANGGAL}}

## 1. Ringkasan

Satu paragraf: produk apa, untuk siapa, masalah apa yang diselesaikan, dan hasil utama yang diinginkan.

## 2. Masalah dan bukti

- **Masalah utama:**
- **Siapa yang mengalaminya:**
- **Bukti atau asumsi:**
- **Cara orang menyelesaikannya sekarang:**
- **Kenapa cara itu kurang:**

## 3. Pengguna dan kebutuhan

| Persona | Kebutuhan utama | Masalah yang dirasakan | Tanda berhasil |
|---|---|---|---|
|  |  |  |  |

## 4. Tujuan dan metrik

- **Tujuan produk:**
- **Metrik utama:**
- **Metrik sekunder:**
- **Cara mengukur:**
- **Baseline saat ini:**

## 5. Tingkat risiko dan klasifikasi data

- **Tingkat risiko:** T1 (tanpa akun/data pribadi/uang) / T2 (akun atau data pribadi) / T3 (uang, data sensitif, aksi sulit dibatalkan)
- **Alasan:**
- **Pengguna:** pribadi / internal / publik Indonesia / publik global

| Data | Contoh field | Kelas | Alasan dikumpulkan | Retensi |
|---|---|---|---|---|
|  |  | publik / internal / pribadi / sensitif |  |  |

> Kumpulkan hanya data yang benar-benar dipakai. Data sensitif (kesehatan, keuangan, biometrik, anak) otomatis menjadikan produk T3.

## 6. Kebutuhan non-fungsional

| Aspek | Target |
|---|---|
| Ketersediaan | mis. 99,5% / bulan |
| Performa | mis. LCP ≤ 2,5 dtk di HP kelas menengah; API p95 ≤ 500 ms |
| Pemulihan | RPO (data yang boleh hilang): · RTO (waktu pulih): |
| Aksesibilitas | WCAG 2.2 AA untuk UI publik |
| Biaya | ≤ Rp … / bulan pada … user |
| Perangkat/bahasa | |

## 7. Lingkup MVP

### Termasuk

- 

### Tidak termasuk (non-goals)

- 

> Non-goals bukan daftar fitur yang tidak akan pernah dibuat. Ini batas tegas untuk versi pertama agar produk bisa selesai.

## 8. User stories dan acceptance criteria

### US-01 — [Nama cerita]

**Sebagai** [persona], **saya ingin** [aksi], **agar** [manfaat].

**Acceptance criteria:**
- [ ] Diberikan [kondisi], ketika [aksi], maka [hasil yang bisa diamati].
- [ ] Diberikan [kondisi gagal], ketika [aksi], maka [penanganan yang benar].

### US-02 — [Nama cerita]

**Sebagai** [persona], **saya ingin** [aksi], **agar** [manfaat].

**Acceptance criteria:**
- [ ] 

## 9. Alur utama

1. 
2. 
3. 

### Alur gagal dan kasus tepi

- Input kosong/salah:
- Data terlalu besar:
- Akses tanpa izin:
- Jaringan putus:
- Aksi berulang:
- Dua pengguna bersamaan:
- Data tidak ditemukan:

## 10. Pengalaman pengguna dan desain

> Isi sebelum membangun UI. Panduan: `references/sistem-ui.md` dan `references/anti-ai-slop.md` di skill product-engineer.

| Keputusan | Isi | Alasan |
|---|---|---|
| Konteks pemakaian | (perangkat, lingkungan, frekuensi; mis. HP Android, di warung, satu tangan) |  |
| Kepadatan | nyaman / padat |  |
| Karakter (3 kata) | (mis. tenang, tepercaya, cepat) |  |
| Warna merek | (hue + sumbernya; bukan default ungu/indigo tanpa alasan) |  |
| Font | (system stack / nama font) |  |
| Radius & bentuk | (mis. 6px kontrol, 10px kartu) |  |
| Mode gelap | ya (disetel) / tidak untuk MVP |  |
| Set ikon | (satu library) |  |
| Suara teks | kamu / Anda; santai / formal |  |

- **Tiga layar terpenting:**
- **Pola rujukan** (produk yang polanya ditiru, bukan tampilannya):
- **Keadaan yang wajib dirancang:** loading, kosong, error, sukses, sebagian, tanpa izin.
- **Aksesibilitas:** WCAG 2.2 AA; keyboard, kontras, label, target sentuh.

### Glosarium istilah UI

| Istilah yang dipakai | Bukan | Arti |
|---|---|---|
| (mis. Pelanggan) | (customer, klien, kontak) |  |

## 11. Batasan, risiko, dan asumsi

| Jenis | Isi | Dampak | Mitigasi |
|---|---|---|---|
| Batasan |  |  |  |
| Risiko |  |  |  |
| Asumsi |  |  |  |

## 12. Keputusan produk

| Tanggal | Keputusan | Alasan | Alternatif yang ditolak |
|---|---|---|---|
|  |  |  |  |

## 13. Pertanyaan terbuka

- 

## 14. Di luar lingkup untuk sekarang (backlog)

| Ide | Nilai | Usaha | Keputusan |
|---|---|---|---|
|  |  |  |  |
