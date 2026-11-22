# Rekayasa Teknis Tingkat Senior

Cara developer senior menulis software: memilih teknologi terbaik **pada saat itu**, pola arsitektur, data, API, frontend, dan error handling. Prinsip dan pola di dokumen ini tahan lama. **Nama teknologi dan nomor versi di dalamnya hanya potret (November 2026) untuk titik awal, bukan kebenaran.** Teknologi terbaru dan terbaik ditentukan lewat riset langsung setiap kali skill ini dipakai, dengan protokol di §0.

## 0. Protokol "teknologi terbaru saat ini" (wajib di Fase 0–2)

Jangan memilih stack dari ingatan atau dari tabel di dokumen ini. Lakukan langkah ini setiap proyek baru, dan setiap kali menambah teknologi baru yang penting:

1. **Tanggal hari ini** diketahui dari konteks sesi. Semua pencarian memakai tahun/bulan saat ini.
2. **Cari lanskap terkini** untuk jenis produk ini (web search): "best [framework/stack] for [jenis produk] [tahun]", hasil survei terbaru (State of JS/CSS, Stack Overflow Developer Survey, JetBrains, Thoughtworks Radar), dan catatan rilis framework utama. Utamakan sumber resmi dan survei, lalu perbandingan dari praktisi. Waspadai artikel promosi dan tulisan yang sudah lama.
3. **Ambil versi stabil terbaru langsung dari registry**, bukan dari ingatan:
   ```bash
   python3 scripts/cek_versi.py next react tailwindcss          # npm
   python3 scripts/cek_versi.py --pypi fastapi pydantic         # PyPI
   python3 scripts/cek_versi.py --crates axum                   # crates.io
   python3 scripts/cek_versi.py --node                          # Node LTS aktif
   ```
   Jika tidak ada jaringan, pakai `npm view <paket> version`, `pip index versions <paket>`, atau `cargo search`; jika tetap tidak bisa, katakan terus terang bahwa versi tidak terverifikasi.
4. **Baca dokumentasi resmi versi itu** (getting started + migration guide mayor terakhir). API dan konvensi sering berubah antar-mayor; pola yang kamu ingat bisa sudah usang.
5. **Uji kecocokan:** apakah versi-versi itu saling kompatibel (peer dependency), apakah runtime di hosting yang dipilih mendukungnya, dan apakah ada advisori keamanan terbuka.
6. **Pilih berdasarkan kriteria, bukan tren:**

   | Kriteria | Pertanyaan |
   |---|---|
   | Kematangan | Rilis stabil (bukan alpha/beta/canary), sudah dipakai produksi luas? |
   | Perawatan | Rilis dalam ~6 bulan terakhir, isu ditanggapi, ada lebih dari satu maintainer atau perusahaan di belakangnya? |
   | Kecocokan | Memenuhi kebutuhan produk ini tanpa fitur spekulatif? |
   | Biaya total | Deploy, belajar, dan merawatnya murah bagi user? Ada jalan keluar (tidak terkunci vendor)? |
   | Ekosistem | Dokumentasi, library pendukung, dan komunitas cukup? |
   | Keamanan | Rekam jejak advisori, dukungan LTS/patch? |
   | Lingkungan | Berjalan di lingkungan user dan hosting yang dipilih? |

7. **Catat hasilnya** di `docs/02-arsitektur.md` (ADR): teknologi, versi yang diverifikasi, **tanggal verifikasi**, sumber, alasan, dan alternatif yang ditolak. Tanggal ini membuat keputusan bisa diaudit dan diperbarui.

Aturan pelengkap:

- **Stabil mengalahkan terbaru.** "Terbaru" berarti rilis stabil terbaru dari lini yang matang. Jangan memakai pra-rilis untuk produksi; jangan memakai rilis mayor yang baru keluar dalam hitungan hari tanpa alasan kuat, dan tunggu patch pertama bila risikonya tinggi.
- **Teknologi baru yang menjanjikan** boleh dipakai jika lolos kriteria di atas dan keunggulannya nyata bagi produk ini. Jika tidak, catat sebagai kandidat di backlog.
- **Project yang sudah ada:** jangan upgrade mayor tanpa alasan dan persetujuan; rencanakan upgrade sebagai pekerjaan terpisah dengan migration guide dan tes.
- **Lingkungan terbatas (misalnya Termux/Android):** pilih runtime yang tersedia di sana, atau jalankan build di CI/layanan remote.

## 1. Memilih teknologi seperti senior

- **Boring by default.** Pilih teknologi yang matang, terdokumentasi, dan banyak dipakai. Yang baru boleh dipakai jika memecahkan masalah nyata yang tidak bisa dipecahkan yang lama.
- **Satu cara untuk satu hal.** Satu library state server, satu library form, satu set ikon, satu ORM. Dua cara untuk hal yang sama adalah tanda project tanpa pemimpin.
- **Ikuti versi stabil terbaru** hasil protokol §0, dengan API yang direkomendasikan dokumentasi saat ini, bukan pola lama dari tutorial atau ingatan.
- **Baca changelog/migration guide** sebelum memakai framework yang baru naik major (misalnya Next.js 16 mengganti `middleware.ts` menjadi `proxy.ts`).
- **Jangan mencampur generasi.** Misalnya jangan memakai `tailwind.config.js` gaya v3 di project Tailwind v4, Pages Router dan App Router sekaligus tanpa alasan migrasi, atau `moment.js` di samping `Intl`/`date-fns`.

## 2. Potret stack sebagai titik awal (November 2026; verifikasi dengan §0)

Tabel ini hanya **hipotesis awal** untuk dipercepat riset. Jika hasil §0 menunjukkan ada yang lebih baik, sudah usang, atau diganti, ikuti hasil riset dan tulis alasannya di ADR.

| Kebutuhan | Default yang sehat | Alternatif bagus | Hindari untuk project baru |
|---|---|---|---|
| Runtime JS | Node.js LTS (24; 26 masuk LTS Okt 2026) | Bun/Deno jika platform mendukung penuh | Node versi non-LTS/EOL |
| Bahasa web | TypeScript `strict` | — | JavaScript tanpa tipe untuk app > kecil |
| Web app full-stack | Next.js 16 (App Router, Server Components) | SvelteKit, React Router v7 (framework mode), Nuxt | Pages Router untuk project baru, Create React App |
| Situs konten/marketing | Astro | Next.js static | SPA untuk halaman yang seharusnya statis |
| SPA/internal tool | Vite + React (+ TanStack Router/Query) | Vite + Svelte/Vue | Webpack config manual |
| Styling | Tailwind CSS v4 (konfigurasi CSS-first `@theme`) | CSS Modules / vanilla CSS dengan custom properties | Campuran beberapa sistem styling |
| Komponen UI | shadcn/ui (kode milik sendiri, di atas Radix/Base UI) atau React Aria | Mantine, Chakra v3 | Komponen kustom dari nol untuk dialog/menu/combobox |
| Ikon | Lucide (satu set saja) | Phosphor, Tabler | Emoji sebagai ikon, campuran set ikon |
| Validasi | Zod (TS), Pydantic v2 (Python) | Valibot, ArkType | Validasi manual dengan `if` berserakan |
| Database | PostgreSQL (17/18) | SQLite (single-user/lokal/edge) | NoSQL untuk data relasional |
| ORM/query | Drizzle atau Prisma (TS); SQLAlchemy 2 / SQLModel (Python) | Kysely, query SQL langsung | String concat SQL |
| Auth | Terkelola (Clerk, Supabase Auth, Firebase Auth) atau library matang (Better Auth, Auth.js) | Keycloak/Zitadel untuk SSO | Auth buatan sendiri |
| State server di client | Loader/Server Components framework; TanStack Query untuk SPA | SWR | `useEffect` + `fetch` + `useState` manual |
| Form | Server Actions + Zod, atau React Hook Form + Zod | TanStack Form, Conform | State form manual per field |
| Tanggal/waktu | `Intl` + `date-fns`/`Temporal` (bila tersedia) | Day.js | moment.js |
| Tes JS | Vitest + Testing Library; Playwright untuk e2e | `node --test` | Jest baru untuk project Vite |
| Python | Python 3.13/3.14, `uv` (env + lock), `ruff` (lint + format), `pytest`, `mypy`/`pyright` | Poetry | `pip install` tanpa lock, black+isort+flake8 terpisah |
| API Python | FastAPI + Pydantic v2 | Django (+ DRF/Ninja) untuk app dengan admin besar, Litestar | Flask untuk API baru yang besar |
| Mobile | Expo (SDK 56, React Native New Architecture, Expo Router) | Flutter | React Native tanpa Expo untuk tim kecil, Cordova |
| Job/antrean | Cron platform, Inngest/Trigger.dev, pg-boss/Graphile Worker, Celery/RQ | BullMQ (butuh Redis) | `setInterval` di proses web |
| Logging | pino (Node), structlog/logging JSON (Python) | OpenTelemetry untuk tracing | `console.log` di produksi |
| Error tracking | Sentry | GlitchTip, Highlight | Tidak ada |

Kalau project sudah memakai stack lain yang sehat, ikuti stack itu. Tabel ini untuk project baru.

## 3. Arsitektur kode

### 3.1 Modular monolith, dikelompokkan per fitur

```text
src/
├── app/                  # routing/entry (halaman, route handler) — tipis
├── features/
│   ├── customers/
│   │   ├── components/   # UI khusus fitur
│   │   ├── actions.ts    # mutasi (server actions / handler)
│   │   ├── queries.ts    # baca data
│   │   ├── schema.ts     # Zod schema + tipe
│   │   ├── service.ts    # aturan bisnis murni (mudah dites)
│   │   └── *.test.ts
│   └── debts/
├── components/ui/        # komponen sistem desain (button, input, dialog)
├── lib/                  # infrastruktur: db, auth, logger, env, format
└── db/                   # skema + migrasi
```

Aturan:

- **Kelompokkan per fitur, bukan per jenis file.** Folder `controllers/`, `services/`, dan `models/` global cepat menjadi tempat sampah.
- **Arah dependensi satu arah:** `app` → `features` → `lib`. Fitur tidak mengimpor isi dalam fitur lain; bagikan lewat ekspor publik atau pindahkan ke `lib`.
- **Handler tipis, logika di service.** Route/action hanya melakukan parse input → panggil service → bentuk respons. Aturan bisnis berupa fungsi murni yang dites tanpa HTTP/DB.
- **Tidak ada `utils.ts` raksasa.** Beri nama sesuai isinya: `format-currency.ts`, `slugify.ts`.
- File > ~300–400 baris atau fungsi > ~50 baris adalah sinyal untuk dipecah, bukan aturan mati.

### 3.2 Konfigurasi dan environment

- Satu modul `env` yang mem-parse `process.env`/`os.environ` dengan skema saat start. Aplikasi gagal start dengan pesan jelas jika ada yang kurang.
- Kode lain mengimpor `env.DATABASE_URL`, bukan membaca `process.env` di mana-mana.
- Variabel yang boleh terlihat di browser diberi prefiks eksplisit (`NEXT_PUBLIC_`, `VITE_`) dan **tidak pernah** berisi secret.

## 4. Tipe dan kebenaran

- TypeScript: `"strict": true`, `"noUncheckedIndexedAccess": true`, `"noImplicitOverride": true`. Tanpa `any`; gunakan `unknown` lalu persempit tipenya. `@ts-ignore` dilarang; jika terpaksa, pakai `@ts-expect-error` dengan alasan.
- **Parse, don't validate:** data dari luar (request, form, env, webhook, API pihak ketiga, `localStorage`) di-parse dengan skema menjadi tipe yang benar di batas sistem. Di dalam sistem, tipe dipercaya dan tidak dicek ulang.
- Modelkan status sebagai **discriminated union**, bukan kumpulan boolean:
  ```ts
  type Payment =
    | { status: "pending"; orderId: string }
    | { status: "paid"; orderId: string; paidAt: Date }
    | { status: "failed"; orderId: string; reason: string };
  ```
  Gunakan `switch` dengan pemeriksaan exhaustive (`const _: never = x`).
- Satu sumber kebenaran untuk tipe: turunkan tipe dari skema (`z.infer`) atau dari skema DB, jangan menulis ulang.
- Python: type hints di semua fungsi publik, `mypy --strict` atau `pyright` mode strict untuk modul inti, dan Pydantic untuk batas sistem.

## 5. Data dan database

### 5.1 Desain skema

- **Primary key:** `bigint generated always as identity` untuk internal, atau UUIDv7 (`uuidv7()` di PostgreSQL 18) jika ID terlihat publik/dibuat di client. Jangan mengekspos ID berurutan untuk data sensitif.
- `created_at`/`updated_at` bertipe `timestamptz` dengan default `now()`. Simpan dalam UTC.
- Default `NOT NULL`; nullable hanya jika "tidak ada nilai" memang bermakna.
- Aturan bisnis ditegakkan **di database juga**: `UNIQUE`, `CHECK (amount >= 0)`, `FOREIGN KEY ... ON DELETE` yang disengaja (`RESTRICT`/`CASCADE`/`SET NULL`).
- Uang sebagai `bigint` satuan terkecil (rupiah tidak punya sen, jadi cukup integer rupiah) atau `numeric(14,2)` untuk mata uang dengan desimal. **Tidak pernah float.**
- Enum kecil yang stabil → `CHECK`/enum DB. Daftar yang bisa diubah admin → tabel.
- Soft delete (`deleted_at`) hanya jika benar-benar dibutuhkan (pemulihan/audit). Jika dipakai, semua query dan unique index harus memperhitungkannya.
- Multi-tenant: kolom `tenant_id`/`owner_id` di setiap tabel milik tenant, ikut dalam index, dan (T3) Row Level Security.

### 5.2 Query dan performa

- Index untuk setiap kolom yang dipakai di `WHERE`, `JOIN`, dan `ORDER BY` query utama, termasuk foreign key. Cek dengan `EXPLAIN ANALYZE`.
- Hindari N+1: ambil relasi dengan join/`include`/batch, bukan query di dalam loop.
- Pagination: cursor/keyset (`WHERE (created_at, id) < (?, ?) ORDER BY created_at DESC, id DESC LIMIT 20`) untuk daftar yang besar; offset hanya untuk data kecil.
- Pilih kolom yang dibutuhkan saja; jangan `SELECT *` untuk respons API.
- Transaksi untuk operasi multi-langkah. Untuk operasi bersamaan pada baris yang sama (saldo, stok), gunakan `SELECT ... FOR UPDATE`, update atomik (`SET stock = stock - 1 WHERE stock > 0`), atau optimistic locking (kolom `version`).
- Serverless: pakai connection pooler (PgBouncer/pooler bawaan penyedia). Jangan membuka koneksi baru per request tanpa pool.

### 5.3 Migrasi

- Setiap perubahan skema lewat file migrasi berversi yang di-commit. Jangan pernah mengubah skema produksi dengan tangan.
- Migrasi harus bisa dijalankan di DB kosong (CI) dan di DB berisi data (staging).
- Perubahan yang merusak memakai pola expand/contract (`panduan-deploy.md`).
- Seed data untuk pengembangan dibuat realistis (nama Indonesia, nominal masuk akal, jumlah data cukup untuk melihat pagination), bukan "test1, test2".

## 6. Desain API

- REST yang konsisten: kata benda jamak (`/customers/{id}/debts`), metode sesuai makna (`GET` aman, `PUT` idempoten, `POST` membuat, `PATCH` sebagian, `DELETE`).
- Status code yang benar: `200/201/204`, `400` (input rusak), `401` (belum login), `403` (tidak berizin), `404`, `409` (konflik), `422` (validasi gagal), `429` (rate limit), `500`.
- Format error tunggal, idealnya **Problem Details (RFC 9457)**:
  ```json
  { "type": "https://app.example/errors/validation", "title": "Data tidak valid",
    "status": 422, "detail": "Nominal harus lebih dari 0.", "errors": { "amount": ["Harus > 0"] } }
  ```
- Validasi request dengan skema; tolak field tak dikenal untuk endpoint sensitif (cegah mass assignment).
- `Idempotency-Key` untuk `POST` yang membuat transaksi/pembayaran.
- Pagination wajib untuk koleksi; batas maksimum `limit`.
- Penamaan JSON konsisten (pilih `camelCase` atau `snake_case`, jangan campur). Tanggal dalam ISO 8601 UTC.
- Dokumentasi otomatis (OpenAPI dari FastAPI/zod-openapi) untuk API yang dipakai pihak lain.
- Untuk app full-stack satu tim, Server Actions/RPC bertipe (tRPC, oRPC) boleh menggantikan REST publik. Aturan validasi, auth, dan error tetap berlaku.

## 7. Frontend dan React

- **Server dulu.** Di Next.js App Router, komponen adalah Server Component secara default. Tambahkan `"use client"` hanya pada komponen interaktif yang kecil, sedalam mungkin di pohon komponen.
- **Data diambil di server/loader**, bukan di `useEffect`. Untuk SPA, gunakan TanStack Query (cache, retry, invalidasi).
- **`useEffect` bukan untuk menurunkan state.** Nilai turunan dihitung saat render. Effect hanya untuk sinkronisasi dengan sistem luar (subscription, DOM, analytics).
- **React Compiler** (stabil sejak 1.0) menangani memoisasi. Jangan menaburkan `useMemo`/`useCallback` tanpa ukuran; pakai hanya sebagai escape hatch setelah profiling.
- State: lokal dulu (`useState`), angkat bila perlu, URL untuk filter/pencarian/tab (bisa dibagikan dan bertahan saat refresh), dan store global (Zustand) hanya untuk state UI lintas halaman yang benar-benar global.
- Mutasi: tampilkan status pending, cegah double-submit, dan revalidasi data setelah sukses. Optimistic update hanya bila rollback-nya jelas.
- Error boundary dan `loading`/`Suspense` per segmen halaman, bukan satu untuk seluruh aplikasi.
- `key` stabil dari ID data, bukan index array, untuk list yang bisa berubah.
- Gambar responsif dengan ukuran eksplisit (`next/image` atau `<img width height srcset loading="lazy">`). Font di-host sendiri dengan `font-display: swap` (`next/font`).
- Bundle: impor bernama dari library besar, dynamic import untuk komponen berat (chart, editor), dan cek ukuran bundle setelah menambah dependency.

## 8. Error handling yang matang

- Bedakan **error yang diharapkan** (validasi gagal, tidak ditemukan, tidak berizin, stok habis) dari **bug/kegagalan infrastruktur**.
  - Error yang diharapkan dikembalikan sebagai nilai/tipe hasil yang jelas dan ditampilkan ke user dengan pesan spesifik.
  - Bug dilempar, ditangkap di batas (error handler global/error boundary), di-log dengan konteks, lalu ditampilkan sebagai pesan umum + ID referensi.
- Jangan `try/catch` di setiap fungsi. Tangkap hanya di tempat kamu bisa **melakukan sesuatu**: retry, fallback yang bermakna, menerjemahkan ke pesan user, atau menambah konteks lalu melempar ulang.
- Dilarang: `catch {}` kosong, `catch (e) { console.log(e) }` lalu melanjutkan seolah sukses, dan mengembalikan `null` diam-diam yang membuat error muncul jauh dari sumbernya.
- Pesan error untuk user: apa yang terjadi, apakah datanya aman, dan apa yang bisa dilakukan. Contoh: "Pembayaran belum diterima. Saldo kamu tidak terpotong. Coba lagi dalam beberapa menit."

## 9. Pekerjaan latar belakang dan integrasi

- Pekerjaan > ~1 detik atau yang bergantung pada layanan luar (email, laporan, pemrosesan gambar, sinkronisasi) dijalankan sebagai job, bukan di request user.
- Setiap job idempoten, punya retry dengan backoff + batas, timeout, dan dead-letter/alert saat gagal permanen.
- Webhook masuk: verifikasi → simpan event mentah → balas `2xx` cepat → proses di job.
- Klien API pihak ketiga dibungkus dalam satu modul (`lib/midtrans.ts`) dengan timeout, retry untuk operasi aman, logging, dan tipe respons yang di-parse.

## 10. Lokalisasi dan format (Indonesia)

- Semua format lewat `Intl`: `new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 })` → `Rp 150.000`.
- Tanggal: `Intl.DateTimeFormat("id-ID", { dateStyle: "medium", timeZone: userTz })` → `22 Nov 2026`. Waktu relatif ("3 menit lalu") dengan `Intl.RelativeTimeFormat`, dan waktu absolut tersedia lewat `title`/tooltip.
- Zona waktu user (WIB/WITA/WIT) disimpan di profil atau dideteksi dari browser. Server menyimpan UTC.
- Nomor telepon disimpan dalam format E.164 (`+6281234567890`) dan ditampilkan rapi.
- Teks UI dikumpulkan di satu tempat jika ada rencana multi-bahasa. Jika tidak, minimal konsisten satu bahasa dan satu sapaan (kamu/Anda).
- Pencarian nama: case-insensitive dan toleran spasi (`ILIKE`/`unaccent`/full-text search).

## 11. Observability di dalam kode

- Logger terstruktur tunggal (`lib/logger`) dengan level. Setiap log membawa `requestId`, `userId` (ID, bukan email), dan konteks operasi.
- Log di batas: request masuk/keluar (method, path, status, durasi), panggilan layanan luar (durasi, status), job (mulai, selesai, gagal), dan event keamanan.
- Jangan log body request mentah, token, password, atau PII.
- Health check: `/healthz` (proses hidup) dan, bila perlu, `/readyz` (DB tersambung).
- Error tracking (Sentry) dengan source maps yang **tidak** dipublikasikan ke browser, serta release/commit tag.

## 12. Developer experience yang menandakan project profesional

- `README` quick start yang benar-benar berjalan di mesin bersih: clone → copy env → install → migrate → seed → dev.
- Script konsisten: `dev`, `build`, `start`, `test`, `test:e2e`, `lint`, `format`, `typecheck`, `db:migrate`, `db:seed`.
- Seed data realistis + akun demo untuk mencoba semua peran.
- `.editorconfig`/formatter yang sama untuk semua orang; hook pre-commit ringan (format + lint file yang berubah) bila tim > 1.
- Tidak ada file sampah di repo: `.DS_Store`, log, build output, dump DB, atau file `test.js`/`coba.py` sementara.

## 13. Checklist teknis sebelum menyatakan selesai

- [ ] Protokol §0 dijalankan: versi diambil dari registry, dokumentasi resmi dibaca, ADR mencatat versi + tanggal verifikasi.
- [ ] Tidak ada API usang atau campuran generasi.
- [ ] Tipe strict lulus tanpa `any`/`ts-ignore`.
- [ ] Input dari luar di-parse dengan skema di batas sistem.
- [ ] Skema DB punya constraint, index, dan tipe yang benar (uang bukan float, waktu `timestamptz`).
- [ ] Tidak ada N+1; daftar memakai pagination.
- [ ] Error yang diharapkan vs bug ditangani berbeda; tidak ada catch kosong.
- [ ] Data diambil di server/loader/query library, bukan `useEffect` manual.
- [ ] Format uang/tanggal lewat `Intl` dengan locale `id-ID`.
- [ ] Logger terstruktur, health check, dan error tracking terpasang.
- [ ] README quick start diuji dari nol.
