import { useLocation } from "react-router-dom";

export default function Result() {
  const location = useLocation();
  const { data } = location.state || {};

  if (!data || data.error) {
    return (
      <div className="text-center text-red-600">
        <h2 className="text-xl font-bold">Terjadi Kesalahan</h2>
        <p>{data?.error || "Tidak ada data hasil."}</p>
      </div>
    );
  }

  const { rekomendasi_utama, ranking } = data;

  return (
    <div className="space-y-8">
      {/* Ranking */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">📊 Hasil Evaluasi Sistem</h2>
        <div className="space-y-2">
          {ranking.map((item, idx) => (
            <div key={item.kode} className="flex justify-between items-center">
              <span className={idx === 0 ? "font-bold text-green-600" : ""}>
                {idx + 1}. {item.nama}
              </span>
              <span className={idx === 0 ? "font-bold" : ""}>
                {item.persen}%
                {idx === 0 && " ✅ REKOMENDASI UTAMA"}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Rekomendasi Akademik */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">🎓 Rekomendasi Akademik</h2>
        <p className="mb-4">
          Berdasarkan hasil evaluasi, kamu paling cocok masuk ke:<br />
          <strong>{rekomendasi_utama.nama}</strong>.
        </p>
        <p className="mb-4">{rekomendasi_utama.summary}</p>
        <div>
          <p className="mb-2">Lihat informasi prodi lengkap di sini:</p>
          <a
            href={rekomendasi_utama.link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            {rekomendasi_utama.link}
          </a>
        </div>
      </div>

      {/* Tombol Ulang */}
      <div className="text-center">
        <a
          href="/"
          className="inline-block px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Coba Lagi
        </a>
      </div>
    </div>
  );
}