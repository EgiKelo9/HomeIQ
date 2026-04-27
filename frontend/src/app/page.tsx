import Link from "next/link";

export default function Home() {
  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-20 top-12 h-72 w-72 rounded-full bg-cyan-400/20 blur-3xl" />
        <div className="absolute right-0 top-0 h-80 w-80 rounded-full bg-emerald-300/15 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-64 w-64 rounded-full bg-amber-200/10 blur-3xl" />
      </div>

      <main className="relative mx-auto flex w-full max-w-6xl flex-1 flex-col px-6 py-16 sm:px-10 lg:px-14">
        <section className="grid gap-10 lg:grid-cols-2 lg:items-center">
          <div className="space-y-6">
            <h1 className="max-w-3xl text-4xl font-black leading-tight sm:text-5xl">
              HomeIQ
            </h1>
            <h3 className="max-w-3xl text-lg font-semibold leading-tight sm:text-xl rounded-md border border-cyan-200/30 bg-cyan-300/10 px-4 py-2.5">
              Dashboard properti Jabodetabek untuk insight, scraping, dan prediksi harga.
            </h3>
            <p className="max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
              HomeIQ menggabungkan data scraping real-estate, analitik pasar, dan model machine learning agar proses riset properti lebih cepat, terukur, dan siap dipakai sebagai dasar keputusan.
            </p>
            <div className="flex flex-col gap-3 pt-2 sm:flex-row">
              <Link
                href="/overview"
                className="inline-flex items-center justify-center rounded-full bg-cyan-300 px-6 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-200"
              >
                Buka Dashboard
              </Link>
              <Link
                href="/model"
                className="inline-flex items-center justify-center rounded-full border border-slate-300/40 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-cyan-200 hover:bg-cyan-200/10"
              >
                Coba Prediksi Harga
              </Link>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-200">
              Cakupan Fitur
            </p>
            <ul className="mt-5 space-y-4 text-sm text-slate-200 sm:text-base">
              <li className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                Overview metrik properti: total listing, rata-rata, median, dan harga tertinggi.
              </li>
              <li className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                Analytics model: R2, MAE, RMSE, feature importance, dan segmentasi pasar.
              </li>
              <li className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                Model prediksi harga rumah berdasarkan fitur bangunan dan lokasi.
              </li>
              <li className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                Scraper manager untuk trigger, monitor, dan ringkasan task crawling.
              </li>
            </ul>
          </div>
        </section>

        <section className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            {
              title: "Overview",
              desc: "Lihat ringkasan data listing terbaru per kota.",
              href: "/overview",
            },
            {
              title: "Analytics",
              desc: "Analisis performa model dan perilaku pasar properti.",
              href: "/analytics",
            },
            {
              title: "Model",
              desc: "Latih model dan lakukan prediksi harga properti.",
              href: "/model",
            },
            {
              title: "Scraper",
              desc: "Kelola sumber data dan progress scraping dari provider.",
              href: "/scraper",
            },
          ].map((item) => (
            <Link
              key={item.title}
              href={item.href}
              className="group rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:-translate-y-1 hover:border-cyan-200/60 hover:bg-cyan-300/10"
            >
              <h2 className="text-lg font-bold text-white">{item.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">{item.desc}</p>
              <p className="mt-4 text-sm font-semibold text-cyan-200 group-hover:text-cyan-100">
                Buka modul
              </p>
            </Link>
          ))}
        </section>

        <section className="mt-16 rounded-3xl border border-emerald-200/30 bg-emerald-300/10 px-6 py-7 sm:px-8">
          <h3 className="text-2xl font-extrabold text-emerald-100">
            Alur pakai yang direkomendasikan
          </h3>
          <p className="mt-2 max-w-3xl text-sm leading-7 text-emerald-50/90 sm:text-base">
            Mulai dari Scraper untuk mengumpulkan data, lanjut ke Overview dan Analytics untuk membaca pola pasar, lalu latih model dan gunakan halaman Model untuk simulasi harga rumah.
          </p>
          <div className="mt-5 flex flex-wrap gap-3 text-sm font-semibold">
            <Link
              href="/scraper"
              className="rounded-full bg-emerald-200 px-5 py-2 text-emerald-950 transition hover:bg-emerald-100"
            >
              1. Mulai Scraping
            </Link>
            <Link
              href="/analytics"
              className="rounded-full border border-emerald-100/60 px-5 py-2 text-emerald-50 transition hover:bg-emerald-200/20"
            >
              2. Baca Analytics
            </Link>
            <Link
              href="/model"
              className="rounded-full border border-emerald-100/60 px-5 py-2 text-emerald-50 transition hover:bg-emerald-200/20"
            >
              3. Latih Model
            </Link>
            <Link
              href="/model"
              className="rounded-full border border-emerald-100/60 px-5 py-2 text-emerald-50 transition hover:bg-emerald-200/20"
            >
              4. Prediksi Harga
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
