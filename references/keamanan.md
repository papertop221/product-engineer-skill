# Keamanan per Tingkat Risiko

Acuan utama: **OWASP Top 10:2025** (risiko web paling umum), **OWASP ASVS 5.0** (standar verifikasi; L1 → L2 → L3 bersifat kumulatif), **NIST SP 800-63B-4** (autentikasi), dan **OWASP Top 10 for LLM Applications 2025**. Tujuannya bukan sertifikasi, tetapi memastikan tidak ada lubang yang umum dan mahal.

Aturan dasar:

- **T1** → semua item bertanda •.
- **T2** → • + ◆ (setara bagian relevan ASVS L2 untuk auth, akses, dan data).
- **T3** → • + ◆ + ★, ditambah review keamanan independen.

Catat hasilnya di `docs/04-kualitas.md` (security baseline + log verifikasi).

## 1. Threat model ringan (wajib T2/T3, disarankan T1)

Lima belas menit cukup. Jawab empat pertanyaan:

1. **Apa yang kita bangun?** Gambar alur data: user → UI → API → DB → layanan luar. Tandai batas kepercayaan (di mana data dari luar masuk).
2. **Apa yang bisa salah?** Untuk setiap batas, pakai STRIDE:

| Ancaman | Pertanyaan | Mitigasi umum |
|---|---|---|
| **S**poofing | Bisakah seseorang menyamar sebagai user lain/sistem lain? | Auth kuat, verifikasi signature webhook |
| **T**ampering | Bisakah data diubah di jalan atau di client? | HTTPS, validasi server, integritas (HMAC/signature) |
| **R**epudiation | Bisakah seseorang menyangkal melakukan aksi? | Audit log aksi penting |
| **I**nformation disclosure | Bisakah data bocor? | Otorisasi per objek, enkripsi, minimisasi data, log tanpa PII |
| **D**enial of service | Bisakah layanan dibuat lumpuh/mahal? | Rate limit, batas ukuran, timeout, budget alert |
| **E**levation of privilege | Bisakah user biasa menjadi admin? | Cek peran di server, least privilege, deny by default |

3. **Apa yang kita lakukan?** Tulis mitigasi per ancaman.
4. **Apakah sudah cukup?** Tandai yang diterima sebagai risiko dan alasannya.

Simpan di `docs/02-arsitektur.md` bagian threat model.

## 2. OWASP Top 10:2025 — checklist praktis

### A01 — Broken Access Control (termasuk SSRF)

- • Deny by default; setiap endpoint menyatakan siapa yang boleh mengaksesnya.
- • Cek kepemilikan **setiap objek** di server: `WHERE id = ? AND owner_id = current_user`. Jangan cukup memeriksa ID dari URL. Ini mencegah IDOR.
- • Menyembunyikan tombol di UI tidak dihitung sebagai kontrol akses.
- ◆ Tes otomatis: user A mencoba membaca/mengubah/menghapus data user B → harus ditolak (403/404).
- ◆ Admin dipisah dari user biasa; aksi admin dicatat di audit log.
- ◆ SSRF: jika server mengambil URL dari input user, pakai allowlist domain dan blokir IP privat/metadata (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`, `::1`).
- ★ Multi-tenant: isolasi tenant ditegakkan di query/row-level security, bukan hanya di kode aplikasi.

### A02 — Security Misconfiguration

- • Debug mati di produksi; halaman error tidak menampilkan stack trace atau versi.
- • Tidak ada kredensial default; endpoint admin/dev tidak terbuka ke publik.
- • Header keamanan untuk web:
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Content-Security-Policy` (mulai dari `default-src 'self'`, lalu longgarkan seperlunya; hindari `unsafe-inline` untuk script)
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `frame-ancestors 'none'` di CSP (atau `X-Frame-Options: DENY`)
  - `Permissions-Policy` untuk mematikan fitur yang tidak dipakai
- • CORS: allowlist origin yang jelas; jangan pernah `*` bersama credentials.
- • Bucket/storage tidak publik kecuali memang untuk aset publik.
- ◆ Konfigurasi dibedakan per environment; staging tidak memakai secret produksi.

### A03 — Software Supply Chain Failures

- • Lockfile di-commit; install di CI memakai mode lock (`npm ci`, `pip install --require-hashes` atau `uv sync --locked`, `cargo build --locked`).
- • Sebelum menambah dependency: cek bahwa package ada, namanya benar (waspadai typosquatting/slopsquatting), terawat, lisensinya cocok, dan jumlah dependency transitifnya wajar.
- • Audit dependency di CI (`npm audit`, `pip-audit`, `cargo audit`, `govulncheck`). Kritis/tinggi memblokir rilis kecuali ada alasan tercatat.
- • Dependency yang tidak dipakai dihapus.
- ◆ Bot update dependency (Dependabot/Renovate) aktif; update keamanan diproses dalam ≤ 7 hari.
- ◆ Versi GitHub Actions/plugin CI di-pin; token CI dengan izin minimum.
- ★ SBOM dibuat saat rilis (misalnya CycloneDX/SPDX); artefak rilis ditandatangani bila platform mendukung.

### A04 — Cryptographic Failures

- • HTTPS di mana-mana; redirect HTTP → HTTPS.
- • Jangan membuat kriptografi sendiri. Gunakan library standar platform.
- • Password: Argon2id (disarankan) atau bcrypt; tidak pernah dalam bentuk reversibel.
- • Token acak dari CSPRNG (`crypto.randomBytes`, `secrets.token_urlsafe`, dan sejenisnya), bukan `Math.random`.
- ◆ Data sensitif dienkripsi saat disimpan (biasanya fitur bawaan database/platform terkelola). Backup juga dienkripsi.
- ★ Kunci enkripsi di KMS/secret manager dan punya prosedur rotasi.

### A05 — Injection

- • SQL: query berparameter/ORM. Jangan pernah menyusun SQL dari string input.
- • Shell: hindari; jika terpaksa, gunakan array argumen tanpa shell (`execFile`, `subprocess.run([...], shell=False)`).
- • Path: normalisasi lalu pastikan tetap di dalam folder yang diizinkan (cegah `../`).
- • HTML: gunakan templating yang auto-escape; hindari `innerHTML`/`dangerouslySetInnerHTML`. Jika HTML dari user harus ditampilkan, sanitasi dengan library matang (misalnya DOMPurify).
- • Validasi input di server dengan skema (Zod, Pydantic, serde, dan sejenisnya): tipe, panjang, format, rentang, serta allowlist untuk enum.

### A06 — Insecure Design

- • Batas bisnis ditegakkan di server: stok tidak bisa negatif, harga diambil dari server (bukan dari client), kupon hanya bisa dipakai sekali.
- • Rate limit pada aksi mahal atau yang bisa disalahgunakan (login, OTP, reset, signup, kirim email/SMS, panggilan AI).
- ◆ Threat model untuk fitur sensitif (lihat §1).
- ◆ Aksi destruktif atau berbiaya memerlukan konfirmasi, dan bila memungkinkan bisa dibatalkan (soft delete + masa tenggang).
- ★ Pemisahan tugas untuk aksi bernilai tinggi (misalnya refund besar memerlukan persetujuan kedua).

### A07 — Authentication Failures

Default: **auth terkelola** (Supabase Auth, Clerk, Auth0, Firebase Auth, Auth.js dengan provider, dan sejenisnya). Jika membangun sendiri, terapkan NIST SP 800-63B-4:

- • Panjang minimal 15 karakter jika password satu-satunya faktor; 8 jika dipakai bersama MFA. Izinkan sampai ≥ 64 karakter, termasuk spasi dan Unicode.
- • **Tanpa** aturan komposisi paksa (wajib simbol/angka) dan **tanpa** kedaluwarsa berkala. Ganti hanya jika ada indikasi bocor.
- • Tolak password yang ada di daftar password umum/bocor.
- • Rate limit/lockout bertahap untuk percobaan login gagal.
- • Pesan error login generik ("email atau password salah").
- • Session: ID baru setelah login, cookie `HttpOnly; Secure; SameSite=Lax` (atau `Strict`), ada timeout idle dan absolut, dan logout menghapus session di server.
- • Reset password: token sekali pakai, berumur pendek, di-hash di database, dan semua session lain dibatalkan setelah reset.
- ◆ MFA tersedia (TOTP/passkey). Admin wajib MFA di T3.
- ◆ Dukung passkey (WebAuthn) bila auth terkelola menyediakannya.
- ◆ Verifikasi email sebelum aksi yang bergantung pada kepemilikan email.

### A08 — Software or Data Integrity Failures

- • Webhook (pembayaran, bot, dan sejenisnya) diverifikasi signature/secret-nya sebelum diproses, lalu diproses secara idempoten (simpan event ID).
- • Jangan men-deserialize data tidak tepercaya ke objek (pickle, Java serialization, `yaml.load` tanpa safe loader).
- • Script pihak ketiga dari CDN memakai Subresource Integrity (`integrity=`), atau di-host sendiri.
- ◆ Auto-update aplikasi desktop/mobile hanya dari sumber yang ditandatangani.
- ★ Pipeline CI terlindungi: branch protection, review wajib, dan tidak ada secret produksi di job PR dari fork.

### A09 — Security Logging & Alerting Failures

- • Log terstruktur untuk event keamanan: login sukses/gagal, perubahan password/email, perubahan izin, aksi admin, dan pembayaran.
- • **Jangan** log password, token, nomor kartu, OTP, isi `.env`, atau data pribadi lengkap. Samarkan bila perlu (`****1234`).
- ◆ Alert untuk lonjakan login gagal, lonjakan error 5xx, dan kegagalan webhook pembayaran.
- ◆ Audit log tidak bisa diubah oleh user biasa dan punya retensi yang jelas.

### A10 — Mishandling of Exceptional Conditions

- • *Fail closed*: jika pengecekan izin, verifikasi signature, atau layanan auth error, **tolak** aksesnya.
- • Error handler global: user melihat pesan ramah + ID referensi, sedangkan detail error masuk ke log.
- • Semua panggilan luar punya timeout. Retry hanya untuk operasi idempoten, dengan backoff dan batas.
- • Transaksi di-rollback saat error; tidak ada status setengah jadi (misalnya pesanan "lunas" tanpa pembayaran tercatat).
- • Uji jalur error: database mati, API luar 500/timeout, disk penuh, dan input yang membuat parser gagal.

## 3. Secrets

- • Secret hanya di environment/secret manager platform. `.env` masuk `.gitignore`; `.env.example` berisi nama variabel dan nilai palsu.
- • Frontend tidak pernah memegang secret. Semua yang dikirim ke browser/aplikasi mobile dianggap publik.
- • Aplikasi gagal start dengan jelas jika secret wajib tidak ada.
- • Jika secret bocor (ter-commit, masuk log/chat): **rotasi segera**, cabut yang lama, lalu bersihkan history bila perlu.
- ◆ Secret berbeda per environment; akses dibatasi ke yang membutuhkan.

## 4. Data pribadi dan privasi (teknis)

- • Kumpulkan seminimal mungkin. Setiap field data pribadi punya alasan pemakaian.
- • Klasifikasikan data di `docs/01-rencana-produk.md`: publik / internal / pribadi / sensitif.
- ◆ User bisa mengekspor dan menghapus datanya. Penghapusan juga menjangkau backup sesuai retensi.
- ◆ Retensi data didefinisikan, dan data lama dihapus otomatis.
- ◆ Data produksi tidak disalin ke staging/lokal tanpa anonimisasi.
- ★ Data sensitif (kesehatan, keuangan, biometrik, anak) dienkripsi di tingkat field, aksesnya dicatat, dan lokasi penyimpanannya dipertimbangkan sesuai regulasi.

Aspek hukumnya (UU PDP, persetujuan, pemberitahuan kebocoran) ada di `siap-publik.md`.

## 5. Upload file

- • Batasi ukuran dan tipe. Cek isi file (magic bytes), bukan hanya ekstensi atau `Content-Type`.
- • Nama file dibuat server (UUID); nama asli hanya disimpan sebagai metadata.
- • Simpan di object storage / di luar webroot. Jangan pernah mengeksekusi file upload.
- • Unduhan file privat lewat URL bertanda tangan yang berumur pendek.
- ◆ Gambar diproses ulang (re-encode) untuk membuang metadata EXIF seperti lokasi GPS.
- ★ Pindai malware untuk file yang dibagikan ke user lain.

## 6. API

- • Auth di setiap endpoint non-publik; otorisasi per objek (A01).
- • Batasi ukuran body, jumlah item per halaman (pagination wajib), dan kedalaman query (GraphQL).
- • Format error konsisten tanpa detail internal.
- • Rate limit per IP dan per user.
- ◆ Kunci API milik user di-hash di database dan bisa dicabut.
- ◆ Idempotency key untuk endpoint yang membuat transaksi.

## 7. Mobile

- • Tidak ada secret di dalam APK/IPA. Semua yang ada di aplikasi bisa diekstrak.
- • Token disimpan di Keystore/Keychain (secure storage), bukan di SharedPreferences/AsyncStorage biasa.
- • Hanya HTTPS. Jangan menonaktifkan validasi sertifikat, termasuk di build debug yang bisa bocor ke rilis.
- • Izin (permission) diminta seminimal mungkin dan saat dibutuhkan.
- ◆ Deep link divalidasi; WebView tidak mengaktifkan JavaScript bridge ke konten yang tidak tepercaya.
- • Signing key rilis disimpan aman dan di-backup. Kehilangan key = tidak bisa update aplikasi (kecuali memakai Play App Signing).

## 8. Fitur AI/LLM — OWASP Top 10 for LLM 2025

| Risiko | Kontrol minimum |
|---|---|
| LLM01 Prompt Injection | Anggap semua input (termasuk dokumen/web yang dibaca model) bisa berisi instruksi jahat; pisahkan instruksi sistem dari data; jangan beri model wewenang lebih dari yang aman jika ia "tertipu" |
| LLM02 Sensitive Information Disclosure | Jangan kirim secret/PII yang tidak perlu ke model; filter output |
| LLM03 Supply Chain | Model/plugin dari sumber resmi; pin versi model |
| LLM04 Data & Model Poisoning | Validasi sumber data untuk RAG/fine-tuning |
| LLM05 Improper Output Handling | Output model = input tidak tepercaya: escape sebelum dirender, validasi skema sebelum dieksekusi, jangan `eval` |
| LLM06 Excessive Agency | Tool seminimal mungkin, izin read-only bila cukup, dan konfirmasi manusia untuk aksi berisiko/berbayar |
| LLM07 System Prompt Leakage | Anggap system prompt bisa bocor; jangan menaruh secret atau aturan akses di sana |
| LLM08 Vector & Embedding Weaknesses | Otorisasi per dokumen pada pencarian RAG (user hanya bisa mengambil dokumen miliknya) |
| LLM09 Misinformation | Tampilkan sumber; tandai jawaban AI; ada jalur koreksi manusia untuk keputusan penting |
| LLM10 Unbounded Consumption | Batas token per request, rate limit per user, budget alert, dan timeout |

Uji dengan prompt berbahaya: "abaikan instruksi sebelumnya", permintaan membocorkan system prompt, dan dokumen yang berisi instruksi tersembunyi.

## 9. Verifikasi keamanan sebelum rilis

| Pemeriksaan | Alat (pilih yang tersedia) | Tingkat |
|---|---|---|
| Secret scan | `gitleaks`, `scripts/audit_rilis.py` | • |
| Audit dependency | `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`, `osv-scanner` | • |
| Header keamanan | `curl -sI https://domain` lalu cocokkan dengan §2 A02 | • |
| SAST | `semgrep --config auto`, CodeQL di GitHub | ◆ |
| Tes otorisasi | Tes otomatis lintas user (A01) | ◆ |
| Review keamanan diff | Skill `security-review` / reviewer terpisah | ◆ |
| DAST ringan | OWASP ZAP baseline scan ke staging | ★ |
| Pentest | Pihak ketiga sebelum skala besar | ★ (rekomendasi ke user) |

Severity temuan:

- **Kritis/Tinggi** → blokir rilis.
- **Sedang** → perbaiki sebelum rilis jika murah; jika tidak, catat dan jadwalkan.
- **Rendah** → masuk backlog.

## 10. Respons kerentanan setelah rilis

- Sediakan kontak keamanan: `security@domain` atau `/.well-known/security.txt` (RFC 9116).
- Advisori dependency kritis ditangani dalam ≤ 7 hari; tinggi ≤ 30 hari.
- Jika ada insiden data pribadi: ikuti runbook di `panduan-deploy.md` dan kewajiban pemberitahuan di `siap-publik.md`.
