import random
import requests
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

GEMINI_API_KEY = "AIzaSyC2aV8fifhkI83aauDUsD_9o7whc_FgFrU"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# === DATA PROGRAM STUDI JTI ===
PRODI_JTI = {
    "kode": ["SIKC", "RPL", "TRK", "TI"],
    "nama": {
        "SIKC": "D4 Sistem Informasi Kota Cerdas",
        "RPL": "D4 Rekayasa Perangkat Lunak",
        "TRK": "D4 Teknologi Rekayasa Komputer",
        "TI": "D3 Teknik Informatika"
    },
    "link": {
        "SIKC": "https://polindra.ac.id/program-studi-s1-sistem-informasi-kota-cerdas/",
        "RPL": "https://polindra.ac.id/program-studi-s1-rekayasa-perangkat-lunak/",
        "TRK": "https://polindra.ac.id/program-studi-s1-terapan-teknologi-rekayasa-komputer/",
        "TI": "https://polindra.ac.id/program-studi-d3-teknik-informatika/"
    }
}

# === BANK SOAL (100+ pertanyaan dibagi 3 kategori) ===
# Setiap kategori punya 35 soal, jadi total 105 soal

BANK_SOAL = []

# ==============================================================================
# BANK SOAL SISTEM PAKAR PENJURUSAN TEKNIK INFORMATIKA (TOTAL 200 SOAL)
# Disusun oleh: AI Expert System Partner
# Pendekatan: Non-Teknis, Real World Case Study, Randomized Weighting
# ==============================================================================

# ------------------------------------------------------------------
# KATEGORI 1: ANALISIS DATA & SISTEM INFORMASI (SIKC/Sistem Informasi)
# Fokus: Organisasi, Pola, Data, Efisiensi, Bisnis Proses
# ------------------------------------------------------------------
analisis_soal = [
    # SOAL 1-35 (Dikutip dari input Anda)
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu ingin mengadakan acara kumpul kelas, tapi teman-temanmu sangat susah mencari waktu yang cocok. Apa yang kamu lakukan?",
        "pilihan": {
            "A": {"text": "Membuat grup chat dan menanyakan satu per satu secara langsung.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 40, "TI": 50}},
            "B": {"text": "Membuat tabel/voting online untuk melihat tanggal mana yang paling banyak dipilih.", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 30, "TI": 50}},
            "C": {"text": "Langsung tentukan satu tanggal dan berharap mereka bisa datang.", "bobot": {"SIKC": 20, "RPL": 30, "TRK": 30, "TI": 20}},
            "D": {"text": "Mencari aplikasi jadwal otomatis yang bisa sinkronisasi kalender.", "bobot": {"SIKC": 70, "RPL": 85, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Saat berbelanja bulanan, bagaimana caramu memastikan uangmu cukup?",
        "pilihan": {
            "A": {"text": "Mencatat pengeluaran di buku/HP dan mengevaluasi di akhir bulan.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 45}},
            "B": {"text": "Menggunakan insting dan perkiraan saja.", "bobot": {"SIKC": 20, "RPL": 30, "TRK": 30, "TI": 20}},
            "C": {"text": "Membuat sistem amplop (pos-pos uang) agar tidak tercampur.", "bobot": {"SIKC": 85, "RPL": 60, "TRK": 40, "TI": 50}},
            "D": {"text": "Mencari promo diskon di aplikasi belanja.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 50, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Jika kamu tersesat di kota baru tanpa Google Maps, apa yang menjadi andalanmu?",
        "pilihan": {
            "A": {"text": "Mencari papan petunjuk jalan dan memahami arah mata angin.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 60, "TI": 50}},
            "B": {"text": "Bertanya pada warga lokal tentang rute tercepat.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 50, "TI": 60}},
            "C": {"text": "Mencoba jalan mana saja yang terlihat ramai (trial & error).", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 70, "TI": 40}},
            "D": {"text": "Mencari menara atau gedung tinggi sebagai patokan sinyal/lokasi.", "bobot": {"SIKC": 50, "RPL": 45, "TRK": 85, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Guru memberikan tugas kelompok yang rumit. Peran apa yang biasanya kamu ambil secara alami?",
        "pilihan": {
            "A": {"text": "Si Tukang Ide: Mencari ide kreatif dan tampilan presentasi.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 40, "TI": 50}},
            "B": {"text": "Si Teknis: Menyiapkan laptop, proyektor, dan alat peraga.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 90, "TI": 60}},
            "C": {"text": "Si Manajer: Membagi tugas, mencatat deadline, dan memastikan semua berjalan.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 30, "TI": 50}},
            "D": {"text": "Si Riset: Mencari bahan materi di internet.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 50, "TI": 80}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu melihat antrean panjang di kantin sekolah yang membuat siswa terlambat masuk kelas. Solusimu?",
        "pilihan": {
            "A": {"text": "Mendesain aplikasi pre-order makanan agar bisa dipesan dari kelas.", "bobot": {"SIKC": 60, "RPL": 95, "TRK": 40, "TI": 60}},
            "B": {"text": "Mengusulkan sistem antrean satu jalur masuk dan satu jalur keluar (alur fisik).", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 50, "TI": 50}},
            "C": {"text": "Menambah jumlah pelayan di kantin.", "bobot": {"SIKC": 50, "RPL": 30, "TRK": 30, "TI": 40}},
            "D": {"text": "Memasang mesin tiket otomatis seperti di bank.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 85, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Saat merapikan lemari buku yang sangat berantakan, strategimu adalah:",
        "pilihan": {
            "A": {"text": "Mengelompokkan buku berdasarkan warna sampul biar estetik.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 30, "TI": 50}},
            "B": {"text": "Mengelompokkan berdasarkan genre/kategori, lalu diurutkan abjad.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 40, "TI": 60}},
            "C": {"text": "Menumpuk buku yang paling sering dibaca di tempat paling mudah diambil.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 50, "TI": 55}},
            "D": {"text": "Membuat rak tambahan sendiri dari kayu bekas.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 90, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Jika kamu menjadi manajer klub sepak bola, data apa yang paling penting bagimu?",
        "pilihan": {
            "A": {"text": "Statistik stamina dan akurasi operan setiap pemain.", "bobot": {"SIKC": 95, "RPL": 40, "TRK": 35, "TI": 50}},
            "B": {"text": "Desain jersey dan merchandise yang menarik fans.", "bobot": {"SIKC": 40, "RPL": 85, "TRK": 30, "TI": 40}},
            "C": {"text": "Kualitas rumput stadion dan pencahayaan lapangan.", "bobot": {"SIKC": 35, "RPL": 30, "TRK": 90, "TI": 50}},
            "D": {"text": "Video rekaman pertandingan untuk dianalisis ulang.", "bobot": {"SIKC": 80, "RPL": 60, "TRK": 50, "TI": 70}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu suka membaca berita tentang 'Smart City'. Apa yang paling membuatmu kagum?",
        "pilihan": {
            "A": {"text": "CCTV yang bisa mendeteksi wajah penjahat secara otomatis.", "bobot": {"SIKC": 70, "RPL": 70, "TRK": 70, "TI": 70}},
            "B": {"text": "Pusat komando yang mengintegrasikan data banjir, macet, dan sampah real-time.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 40, "TI": 50}},
            "C": {"text": "Aplikasi pelaporan warga yang mudah digunakan di HP.", "bobot": {"SIKC": 60, "RPL": 90, "TRK": 40, "TI": 50}},
            "D": {"text": "Tiang lampu jalan yang hemat energi dan bertenaga surya.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 90, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Ketika menghadapi masalah yang rumit (misal: nilai turun drastis), apa respons pertamamu?",
        "pilihan": {
            "A": {"text": "Panik dan belajar semua hal sekaligus.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}},
            "B": {"text": "Mencari pola: di pelajaran apa aku lemah dan kenapa (kurang tidur/kurang latihan)?", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 40, "TI": 60}},
            "C": {"text": "Membuat jadwal belajar baru yang lebih ketat.", "bobot": {"SIKC": 85, "RPL": 50, "TRK": 40, "TI": 50}},
            "D": {"text": "Mencari bimbel online yang punya metode cepat.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 40, "TI": 65}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu diminta mengurus pendaftaran lomba 17 Agustus. Cara kerjamu:",
        "pilihan": {
            "A": {"text": "Menyiapkan kertas formulir fisik agar mudah diisi warga.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 50, "TI": 40}},
            "B": {"text": "Membuat Google Form yang otomatis masuk ke Excel/Spreadsheet.", "bobot": {"SIKC": 95, "RPL": 70, "TRK": 40, "TI": 60}},
            "C": {"text": "Meminta warga WA ke nomormu satu per satu.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Membuat poster digital yang ada QR Code-nya.", "bobot": {"SIKC": 70, "RPL": 85, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Apa pendapatmu tentang 'Big Data' (Data dalam jumlah sangat besar)?",
        "pilihan": {
            "A": {"text": "Sesuatu yang membingungkan dan memusingkan.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}},
            "B": {"text": "Harta karun informasi untuk memprediksi masa depan.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 30, "TI": 60}},
            "C": {"text": "Bahan untuk melatih kecerdasan buatan (AI).", "bobot": {"SIKC": 80, "RPL": 80, "TRK": 50, "TI": 70}},
            "D": {"text": "Membutuhkan komputer super canggih untuk menyimpannya.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 90, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Di sebuah perpustakaan, buku sering hilang atau salah tempat. Solusimu?",
        "pilihan": {
            "A": {"text": "Memasang chip pelacak di setiap buku.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Membuat sistem peminjaman digital yang ketat (scan barcode).", "bobot": {"SIKC": 95, "RPL": 75, "TRK": 50, "TI": 60}},
            "C": {"text": "Membuat aplikasi pencari lokasi buku di rak.", "bobot": {"SIKC": 60, "RPL": 90, "TRK": 40, "TI": 50}},
            "D": {"text": "Menambah petugas jaga di setiap lorong.", "bobot": {"SIKC": 40, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Saat melihat kemacetan lalu lintas, apa yang ada di pikiranmu?",
        "pilihan": {
            "A": {"text": "Seandainya lampu merahnya bisa menyesuaikan sendiri dengan panjang antrean.", "bobot": {"SIKC": 90, "RPL": 60, "TRK": 50, "TI": 60}},
            "B": {"text": "Mobil-mobil ini butuh jalan yang lebih lebar.", "bobot": {"SIKC": 40, "RPL": 30, "TRK": 60, "TI": 40}},
            "C": {"text": "Orang-orang harusnya pakai aplikasi navigasi biar tidak lewat sini.", "bobot": {"SIKC": 60, "RPL": 90, "TRK": 40, "TI": 50}},
            "D": {"text": "Pasti ada kecelakaan atau perbaikan jalan di depan.", "bobot": {"SIKC": 70, "RPL": 40, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu lebih suka tugas sekolah yang sifatnya:",
        "pilihan": {
            "A": {"text": "Membuat produk atau karya seni.", "bobot": {"SIKC": 40, "RPL": 85, "TRK": 40, "TI": 50}},
            "B": {"text": "Melakukan survei, wawancara, dan menyimpulkan hasil.", "bobot": {"SIKC": 95, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Eksperimen di laboratorium dengan alat.", "bobot": {"SIKC": 40, "RPL": 30, "TRK": 85, "TI": 50}},
            "D": {"text": "Menghitung dan memecahkan soal logika.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 50, "TI": 90}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Bagaimana caramu menilai apakah sebuah toko online itu terpercaya?",
        "pilihan": {
            "A": {"text": "Melihat tampilan web/aplikasinya bagus atau tidak.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}},
            "B": {"text": "Menganalisis rating bintang dan membaca pola review pembeli.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 30, "TI": 50}},
            "C": {"text": "Mengecek apakah servernya sering down.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 80, "TI": 60}},
            "D": {"text": "Mencari info pemilik tokonya di Google.", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Temanmu curhat bisnis kue-nya rugi. Apa saran pertamamu?",
        "pilihan": {
            "A": {"text": "Coba hitung ulang harga bahan baku vs harga jualnya.", "bobot": {"SIKC": 90, "RPL": 30, "TRK": 30, "TI": 50}},
            "B": {"text": "Bikin akun medsos yang keren buat promosi.", "bobot": {"SIKC": 50, "RPL": 85, "TRK": 30, "TI": 50}},
            "C": {"text": "Beli oven baru yang lebih canggih.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 85, "TI": 40}},
            "D": {"text": "Ganti resep kuenya biar lebih enak.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Dalam permainan strategi (seperti Mobile Legends/PUBG), apa fokus utamamu?",
        "pilihan": {
            "A": {"text": "Melihat peta (map awareness) dan memprediksi gerakan musuh.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 50}},
            "B": {"text": "Mencoba kombinasi skill hero yang baru.", "bobot": {"SIKC": 40, "RPL": 85, "TRK": 30, "TI": 50}},
            "C": {"text": "Memastikan ping/koneksi internet stabil.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 90, "TI": 60}},
            "D": {"text": "Menjadi pemimpin tim (shotcaller).", "bobot": {"SIKC": 80, "RPL": 60, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Jika kamu punya data nilai rapormu dari SD sampai SMA, apa yang ingin kamu lihat?",
        "pilihan": {
            "A": {"text": "Grafik kenaikan atau penurunan prestasi per semester.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 30, "TI": 50}},
            "B": {"text": "Menyimpannya secara digital agar tidak hilang.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 60, "TI": 70}},
            "C": {"text": "Hanya melihat nilai yang bagus-bagus saja.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}},
            "D": {"text": "Membandingkannya dengan nilai teman.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu diminta menjadi sekretaris kelas. Reaksimu?",
        "pilihan": {
            "A": {"text": "Senang, karena suka mencatat dan merapikan dokumen.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "B": {"text": "Biasa saja, asal tidak disuruh angkat-angkat barang.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "C": {"text": "Menolak, lebih suka bagian dekorasi atau dokumentasi.", "bobot": {"SIKC": 30, "RPL": 80, "TRK": 40, "TI": 40}},
            "D": {"text": "Menerima, dan akan membuat sistem absen digital.", "bobot": {"SIKC": 80, "RPL": 85, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Ketika melihat antrean kasir supermarket yang panjang, apa analisismu?",
        "pilihan": {
            "A": {"text": "Kasirnya kurang cepat bekerjanya.", "bobot": {"SIKC": 50, "RPL": 30, "TRK": 30, "TI": 40}},
            "B": {"text": "Sistem barcode scannernya mungkin error/lambat.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 85, "TI": 60}},
            "C": {"text": "Alur antreannya salah, harusnya dipisah antara belanjaan sedikit dan banyak.", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 40, "TI": 60}},
            "D": {"text": "Orang-orang terlalu banyak belanja.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Apa hal yang paling penting dalam sebuah presentasi tugas?",
        "pilihan": {
            "A": {"text": "Tampilan slide yang penuh animasi keren.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}},
            "B": {"text": "Data dan fakta yang disampaikan valid serta terstruktur.", "bobot": {"SIKC": 95, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Sound system dan mik yang jernih.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 90, "TI": 50}},
            "D": {"text": "Gaya bicara yang lucu.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Jika kamu menjadi panitia pameran, bagian mana yang kamu pilih?",
        "pilihan": {
            "A": {"text": "Seksi Acara: Mengatur rundown dan jadwal.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "B": {"text": "Seksi Perlengkapan: Mengurus listrik dan tenda.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 95, "TI": 50}},
            "C": {"text": "Seksi Publikasi: Mendesain poster dan tiket.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}},
            "D": {"text": "Seksi Keamanan.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 50, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Saat belajar sejarah, cara apa yang paling membantumu mengingat?",
        "pilihan": {
            "A": {"text": "Membuat garis waktu (timeline) kejadian secara urut.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "B": {"text": "Menonton film dokumenter.", "bobot": {"SIKC": 50, "RPL": 70, "TRK": 40, "TI": 50}},
            "C": {"text": "Menghafal tahun dan nama tokoh.", "bobot": {"SIKC": 60, "RPL": 30, "TRK": 30, "TI": 40}},
            "D": {"text": "Mencari tahu 'kenapa' perang itu terjadi (sebab-akibat).", "bobot": {"SIKC": 85, "RPL": 50, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Menurutmu, apa fungsi utama komputer bagi perusahaan?",
        "pilihan": {
            "A": {"text": "Alat untuk membuat desain produk.", "bobot": {"SIKC": 40, "RPL": 85, "TRK": 30, "TI": 50}},
            "B": {"text": "Alat untuk mengolah data keuangan dan karyawan.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 40, "TI": 60}},
            "C": {"text": "Alat untuk komunikasi jarak jauh.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 80, "TI": 60}},
            "D": {"text": "Agar terlihat modern.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Apa yang kamu lakukan jika internet di rumah mati total?",
        "pilihan": {
            "A": {"text": "Menelepon provider untuk menanyakan estimasi perbaikan.", "bobot": {"SIKC": 80, "RPL": 40, "TRK": 50, "TI": 60}},
            "B": {"text": "Mengutak-atik kabel modem siapa tahu kendor.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 70}},
            "C": {"text": "Main game offline di HP.", "bobot": {"SIKC": 30, "RPL": 60, "TRK": 30, "TI": 40}},
            "D": {"text": "Tidur.", "bobot": {"SIKC": 10, "RPL": 10, "TRK": 10, "TI": 10}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu melihat tumpukan sampah di sungai. Ide solusimu?",
        "pilihan": {
            "A": {"text": "Membuat robot pembersih sampah otomatis.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 90, "TI": 70}},
            "B": {"text": "Menganalisis dari mana asal sampah (hulu sungai) dan mengedukasi warga.", "bobot": {"SIKC": 95, "RPL": 40, "TRK": 40, "TI": 60}},
            "C": {"text": "Membuat aplikasi pelaporan 'Buang Sampah Sembarangan'.", "bobot": {"SIKC": 60, "RPL": 95, "TRK": 40, "TI": 60}},
            "D": {"text": "Kerja bakti membersihkannya.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 50, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Dalam kerja kelompok, temanmu ada yang tidak bekerja (free rider). Sikapmu?",
        "pilihan": {
            "A": {"text": "Mengeluarkan dia dari kelompok.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "B": {"text": "Mencari tahu alasannya, lalu membagi tugas yang lebih ringan untuknya.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 40, "TI": 50}},
            "C": {"text": "Mengerjakan tugasnya sendirian biar cepat selesai.", "bobot": {"SIKC": 30, "RPL": 50, "TRK": 50, "TI": 40}},
            "D": {"text": "Marah-marah di grup chat.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu disuruh belanja ke pasar dengan daftar panjang. Trikmu?",
        "pilihan": {
            "A": {"text": "Mengelompokkan daftar belanjaan sesuai letak kios (Sayur, Daging, Bumbu).", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 40, "TI": 50}},
            "B": {"text": "Beli satu per satu sesuai urutan catatannya.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "C": {"text": "Menghafal semuanya tanpa catatan.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Minta tolong pedagang pilihlah semuanya.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Apa yang membuatmu tertarik dengan teknologi 'Face Recognition' (Pengenal Wajah)?",
        "pilihan": {
            "A": {"text": "Bagaimana kamera bisa membedakan wajah si A dan si B.", "bobot": {"SIKC": 90, "RPL": 80, "TRK": 60, "TI": 80}},
            "B": {"text": "Bagaimana cara coding agar akurasinya tinggi.", "bobot": {"SIKC": 60, "RPL": 95, "TRK": 50, "TI": 80}},
            "C": {"text": "Sensor inframerah yang dipakai saat gelap.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 95, "TI": 70}},
            "D": {"text": "Keren saja buat buka kunci HP.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 50, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Jika kamu punya uang lebih, kamu akan investasikan untuk:",
        "pilihan": {
            "A": {"text": "Membeli gadget terbaru.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 80, "TI": 50}},
            "B": {"text": "Modal bisnis kecil-kecilan dengan perhitungan matang.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Membeli software/aplikasi premium.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 40, "TI": 60}},
            "D": {"text": "Ditabung saja di celengan.", "bobot": {"SIKC": 60, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Bagaimana caramu mengatur file di laptop?",
        "pilihan": {
            "A": {"text": "Semua ditaruh di Desktop biar gampang dicari.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 20}},
            "B": {"text": "Dibuatkan folder berjenjang: Tahun > Mata Pelajaran > Tugas.", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 40, "TI": 60}},
            "C": {"text": "Menggunakan nama file yang aneh-aneh.", "bobot": {"SIKC": 20, "RPL": 40, "TRK": 20, "TI": 20}},
            "D": {"text": "Jarang menyimpan file, seringnya hilang.", "bobot": {"SIKC": 10, "RPL": 10, "TRK": 10, "TI": 10}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Ketika melihat info hoax di grup keluarga, apa tindakanmu?",
        "pilihan": {
            "A": {"text": "Langsung keluar grup.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}},
            "B": {"text": "Mencari sumber berita asli dan data pembandingnya, lalu share.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 40, "TI": 60}},
            "C": {"text": "Diam saja.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Melaporkan pengirimnya ke polisi.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Apa yang paling menarik dari sebuah supermarket?",
        "pilihan": {
            "A": {"text": "Bagaimana mereka mengatur stok ribuan barang agar tidak habis.", "bobot": {"SIKC": 95, "RPL": 40, "TRK": 30, "TI": 50}},
            "B": {"text": "Mesin kasir otomatisnya.", "bobot": {"SIKC": 50, "RPL": 70, "TRK": 60, "TI": 60}},
            "C": {"text": "Freezer pendingin daging yang besar.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 85, "TI": 50}},
            "D": {"text": "Diskonnya.", "bobot": {"SIKC": 60, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Jika kamu menjadi Kepala Sekolah sehari, apa kebijakan pertamamu?",
        "pilihan": {
            "A": {"text": "Mengganti semua papan tulis dengan layar sentuh.", "bobot": {"SIKC": 40, "RPL": 60, "TRK": 80, "TI": 60}},
            "B": {"text": "Membuat aplikasi sekolah untuk absen dan nilai.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 70}},
            "C": {"text": "Mengevaluasi kurikulum agar lebih relevan dengan dunia kerja.", "bobot": {"SIKC": 95, "RPL": 40, "TRK": 30, "TI": 50}},
            "D": {"text": "Meliburkan sekolah.", "bobot": {"SIKC": 10, "RPL": 10, "TRK": 10, "TI": 10}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu lebih suka bekerja di ruangan yang seperti apa?",
        "pilihan": {
            "A": {"text": "Ruangan penuh layar monitor dan server.", "bobot": {"SIKC": 40, "RPL": 60, "TRK": 95, "TI": 70}},
            "B": {"text": "Ruangan kantor yang rapi dengan papan tulis untuk brainstorming.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 50}},
            "C": {"text": "Di mana saja asal bisa bawa laptop (Work from Anywhere).", "bobot": {"SIKC": 60, "RPL": 90, "TRK": 40, "TI": 70}},
            "D": {"text": "Ruangan bengkel yang penuh peralatan.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 90, "TI": 60}}
        }
    },
    # SOAL 36-50 (Lanjutan untuk melengkapi 50 soal)
    {
        "kategori": "analisis",
        "pertanyaan": "Saat kamu mendapat tugas penelitian, langkah pertama yang kamu lakukan adalah:",
        "pilihan": {
            "A": {"text": "Langsung mengumpulkan semua informasi yang ada di internet.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 40, "TI": 50}},
            "B": {"text": "Menentukan hipotesis (dugaan awal) dan variabel data yang akan diuji.", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 30, "TI": 80}},
            "C": {"text": "Mencari teman yang bisa diajak kerja sama.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Membuat presentasi yang menarik untuk hasil akhir.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu sedang membeli tiket konser online dan situsnya lambat. Kamu akan:",
        "pilihan": {
            "A": {"text": "Langsung tutup situsnya dan coba cari calo tiket.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}},
            "B": {"text": "Mencoba terus sampai berhasil, sambil menganalisis jam terbaik situs bekerja.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 50, "TI": 60}},
            "C": {"text": "Membuka di perangkat lain (HP atau PC).", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 85, "TI": 50}},
            "D": {"text": "Meminta teman untuk membelikan di tempat lain.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Jika kamu mengelola tim pelayanan pelanggan, data apa yang paling kamu butuhkan untuk meningkatkan kualitas?",
        "pilihan": {
            "A": {"text": "Jumlah *like* di media sosial.","bobot": {"SIKC": 40, "RPL": 80, "TRK": 30, "TI": 40}},
            "B": {"text": "Data kecepatan respons dan tingkat kepuasan (rating) pelanggan.", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 40, "TI": 60}},
            "C": {"text": "Kualitas koneksi internet di kantor layanan.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 90, "TI": 50}},
            "D": {"text": "Tampilan seragam yang dipakai petugas.","bobot": {"SIKC": 30, "RPL": 50, "TRK": 30, "TI": 30}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu ingin mengatur pengeluaran untuk makan selama sebulan. Metode terbaik adalah:",
        "pilihan": {
            "A": {"text": "Memasak sendiri setiap hari.", "bobot": {"SIKC": 60, "RPL": 40, "TRK": 40, "TI": 50}},
            "B": {"text": "Mencatat total belanja harian dan membandingkannya dengan anggaran mingguan.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 30, "TI": 60}},
            "C": {"text": "Langsung menabung sisanya di awal bulan.", "bobot": {"SIKC": 70, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Mencari teman untuk patungan makanan.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Dalam survei online, kamu menemukan banyak data yang tidak konsisten atau mencurigakan. Kamu akan:",
        "pilihan": {
            "A": {"text": "Membuang semua data yang mencurigakan itu.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 50}},
            "B": {"text": "Mencoba mencari pola dari data yang aneh itu, apakah ada kesamaan *input*.", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 40, "TI": 70}},
            "C": {"text": "Mengulang survei dari awal.", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 40, "TI": 50}},
            "D": {"text": "Menggunakan software khusus untuk memperbaiki datanya.", "bobot": {"SIKC": 60, "RPL": 80, "TRK": 50, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Saat melihat pameran lukisan, kamu lebih tertarik pada:",
        "pilihan": {
            "A": {"text": "Teknik kuas dan media yang digunakan (oil, acrylic).", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 40, "TI": 50}},
            "B": {"text": "Biografi pelukis dan sejarah di balik lukisan itu.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Berapa harga lukisan termahal.", "bobot": {"SIKC": 60, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Lampu sorot yang menerangi lukisan.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 90, "TI": 40}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Apa yang paling berkesan dari aplikasi navigasi lalu lintas (misal: Waze)?",
        "pilihan": {
            "A": {"text": "Suara navigasi yang lucu.", "bobot": {"SIKC": 30, "RPL": 70, "TRK": 30, "TI": 40}},
            "B": {"text": "Kecepatan update data kemacetannya yang *real-time*.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 50, "TI": 60}},
            "C": {"text": "Tampilan peta yang detail dan 3D.", "bobot": {"SIKC": 50, "RPL": 80, "TRK": 40, "TI": 50}},
            "D": {"text": "GPS di HP yang bekerja akurat.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 90, "TI": 60}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu sedang menyusun daftar kontak teman. Cara terbaik agar mudah dicari adalah:",
        "pilihan": {
            "A": {"text": "Mengurutkan berdasarkan nama depan saja.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "B": {"text": "Menambahkan label/tag (misal: Teman Sekolah, Teman Main, Keluarga).", "bobot": {"SIKC": 90, "RPL": 70, "TRK": 40, "TI": 60}},
            "C": {"text": "Hanya mencatat nomor yang paling sering dihubungi.", "bobot": {"SIKC": 60, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Menyimpan nama dengan emoji lucu.", "bobot": {"SIKC": 40, "RPL": 85, "TRK": 30, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Jika kamu bertugas mengelola jadwal kereta api, prioritas utamamu adalah:",
        "pilihan": {
            "A": {"text": "Memastikan harga tiketnya terjangkau.", "bobot": {"SIKC": 50, "RPL": 30, "TRK": 30, "TI": 40}},
            "B": {"text": "Membuat sistem pemesanan tiket yang canggih.", "bobot": {"SIKC": 70, "RPL": 90, "TRK": 40, "TI": 60}},
            "C": {"text": "Memastikan setiap kereta berangkat dan tiba tepat waktu sesuai skema yang teratur.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 50, "TI": 70}},
            "D": {"text": "Memastikan jalur rel keretanya aman.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu ingin tahu kenapa harga cabai di pasar fluktuatif (naik turun). Yang kamu cari adalah:",
        "pilihan": {
            "A": {"text": "Siapa yang paling diuntungkan dari kenaikan harga itu.", "bobot": {"SIKC": 70, "RPL": 40, "TRK": 30, "TI": 40}},
            "B": {"text": "Data panen, distribusi, dan permintaan cabai dari 3 bulan terakhir.", "bobot": {"SIKC": 95, "RPL": 40, "TRK": 30, "TI": 60}},
            "C": {"text": "Berita tentang cuaca buruk di daerah sentra cabai.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 40, "TI": 50}},
            "D": {"text": "Mencari petani cabai untuk diwawancara.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Apa manfaat utama dari sebuah *flowchart* (diagram alir) dalam pekerjaan?",
        "pilihan": {
            "A": {"text": "Membuat tampilan dokumen lebih menarik.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 30, "TI": 50}},
            "B": {"text": "Menggambarkan urutan langkah/proses secara sistematis agar tidak ada yang terlewat.", "bobot": {"SIKC": 95, "RPL": 90, "TRK": 40, "TI": 90}},
            "C": {"text": "Mengganti tulisan dengan gambar.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 40, "TI": 40}},
            "D": {"text": "Menghemat kertas.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu mengelola sebuah toko buku. Agar pembeli cepat menemukan buku, kamu akan:",
        "pilihan": {
            "A": {"text": "Memasang rak-rak baru yang kokoh.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 90, "TI": 40}},
            "B": {"text": "Mengelompokkan buku berdasarkan tema, penulis, dan tahun terbit.", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 40, "TI": 60}},
            "C": {"text": "Membuat kopi gratis untuk pembeli.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 30, "TI": 30}},
            "D": {"text": "Membuat aplikasi yang bisa mencari buku di gudang.", "bobot": {"SIKC": 70, "RPL": 90, "TRK": 40, "TI": 70}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Apa hal pertama yang kamu periksa jika tagihan listrik bulananmu naik drastis?",
        "pilihan": {
            "A": {"text": "Apakah ada tetangga yang mencuri listrik.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "B": {"text": "Membandingkan data pemakaian listrik 6 bulan terakhir.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 30, "TI": 60}},
            "C": {"text": "Memastikan meteran listriknya tidak rusak.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 50}},
            "D": {"text": "Mencari tahu penyebab kenapa harga listrik per KWH naik.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Kamu lebih suka membaca buku yang topiknya:",
        "pilihan": {
            "A": {"text": "Filosofi dan kisah-kisah imajinatif.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 30, "TI": 60}},
            "B": {"text": "Sejarah, politik, atau ekonomi (data dan fakta).", "bobot": {"SIKC": 95, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Cara merakit atau memperbaiki alat-alat elektronik.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "D": {"text": "Matematika dan teori-teori fisika.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 40, "TI": 95}}
        }
    },
    {
        "kategori": "analisis",
        "pertanyaan": "Jika kamu disuruh menganalisis pertumbuhan penduduk sebuah kota, metode apa yang paling kamu andalkan?",
        "pilihan": {
            "A": {"text": "Bertanya kepada warga senior di kota itu.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "B": {"text": "Membaca data sensus penduduk dan menganalisis tren per tahun.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 30, "TI": 60}},
            "C": {"text": "Melihat ramainya lalu lintas di jalanan.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}},
            "D": {"text": "Membuat poster 'Ayo Punya Anak Lagi'.", "bobot": {"SIKC": 20, "RPL": 40, "TRK": 30, "TI": 30}}
        }
    }
]

# ------------------------------------------------------------------
# KATEGORI 2: PENGEMBANGAN APLIKASI (RPL/Rekayasa Perangkat Lunak)
# Fokus: Kreativitas, Logika, User Experience (UX), Creation
# ------------------------------------------------------------------
pengembangan_soal = [
    # SOAL 1-35 (Dikutip dari input Anda)
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu bisa membuat satu aplikasi untuk membantu hidupmu, aplikasi apa itu?",
        "pilihan": {
            "A": {"text": "Aplikasi pendeteksi lokasi barang yang hilang di kamar.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Aplikasi yang bisa mengerjakan PR Matematika otomatis.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 40, "TI": 90}},
            "C": {"text": "Aplikasi 'Lemari Pintar' yang menyarankan outfit baju harian.", "bobot": {"SIKC": 60, "RPL": 95, "TRK": 30, "TI": 50}},
            "D": {"text": "Aplikasi pencatat keuangan daerah.", "bobot": {"SIKC": 90, "RPL": 60, "TRK": 30, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Saat bermain game, apa yang sering membuatmu kesal?",
        "pilihan": {
            "A": {"text": "Internetnya lemot (lag) terus.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Tombol kontrolnya susah dipencet dan menunya membingungkan.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 30, "TI": 50}},
            "C": {"text": "Cerita gamenya membosankan.", "bobot": {"SIKC": 50, "RPL": 70, "TRK": 30, "TI": 40}},
            "D": {"text": "Grafiknya kurang realistis.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 60, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu ingin membuat poster untuk pensi sekolah. Apa fokus utamamu?",
        "pilihan": {
            "A": {"text": "Memastikan semua info tanggal dan tempat tertulis benar.", "bobot": {"SIKC": 80, "RPL": 40, "TRK": 30, "TI": 50}},
            "B": {"text": "Memilih kombinasi warna dan font yang menarik mata.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 30, "TI": 50}},
            "C": {"text": "Memastikan posternya bisa dicetak dengan printer sekolah.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 80, "TI": 50}},
            "D": {"text": "Menyebarkan posternya ke sebanyak mungkin orang.", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Bagaimana caramu mengatur tampilan layar HP-mu?",
        "pilihan": {
            "A": {"text": "Berantakan, yang penting ada aplikasinya.", "bobot": {"SIKC": 30, "RPL": 20, "TRK": 40, "TI": 30}},
            "B": {"text": "Mengelompokkan aplikasi dalam folder berdasarkan fungsinya.", "bobot": {"SIKC": 85, "RPL": 70, "TRK": 40, "TI": 60}},
            "C": {"text": "Menghias dengan widget, tema, dan icon pack yang keren.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 30, "TI": 50}},
            "D": {"text": "Membiarkan settingan bawaan pabrik.", "bobot": {"SIKC": 40, "RPL": 30, "TRK": 60, "TI": 40}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu harus memberi instruksi jalan ke temanmu, cara mana yang kamu pilih?",
        "pilihan": {
            "A": {"text": "Mengirimkan titik lokasi (Share loc) saja.", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 60, "TI": 50}},
            "B": {"text": "Menulis langkah demi langkah: 'Maju 100m, belok kiri, lalu...'", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 30, "TI": 90}},
            "C": {"text": "Menelpon dan memandunya secara langsung.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 40, "TI": 30}},
            "D": {"text": "Menggambar peta manual di kertas lalu difoto.", "bobot": {"SIKC": 40, "RPL": 60, "TRK": 30, "TI": 40}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Apa bagian paling seru dari bermain LEGO atau Minecraft?",
        "pilihan": {
            "A": {"text": "Membangun sesuatu dari nol sesuai imajinasi sendiri.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 50, "TI": 60}},
            "B": {"text": "Mengikuti buku panduan instruksi dengan presisi.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 80, "TI": 70}},
            "C": {"text": "Melihat bagaimana mekanisme pintu/roda bekerja.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 90, "TI": 60}},
            "D": {"text": "Mengumpulkan material/bahan sebanyak-banyaknya.", "bobot": {"SIKC": 80, "RPL": 40, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu sedang mencoba resep masakan baru, tapi rasanya aneh. Apa yang kamu lakukan?",
        "pilihan": {
            "A": {"text": "Mengecek kompor dan pancinya, siapa tahu rusak.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 85, "TI": 40}},
            "B": {"text": "Memodifikasi resepnya: tambah garam, kurangi gula, coba lagi.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 30, "TI": 60}},
            "C": {"text": "Mencatat persis apa yang salah untuk data masakan berikutnya.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 50}},
            "D": {"text": "Beli makanan jadi saja.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Di sebuah website sekolah, menurutmu apa yang paling penting?",
        "pilihan": {
            "A": {"text": "Website itu tidak pernah 'down' atau error saat diakses.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 90, "TI": 70}},
            "B": {"text": "Informasi nilai dan jadwalnya lengkap.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 40, "TI": 50}},
            "C": {"text": "Tombol menunya jelas dan gampang dicari, tidak membingungkan.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 30, "TI": 50}},
            "D": {"text": "Keamanan data siswa terjamin.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 80, "TI": 90}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu diminta membuat aturan permainan (board game) baru. Kamu akan:",
        "pilihan": {
            "A": {"text": "Membuat papan permainan yang kokoh dari kayu.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 90, "TI": 50}},
            "B": {"text": "Merancang aturan main yang seru, adil, dan logis.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 30, "TI": 80}},
            "C": {"text": "Mencatat skor setiap pemain di papan tulis.", "bobot": {"SIKC": 85, "RPL": 40, "TRK": 30, "TI": 50}},
            "D": {"text": "Menjadi wasit saja.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 50, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu punya robot pembersih kamar, fitur apa yang ingin kamu tambahkan (program)?",
        "pilihan": {
            "A": {"text": "Fitur 'Jangan Tabrak Kucing' (Logika pendeteksi).", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 60, "TI": 80}},
            "B": {"text": "Baterai yang tahan 1 minggu.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 50}},
            "C": {"text": "Laporan harian berapa banyak debu yang terhisap.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 40, "TI": 50}},
            "D": {"text": "Roda yang bisa memanjat tangga.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 85, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Saat menggunakan aplikasi chat, apa yang menurutmu paling keren?",
        "pilihan": {
            "A": {"text": "Stiker dan filter wajah yang lucu-lucu.", "bobot": {"SIKC": 30, "RPL": 90, "TRK": 30, "TI": 50}},
            "B": {"text": "Pesan terkirim sangat cepat tanpa delay.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 90, "TI": 60}},
            "C": {"text": "Bisa mencari riwayat chat tahun lalu dengan mudah.", "bobot": {"SIKC": 90, "RPL": 60, "TRK": 40, "TI": 50}},
            "D": {"text": "Enkripsi keamanan agar tidak disadap.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 60, "TI": 90}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Temanmu mengeluh blog pribadinya sepi pengunjung. Sarannmu?",
        "pilihan": {
            "A": {"text": "Ganti tampilan (tema) biar lebih enak dibaca dan modern.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 30, "TI": 50}},
            "B": {"text": "Cek apakah server hostingnya lemot.", "bobot": {"SIKC": 30, "RPL": 50, "TRK": 90, "TI": 60}},
            "C": {"text": "Analisis jam berapa biasanya orang buka internet.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 50}},
            "D": {"text": "Share link blognya di semua medsos.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Ketika melihat tombol lift, apa yang kamu pikirkan?",
        "pilihan": {
            "A": {"text": "Bagaimana cara kerja kabel penarik liftnya.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 90, "TI": 50}},
            "B": {"text": "Kenapa tombol 'tutup pintu' sering tidak berfungsi?", "bobot": {"SIKC": 50, "RPL": 80, "TRK": 60, "TI": 70}},
            "C": {"text": "Logika: Jika ditekan lantai 5, tapi ada orang di lantai 3, mana dulu?", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 90}},
            "D": {"text": "Berapa kapasitas maksimal orang di dalamnya.", "bobot": {"SIKC": 80, "RPL": 40, "TRK": 50, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu ingin membuat kejutan ulang tahun yang rumit. Persiapannya:",
        "pilihan": {
            "A": {"text": "Membuat skenario: 'Jika dia datang jam 7, kita A. Jika jam 8, kita B.'", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 30, "TI": 80}},
            "B": {"text": "Menghias ruangan dengan balon dan lampu.", "bobot": {"SIKC": 30, "RPL": 60, "TRK": 50, "TI": 40}},
            "C": {"text": "Mengumpulkan uang patungan dari teman-teman.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "D": {"text": "Menyiapkan sound system yang kencang.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 90, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Apa yang membuatmu tertarik pada 'Artificial Intelligence' (AI)?",
        "pilihan": {
            "A": {"text": "Bagaimana cara membuat AI bisa 'belajar' sendiri (coding-nya).", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 90}},
            "B": {"text": "Komputer super cepat yang menjalankannya.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 60}},
            "C": {"text": "Dampak AI terhadap data pekerjaan manusia.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 60}},
            "D": {"text": "Robot fisik yang bisa bergerak seperti manusia.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 85, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Ketika melihat menu restoran yang tulisannya kecil dan warnanya silau, kamu berpikir:",
        "pilihan": {
            "A": {"text": "Ini desainnya gagal, susah dibaca pelanggan.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}},
            "B": {"text": "Berapa banyak kertas yang dihabiskan untuk mencetak ini.", "bobot": {"SIKC": 80, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Makanannya mahal atau tidak.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Pasti printernya tintanya mau habis.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 80, "TI": 40}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu menjadi sutradara film, apa peran utamamu?",
        "pilihan": {
            "A": {"text": "Mengatur alur cerita agar penonton penasaran dan terkejut (plot twist).", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 30, "TI": 70}},
            "B": {"text": "Mengatur jadwal syuting agar efisien waktu.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Memastikan kamera dan lighting berfungsi maksimal.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 90, "TI": 60}},
            "D": {"text": "Mencari sponsor dana.", "bobot": {"SIKC": 80, "RPL": 30, "TRK": 30, "TI": 40}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu punya ide bisnis kaos. Langkah pertamamu?",
        "pilihan": {
            "A": {"text": "Membuat desain sablon yang unik dan kekinian di laptop.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 30, "TI": 50}},
            "B": {"text": "Mencari konveksi yang murah.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 40, "TI": 50}},
            "C": {"text": "Membeli mesin jahit.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 90, "TI": 40}},
            "D": {"text": "Survei pasar.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Apa yang kamu rasakan saat berhasil memecahkan teka-teki sulit?",
        "pilihan": {
            "A": {"text": "Puas banget, rasanya ingin cari teka-teki lain.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 80}},
            "B": {"text": "Biasa saja.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}},
            "C": {"text": "Lelah.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}},
            "D": {"text": "Ingin memberi tahu teman caranya.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 50, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Menurutmu, apa kekurangan terbesar dari 'Remote TV' konvensional?",
        "pilihan": {
            "A": {"text": "Terlalu banyak tombol yang tidak pernah dipakai (User Interface buruk).", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 30, "TI": 60}},
            "B": {"text": "Baterainya cepat habis.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 50}},
            "C": {"text": "Sering hilang terselip di sofa.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 40, "TI": 50}},
            "D": {"text": "Jangkauan sinyalnya pendek.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 85, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu ingin membuat video YouTube. Fokus editingmu?",
        "pilihan": {
            "A": {"text": "Memberi efek transisi dan teks yang pas dengan ketukan lagu.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 60}},
            "B": {"text": "Memastikan durasi videonya tidak kepanjangan.", "bobot": {"SIKC": 85, "RPL": 50, "TRK": 30, "TI": 50}},
            "C": {"text": "Rendering videonya biar kualitas 4K.", "bobot": {"SIKC": 30, "RPL": 60, "TRK": 80, "TI": 50}},
            "D": {"text": "Menganalisis jam upload terbaik.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu bekerja di perusahaan ojek online, fitur apa yang mau kamu buat?",
        "pilihan": {
            "A": {"text": "Fitur 'Chat Otomatis' yang menerjemahkan bahasa asing driver-turis.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 80}},
            "B": {"text": "Sistem bonus poin yang lebih adil.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 60}},
            "C": {"text": "Helm pintar yang ada bluetooth-nya.", "bobot": {"SIKC": 30, "RPL": 50, "TRK": 95, "TI": 60}},
            "D": {"text": "Motor listrik untuk driver.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Apa reaksimu saat aplikasi favoritmu update dan tampilannya berubah total?",
        "pilihan": {
            "A": {"text": "Kesal karena harus belajar pakai lagi.", "bobot": {"SIKC": 50, "RPL": 30, "TRK": 40, "TI": 30}},
            "B": {"text": "Mengeksplorasi apa saja yang baru dan membandingkan dengan yang lama.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 30, "TI": 60}},
            "C": {"text": "Tidak peduli, asal masih bisa dipakai.", "bobot": {"SIKC": 60, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Takut aplikasinya jadi berat.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 80, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu diminta mendesain kamar tidur impian. Apa yang kamu gambar duluan?",
        "pilihan": {
            "A": {"text": "Tata letak (layout) kasur dan meja agar pergerakan enak.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 40, "TI": 60}},
            "B": {"text": "Daftar barang yang harus dibeli.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Posisi colokan listrik.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "D": {"text": "Warna cat tembok.", "bobot": {"SIKC": 50, "RPL": 80, "TRK": 30, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Apa definisi 'Cerdas' menurutmu?",
        "pilihan": {
            "A": {"text": "Bisa menciptakan solusi baru yang belum terpikirkan orang lain.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 30, "TI": 70}},
            "B": {"text": "Tahu banyak informasi dan data.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 30, "TI": 60}},
            "C": {"text": "Bisa memperbaiki segala macam alat.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 95, "TI": 60}},
            "D": {"text": "Nilai ujiannya 100 terus.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 60, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu seorang pelukis, kamu lebih suka melukis:",
        "pilihan": {
            "A": {"text": "Abstrak dan imajinatif.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}},
            "B": {"text": "Pemandangan alam yang realistis.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 50, "TI": 50}},
            "C": {"text": "Sketsa bangunan teknik.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 90, "TI": 60}},
            "D": {"text": "Potret wajah tokoh sejarah.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 30, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu sedang menulis cerita novel. Tiba-tiba idemu mentok (writer's block). Solusimu?",
        "pilihan": {
            "A": {"text": "Membuat diagram alur cerita bercabang (Mind map).", "bobot": {"SIKC": 60, "RPL": 95, "TRK": 30, "TI": 60}},
            "B": {"text": "Mencari inspirasi dari data penjualan novel terlaris.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Jalan-jalan cari angin.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 40, "TI": 40}},
            "D": {"text": "Ganti laptop yang keyboardnya lebih enak.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 80, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Apa yang kamu lakukan jika tombol 'Like' di Instagram hilang?",
        "pilihan": {
            "A": {"text": "Merasa aneh, karena interaksi jadi tidak terlihat.", "bobot": {"SIKC": 60, "RPL": 85, "TRK": 30, "TI": 50}},
            "B": {"text": "Senang, jadi tidak perlu pusing mikirin jumlah like (Data).", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 50}},
            "C": {"text": "Mencari cara memunculkannya kembali lewat pengaturan.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 60, "TI": 70}},
            "D": {"text": "Pasti servernya lagi error.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 85, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu ingin membuat kode rahasia dengan temanmu. Caranya?",
        "pilihan": {
            "A": {"text": "Menggeser setiap huruf satu langkah (A jadi B, B jadi C).", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 30, "TI": 80}},
            "B": {"text": "Menulis di kertas lalu dibakar setelah dibaca.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 70, "TI": 40}},
            "C": {"text": "Menggunakan bahasa asing.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 30, "TI": 50}},
            "D": {"text": "Mengedipkan mata sebagai sinyal.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 50, "TI": 40}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Bagaimana pendapatmu tentang 'Dark Mode' (Mode Gelap) di HP?",
        "pilihan": {
            "A": {"text": "Sangat membantu mata dan terlihat elegan (UX).", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 60}},
            "B": {"text": "Hemat baterai (Hardware).", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 90, "TI": 60}},
            "C": {"text": "Susah dibaca kalau di bawah matahari.", "bobot": {"SIKC": 50, "RPL": 70, "TRK": 40, "TI": 50}},
            "D": {"text": "Tidak terbiasa.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    },
    # SOAL 36-50 (Lanjutan untuk melengkapi 50 soal)
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu menemukan aplikasi yang desainnya sangat bagus tapi fiturnya sedikit. Reaksimu?",
        "pilihan": {
            "A": {"text": "Langsung hapus, karena tidak fungsional.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "B": {"text": "Akan dipakai, karena desainnya membuat nyaman.", "bobot": {"SIKC": 60, "RPL": 95, "TRK": 40, "TI": 50}},
            "C": {"text": "Mencari tahu apakah ada update fitur yang akan datang.", "bobot": {"SIKC": 50, "RPL": 80, "TRK": 40, "TI": 60}},
            "D": {"text": "Mengirimkan *feedback* agar ditambahkan fitur baru.", "bobot": {"SIKC": 70, "RPL": 90, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Dalam membuat video tutorial memasak, hal paling penting adalah:",
        "pilihan": {
            "A": {"text": "Kualitas kamera dan pencahayaan yang bagus.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 50, "TI": 40}},
            "B": {"text": "Resep yang unik dan belum pernah ada.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 40, "TI": 60}},
            "C": {"text": "Langkah-langkah yang berurutan, jelas, dan mudah diikuti penonton.", "bobot": {"SIKC": 80, "RPL": 95, "TRK": 40, "TI": 90}},
            "D": {"text": "Data jumlah kalori pada masakan itu.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu lebih suka mengikuti panduan yang formatnya:",
        "pilihan": {
            "A": {"text": "Teks panjang dan detail.", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 40, "TI": 50}},
            "B": {"text": "Hanya gambar-gambar ilustrasi.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 50, "TI": 50}},
            "C": {"text": "Video *step-by-step*.", "bobot": {"SIKC": 50, "RPL": 85, "TRK": 60, "TI": 60}},
            "D": {"text": "Diagram alir dan poin-poin singkat.", "bobot": {"SIKC": 90, "RPL": 95, "TRK": 40, "TI": 80}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu menjadi *game master* di *game online*, apa hal paling penting yang kamu ciptakan?",
        "pilihan": {
            "A": {"text": "Aturan permainan (mekanisme *game*) yang adil dan logis.", "bobot": {"SIKC": 60, "RPL": 95, "TRK": 40, "TI": 90}},
            "B": {"text": "Desain karakter dan *map* yang indah.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}},
            "C": {"text": "Spesifikasi *server* yang kencang.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 95, "TI": 60}},
            "D": {"text": "Sistem keamanan anti-curang.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 50, "TI": 70}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Saat melihat desain *packaging* produk, kamu lebih fokus ke:",
        "pilihan": {
            "A": {"text": "Material bahan *packaging* (plastik/kertas/aluminium).", "bobot": {"SIKC": 40, "RPL": 60, "TRK": 90, "TI": 50}},
            "B": {"text": "Warna, *font*, dan logo yang menarik.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 30, "TI": 50}},
            "C": {"text": "Informasi nutrisi dan tanggal kedaluwarsa.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 40, "TI": 50}},
            "D": {"text": "Kemudahan saat dibuka dan ditutup (ergonomi).", "bobot": {"SIKC": 50, "RPL": 85, "TRK": 70, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu ingin membuat sistem *e-wallet* baru. Apa yang paling penting agar pengguna mau memakainya?",
        "pilihan": {
            "A": {"text": "Keamanan data yang sangat ketat (enkripsi).", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 80, "TI": 90}},
            "B": {"text": "Tampilan aplikasi yang intuitif dan proses transaksi yang cepat.", "bobot": {"SIKC": 70, "RPL": 95, "TRK": 50, "TI": 80}},
            "C": {"text": "Banyak *promo* dan *cashback*.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 50}},
            "D": {"text": "Bisa *top-up* dari mana saja.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 60, "TI": 50}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu menjadi *master chef*, kamu lebih suka:",
        "pilihan": {
            "A": {"text": "Membuat resep baru yang belum pernah ada.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 60}},
            "B": {"text": "Membuat laporan inventaris bahan baku dapur.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Memastikan semua alat dapur berfungsi sempurna.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 50}},
            "D": {"text": "Menghitung berapa porsi maksimal yang bisa dibuat dalam 1 jam.", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 40, "TI": 70}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu sedang membuat *PowerPoint* untuk presentasi. Agar tidak bosan, kamu akan:",
        "pilihan": {
            "A": {"text": "Mengurangi teks dan memperbanyak visualisasi/gambar.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 60}},
            "B": {"text": "Memastikan *font* dan warnanya terbaca jelas dari jauh.", "bobot": {"SIKC": 60, "RPL": 90, "TRK": 40, "TI": 50}},
            "C": {"text": "Menyusun *slide* dengan alur cerita yang menarik.", "bobot": {"SIKC": 70, "RPL": 85, "TRK": 30, "TI": 60}},
            "D": {"text": "Memastikan proyektornya tidak bermasalah.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 90, "TI": 40}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Apa yang paling kamu perhatikan saat mengunjungi sebuah *website* baru?",
        "pilihan": {
            "A": {"text": "Keamanan (*HTTPS*).", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 90, "TI": 80}},
            "B": {"text": "Warna dan tata letak menu. (Desain UX/UI)", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 60}},
            "C": {"text": "Informasi apa yang ada di halaman depan.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 30, "TI": 50}},
            "D": {"text": "Berapa lama *website* itu *loading*.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 85, "TI": 70}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu mendesain sebuah mesin penjual otomatis (*vending machine*), bagian mana yang kamu buat paling mudah?",
        "pilihan": {
            "A": {"text": "Mekanisme pengeluaran uang kembalian.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 95, "TI": 60}},
            "B": {"text": "Tombol-tombol pilihan produk dan layar instruksi.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 70}},
            "C": {"text": "Sistem inventaris stok produk di dalamnya.", "bobot": {"SIKC": 90, "RPL": 60, "TRK": 40, "TI": 50}},
            "D": {"text": "Kotak besi luar agar tahan banting.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 90, "TI": 40}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Kamu ingin membuat kampanye sosial untuk melestarikan lingkungan. Fokus utamamu:",
        "pilihan": {
            "A": {"text": "Membuat media sosial yang desainnya menarik perhatian anak muda.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 30, "TI": 50}},
            "B": {"text": "Mengumpulkan data dampak sampah plastik dalam 10 tahun terakhir.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "C": {"text": "Mencari *sponsor* dana untuk kampanye.", "bobot": {"SIKC": 70, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Mengajak orang-orang untuk ikut aksi bersih-bersih.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 50, "TI": 40}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Apa yang membuatmu kagum dengan *chatbots* (AI yang membalas pesan otomatis)?",
        "pilihan": {
            "A": {"text": "Kecepatannya dalam merespons pertanyaan yang logis.", "bobot": {"SIKC": 70, "RPL": 95, "TRK": 40, "TI": 80}},
            "B": {"text": "Data yang digunakan untuk melatih AI itu.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 40, "TI": 60}},
            "C": {"text": "Bahasa yang digunakan sangat alami seperti manusia.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 30, "TI": 70}},
            "D": {"text": "Kemampuan *server*-nya untuk menjawab jutaan *chat*.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 95, "TI": 60}}
        }
    },
    {
        "kategori": "pengembangan",
        "pertanyaan": "Jika kamu membuat peta petunjuk jalan untuk anak kecil, yang kamu prioritaskan adalah:",
        "pilihan": {
            "A": {"text": "Warna yang cerah dan gambar yang lucu.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 30, "TI": 50}},
            "B": {"text": "Alur jalan yang paling aman (tanpa harus memprediksi rute).", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 40, "TI": 50}},
            "C": {"text": "Keterangan langkah yang sangat sederhana dan berulang.", "bobot": {"SIKC": 80, "RPL": 90, "TRK": 30, "TI": 85}},
            "D": {"text": "Membuat petanya dari kertas yang tebal.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 90, "TI": 40}}
        }
    }
]

# ------------------------------------------------------------------
# KATEGORI 3: PERANGKAT KERAS & JARINGAN (TRK/TKJ/Teknik Komputer)
# Fokus: Infrastruktur, Fisik, Konektivitas, Mekanik, Troubleshooting
# ------------------------------------------------------------------
hardware_soal = [
    # SOAL 1-35 (Dikutip dari input Anda)
    {
        "kategori": "hardware",
        "pertanyaan": "Wifi di rumahmu tiba-tiba lemot banget. Apa tindakan pertamamu?",
        "pilihan": {
            "A": {"text": "Melihat lampu indikator di modem/router, nyala atau kedip?", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 70}},
            "B": {"text": "Komplain ke customer service lewat aplikasi.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 30, "TI": 40}},
            "C": {"text": "Cek kuota internet masih ada atau tidak.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 40, "TI": 50}},
            "D": {"text": "Restart HP atau laptopmu.", "bobot": {"SIKC": 40, "RPL": 70, "TRK": 60, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Saat merakit meja belajar baru dari kardus, bagian mana yang kamu suka?",
        "pilihan": {
            "A": {"text": "Memasang baut dan menyambungkan kaki meja sampai kokoh.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Membaca buku panduannya biar tidak salah urutan.", "bobot": {"SIKC": 60, "RPL": 80, "TRK": 50, "TI": 70}},
            "C": {"text": "Menghias meja setelah jadi.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}},
            "D": {"text": "Memastikan meja muat di sudut kamar (ukur ruang).", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 50, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kabel charger HP-mu sering putus atau rusak. Apa yang kamu pikirkan?",
        "pilihan": {
            "A": {"text": "Kenapa kualitas bahannya jelek sekali ya?", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 80, "TI": 50}},
            "B": {"text": "Harusnya ada charger nirkabel (wireless) di mana-mana.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 90, "TI": 60}},
            "C": {"text": "Mencari toko yang jual charger paling murah.", "bobot": {"SIKC": 70, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Mendesain pelindung kabel biar awet.", "bobot": {"SIKC": 40, "RPL": 85, "TRK": 60, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kamu masuk ke ruangan server yang dingin dan penuh kabel. Kesanmu?",
        "pilihan": {
            "A": {"text": "Keren, seperti di film sci-fi! Ingin tahu kabel ini ke mana saja.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 70}},
            "B": {"text": "Bising sekali suaranya.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 40, "TI": 30}},
            "C": {"text": "Data apa saja ya yang tersimpan di sini?", "bobot": {"SIKC": 90, "RPL": 60, "TRK": 40, "TI": 60}},
            "D": {"text": "Pasti program yang jalan di sini berat banget.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 50, "TI": 70}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "HP-mu jatuh ke air. Tindakan penyelamatan pertamamu?",
        "pilihan": {
            "A": {"text": "Langsung nyalakan untuk cek masih hidup atau tidak.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 10, "TI": 20}},
            "B": {"text": "Matikan, bongkar casing/baterai, lalu kubur di beras (keringkan).", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 95, "TI": 70}},
            "C": {"text": "Browsing di internet cara memperbaiki HP basah.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 50, "TI": 70}},
            "D": {"text": "Langsung bawa ke tukang servis.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa yang paling kamu benci dari komputer sekolah?",
        "pilihan": {
            "A": {"text": "Koneksi internetnya sering putus-nyambung.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 90, "TI": 70}},
            "B": {"text": "Aplikasinya jadul dan susah dipakai.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 40, "TI": 60}},
            "C": {"text": "Banyak file sampah dari murid lain.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 40, "TI": 50}},
            "D": {"text": "Mouse dan keyboard-nya kotor/rusak.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 80, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Di rumahmu ada 'Area Mati Sinyal' (Blank Spot). Solusimu?",
        "pilihan": {
            "A": {"text": "Pindah duduk ke dekat jendela kalau mau internetan.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 40, "TI": 30}},
            "B": {"text": "Membeli alat penguat sinyal (Repeater/Extender) dan memasangnya.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 95, "TI": 75}},
            "C": {"text": "Download film dulu saat ada sinyal biar bisa ditonton offline.", "bobot": {"SIKC": 70, "RPL": 70, "TRK": 40, "TI": 50}},
            "D": {"text": "Komplain ke provider seluler.", "bobot": {"SIKC": 60, "RPL": 40, "TRK": 50, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kamu ingin beli laptop baru. Spesifikasi apa yang paling kamu perhatikan?",
        "pilihan": {
            "A": {"text": "Prosesor dan RAM-nya (Kecepatan mesin).", "bobot": {"SIKC": 50, "RPL": 70, "TRK": 95, "TI": 80}},
            "B": {"text": "Resolusi layar dan akurasi warna.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 50, "TI": 60}},
            "C": {"text": "Desainnya tipis dan ringan.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 40, "TI": 50}},
            "D": {"text": "Kapasitas penyimpanan (Harddisk/SSD) untuk simpan banyak data.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 60, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Jika kamu melihat kabel earphone kusut parah, reaksimu:",
        "pilihan": {
            "A": {"text": "Sabar mengurainya pelan-pelan sampai lurus kembali.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 50}},
            "B": {"text": "Kesal, mending beli headset bluetooth saja.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 70, "TI": 60}},
            "C": {"text": "Langsung tarik saja, semoga tidak putus.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 10, "TI": 20}},
            "D": {"text": "Memikirkan alat penggulung kabel otomatis.", "bobot": {"SIKC": 60, "RPL": 85, "TRK": 50, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Temanmu minta tolong 'rakit PC gaming'. Bagian mana yang kamu bantu?",
        "pilihan": {
            "A": {"text": "Memilihkan komponen yang kompatibel (Cek soket prosesor, jenis RAM).", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 95, "TI": 70}},
            "B": {"text": "Menginstall Windows dan game-gamenya.", "bobot": {"SIKC": 60, "RPL": 80, "TRK": 60, "TI": 70}},
            "C": {"text": "Menghitung total harganya biar sesuai budget.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 40, "TI": 50}},
            "D": {"text": "Menata kabel di dalam casing biar rapi (Cable management).", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa pendapatmu tentang mobil listrik?",
        "pilihan": {
            "A": {"text": "Teknologi baterai dan motor penggeraknya canggih.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 95, "TI": 70}},
            "B": {"text": "Sistem autopilot (nyetir sendiri)-nya keren.", "bobot": {"SIKC": 60, "RPL": 95, "TRK": 50, "TI": 80}},
            "C": {"text": "Bagus untuk mengurangi data polusi udara kota.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 40, "TI": 50}},
            "D": {"text": "Panel layar sentuh di dashboard-nya futuristik.", "bobot": {"SIKC": 50, "RPL": 80, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Di belakang TV atau komputermu, kondisinya adalah...",
        "pilihan": {
            "A": {"text": "Hutan kabel yang semrawut dan penuh debu.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 20, "TI": 30}},
            "B": {"text": "Rapi, kabel diikat pakai 'cable ties' atau velkro.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 95, "TI": 60}},
            "C": {"text": "Tidak tahu, tidak pernah melihat ke sana.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 10, "TI": 20}},
            "D": {"text": "Kabelnya diberi label biar tahu mana kabel apa.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 80, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Saat listrik di rumah mati (jepret), apa yang kamu lakukan?",
        "pilihan": {
            "A": {"text": "Mencari lilin atau senter.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 40, "TI": 50}},
            "B": {"text": "Cek sekring/MCB meteran listrik, coba nyalakan lagi.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "C": {"text": "Lapor ke PLN lewat aplikasi.", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 40, "TI": 50}},
            "D": {"text": "Mikirin alat elektronik apa yang tadi nyala barengan.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 80, "TI": 70}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Bagaimana caramu mengirim file besar ke teman di sebelahmu?",
        "pilihan": {
            "A": {"text": "Pakai Flashdisk/Harddisk eksternal biar cepat.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 90, "TI": 60}},
            "B": {"text": "Upload ke Google Drive lalu kirim link.", "bobot": {"SIKC": 85, "RPL": 70, "TRK": 50, "TI": 60}},
            "C": {"text": "Kirim lewat WhatsApp (meski pecah).", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}},
            "D": {"text": "Pakai fitur Share terdekat (AirDrop/QuickShare).", "bobot": {"SIKC": 60, "RPL": 85, "TRK": 70, "TI": 70}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kamu penasaran dengan cara kerja Drone. Apanya yang paling bikin penasaran?",
        "pilihan": {
            "A": {"text": "Motor baling-baling dan keseimbangan terbangnya.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Program remote control dan fitur 'pulang otomatis'.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 50, "TI": 80}},
            "C": {"text": "Hasil rekaman videonya.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 40, "TI": 50}},
            "D": {"text": "Berapa lama baterainya kuat terbang.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 85, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Jika keyboard laptopmu ada tombol yang copot, kamu akan:",
        "pilihan": {
            "A": {"text": "Mencoba memasangnya kembali dengan hati-hati.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 60}},
            "B": {"text": "Pakai keyboard eksternal (USB).", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 70, "TI": 50}},
            "C": {"text": "Menggunakan On-Screen Keyboard (di layar).", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 40, "TI": 50}},
            "D": {"text": "Membiarkannya ompong.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa yang kamu bayangkan tentang 'Cloud Storage' (Penyimpanan Awan)?",
        "pilihan": {
            "A": {"text": "Gedung besar penuh harddisk yang menyala 24 jam di suatu tempat.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 95, "TI": 70}},
            "B": {"text": "Data yang melayang di udara lewat sinyal.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 40, "TI": 30}},
            "C": {"text": "Cara praktis backup data biar tidak hilang.", "bobot": {"SIKC": 90, "RPL": 60, "TRK": 50, "TI": 60}},
            "D": {"text": "Aplikasi Google Drive atau Dropbox.", "bobot": {"SIKC": 60, "RPL": 90, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kipas angin di kamarmu bunyinya berisik. Apa dugaanmu?",
        "pilihan": {
            "A": {"text": "Mungkin kotor atau pelumasnya habis (masalah mekanik).", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Beli baru saja.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 30, "TI": 40}},
            "C": {"text": "Listriknya tidak stabil.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 80, "TI": 50}},
            "D": {"text": "Hantunya lagi main kipas.", "bobot": {"SIKC": 10, "RPL": 10, "TRK": 10, "TI": 10}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kamu melihat tukang sedang memanjat tiang telepon/internet. Apa pikirmu?",
        "pilihan": {
            "A": {"text": "Semoga dia tidak jatuh.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 50, "TI": 50}},
            "B": {"text": "Rumit juga ya menyambung kabel serat optik (fiber) itu.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 70}},
            "C": {"text": "Pasti internet satu komplek lagi gangguan.", "bobot": {"SIKC": 80, "RPL": 60, "TRK": 50, "TI": 60}},
            "D": {"text": "Kenapa tidak pakai nirkabel semua saja ya?", "bobot": {"SIKC": 60, "RPL": 80, "TRK": 85, "TI": 70}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Jika kamu punya uang untuk upgrade PC, apa yang kamu beli duluan?",
        "pilihan": {
            "A": {"text": "Monitor yang lebih besar dan jernih.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 50, "TI": 60}},
            "B": {"text": "SSD (Storage) biar booting/loading super cepat.", "bobot": {"SIKC": 50, "RPL": 70, "TRK": 95, "TI": 80}},
            "C": {"text": "Keyboard mekanik yang bunyinya 'tek tek tek'.", "bobot": {"SIKC": 40, "RPL": 85, "TRK": 50, "TI": 60}},
            "D": {"text": "Langganan internet yang lebih kencang.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 80, "TI": 70}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa yang kamu lakukan sebelum mencabut Flashdisk dari komputer?",
        "pilihan": {
            "A": {"text": "Langsung cabut saja, buru-buru.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 10, "TI": 20}},
            "B": {"text": "Klik 'Eject' atau 'Safely Remove' dulu.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 95, "TI": 70}},
            "C": {"text": "Tutup semua file yang ada di flashdisk.", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 60, "TI": 60}},
            "D": {"text": "Scan virus dulu.", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 50, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kamu diminta memasang sound system untuk acara sekolah. Tantangannya?",
        "pilihan": {
            "A": {"text": "Menghindari kabel melintang yang bisa bikin orang tersandung.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 85, "TI": 50}},
            "B": {"text": "Mengatur agar suaranya tidak mendengung (feedback) dan jernih.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "C": {"text": "Memilih lagu yang bagus.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 30, "TI": 40}},
            "D": {"text": "Mendata alat apa saja yang dipinjam.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kenapa baterai HP lama-kelamaan jadi boros (bocor)?",
        "pilihan": {
            "A": {"text": "Karena sering dipakai main game berat.", "bobot": {"SIKC": 50, "RPL": 70, "TRK": 60, "TI": 60}},
            "B": {"text": "Kesehatan kimiawi baterainya menurun (Cycle count).", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 95, "TI": 70}},
            "C": {"text": "Kebanyakan aplikasi yang jalan di background.", "bobot": {"SIKC": 60, "RPL": 85, "TRK": 50, "TI": 60}},
            "D": {"text": "Salah nge-charge.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 70, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa gunanya Casing HP menurutmu?",
        "pilihan": {
            "A": {"text": "Melindungi fisik HP dari benturan keras.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Biar tampilannya lucu dan estetik.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}},
            "C": {"text": "Tempat nyelipin kartu ATM/Uang.", "bobot": {"SIKC": 85, "RPL": 40, "TRK": 40, "TI": 50}},
            "D": {"text": "Biar tidak licin dipegang.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 60, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Jika kamu masuk toko komputer, aroma apa yang khas?",
        "pilihan": {
            "A": {"text": "Aroma plastik dan elektronik baru.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 60}},
            "B": {"text": "Aroma pewangi ruangan.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 50, "TI": 50}},
            "C": {"text": "Dingin AC-nya.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 60, "TI": 50}},
            "D": {"text": "Tidak memperhatikan aroma.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa yang kamu lakukan dengan barang elektronik bekas yang rusak?",
        "pilihan": {
            "A": {"text": "Membongkarnya, ingin lihat isinya (kanibalan komponen).", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 70}},
            "B": {"text": "Menjualnya ke tukang loak.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 40, "TI": 50}},
            "C": {"text": "Dibuang ke tempat sampah.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}},
            "D": {"text": "Disimpan di gudang selamanya.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Menurutmu, apa penemuan hardware terpenting abad ini?",
        "pilihan": {
            "A": {"text": "Smartphone (Layar sentuh).", "bobot": {"SIKC": 60, "RPL": 90, "TRK": 70, "TI": 80}},
            "B": {"text": "Transistor/Prosesor (Otak komputer mikro).", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 95, "TI": 85}},
            "C": {"text": "Internet (Konektivitas).", "bobot": {"SIKC": 90, "RPL": 80, "TRK": 80, "TI": 85}},
            "D": {"text": "Kamera digital.", "bobot": {"SIKC": 50, "RPL": 70, "TRK": 60, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Saat menyambungkan laptop ke proyektor tapi tidak muncul gambar, kamu:",
        "pilihan": {
            "A": {"text": "Panik dan minta bantuan teman.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}},
            "B": {"text": "Cek kabel VGA/HDMI-nya, goyang-goyangkan sedikit.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "C": {"text": "Tekan tombol Windows+P untuk setting layar.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 60, "TI": 70}},
            "D": {"text": "Restart laptop.", "bobot": {"SIKC": 40, "RPL": 60, "TRK": 50, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kamu lebih suka mouse pakai kabel atau wireless?",
        "pilihan": {
            "A": {"text": "Kabel, karena responsnya lebih cepat (zero latency) buat gaming.", "bobot": {"SIKC": 40, "RPL": 60, "TRK": 95, "TI": 70}},
            "B": {"text": "Wireless, biar meja terlihat rapi dan bersih.", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 40, "TI": 60}},
            "C": {"text": "Touchpad laptop saja cukup.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 30, "TI": 40}},
            "D": {"text": "Tergantung harga.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa yang kamu pikirkan saat melihat Robot di film?",
        "pilihan": {
            "A": {"text": "Bagaimana cara menyusun kerangka besinya agar bisa jalan.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 95, "TI": 60}},
            "B": {"text": "Bagaimana coding AI-nya agar dia pintar.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 80}},
            "C": {"text": "Apakah robot itu akan mengambil alih dunia?", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 30, "TI": 50}},
            "D": {"text": "Berapa harganya.", "bobot": {"SIKC": 60, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    # SOAL 36-50 (Lanjutan untuk melengkapi 50 soal)
    {
        "kategori": "hardware",
        "pertanyaan": "Jika kamu harus menyambungkan kabel listrik (fase, netral, ground) yang berantakan, kamu akan:",
        "pilihan": {
            "A": {"text": "Mencoba menyambungkan satu per satu sampai lampunya menyala.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 80, "TI": 50}},
            "B": {"text": "Menggunakan alat ukur (multimeter) untuk cek arus dan tegangan tiap kabel.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 95, "TI": 70}},
            "C": {"text": "Memanggil tukang listrik.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 50, "TI": 40}},
            "D": {"text": "Mencari *diagram* rangkaian listrik rumah itu.", "bobot": {"SIKC": 80, "RPL": 60, "TRK": 70, "TI": 80}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa yang kamu lakukan saat komputer di lab sekolah tidak bisa menyala?",
        "pilihan": {
            "A": {"text": "Mengecek kabel power, monitor, dan menekan tombol *reset*.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Mencoba *login* dengan akun lain.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 50, "TI": 70}},
            "C": {"text": "Langsung lapor guru.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 40, "TI": 30}},
            "D": {"text": "Membongkar *casing* CPU-nya.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 85, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Menurutmu, di mana tempat terbaik untuk menaruh router/modem Wi-Fi di rumah?",
        "pilihan": {
            "A": {"text": "Di dekat jendela, agar sinyal ke luar rumah kuat.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 80, "TI": 50}},
            "B": {"text": "Di tengah rumah, di tempat tinggi, dan jauh dari tembok beton.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 95, "TI": 70}},
            "C": {"text": "Di kamar tidurmu saja.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 50, "TI": 40}},
            "D": {"text": "Di dekat TV.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 60, "TI": 40}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kenapa kebanyakan ATM punya tombol-tombol yang terbuat dari logam/besi?",
        "pilihan": {
            "A": {"text": "Agar terlihat canggih.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 40, "TI": 40}},
            "B": {"text": "Agar tahan banting/rusak dan sulit dibobol.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 95, "TI": 70}},
            "C": {"text": "Agar bisa menghantarkan listrik lebih baik.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 85, "TI": 60}},
            "D": {"text": "Agar mudah dibersihkan.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 60, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Jika kamu diminta merakit *charger* HP sendiri, bagian paling sulit adalah:",
        "pilihan": {
            "A": {"text": "Membuat *casing* plastik yang bagus.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 40, "TI": 50}},
            "B": {"text": "Menghitung dan merakit komponen *chip* di dalamnya agar listriknya stabil.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 95, "TI": 90}},
            "C": {"text": "Mencari kabel USB yang kuat.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 60}},
            "D": {"text": "Menghitung modal dan biaya jualnya.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Kamu menemukan kabel jaringan internet yang terkelupas. Tindakanmu:",
        "pilihan": {
            "A": {"text": "Membungkusnya dengan isolasi biasa.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 60, "TI": 50}},
            "B": {"text": "Memotong bagian yang terkelupas dan menyambungnya kembali dengan benar.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 95, "TI": 70}},
            "C": {"text": "Membiarkannya saja asal masih bisa internetan.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 10, "TI": 20}},
            "D": {"text": "Mengganti semua kabel di rumah.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 80, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Ketika membeli *power bank*, yang paling kamu perhatikan adalah:",
        "pilihan": {
            "A": {"text": "Desain dan warnanya.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 40, "TI": 50}},
            "B": {"text": "Kapasitas (mAh) dan fitur *fast charging*.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 95, "TI": 70}},
            "C": {"text": "Merk dan harganya.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 60, "TI": 50}},
            "D": {"text": "Fitur keamanan anti konslet.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 90, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa yang paling sulit dari membuat *server* untuk *website* sekolah?",
        "pilihan": {
            "A": {"text": "Membuat *hardware*-nya bisa menyala 24 jam nonstop (Tahan panas).", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 95, "TI": 70}},
            "B": {"text": "Desain *website*-nya agar bagus dilihat.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 30, "TI": 50}},
            "C": {"text": "Memastikan data siswa tidak hilang atau dicuri.", "bobot": {"SIKC": 90, "RPL": 60, "TRK": 80, "TI": 90}},
            "D": {"text": "Merekam semua data aktivitas pengunjung *website*.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Jika kamu merancang sebuah *smartwatch*, kamu akan fokus pada:",
        "pilihan": {
            "A": {"text": "Kualitas material dan *strap* yang nyaman dipakai.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 60, "TI": 50}},
            "B": {"text": "Akurasi sensor kesehatan (detak jantung, oksigen).", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 95, "TI": 70}},
            "C": {"text": "Tampilan *user interface*-nya yang mudah disentuh.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 40, "TI": 60}},
            "D": {"text": "Baterai yang tahan 2 minggu.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 90, "TI": 60}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa perbedaan paling mendasar antara *speaker* aktif dan pasif?",
        "pilihan": {
            "A": {"text": "*Speaker* aktif lebih mahal.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "B": {"text": "*Speaker* aktif punya amplifier (penguat suara) di dalamnya.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 95, "TI": 70}},
            "C": {"text": "*Speaker* pasif bunyinya lebih pelan.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 40, "TI": 30}},
            "D": {"text": "*Speaker* aktif desainnya lebih modern.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 50, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Jika kamu menjadi teknisi jaringan, hal pertama yang kamu pastikan adalah:",
        "pilihan": {
            "A": {"text": "Semua kabel sudah tertancap dengan rapi dan benar.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 95, "TI": 70}},
            "B": {"text": "Semua *user* tahu *password* Wi-Fi.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "C": {"text": "Sudah *login* ke *website* *provider*.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 70, "TI": 50}},
            "D": {"text": "Semua *hardware* masih garansi.", "bobot": {"SIKC": 80, "RPL": 40, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Apa yang membuatmu kagum dengan *chip* seukuran kuku yang ada di HP?",
        "pilihan": {
            "A": {"text": "Desainnya yang rumit dan kecil.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 95, "TI": 70}},
            "B": {"text": "Bisa menyimpan data sebanyak itu.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 70, "TI": 60}},
            "C": {"text": "Kecepatannya memproses triliunan data per detik.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 95, "TI": 90}},
            "D": {"text": "Diproduksi di pabrik yang bersih.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 70, "TI": 50}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Ketika melihat robot sedang mengelas (menyambung besi), kamu fokus pada:",
        "pilihan": {
            "A": {"text": "Presisi pergerakan sendi robotnya.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 95, "TI": 70}},
            "B": {"text": "Kualitas hasil lasannya.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 80, "TI": 60}},
            "C": {"text": "Program yang mengendalikan gerakan robot itu.", "bobot": {"SIKC": 60, "RPL": 90, "TRK": 50, "TI": 85}},
            "D": {"text": "Harga robot itu.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "hardware",
        "pertanyaan": "Mengapa kita sering disarankan untuk *update software* (misal: *firmware*) pada router Wi-Fi?",
        "pilihan": {
            "A": {"text": "Agar tampilannya jadi lebih bagus.", "bobot": {"SIKC": 30, "RPL": 70, "TRK": 40, "TI": 50}},
            "B": {"text": "Agar koneksi Wi-Fi lebih cepat.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 85, "TI": 60}},
            "C": {"text": "Untuk menambal kelemahan keamanan jaringan yang sudah ditemukan.", "bobot": {"SIKC": 80, "RPL": 60, "TRK": 95, "TI": 80}},
            "D": {"text": "Karena paksaan dari pabrik.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    }
]

# ------------------------------------------------------------------
# KATEGORI 4: LOGIKA, ALGORITMA, & MATEMATIKA (TI/Teknik Informatika)
# Fokus: Logika, Pemecahan Masalah Sistematis, Abstraksi, Kuantitatif
# ------------------------------------------------------------------
logika_soal = [
    # SOAL 1-50 (Lengkap)
    {
        "kategori": "logika",
        "pertanyaan": "Kamu punya 100 bola yang harus diurutkan dari terkecil ke terbesar. Apa cara paling efisien?",
        "pilihan": {
            "A": {"text": "Mengambil 2 bola acak, membandingkan, dan menaruhnya. Ulangi 100 kali.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 50, "TI": 50}},
            "B": {"text": "Membuat tumpukan: ambil 1 bola, bandingkan dengan tumpukan terakhir, dan masukkan di tempatnya.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 50, "TI": 95}},
            "C": {"text": "Mengurutkan berdasarkan warna, lalu ukurannya.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 40, "TI": 70}},
            "D": {"text": "Meminta bantuan teman.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Saat bermain Catur, fokus utamamu adalah:",
        "pilihan": {
            "A": {"text": "Memprediksi 5-6 langkah ke depan yang mungkin dilakukan lawan.", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 50, "TI": 95}},
            "B": {"text": "Memastikan semua bidakmu tidak dimakan.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 40, "TI": 70}},
            "C": {"text": "Pindah bidak yang paling dekat dengan Raja lawan.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 50, "TI": 85}},
            "D": {"text": "Membuat bidakmu terlihat cantik di papan.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu ingin membuat *password* yang sangat kuat. Caranya?",
        "pilihan": {
            "A": {"text": "Menggunakan tanggal lahir atau nama pacar.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 40, "TI": 20}},
            "B": {"text": "Kombinasi acak: huruf besar, kecil, angka, dan simbol.", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 90, "TI": 95}},
            "C": {"text": "Menggunakan kata yang panjang.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 60, "TI": 70}},
            "D": {"text": "*Password* yang sama untuk semua akun.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 10}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu adalah seorang detektif, data apa yang paling kamu cari?",
        "pilihan": {
            "A": {"text": "Pola dan urutan waktu kejadian (kronologi) yang logis.", "bobot": {"SIKC": 90, "RPL": 70, "TRK": 50, "TI": 90}},
            "B": {"text": "Sidik jari atau jejak kaki.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 80, "TI": 70}},
            "C": {"text": "Bukti fisik berupa senjata.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 90, "TI": 60}},
            "D": {"text": "Kesaksian teman/keluarga korban.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu ingin mengirim paket ke 5 alamat berbeda. Agar bensinnya hemat, apa yang kamu cari?",
        "pilihan": {
            "A": {"text": "Rute terpendek yang menghubungkan semua alamat (Masalah *Travelling Salesman*).", "bobot": {"SIKC": 90, "RPL": 85, "TRK": 60, "TI": 95}},
            "B": {"text": "Waktu yang paling sepi di jalan.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 50, "TI": 80}},
            "C": {"text": "Meminta jasa kurir.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Motor yang paling irit bensin.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 80, "TI": 50}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Ketika kamu mencoba resep kue baru, kamu lebih fokus pada:",
        "pilihan": {
            "A": {"text": "Bahan-bahan harus yang paling mahal dan berkualitas.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 40, "TI": 50}},
            "B": {"text": "Timbangan bahan yang presisi dan urutan langkah yang benar.", "bobot": {"SIKC": 80, "RPL": 90, "TRK": 60, "TI": 95}},
            "C": {"text": "Tampilan kuenya setelah matang.", "bobot": {"SIKC": 50, "RPL": 95, "TRK": 40, "TI": 60}},
            "D": {"text": "*Review* dari temanmu.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu menulis program sederhana untuk kalkulator. Hal paling sulit adalah:",
        "pilihan": {
            "A": {"text": "Desain tampilannya.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 40, "TI": 60}},
            "B": {"text": "Membuatnya bisa menghitung operasi yang rumit (Order of Operations).", "bobot": {"SIKC": 70, "RPL": 80, "TRK": 50, "TI": 95}},
            "C": {"text": "Memastikan tombolnya tidak *error*.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 80, "TI": 70}},
            "D": {"text": "Membuatnya bisa *support* banyak bahasa.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Dalam film tentang pembajakan, hal yang kamu kagumi adalah:",
        "pilihan": {
            "A": {"text": "Aksi tembak-tembakan.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 60, "TI": 50}},
            "B": {"text": "Logika sistem keamanan yang berhasil mereka bobol.", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 80, "TI": 90}},
            "C": {"text": "Efek ledakannya yang realistis.", "bobot": {"SIKC": 40, "RPL": 60, "TRK": 90, "TI": 50}},
            "D": {"text": "Kapal/pesawat yang canggih.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 90, "TI": 70}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu menemukan petunjuk: *start* dari A, *move* ke B, jika C benar, *move* ke D, jika tidak *move* ke E. Kamu akan:",
        "pilihan": {
            "A": {"text": "Bingung dan coba acak.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}},
            "B": {"text": "Mencoba semua kemungkinan rute.", "bobot": {"SIKC": 70, "RPL": 80, "TRK": 60, "TI": 90}},
            "C": {"text": "Membuat diagram alir untuk memastikan alur logikanya benar.", "bobot": {"SIKC": 90, "RPL": 95, "TRK": 70, "TI": 95}},
            "D": {"text": "Menebak-nebak saja.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 40, "TI": 30}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa yang kamu lakukan saat bermain Sudoku atau teka-teki logika lainnya?",
        "pilihan": {
            "A": {"text": "Mengidentifikasi aturan mainnya, lalu eliminasi kemungkinan yang salah.", "bobot": {"SIKC": 85, "RPL": 80, "TRK": 60, "TI": 90}},
            "B": {"text": "Mencoba isi angka/kata secara acak di awal.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 50, "TI": 50}},
            "C": {"text": "Memakai pensil agar bisa dihapus.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Minta *clue* ke teman.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu diminta membuat sandi Morse (titik dan garis), fokusmu adalah:",
        "pilihan": {
            "A": {"text": "Membuat aturan yang mudah diingat tapi susah dipecahkan orang lain.", "bobot": {"SIKC": 70, "RPL": 90, "TRK": 50, "TI": 95}},
            "B": {"text": "Memastikan alat kirim sandi (senter/radio) berfungsi baik.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "C": {"text": "Mengirim sandinya secepat mungkin.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 60, "TI": 70}},
            "D": {"text": "Membuat daftar kata-kata yang akan disandikan.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu sedang main *game* balap mobil. Yang paling kamu perhitungkan adalah:",
        "pilihan": {
            "A": {"text": "Kecepatan maksimal mobilmu.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 90, "TI": 70}},
            "B": {"text": "Sudut dan timing pengereman di tikungan (fisika/algoritma).", "bobot": {"SIKC": 80, "RPL": 90, "TRK": 70, "TI": 95}},
            "C": {"text": "Tampilan *custom* mobilmu.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 40, "TI": 60}},
            "D": {"text": "Jalur mana yang ada *shortcut* tersembunyi.", "bobot": {"SIKC": 70, "RPL": 80, "TRK": 50, "TI": 85}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa yang paling kamu perhatikan saat menonton film *thriller*/misteri?",
        "pilihan": {
            "A": {"text": "Alur cerita yang membuat tegang.", "bobot": {"SIKC": 60, "RPL": 90, "TRK": 40, "TI": 70}},
            "B": {"text": "Kesalahan-kesalahan kecil (lubang plot) yang tidak logis.", "bobot": {"SIKC": 80, "RPL": 80, "TRK": 50, "TI": 95}},
            "C": {"text": "Aktor favoritmu.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 30, "TI": 30}},
            "D": {"text": "Kualitas suara dan *CGI* (Efek visual).", "bobot": {"SIKC": 40, "RPL": 70, "TRK": 80, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu diminta menghitung jarak tempuh cahaya ke planet terdekat, kamu akan:",
        "pilihan": {
            "A": {"text": "Mencari *website* yang sudah menghitungnya.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 50, "TI": 80}},
            "B": {"text": "Menerapkan rumus fisika dasar (jarak = kecepatan x waktu).", "bobot": {"SIKC": 80, "RPL": 60, "TRK": 60, "TI": 95}},
            "C": {"text": "Menggunakan perkiraan berdasarkan pengalaman.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Menggambar diagram tata surya.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 40, "TI": 70}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa yang paling kamu perlukan agar bisa menjadi seorang *hacker* (peretas) yang hebat?",
        "pilihan": {
            "A": {"text": "Komputer dengan *hardware* tercepat.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 90, "TI": 60}},
            "B": {"text": "Memahami sistem keamanan dan kelemahan logikanya.", "bobot": {"SIKC": 80, "RPL": 90, "TRK": 80, "TI": 95}},
            "C": {"text": "Akses internet yang super cepat.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 95, "TI": 70}},
            "D": {"text": "Kemampuan bersandiwara (sosial).", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu merancang sebuah robot sederhana, hal pertama yang kamu buat adalah:",
        "pilihan": {
            "A": {"text": "Kerangka badan robot dari besi.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Alur perintah (logika) agar robot tahu apa yang harus dilakukan (misal: maju, mundur).", "bobot": {"SIKC": 70, "RPL": 90, "TRK": 60, "TI": 95}},
            "C": {"text": "Desain luar robot agar terlihat keren.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 40, "TI": 60}},
            "D": {"text": "Power supply (baterai) yang kuat.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 90, "TI": 70}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu sedang bermain kartu Remi. Agar menang, fokus utamamu adalah:",
        "pilihan": {
            "A": {"text": "Menghafal kartu apa saja yang sudah dikeluarkan lawan.", "bobot": {"SIKC": 90, "RPL": 70, "TRK": 50, "TI": 90}},
            "B": {"text": "Membuat *face* atau *poker face* agar lawan tidak tahu kartu kita.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 40, "TI": 60}},
            "C": {"text": "Mengatur kartu di tangan agar rapi.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 40, "TI": 50}},
            "D": {"text": "Mencoba mengelabui lawan dengan gerakan tangan.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 50, "TI": 80}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa manfaat terbesar dari Matematika dalam kehidupan sehari-hari?",
        "pilihan": {
            "A": {"text": "Membantu berhitung saat belanja di pasar.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 40, "TI": 70}},
            "B": {"text": "Melatih otak untuk berpikir logis dan sistematis.", "bobot": {"SIKC": 80, "RPL": 80, "TRK": 60, "TI": 95}},
            "C": {"text": "Memecahkan teka-teki.", "bobot": {"SIKC": 70, "RPL": 90, "TRK": 50, "TI": 90}},
            "D": {"text": "Agar tidak dibohongi orang lain.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu menjadi *programmer* lampu lalu lintas, tujuanmu adalah:",
        "pilihan": {
            "A": {"text": "Membuat lampu merah dan hijau menyala bergantian.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 50, "TI": 70}},
            "B": {"text": "Membuat lampu yang bisa memprioritaskan jalan terpadat (algoritma *real-time*).", "bobot": {"SIKC": 90, "RPL": 80, "TRK": 60, "TI": 95}},
            "C": {"text": "Memastikan lampu LED-nya tidak putus.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 90, "TI": 50}},
            "D": {"text": "Menghitung durasi lampu merah agar adil.", "bobot": {"SIKC": 85, "RPL": 70, "TRK": 50, "TI": 90}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Dalam membuat kode rahasia, apa yang membuatnya paling sulit dipecahkan?",
        "pilihan": {
            "A": {"text": "Menggunakan banyak huruf yang berbeda.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 40, "TI": 70}},
            "B": {"text": "Menggunakan kunci enkripsi yang kompleks (misal: pergeseran huruf yang berubah-ubah).", "bobot": {"SIKC": 80, "RPL": 90, "TRK": 70, "TI": 95}},
            "C": {"text": "Menyembunyikan kodenya di tempat rahasia.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 60, "TI": 50}},
            "D": {"text": "Menulisnya di kertas yang berbeda-beda.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu harus menyusun rencana kerja 1 bulan, kamu akan:",
        "pilihan": {
            "A": {"text": "Mencatat semua tugas yang harus dikerjakan.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 50, "TI": 70}},
            "B": {"text": "Membuat matriks prioritas (Penting vs Mendesak) untuk urutan kerja.", "bobot": {"SIKC": 95, "RPL": 80, "TRK": 50, "TI": 90}},
            "C": {"text": "Membuat jadwal yang dihias agar semangat.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 40, "TI": 60}},
            "D": {"text": "Langsung bekerja tanpa rencana.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 10}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Dalam permainan *puzzle* balok, yang kamu utamakan adalah:",
        "pilihan": {
            "A": {"text": "Mencari warna balok yang seragam.", "bobot": {"SIKC": 50, "RPL": 80, "TRK": 40, "TI": 60}},
            "B": {"text": "Mengidentifikasi pola dan bentuk lubang yang harus diisi.", "bobot": {"SIKC": 80, "RPL": 90, "TRK": 50, "TI": 95}},
            "C": {"text": "Membuat tumpukan balok yang tinggi.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 50, "TI": 40}},
            "D": {"text": "Mencoba memecahkan rekor waktu tercepat.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 60, "TI": 85}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kenapa sebuah *software* bisa tiba-tiba *hang* (macet)?",
        "pilihan": {
            "A": {"text": "Komputer kehabisan memori untuk menjalankan program.", "bobot": {"SIKC": 70, "RPL": 70, "TRK": 90, "TI": 80}},
            "B": {"text": "Ada *bug* (kesalahan) di dalam alur perintah (*coding*) program itu.", "bobot": {"SIKC": 80, "RPL": 95, "TRK": 60, "TI": 95}},
            "C": {"text": "Suhu *laptop* terlalu panas.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 95, "TI": 70}},
            "D": {"text": "Karena virus.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 80, "TI": 70}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu menjadi bandar saham, yang paling kamu hitung adalah:",
        "pilihan": {
            "A": {"text": "Siapa saja *public figure* yang mendukung saham itu.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 40, "TI": 60}},
            "B": {"text": "Data statistik untung/rugi perusahaan 10 tahun terakhir.", "bobot": {"SIKC": 95, "RPL": 40, "TRK": 40, "TI": 80}},
            "C": {"text": "Menggunakan rumus matematika/prediksi untuk melihat tren kenaikan/penurunan.", "bobot": {"SIKC": 90, "RPL": 70, "TRK": 50, "TI": 95}},
            "D": {"text": "Membaca berita politik.", "bobot": {"SIKC": 70, "RPL": 40, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu menemukan mesin yang bekerja lambat. Agar cepat, kamu akan:",
        "pilihan": {
            "A": {"text": "Membongkar mesin dan membersihkan debu di dalamnya.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 90, "TI": 60}},
            "B": {"text": "Mencari tahu langkah (proses) mana yang paling memakan waktu.", "bobot": {"SIKC": 90, "RPL": 80, "TRK": 60, "TI": 95}},
            "C": {"text": "Mengganti mesinnya dengan yang baru.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Minyak pelumasnya ditambah.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 85, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu membuat peta harta karun, hal yang paling sulit adalah:",
        "pilihan": {
            "A": {"text": "Menggambar peta agar terlihat indah.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 40, "TI": 50}},
            "B": {"text": "Membuat petunjuk yang logis, tapi butuh pemecahan masalah untuk sampai ke sana.", "bobot": {"SIKC": 80, "RPL": 90, "TRK": 50, "TI": 95}},
            "C": {"text": "Mencari tempat yang aman untuk menyembunyikan harta karun.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 60, "TI": 70}},
            "D": {"text": "Membuat kertas petanya terlihat kuno.", "bobot": {"SIKC": 30, "RPL": 70, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu ingin membuat sistem absen kelas otomatis. Cara kerja terbaiknya:",
        "pilihan": {
            "A": {"text": "Menggunakan deteksi wajah saat masuk kelas.", "bobot": {"SIKC": 70, "RPL": 80, "TRK": 70, "TI": 80}},
            "B": {"text": "Membuat aplikasi yang mencatat kehadiran setiap hari dan menghitung persentase otomatis.", "bobot": {"SIKC": 95, "RPL": 90, "TRK": 50, "TI": 90}},
            "C": {"text": "Membagikan kartu *barcode* ke setiap siswa.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 80, "TI": 70}},
            "D": {"text": "Meminta guru mengabsen secara manual.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 50}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kenapa di jalan tol harus ada rambu batas kecepatan (misal: 100 km/jam)?",
        "pilihan": {
            "A": {"text": "Agar mobilnya tidak rusak.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 80, "TI": 50}},
            "B": {"text": "Agar arus lalu lintas tetap efisien dan aman (berdasarkan perhitungan).", "bobot": {"SIKC": 90, "RPL": 70, "TRK": 60, "TI": 90}},
            "C": {"text": "Agar pengemudi tidak bosan.", "bobot": {"SIKC": 20, "RPL": 30, "TRK": 30, "TI": 30}},
            "D": {"text": "Agar mobil tidak kehabisan bensin.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 50, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu menjadi *game developer*, tantangan terbesar dalam membuat *game* strategi adalah:",
        "pilihan": {
            "A": {"text": "Membuat desain grafis yang realistis.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 50, "TI": 60}},
            "B": {"text": "Membuat *Artificial Intelligence* (AI) musuh yang pintar dan tidak mudah dikalahkan.", "bobot": {"SIKC": 80, "RPL": 85, "TRK": 60, "TI": 95}},
            "C": {"text": "Memastikan *game*-nya tidak *lag*.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 90, "TI": 70}},
            "D": {"text": "Menulis cerita *game* yang panjang.", "bobot": {"SIKC": 60, "RPL": 80, "TRK": 40, "TI": 70}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Ketika ada dua pilihan yang sama-sama bagus (A dan B), kamu memutuskan dengan cara:",
        "pilihan": {
            "A": {"text": "Melempar koin (*random*).", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}},
            "B": {"text": "Membuat daftar pro dan kontra, memberi bobot nilai pada setiap aspek, lalu menghitung hasilnya.", "bobot": {"SIKC": 95, "RPL": 80, "TRK": 50, "TI": 95}},
            "C": {"text": "Mencari nasihat dari orang tua atau mentor.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 40, "TI": 50}},
            "D": {"text": "Memilih yang paling cepat bisa dilakukan.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 50, "TI": 80}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Dalam *game* RPG, hal yang paling kamu optimalkan (*build*) adalah:",
        "pilihan": {
            "A": {"text": "Desain baju dan aksesoris karakter.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 40, "TI": 60}},
            "B": {"text": "Mengombinasikan *skill* dan *item* agar menghasilkan damage maksimal.", "bobot": {"SIKC": 70, "RPL": 85, "TRK": 50, "TI": 95}},
            "C": {"text": "Memastikan koneksi internet stabil saat *raid*.", "bobot": {"SIKC": 50, "RPL": 50, "TRK": 90, "TI": 70}},
            "D": {"text": "Mencari *bug* di *game* itu.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 60, "TI": 80}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa yang paling kamu perhatikan saat menyelesaikan persamaan Matematika yang panjang?",
        "pilihan": {
            "A": {"text": "Keindahan tulisan tanganmu.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 40, "TI": 30}},
            "B": {"text": "Mengaplikasikan urutan operasi yang benar (kali/bagi dulu, baru tambah/kurang).", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 60, "TI": 95}},
            "C": {"text": "Berapa lama waktu yang dibutuhkan.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 50, "TI": 70}},
            "D": {"text": "Memastikan semua angkanya ganjil/genap.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu adalah seorang wasit di pertandingan. Apa yang paling penting agar keputusanmu adil?",
        "pilihan": {
            "A": {"text": "Menggunakan data rekaman video *real-time* untuk keputusan.", "bobot": {"SIKC": 95, "RPL": 70, "TRK": 80, "TI": 90}},
            "B": {"text": "Memastikan penonton mendukung keputusanmu.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "C": {"text": "Memastikan alat komunikasi dengan asisten wasit berjalan baik.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 95, "TI": 70}},
            "D": {"text": "Menghafal semua peraturan permainan.", "bobot": {"SIKC": 80, "RPL": 60, "TRK": 50, "TI": 85}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Mengapa mesin pencari (Google, Bing) bisa memberikan hasil yang relevan?",
        "pilihan": {
            "A": {"text": "Karena mereka punya *server* yang besar.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 90, "TI": 70}},
            "B": {"text": "Karena *website* harus membayar untuk muncul di halaman pertama.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "C": {"text": "Karena menggunakan algoritma kompleks untuk mengurutkan relevansi data.", "bobot": {"SIKC": 95, "RPL": 80, "TRK": 60, "TI": 95}},
            "D": {"text": "Karena internet kita cepat.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 80, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu menjadi *manager* gudang, cara tercepat menemukan sebuah barang adalah:",
        "pilihan": {
            "A": {"text": "Mengingat-ingat kapan barang itu datang.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 50}},
            "B": {"text": "Membuat sistem penamaan dan penempatan barang yang teratur (indeks).", "bobot": {"SIKC": 95, "RPL": 70, "TRK": 60, "TI": 90}},
            "C": {"text": "Membongkar semua kotak di gudang.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}},
            "D": {"text": "Meminta bantuan *supervisor*.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa yang paling kamu perlukan saat membaca buku petunjuk cara merakit perabot baru?",
        "pilihan": {
            "A": {"text": "Gambar-gambar yang estetik.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 50, "TI": 60}},
            "B": {"text": "Urutan langkah 1, 2, 3 yang logis dan jelas.", "bobot": {"SIKC": 90, "RPL": 95, "TRK": 70, "TI": 95}},
            "C": {"text": "Membaca *review* dari orang yang sudah merakit.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 50, "TI": 70}},
            "D": {"text": "Alat-alat yang lengkap.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu diminta membuat *spreadsheet* untuk memprediksi hasil pertandingan, yang kamu fokuskan adalah:",
        "pilihan": {
            "A": {"text": "Membuat tabelnya terlihat keren.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 30, "TI": 50}},
            "B": {"text": "Memasukkan rumus (*formula*) dan fungsi statistik yang benar.", "bobot": {"SIKC": 90, "RPL": 85, "TRK": 50, "TI": 95}},
            "C": {"text": "Data pemain yang cedera.", "bobot": {"SIKC": 70, "RPL": 40, "TRK": 40, "TI": 50}},
            "D": {"text": "Membandingkan hasil prediksimu dengan prediksi orang lain.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 40, "TI": 85}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa yang membuat sebuah *game* *puzzle* terasa menantang?",
        "pilihan": {
            "A": {"text": "Kualitas grafis yang tinggi.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 60, "TI": 60}},
            "B": {"text": "Alur pemecahan masalahnya yang butuh langkah-langkah panjang dan terperinci.", "bobot": {"SIKC": 70, "RPL": 90, "TRK": 50, "TI": 95}},
            "C": {"text": "Suara dan musik yang menyeramkan.", "bobot": {"SIKC": 30, "RPL": 60, "TRK": 40, "TI": 40}},
            "D": {"text": "Kontrol tombol yang rumit.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 70, "TI": 50}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Saat melihat pohon Natal yang berhias lampu, kamu lebih tertarik pada:",
        "pilihan": {
            "A": {"text": "Warna lampu yang beragam.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 40, "TI": 50}},
            "B": {"text": "Bagaimana rangkaian listriknya bisa dibuat berkedip dengan pola tertentu.", "bobot": {"SIKC": 70, "RPL": 80, "TRK": 95, "TI": 90}},
            "C": {"text": "Berapa banyak lampu yang dipakai.", "bobot": {"SIKC": 90, "RPL": 50, "TRK": 60, "TI": 70}},
            "D": {"text": "Kualitas pohonnya.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu sedang mencoba resep kue baru dan butuh 100 gram gula, tapi timbanganmu rusak. Kamu akan:",
        "pilihan": {
            "A": {"text": "Menggunakan perkiraan saja (insting).", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 40, "TI": 50}},
            "B": {"text": "Mencari benda lain yang beratnya 100 gram untuk pembanding (metode takaran).", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 60, "TI": 90}},
            "C": {"text": "Membatalkan rencana membuat kue.", "bobot": {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 20}},
            "D": {"text": "Mencari timbangan digital yang baru.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 90, "TI": 70}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu membuat program untuk menyortir baju kotor (putih, warna, tebal, tipis), apa langkah terbesarmu?",
        "pilihan": {
            "A": {"text": "Memastikan mesin cucinya punya mode lengkap.", "bobot": {"SIKC": 50, "RPL": 60, "TRK": 90, "TI": 70}},
            "B": {"text": "Membuat sistem klasifikasi yang rinci dan tidak ambigu (Logika Boolean).", "bobot": {"SIKC": 90, "RPL": 80, "TRK": 60, "TI": 95}},
            "C": {"text": "Membuat desain keranjang cucian yang banyak.", "bobot": {"SIKC": 40, "RPL": 95, "TRK": 40, "TI": 60}},
            "D": {"text": "Menghitung berapa banyak deterjen yang dibutuhkan.", "bobot": {"SIKC": 70, "RPL": 50, "TRK": 40, "TI": 80}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa yang paling kamu sukai dari Matematika?",
        "pilihan": {
            "A": {"text": "Mencari pola angka yang tersembunyi.", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 50, "TI": 95}},
            "B": {"text": "Menemukan rumus untuk memecahkan masalah.", "bobot": {"SIKC": 70, "RPL": 85, "TRK": 60, "TI": 90}},
            "C": {"text": "Menghitung dengan cepat.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 50, "TI": 80}},
            "D": {"text": "Mencari tahu asal usul rumus (sejarah).", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 40, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu adalah seorang *dispatcher* taksi *online*. Bagaimana cara memprioritaskan pesanan?",
        "pilihan": {
            "A": {"text": "Memilih pesanan dengan harga paling mahal.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 50}},
            "B": {"text": "Menggunakan algoritma: terdekat dari driver + skor *rating* driver + rute terpendek.", "bobot": {"SIKC": 95, "RPL": 90, "TRK": 60, "TI": 95}},
            "C": {"text": "Memilih *driver* yang paling ramah.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 40, "TI": 50}},
            "D": {"text": "Memilih pesanan yang alamatnya paling mudah dibaca.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 50, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Dalam *game* RPG, yang kamu khawatirkan adalah:",
        "pilihan": {
            "A": {"text": "Koneksi internet tiba-tiba mati.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 95, "TI": 60}},
            "B": {"text": "Kehilangan *item* langka.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 50, "TI": 60}},
            "C": {"text": "Musuh yang terlalu kuat dan tidak ada celah logikanya.", "bobot": {"SIKC": 70, "RPL": 80, "TRK": 50, "TI": 90}},
            "D": {"text": "*Skill* karakter yang *bug* (tidak bekerja).", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 60, "TI": 95}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu diminta membuat *smartwatch* yang menghitung langkah kaki, yang paling kamu hitung adalah:",
        "pilihan": {
            "A": {"text": "Kualitas sensor gerak (akselerometer) agar presisi.", "bobot": {"SIKC": 70, "RPL": 80, "TRK": 95, "TI": 90}},
            "B": {"text": "Warna jam tangan yang bagus.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 40, "TI": 50}},
            "C": {"text": "Berapa banyak *user* yang akan membeli.", "bobot": {"SIKC": 90, "RPL": 40, "TRK": 30, "TI": 50}},
            "D": {"text": "Desain layarnya yang *simple*.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 40, "TI": 70}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu sedang mengamati antrean di sebuah bank. Agar antrean efisien, kamu akan:",
        "pilihan": {
            "A": {"text": "Menambah jumlah kursi di ruang tunggu.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}},
            "B": {"text": "Menerapkan sistem antrean tunggal yang bercabang ke banyak teller.", "bobot": {"SIKC": 90, "RPL": 70, "TRK": 50, "TI": 95}},
            "C": {"text": "Memasang AC yang dingin.", "bobot": {"SIKC": 30, "RPL": 40, "TRK": 60, "TI": 40}},
            "D": {"text": "Menyediakan *snack* gratis.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa yang paling kamu suka dari program Excel (Spreadsheet)?",
        "pilihan": {
            "A": {"text": "Warna tabel yang bisa diganti-ganti.", "bobot": {"SIKC": 40, "RPL": 80, "TRK": 30, "TI": 50}},
            "B": {"text": "Kemampuan membuat rumus matematika yang kompleks.", "bobot": {"SIKC": 80, "RPL": 70, "TRK": 50, "TI": 95}},
            "C": {"text": "Bisa untuk membuat laporan data keuangan.", "bobot": {"SIKC": 95, "RPL": 50, "TRK": 40, "TI": 70}},
            "D": {"text": "Bisa diekspor ke format PDF.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 50, "TI": 60}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu menjadi *game developer*, apa yang paling kamu tes sebelum *game* dirilis?",
        "pilihan": {
            "A": {"text": "Apakah grafisnya sudah bagus.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 50, "TI": 60}},
            "B": {"text": "Apakah ada *bug* atau celah yang bisa merusak alur permainan (logika *game*).", "bobot": {"SIKC": 80, "RPL": 95, "TRK": 60, "TI": 95}},
            "C": {"text": "Apakah *server*-nya tahan diakses banyak orang.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 90, "TI": 70}},
            "D": {"text": "Waktu *loading* saat masuk *game*.", "bobot": {"SIKC": 50, "RPL": 70, "TRK": 80, "TI": 85}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu diminta menghitung rata-rata nilai UN teman sekelasmu. Yang kamu lakukan:",
        "pilihan": {
            "A": {"text": "Menghitung total nilai semua mata pelajaran, lalu dibagi jumlah mata pelajaran.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 50, "TI": 80}},
            "B": {"text": "Menjumlahkan semua nilai teman, lalu dibagi jumlah siswa.", "bobot": {"SIKC": 95, "RPL": 70, "TRK": 50, "TI": 90}},
            "C": {"text": "Hanya menghitung nilai yang paling tinggi saja.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}},
            "D": {"text": "Meminta guru yang menghitung.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu membuat peta digital (seperti Google Maps), hal paling sulit adalah:",
        "pilihan": {
            "A": {"text": "Membuat tampilannya bagus dan berwarna.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 40, "TI": 60}},
            "B": {"text": "Membuat data jalan (*routing*) yang akurat dan selalu *update*.", "bobot": {"SIKC": 90, "RPL": 80, "TRK": 60, "TI": 95}},
            "C": {"text": "Memastikan servernya tidak *down*.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 95, "TI": 70}},
            "D": {"text": "Membuat *traffic light*-nya otomatis.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 80, "TI": 90}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Dalam menyusun *timeline* (garis waktu) sejarah, kamu fokus pada:",
        "pilihan": {
            "A": {"text": "Nama-nama tokoh yang paling terkenal.", "bobot": {"SIKC": 60, "RPL": 40, "TRK": 40, "TI": 50}},
            "B": {"text": "Korelasi sebab-akibat antar kejadian secara berurutan.", "bobot": {"SIKC": 95, "RPL": 80, "TRK": 50, "TI": 95}},
            "C": {"text": "Tampilan garis waktunya yang interaktif.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 40, "TI": 70}},
            "D": {"text": "Kualitas buku yang kamu baca.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa yang paling menarik dari robot yang bisa bermain sepak bola?",
        "pilihan": {
            "A": {"text": "Motor penggeraknya yang cepat.", "bobot": {"SIKC": 40, "RPL": 50, "TRK": 95, "TI": 60}},
            "B": {"text": "Strategi (*decision making*) robot saat mengoper dan menembak bola.", "bobot": {"SIKC": 80, "RPL": 90, "TRK": 60, "TI": 95}},
            "C": {"text": "Desain tubuh robot yang mirip manusia.", "bobot": {"SIKC": 50, "RPL": 90, "TRK": 50, "TI": 70}},
            "D": {"text": "Koneksi *wireless* antar robot.", "bobot": {"SIKC": 60, "RPL": 60, "TRK": 90, "TI": 80}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu diminta menghitung diskon yang bertingkat (*double discount*), kamu akan:",
        "pilihan": {
            "A": {"text": "Menghitung total diskonnya (misal: 50% + 20% = 70%).", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 50}},
            "B": {"text": "Menghitung diskon pertama, lalu sisa harga didiskon lagi (logika urutan).", "bobot": {"SIKC": 90, "RPL": 70, "TRK": 50, "TI": 95}},
            "C": {"text": "Meminta kasir yang menghitung.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 40}},
            "D": {"text": "Membandingkan dengan harga di toko sebelah.", "bobot": {"SIKC": 80, "RPL": 50, "TRK": 40, "TI": 70}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Kamu diminta membuat prediksi cuaca untuk besok. Data yang paling kamu andalkan adalah:",
        "pilihan": {
            "A": {"text": "Melihat berita di TV.", "bobot": {"SIKC": 50, "RPL": 40, "TRK": 40, "TI": 50}},
            "B": {"text": "Menganalisis data pola suhu, tekanan udara, dan kelembaban 7 hari terakhir.", "bobot": {"SIKC": 95, "RPL": 60, "TRK": 50, "TI": 90}},
            "C": {"text": "Mencari *drone* yang bisa memantau awan.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 90, "TI": 80}},
            "D": {"text": "Mendengarkan ramalan dari orang pintar.", "bobot": {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 30}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu menjadi *programmer* *Google Sheets*, hal paling sulit adalah:",
        "pilihan": {
            "A": {"text": "Membuat tampilannya menarik.", "bobot": {"SIKC": 40, "RPL": 90, "TRK": 40, "TI": 60}},
            "B": {"text": "Membuat *database* untuk menyimpan data.", "bobot": {"SIKC": 95, "RPL": 70, "TRK": 60, "TI": 80}},
            "C": {"text": "Menulis algoritma *IF-THEN-ELSE* yang sangat panjang dan bertingkat.", "bobot": {"SIKC": 80, "RPL": 95, "TRK": 50, "TI": 95}},
            "D": {"text": "Memastikan *server*-nya bisa diakses banyak orang.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 90, "TI": 70}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Apa manfaat terbesar dari *pseudocode* (alur bahasa manusia sebelum *coding*)?",
        "pilihan": {
            "A": {"text": "Membuat *coding* terlihat canggih.", "bobot": {"SIKC": 40, "RPL": 60, "TRK": 40, "TI": 50}},
            "B": {"text": "Membuat alur logika lebih mudah dipahami manusia sebelum diterjemahkan ke bahasa mesin.", "bobot": {"SIKC": 90, "RPL": 95, "TRK": 50, "TI": 95}},
            "C": {"text": "Menghemat waktu *coding*.", "bobot": {"SIKC": 70, "RPL": 80, "TRK": 50, "TI": 90}},
            "D": {"text": "Menghilangkan *bug*.", "bobot": {"SIKC": 60, "RPL": 70, "TRK": 50, "TI": 85}}
        }
    },
    {
        "kategori": "logika",
        "pertanyaan": "Jika kamu memiliki kemampuan untuk memprediksi satu hal di masa depan, kamu akan pilih:",
        "pilihan": {
            "A": {"text": "Kapan kamu akan kaya.", "bobot": {"SIKC": 60, "RPL": 50, "TRK": 40, "TI": 60}},
            "B": {"text": "Hasil dari semua ujian yang kamu ikuti.", "bobot": {"SIKC": 70, "RPL": 60, "TRK": 50, "TI": 80}},
            "C": {"text": "Pola dan waktu munculnya *virus* baru di dunia.", "bobot": {"SIKC": 90, "RPL": 80, "TRK": 70, "TI": 95}},
            "D": {"text": "Siapa jodohmu.", "bobot": {"SIKC": 40, "RPL": 40, "TRK": 40, "TI": 40}}
        }
    }
]

# Gabungkan semua soal dan beri nomor
no = 1
for soal in analisis_soal:
    soal["no"] = no
    BANK_SOAL.append(soal)
    no += 1
for soal in pengembangan_soal:
    soal["no"] = no
    BANK_SOAL.append(soal)
    no += 1
for soal in hardware_soal:
    soal["no"] = no
    BANK_SOAL.append(soal)
    no += 1
for soal in logika_soal:
    soal["no"] = no
    BANK_SOAL.append(soal)
    no += 1

# === FUNGSI PERHITUNGAN BOBOT MAKSIMAL ===
def hitung_bobot_maksimal(soal_terpilih):
    """
    Menghitung bobot maksimal untuk setiap prodi dari soal yang terpilih
    """
    bobot_maks = {prodi: 0 for prodi in PRODI_JTI["kode"]}
    
    for soal in soal_terpilih:
        for pilihan_key, pilihan_data in soal["pilihan"].items():
            bobot_pilihan = pilihan_data["bobot"]
            for prodi in PRODI_JTI["kode"]:
                if bobot_pilihan[prodi] > bobot_maks[prodi]:
                    bobot_maks[prodi] = bobot_pilihan[prodi]
    
    # Jumlahkan bobot maksimal dari semua soal
    bobot_maks_total = {prodi: 0 for prodi in PRODI_JTI["kode"]}
    for soal in soal_terpilih:
        for prodi in PRODI_JTI["kode"]:
            maks_soal_ini = max([pilihan["bobot"][prodi] for pilihan in soal["pilihan"].values()])
            bobot_maks_total[prodi] += maks_soal_ini
    
    return bobot_maks_total

# === FUNGSI GENERATE SUMMARY AI (RINGKAS) ===
# === FUNGSI GENERATE SUMMARY AI DENGAN RETRY & 429 HANDLING ===
def generate_summary_ai(prodi_nama, prodi_kode, jawaban_user, rank=1, persen=0, max_retries=3):
    """
    Generate summary ringkas dengan struktur:
    - Alasan dipilih
    - Pendukung (mata kuliah/keahlian)
    - Saran belajar
    
    Output: 1-3 paragraf maksimal
    """
    # 1. Context dari jawaban user
    bukti_text = ""
    if jawaban_user and len(jawaban_user) > 0:
        bukti_list = []
        for ans in jawaban_user[:2]:  # Hanya 2 contoh
            pilihan = ans.get('pilihan', 'Pilihan tidak diketahui')
            bukti_list.append(f"- {pilihan}")
        bukti_text = "\n".join(bukti_list)
    else:
        bukti_text = "- Pola jawaban seimbang"

    # 2. Hitung dominasi kategori
    kategori_count = {"analisis": 0, "pengembangan": 0, "hardware": 0}
    for ans in jawaban_user:
        kat = ans.get("kategori", "")
        if kat in kategori_count:
            kategori_count[kat] += 1
    
    kategori_dominan = max(kategori_count, key=kategori_count.get) if kategori_count else "pengembangan"
    fokus_map = {
        "analisis": "analisis data dan sistem informasi",
        "pengembangan": "pengembangan aplikasi",
        "hardware": "perangkat keras dan jaringan"
    }
    fokus = fokus_map.get(kategori_dominan, "teknologi informasi")

    # 3. Prompt Engineering - Natural & Meyakinkan
    prompt = f"""Kamu adalah konselor akademik Polindra yang ramah dan meyakinkan. Tulis penjelasan untuk calon mahasiswa tentang:

Prodi: {prodi_nama} ({prodi_kode})
Minat dominan: {fokus}

Contoh pola jawaban siswa:
{bukti_text}

STRUKTUR WAJIB (3 paragraf terpisah):

Paragraf 1: Alasan Kecocokan
Jelaskan dalam 2-3 kalimat mengapa prodi ini cocok dengan minat siswa di bidang {fokus}. Gunakan bahasa yang mengalir, meyakinkan, dan personal (gunakan "kamu"). Hindari kata "Mengapa Prodi Ini Cocok" atau "Tentu".

Paragraf 2: Apa yang Dipelajari
Tulis 3-4 poin singkat tentang mata kuliah/keahlian menarik yang akan dipelajari. Setiap poin 1 baris saja, langsung ke inti. Gunakan format list dengan tanda "-" atau bullet point.

Paragraf 3: Saran Persiapan
Berikan saran praktis dalam 2-3 kalimat untuk mempersiapkan diri. Buat actionable dan memotivasi.

ATURAN PENULISAN:
- Total MAKSIMAL 180 kata
- Pisahkan setiap paragraf dengan baris kosong (gunakan "\\n\\n")
- Bahasa ramah, natural, dan meyakinkan seperti berbicara langsung
- JANGAN gunakan heading seperti "Mengapa Prodi Ini Cocok", "Apa yang Dipelajari", dll
- JANGAN gunakan kata "Tentu", "Halo", atau pembuka klise lainnya
- Langsung mulai dengan kalimat yang menarik
- Gunakan "kamu" untuk personal touch"""

    # Safety Settings
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 2048,
            "temperature": 0.75,
            "topP": 0.9
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }

    # FALLBACK TEXT (digunakan saat error)
    fallback_text = f"""Prodi ini sangat cocok untuk kamu yang memiliki minat kuat dalam {fokus}. Dari pola jawabanmu, terlihat potensi besar untuk berkembang di bidang ini dan menciptakan solusi teknologi yang bermanfaat.

Di prodi ini, kamu akan mempelajari:
- Konsep fundamental dan teori yang mendalam
- Praktik langsung dengan tools dan teknologi terkini
- Penyelesaian masalah nyata melalui project-based learning
- Kolaborasi tim dalam pengembangan sistem

Untuk persiapan, mulailah dengan memperkuat logika dan kemampuan problem solving. Eksplorasi dasar-dasar teknologi terkait melalui tutorial online, dan jangan ragu untuk mencoba hands-on dengan tools sederhana."""

    # === RETRY MECHANISM ===
    for attempt in range(max_retries):
        try:
            print(f"🤖 Request AI untuk {prodi_kode} (Rank {rank}) - Attempt {attempt + 1}/{max_retries}")
            
            response = requests.post(
                GEMINI_URL, 
                json=payload, 
                headers={"Content-Type": "application/json"}, 
                timeout=20
            )

            # === HANDLING STATUS CODE 429 (Rate Limit) ===
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 'unknown')
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                
                print(f"🚨 RATE LIMIT HIT (429)!")
                print(f"   Retry-After header: {retry_after} seconds")
                print(f"   Waiting {wait_time}s before retry...")
                
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    print("❌ Max retries reached, using fallback response")
                    return fallback_text

            # === HANDLING STATUS CODE 200 (Success) ===
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            text = parts[0]["text"].strip()
                            # Bersihkan formatting berlebihan
                            text = text.replace("**", "").replace("*", "")
                            text = text.replace("# ", "").replace("## ", "").replace("### ", "")
                            # Pastikan ada spacing antar paragraf
                            text = text.replace("\n\n\n", "\n\n")  # Hilangkan triple newline
                            print(f"✅ Summary generated ({len(text)} chars)")
                            return text
                    
                    # Cek finish reason
                    finish_reason = candidate.get('finishReason', 'UNKNOWN')
                    print(f"⚠️ Respons tidak lengkap. Reason: {finish_reason}")
                    
                    if attempt < max_retries - 1:
                        print(f"   Retrying in 1s...")
                        time.sleep(1)
                        continue
                    else:
                        return fallback_text
                else:
                    print("⚠️ No candidates in response")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        return fallback_text
            
            # === HANDLING OTHER HTTP ERRORS ===
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text[:200]}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    return fallback_text

        except requests.Timeout:
            print(f"⏱️ Request timeout (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"   Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                print("❌ Max retries reached after timeout")
                return fallback_text
        
        except requests.RequestException as e:
            print(f"❌ Request Exception: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"   Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                return fallback_text
        
        except Exception as e:
            print(f"❌ Unexpected Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return fallback_text
    
    # Jika keluar dari loop tanpa return (seharusnya tidak terjadi)
    print("⚠️ Unexpected exit from retry loop")
    return fallback_text

# === FLASK APP ===
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "http://10.0.173.172:5173",
    "http://192.168.153.1:5173",
    "http://192.168.102.1:5173"
])

# Ubah bagian get-questions untuk 4 kategori
@app.route("/api/get-questions", methods=["POST"])
def get_questions():
    try:
        data = request.get_json()
        n_soal = data.get("n_soal", 10)
        
        if n_soal > len(BANK_SOAL):
            n_soal = len(BANK_SOAL)
        
        # Pisahkan soal berdasarkan 4 kategori
        soal_per_kategori = {
            "analisis": [s for s in BANK_SOAL if s["kategori"] == "analisis"],
            "pengembangan": [s for s in BANK_SOAL if s["kategori"] == "pengembangan"],
            "hardware": [s for s in BANK_SOAL if s["kategori"] == "hardware"],
            "logika": [s for s in BANK_SOAL if s["kategori"] == "logika"]  # TAMBAH kategori logika
        }
        
        # Hitung pembagian soal per kategori (dibagi rata untuk 4 kategori)
        n_per_kategori = n_soal // 4
        sisa = n_soal % 4
        
        jumlah_soal = {
            "analisis": n_per_kategori,
            "pengembangan": n_per_kategori,
            "hardware": n_per_kategori,
            "logika": n_per_kategori  # TAMBAH logika
        }
        
        # Distribusikan sisa soal secara berurutan
        kategori_list = ["analisis", "pengembangan", "hardware", "logika"]
        for i in range(sisa):
            jumlah_soal[kategori_list[i]] += 1
        
        print(f"\n📊 Distribusi Soal (Total: {n_soal}):")
        print(f"   - Analisis: {jumlah_soal['analisis']} soal")
        print(f"   - Pengembangan: {jumlah_soal['pengembangan']} soal")
        print(f"   - Hardware: {jumlah_soal['hardware']} soal")
        print(f"   - Logika: {jumlah_soal['logika']} soal")
        
        # Ambil soal acak dari setiap kategori
        soal_terpilih = []
        for kategori, jumlah in jumlah_soal.items():
            if jumlah > 0:
                available = soal_per_kategori[kategori]
                if len(available) >= jumlah:
                    selected = random.sample(available, jumlah)
                    soal_terpilih.extend(selected)
                else:
                    # Jika soal tidak cukup, ambil semua yang ada
                    soal_terpilih.extend(available)
        
        # Acak urutan soal agar kategori tidak berurutan
        random.shuffle(soal_terpilih)
        
        # Format soal untuk frontend
        soal_formatted = []
        for i, item in enumerate(soal_terpilih, 1):
            soal_formatted.append({
                "no": i,
                "kategori": item["kategori"],
                "pertanyaan": item["pertanyaan"],
                "pilihan": {k: v["text"] for k, v in item["pilihan"].items()}
            })
        
        # Simpan metadata
        soal_metadata = []
        for item in soal_terpilih:
            soal_metadata.append({
                "kategori": item["kategori"],
                "pilihan_bobot": item["pilihan"]
            })
        
        return jsonify({
            "soal": soal_formatted,
            "metadata": soal_metadata,
            "distribusi": jumlah_soal
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/rekomendasi", methods=["POST"])
def api_rekomendasi():
    try:
        data = request.get_json()
        jawaban = data.get("jawaban", [])
        metadata = data.get("metadata", [])
        
        if not isinstance(jawaban, list) or len(jawaban) == 0:
            return jsonify({"error": "Format jawaban tidak valid."}), 400
        
        if not metadata or len(metadata) == 0:
            return jsonify({"error": "Metadata soal tidak ditemukan. Silakan ulang kuis."}), 400
        
        # Rekonstruksi soal dari metadata
        soal_terpilih = []
        for i, meta in enumerate(metadata):
            soal_terpilih.append({
                "no": i + 1,
                "kategori": meta["kategori"],
                "pertanyaan": f"Pertanyaan {i+1}",  # Nama generik
                "pilihan": meta["pilihan_bobot"]
            })
        
        # Hitung bobot maksimal
        bobot_maks = hitung_bobot_maksimal(soal_terpilih)
        
        print("\n=== BOBOT MAKSIMAL PER PRODI ===")
        for prodi, maks in bobot_maks.items():
            print(f"{prodi}: {maks}")
        
        # Hitung skor user - PERBAIKAN: Susun jawaban_user dengan struktur lengkap
        skor_user = {prodi: 0 for prodi in PRODI_JTI["kode"]}
        jawaban_user = []
        jawaban_per_prodi = {prodi: [] for prodi in PRODI_JTI["kode"]}  # BARU: Tracking per prodi
        
        for i, soal in enumerate(soal_terpilih):
            if i >= len(jawaban):
                break
            
            ans = jawaban[i].upper()
            if ans not in soal["pilihan"]:
                continue
            
            pilihan_data = soal["pilihan"][ans]
            bobot_pilihan = pilihan_data["bobot"]
            
            # PERBAIKAN: Struktur yang konsisten dengan key yang benar
            jawaban_item = {
                "pilihan": pilihan_data["text"],  # Key 'pilihan' bukan 'soal'
                "kategori": soal["kategori"],
                "bobot": bobot_pilihan
            }
            jawaban_user.append(jawaban_item)
            
            # Tracking jawaban yang berkontribusi tinggi per prodi
            for prodi in PRODI_JTI["kode"]:
                skor_user[prodi] += bobot_pilihan[prodi]
                jawaban_per_prodi[prodi].append({
                    "pilihan": pilihan_data["text"],
                    "kategori": soal["kategori"],
                    "skor": bobot_pilihan[prodi]
                })
        
        print("\n=== SKOR USER ===")
        for prodi, skor in skor_user.items():
            print(f"{prodi}: {skor}")
        
        # Hitung persentase
        hasil_akhir = []
        for prodi in PRODI_JTI["kode"]:
            if bobot_maks[prodi] > 0:
                persen = round((skor_user[prodi] / bobot_maks[prodi]) * 100, 1)
            else:
                persen = 0
            
            hasil_akhir.append({
                "kode": prodi,
                "nama": PRODI_JTI["nama"][prodi],
                "link": PRODI_JTI["link"][prodi],
                "persen": persen,
                "skor": skor_user[prodi],
                "maks": bobot_maks[prodi]
            })
        
        # Urutkan
        hasil_akhir.sort(key=lambda x: x["persen"], reverse=True)
        
        print("\n=== HASIL PERSENTASE ===")
        for rank, prodi in enumerate(hasil_akhir, 1):
            print(f"#{rank} {prodi['nama']}: {prodi['persen']}% ({prodi['skor']}/{prodi['maks']})")
        
        # Generate summary - PERBAIKAN: Kirim jawaban yang relevan per prodi
        rekomendasi_lengkap = []
        for rank, prodi in enumerate(hasil_akhir, 1):
            # Ambil top 3 jawaban yang paling berkontribusi untuk prodi ini
            jawaban_prodi_ini = sorted(
                jawaban_per_prodi[prodi['kode']], 
                key=lambda x: x['skor'], 
                reverse=True
            )[:3]
            
            summary = generate_summary_ai(
                prodi["nama"],
                prodi["kode"],
                jawaban_prodi_ini,  # Kirim jawaban yang spesifik untuk prodi ini
                rank,
                prodi["persen"]
            )
            
            rekomendasi_lengkap.append({
                "rank": rank,
                "kode": prodi["kode"],
                "nama": prodi["nama"],
                "link": prodi["link"],
                "persen": prodi["persen"],
                "summary": summary
            })
            
            # Jeda antar request
            if rank < len(hasil_akhir):
                time.sleep(0.7)
        
        return jsonify({
            "rekomendasi": rekomendasi_lengkap,
            "debug": {
                "bobot_maks": bobot_maks,
                "skor_user": skor_user
            }
        })
        
    except Exception as e:
        print(f"❌ Error Critical: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ Polindra JTI Rekomendasi API v2.0 - Ready!"

if __name__ == "__main__":
    print("\n=== SISTEM REKOMENDASI JTI POLINDRA ===")
    print(f"📚 Total Bank Soal: {len(BANK_SOAL)}")
    print(f"🎯 Program Studi: {', '.join(PRODI_JTI['kode'])}")
    print("\n🚀 Starting server...\n")
    app.run(debug=True, port=5000)