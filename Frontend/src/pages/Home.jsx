import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const [jurusan, setJurusan] = useState("");
  const [nSoal, setNSoal] = useState(10);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!jurusan) return alert("Pilih jurusan dulu!");
    navigate("/quiz", { state: { jurusan, nSoal } });
  };

  const jurusanMap = {
    teknik: "Teknik",
    kesehatan: "Kesehatan",
    informatika: "Informatika"
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 text-center">Mulai Kuis Minat</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Pilih Jurusan</label>
          <select
            value={jurusan}
            onChange={(e) => setJurusan(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          >
            <option value="">-- Pilih --</option>
            <option value="teknik">Teknik</option>
            <option value="kesehatan">Kesehatan</option>
            <option value="informatika">Informatika</option>
          </select>
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 mb-2">Jumlah Soal</label>
          <div className="flex gap-4">
            {[10, 15, 20].map((n) => (
              <label key={n} className="flex items-center">
                <input
                  type="radio"
                  name="nSoal"
                  value={n}
                  checked={nSoal === n}
                  onChange={() => setNSoal(n)}
                  className="mr-2"
                />
                {n}
              </label>
            ))}
          </div>
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Mulai Kuis
        </button>
      </form>
    </div>
  );
}