const API_URL = "http://localhost:5000/api/rekomendasi";

export const kirimJawaban = async (jurusan, jawaban, n_soal = 10) => {
  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ jurusan, jawaban, n_soal }),
    });
    if (!res.ok) throw new Error("Gagal kirim data");
    return await res.json();
  } catch (err) {
    console.error("Error API:", err);
    throw err;
  }
};