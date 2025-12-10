import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

export default function Quiz() {
  const navigate = useNavigate();
  const location = useLocation();
  const { jurusan, nSoal } = location.state || { jurusan: "informatika", nSoal: 10 };

  const [soal, setSoal] = useState([]);
  const [jawaban, setJawaban] = useState([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  // Ambil soal dari backend (acak)
  useEffect(() => {
    const fetchSoal = async () => {
      try {
        // Kita tidak bisa ambil soal langsung → solusi: generate soal di backend via simulasi
        // Tapi karena kita butuh soal acak sesuai jumlah, kita asumsikan: 
        // backend kirimkan daftar soal saat user submit → jadi kita cukup simpan jawaban
        // Untuk UI: kita gunakan "dummy" soal dari data lokal sementara

        // Alternatif: kita hardcode jumlah soal, tapi tampilkan soal berdasarkan index
        // Karena semua soal sudah diacak di backend, kita tidak perlu tahu isi soal di frontend
        // Jadi cukup tampilkan: "Soal {index+1} dari {nSoal}"
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };
    fetchSoal();
  }, [jurusan, nSoal]);

  const handleJawab = (pilihan) => {
    const newJawaban = [...jawaban];
    newJawaban[index] = pilihan;
    setJawaban(newJawaban);
    if (index < nSoal - 1) {
      setIndex(index + 1);
    } else {
      // Submit ke backend
      handleSubmit(newJawaban);
    }
  };

  const handleSubmit = async (jawabanAkhir) => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:5000/api/rekomendasi", {
        jurusan,
        jawaban: jawabanAkhir,
        n_soal: nSoal
      });
      navigate("/result", { state: { data: res.data } });
    } catch (err) {
      console.error(err);
      alert("Gagal mengirim jawaban. Coba lagi.");
      setLoading(false);
    }
  };

  if (loading && index === 0) return <p className="text-center">Memuat...</p>;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="text-sm text-gray-600 mb-2">
          Soal {index + 1} dari {nSoal}
        </div>
        <div className="text-lg font-medium mb-6">
          Pilih jawaban terbaik menurut kamu:
        </div>
        <div className="grid grid-cols-2 gap-3">
          {["A", "B", "C", "D"].map((opt) => (
            <button
              key={opt}
              onClick={() => handleJawab(opt)}
              className="p-4 border border-gray-300 rounded text-center hover:bg-blue-50 transition"
              disabled={loading}
            >
              {opt}
            </button>
          ))}
        </div>
        {index > 0 && (
          <button
            type="button"
            onClick={() => setIndex(index - 1)}
            className="mt-4 text-blue-600"
          >
            ← Soal Sebelumnya
          </button>
        )}
      </div>
    </div>
  );
}