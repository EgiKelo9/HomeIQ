import Link from "next/link";

export default function Home() {
  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden bg-slate-950 text-slate-100 scroll-smooth">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-20 top-12 h-72 w-72 rounded-full bg-cyan-400/20 blur-3xl" />
        <div className="absolute right-0 top-0 h-80 w-80 rounded-full bg-emerald-300/15 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-64 w-64 rounded-full bg-amber-200/10 blur-3xl" />
      </div>

      {/* Sticky Navbar */}
      <nav className="sticky top-0 z-50 w-full border-b border-white/10 bg-slate-950/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 sm:px-10 lg:px-14">
          <div className="text-lg sm:text-xl font-bold text-cyan-300">
            <Link href="#hero">HomeIQ</Link>
          </div>
          <div className="flex gap-4 sm:gap-6 text-xs sm:text-sm font-medium text-slate-300">
            <Link href="#hero" className="hover:text-cyan-200 transition">Beranda</Link>
            <Link href="#features" className="hover:text-cyan-200 transition">Fitur</Link>
            <Link href="#workflow" className="hover:text-cyan-200 transition">Alur Pakai</Link>
          </div>
        </div>
      </nav>

      <main className="relative mx-auto flex w-full max-w-6xl flex-1 flex-col gap-24 sm:gap-32 px-6 py-12 md:py-20 sm:px-10 lg:px-14">
        {/* Section 1: Hero */}
        <section id="hero" className="grid scroll-mt-28 gap-10 lg:grid-cols-2 lg:items-center pt-4 md:pt-8 mt-0">
          <div className="space-y-6">
            <h1 className="max-w-3xl text-4xl font-black leading-tight sm:text-5xl md:text-6xl">
              HomeIQ
            </h1>
            <h3 className="max-w-3xl text-base sm:text-lg font-semibold leading-tight rounded-md border border-cyan-200/30 bg-cyan-300/10 px-4 py-2.5">
              Dashboard properti Jabodetabek untuk insight, scraping, dan prediksi harga.
            </h3>
            <p className="max-w-2xl text-base leading-7 sm:leading-8 text-slate-300 sm:text-lg">
              HomeIQ menggabungkan data scraping real-estate, analitik pasar, dan model machine learning agar proses riset properti lebih cepat, terukur, dan siap dipakai sebagai dasar keputusan.
            </p>
            <div className="flex flex-col gap-3 pt-4 sm:flex-row w-full sm:w-auto">
              <Link
                href="/overview"
                className="inline-flex w-full sm:w-auto items-center justify-center rounded-full bg-cyan-300 px-6 py-3.5 text-sm font-bold text-slate-950 transition hover:bg-cyan-200"
              >
                Buka Dashboard
              </Link>
              <Link
                href="/model"
                className="inline-flex w-full sm:w-auto items-center justify-center rounded-full border border-slate-300/40 px-6 py-3.5 text-sm font-semibold text-slate-100 transition hover:border-cyan-200 hover:bg-cyan-200/10"
              >
                Coba Prediksi Harga
              </Link>
            </div>
          </div>

          <div className="mt-8 lg:mt-0 rounded-3xl border border-white/10 bg-white/5 p-6 sm:p-8 backdrop-blur-xl">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-200">
              Cakupan Fitur
            </p>
            <ul className="mt-6 space-y-4 text-sm text-slate-200 sm:text-base">
              <li className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 leading-relaxed">
                Overview metrik properti: total listing, rata-rata, median, dan harga tertinggi.
              </li>
              <li className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 leading-relaxed">
                Analytics model: R2, MAE, RMSE, feature importance, dan segmentasi pasar.
              </li>
              <li className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 leading-relaxed">
                Model prediksi harga rumah berdasarkan fitur bangunan dan lokasi.
              </li>
              <li className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 leading-relaxed">
                Scraper manager untuk trigger, monitor, dan ringkasan task crawling.
              </li>
            </ul>
          </div>
        </section>

        {/* Section 2: Features */}
        <section id="features" className="scroll-mt-28 flex flex-col justify-center">
          <div className="mb-10 text-center px-4">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-4">Modul Dashboard</h2>
            <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">Akses cepat ke berbagai modul untuk mengelola data properti.</p>
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
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
              className="group rounded-2xl border border-white/10 bg-white/5 p-6 sm:p-7 transition hover:-translate-y-1 hover:border-cyan-200/60 hover:bg-cyan-300/10 flex flex-col h-full"
            >
              <h2 className="text-lg sm:text-xl font-bold text-white">{item.title}</h2>
              <p className="mt-3 text-sm sm:text-base leading-6 text-slate-300 flex-1">{item.desc}</p>
              <p className="mt-6 text-sm font-semibold text-cyan-200 group-hover:text-cyan-100">
                Buka modul &rarr;
              </p>
            </Link>
          ))}
          </div>
        </section>

        {/* Section 3: Workflow */}
        <section id="workflow" className="scroll-mt-28 flex flex-col justify-center mb-8 md:mb-16">
          <div className="rounded-3xl border border-emerald-200/30 bg-emerald-300/10 px-6 py-10 sm:px-12 sm:py-14 backdrop-blur-sm">
            <h3 className="text-2xl sm:text-3xl font-extrabold text-emerald-100 text-center mb-6">
              Alur pakai yang direkomendasikan
            </h3>
            <p className="max-w-4xl mx-auto text-center text-sm sm:text-base leading-7 sm:leading-8 text-emerald-50/90 mb-10">
              Mulai dari Scraper untuk mengumpulkan data, lanjut ke Overview dan Analytics untuk membaca pola pasar, lalu latih model dan gunakan halaman Model untuk simulasi harga rumah.
            </p>
            <div className="flex flex-col sm:flex-row flex-wrap justify-center gap-3 sm:gap-4 text-sm font-semibold">
              <Link
                href="/scraper"
                className="flex items-center justify-center rounded-full bg-emerald-200 px-6 py-3 sm:py-3.5 text-emerald-950 transition hover:bg-emerald-100 shadow-lg shadow-emerald-500/20"
              >
                1. Mulai Scraping
              </Link>
              <Link
                href="/model"
                className="flex items-center justify-center rounded-full border border-emerald-100/60 px-6 py-3 sm:py-3.5 text-emerald-50 transition hover:bg-emerald-200/20 hover:border-emerald-200 shadow-sm"
              >
                2. Latih Model
              </Link>
              <Link
                href="/model"
                className="flex items-center justify-center rounded-full border border-emerald-100/60 px-6 py-3 sm:py-3.5 text-emerald-50 transition hover:bg-emerald-200/20 hover:border-emerald-200 shadow-sm"
              >
                3. Prediksi Harga
              </Link>
              <Link
                href="/analytics"
                className="flex items-center justify-center rounded-full border border-emerald-100/60 px-6 py-3 sm:py-3.5 text-emerald-50 transition hover:bg-emerald-200/20 hover:border-emerald-200 shadow-sm"
              >
                4. Baca Analytics
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
