import random
import requests
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

GEMINI_API_KEY = "AIzaSyCdg26ztrLrBf9FnJLnIBVqJ-wFbcZZBOc"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# === 1. DATA PERTANYAAN DAN BOBOT ===
DATA_JURUSAN = {
    "teknik": {
        "prodi": ["TM", "PM", "TRIK", "TP"],
        "prodi_nama": {
            "TM": "D3 Teknik Mesin",
            "PM": "S1 Terapan Perancangan Manufaktur",
            "TRIK": "S1 Terapan Teknologi Rekayasa Instrumentasi dan Kontrol",
            "TP": "D3 Teknik Pendingin & Tata Udara"
        },
        "prodi_link": {
            "TM": "https://polindra.ac.id/program-studi-d3-teknik-mesin/",
            "PM": "https://polindra.ac.id/program-studi-s1-perancangan-manufaktur/",
            "TRIK": "https://polindra.ac.id/program-studi-s1-teknologi-rekayasa-instrumentasi-kontrol/",
            "TP": "https://polindra.ac.id/program-studi-d3-teknik-pendingin/"
        },
        "pertanyaan": []
    },
    "kesehatan": {
        "prodi": ["KP", "TLM", "TREM"],
        "prodi_nama": {
            "KP": "D3 Keperawatan",
            "TLM": "S1 Teknologi Laboratorium Medis",
            "TREM": "S1 Teknologi Rekayasa Elektromedis"
        },
        "prodi_link": {
            "KP": "https://polindra.ac.id/program-studi-d3-keperawatan/",
            "TLM": "https://polindra.ac.id/program-studi-s1-terapan-perancangan-manufaktur/",
            "TREM": "https://polindra.ac.id/program-studi-s1-terapan-teknologi-rekayasa-elektro-medis/"
        },
        "pertanyaan": []
    },
    "informatika": {
        "prodi": ["TI", "RPL", "SIKC", "TRK"],
        "prodi_nama": {
            "TI": "D3 Teknik Informatika",
            "RPL": "S1 Terapan Rekayasa Perangkat Lunak",
            "SIKC": "S1 Terapan Sistem Informasi Kota Cerdas",
            "TRK": "S1 Terapan Teknologi Rekayasa Komputer"
        },
        "prodi_link": {
            "TI": "https://polindra.ac.id/program-studi-d3-teknik-informatika/",
            "RPL": "https://polindra.ac.id/program-studi-s1-rekayasa-perangkat-lunak/",
            "SIKC": "https://polindra.ac.id/program-studi-s1-sistem-informasi-kota-cerdas/",
            "TRK": "https://polindra.ac.id/program-studi-s1-terapan-teknologi-rekayasa-komputer/"
        },
        "pertanyaan": []
    }
}

# === 2. ISI DATA TEKNIK (45 pertanyaan) ===
# Format: [no, pertanyaan, {'A': (text, {prodi: bobot}), ...}]

# Teknik
teknik_data = [
    (1, "Ketika membayangkan kerja di bidang teknik, apa yang paling menarik buat kamu?",
     {"A": ("Mengoperasikan atau memperbaiki mesin", {"TM": 50, "PM": 20, "TRIK": 15, "TP": 15}),
      "B": ("Mendesain komponen atau produk teknik", {"TM": 15, "PM": 55, "TRIK": 15, "TP": 15}),
      "C": ("Mengatur sensor, kontrol, atau otomasi", {"TM": 10, "PM": 15, "TRIK": 60, "TP": 15}),
      "D": ("Menginstal dan menganalisis sistem pendingin", {"TM": 10, "PM": 15, "TRIK": 15, "TP": 60})}),
    (2, "Jika diminta menyelesaikan tugas kelompok, peran apa yang biasanya kamu ambil?",
     {"A": ("Mengatur alur kerja teknis", {"TM": 45, "PM": 30, "TRIK": 15, "TP": 10}),
      "B": ("Membuat rancangan langkah kerja", {"TM": 20, "PM": 55, "TRIK": 15, "TP": 10}),
      "C": ("Mengecek alat/perangkat yang dibutuhkan", {"TM": 10, "PM": 15, "TRIK": 50, "TP": 25}),
      "D": ("Membantu tugas dasar teknis", {"TM": 20, "PM": 20, "TRIK": 20, "TP": 40})}),
    (3, "Kamu lebih suka mempelajari topik yang seperti apa?",
     {"A": ("Topik tentang mesin dan mekanika", {"TM": 60, "PM": 20, "TRIK": 10, "TP": 10}),
      "B": ("Topik tentang desain dan manufaktur", {"TM": 15, "PM": 60, "TRIK": 15, "TP": 10}),
      "C": ("Topik tentang sensor, rangkaian, dan control", {"TM": 10, "PM": 15, "TRIK": 60, "TP": 15}),
      "D": ("Topik tentang sistem pendingin dan HVAC", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (4, "Jika menghadapi masalah, kamu lebih nyaman cara mana?",
     {"A": ("Observasi kondisi mesin/komponen", {"TM": 55, "PM": 25, "TRIK": 10, "TP": 10}),
      "B": ("Menyusun langkah-langkah perbaikan", {"TM": 20, "PM": 55, "TRIK": 15, "TP": 10}),
      "C": ("Mencoba mengetes alat atau sensor", {"TM": 10, "PM": 15, "TRIK": 55, "TP": 20}),
      "D": ("Menganalisis dasar kerja sistem pendingin", {"TM": 15, "PM": 10, "TRIK": 15, "TP": 60})}),
    (5, "Kamu lebih suka bekerja dengan...",
     {"A": ("Data dan analisa performa mesin", {"TM": 55, "PM": 25, "TRIK": 10, "TP": 10}),
      "B": ("Proses desain", {"TM": 15, "PM": 60, "TRIK": 15, "TP": 10}),
      "C": ("Perangkat fisik dan alat elektronik/control", {"TM": 10, "PM": 15, "TRIK": 55, "TP": 20}),
      "D": ("Komponen sistem pendingin", {"TM": 15, "PM": 10, "TRIK": 15, "TP": 60})}),
    (6, "Jika diberikan proyek kecil, kamu lebih tertarik pada bagian apa?",
     {"A": ("Menggali masalah mekanik", {"TM": 60, "PM": 20, "TRIK": 10, "TP": 10}),
      "B": ("Menyusun rancangan teknis", {"TM": 15, "PM": 60, "TRIK": 15, "TP": 10}),
      "C": ("Menyiapkan alat sensor/otomasi", {"TM": 10, "PM": 15, "TRIK": 55, "TP": 20}),
      "D": ("Menjalankan tugas-tugas instalasi pendingin", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (7, "Kamu paling nyaman belajar dengan cara...",
     {"A": ("Diskusi mekanik dan contoh kasus", {"TM": 55, "PM": 25, "TRIK": 10, "TP": 10}),
      "B": ("Belajar teori dan konsep desain", {"TM": 15, "PM": 60, "TRIK": 15, "TP": 10}),
      "C": ("Mencoba langsung alat control", {"TM": 10, "PM": 15, "TRIK": 55, "TP": 20}),
      "D": ("Melihat contoh instalasi pendingin", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (8, "Lingkungan kerja seperti apa yang kamu bayangkan?",
     {"A": ("Bengkel atau workshop mesin", {"TM": 60, "PM": 20, "TRIK": 10, "TP": 10}),
      "B": ("Studio desain dan manufaktur", {"TM": 10, "PM": 60, "TRIK": 20, "TP": 10}),
      "C": ("Area lab kontrol industri", {"TM": 10, "PM": 15, "TRIK": 55, "TP": 20}),
      "D": ("Lapangan instalasi AC/Refrigerasi", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (9, "Kamu cenderung teratur dalam hal...",
     {"A": ("Mengelola data mesin & maintenance", {"TM": 55, "PM": 25, "TRIK": 10, "TP": 10}),
      "B": ("Menyusun alur kerja desain", {"TM": 15, "PM": 60, "TRIK": 15, "TP": 10}),
      "C": ("Menata alat kontrol", {"TM": 10, "PM": 15, "TRIK": 55, "TP": 20}),
      "D": ("Menata alat pendingin", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (10, "Ketika diberi tugas baru, reaksi kamu?",
     {"A": ("Menanyakan kondisi mesin/masalah utama", {"TM": 60, "PM": 20, "TRIK": 10, "TP": 10}),
      "B": ("Membayangkan langkah kerja teknis", {"TM": 15, "PM": 60, "TRIK": 15, "TP": 10}),
      "C": ("Mengecek alat kontrol yang diperlukan", {"TM": 10, "PM": 15, "TRIK": 55, "TP": 20}),
      "D": ("Membaca dasar sistem pendingin", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (11, "Jika diminta mempelajari hal baru, kamu lebih...",
     {"A": ("Cari gambaran mesin/permesinan", {"TM": 60, "PM": 20, "TRIK": 10, "TP": 10}),
      "B": ("Cari struktur desain", {"TM": 15, "PM": 60, "TRIK": 15, "TP": 10}),
      "C": ("Coba langsung alat control", {"TM": 10, "PM": 10, "TRIK": 60, "TP": 20}),
      "D": ("Menghafal materi dasar pendingin", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (12, "Kamu nyaman dengan data dalam bentuk...",
     {"A": ("Grafik performa mesin", {"TM": 60, "PM": 20, "TRIK": 10, "TP": 10}),
      "B": ("Diagram desain", {"TM": 10, "PM": 60, "TRIK": 20, "TP": 10}),
      "C": ("Hasil pengukuran sensor/alat", {"TM": 10, "PM": 10, "TRIK": 60, "TP": 20}),
      "D": ("Data suhu/tekanan pendingin", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (13, "Aktivitas apa yang membuat kamu fokus?",
     {"A": ("Mengamati kerja mesin", {"TM": 60, "PM": 20, "TRIK": 10, "TP": 10}),
      "B": ("Menyusun langkah desain", {"TM": 10, "PM": 60, "TRIK": 20, "TP": 10}),
      "C": ("Melihat kinerja alat otomatis", {"TM": 10, "PM": 10, "TRIK": 60, "TP": 20}),
      "D": ("Mengamati proses pendinginan", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (14, "Kamu tertarik pada kegiatan yang...",
     {"A": ("Melibatkan mesin/permesinan", {"TM": 60, "PM": 20, "TRIK": 10, "TP": 10}),
      "B": ("Melibatkan desain manufaktur", {"TM": 10, "PM": 60, "TRIK": 20, "TP": 10}),
      "C": ("Melibatkan alat elektronik/kontrol", {"TM": 10, "PM": 10, "TRIK": 60, "TP": 20}),
      "D": ("Melibatkan instalasi HVAC", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (15, "Kamu paling suka hasil akhir berupa...",
     {"A": ("Mesin yang berfungsi Kembali", {"TM": 65, "PM": 20, "TRIK": 10, "TP": 5}),
      "B": ("Desain produk", {"TM": 10, "PM": 65, "TRIK": 15, "TP": 10}),
      "C": ("Alat kontrol berfungsi stabil", {"TM": 10, "PM": 10, "TRIK": 60, "TP": 20}),
      "D": ("Sistem pendingin bekerja optimal", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (16, "Dalam proyek besar, bagian mana yang paling menarik bagimu?",
     {"A": ("Penanganan mesin dan unit mekanik", {"TM": 60, "PM": 20, "TRIK": 10, "TP": 10}),
      "B": ("Penyusunan desain dan perhitungan", {"TM": 10, "PM": 65, "TRIK": 15, "TP": 10}),
      "C": ("Integrasi sensor, wiring, atau control", {"TM": 10, "PM": 10, "TRIK": 65, "TP": 15}),
      "D": ("Instalasi dan pengecekan sistem pendingin", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (17, "Kamu lebih suka menyelesaikan tugas yang ...",
     {"A": ("Membutuhkan kekuatan analisa mekanika", {"TM": 60, "PM": 25, "TRIK": 10, "TP": 5}),
      "B": ("Membutuhkan ketelitian dalam gambar Teknik", {"TM": 10, "PM": 65, "TRIK": 15, "TP": 10}),
      "C": ("Membutuhkan kesabaran menghubungkan alat kontrol", {"TM": 10, "PM": 15, "TRIK": 60, "TP": 15}),
      "D": ("Membutuhkan pengukuran suhu, tekanan, freon", {"TM": 10, "PM": 10, "TRIK": 15, "TP": 65})}),
    (18, "Jika diberi dua pilihan belajar, kamu pilih...",
     {"A": ("Cara kerja piston, gearbox, atau mesin industri", {"TM": 70, "PM": 15, "TRIK": 10, "TP": 5}),
      "B": ("Desain mold, jig, fixture, atau komponen manufaktur", {"TM": 10, "PM": 65, "TRIK": 15, "TP": 10}),
      "C": ("PLC, mikrokontroler, sensor industri", {"TM": 10, "PM": 10, "TRIK": 65, "TP": 15}),
      "D": ("Kompresor, kondensor, evaporator, ducting", {"TM": 5, "PM": 10, "TRIK": 15, "TP": 70})}),
    (19, "Dalam kerja nyata, kamu lebih ingin...",
     {"A": ("Bekerja langsung dengan mesin dan bengkel", {"TM": 70, "PM": 15, "TRIK": 10, "TP": 5}),
      "B": ("Mendesain produk dan peralatan teknik", {"TM": 10, "PM": 70, "TRIK": 10, "TP": 10}),
      "C": ("Menangani sistem kontrol dan otomasi", {"TM": 10, "PM": 10, "TRIK": 70, "TP": 10}),
      "D": ("Bekerja di dunia HVAC/pendingin", {"TM": 5, "PM": 10, "TRIK": 10, "TP": 75})}),
    (20, "Kamu merasa kuat di kemampuan...",
     {"A": ("Mekanika dan memahami komponen mesin", {"TM": 70, "PM": 15, "TRIK": 10, "TP": 5}),
      "B": ("Menggambar teknik dan memvisualisasikan bentuk", {"TM": 10, "PM": 70, "TRIK": 10, "TP": 10}),
      "C": ("Menghubungkan perangkat kontrol", {"TM": 10, "PM": 10, "TRIK": 70, "TP": 10}),
      "D": ("Mengenal instalasi pendingin", {"TM": 5, "PM": 10, "TRIK": 10, "TP": 75})}),
    (21, "Kamu lebih tertarik pada materi yang...",
     {"A": ("Berhubungan dengan mesin dan permesinan", {"TM": 70, "PM": 15, "TRIK": 10, "TP": 5}),
      "B": ("Menjelaskan langkah desain dan manufaktur", {"TM": 10, "PM": 70, "TRIK": 10, "TP": 10}),
      "C": ("Berhubungan dengan sinyal dan kendali", {"TM": 10, "PM": 10, "TRIK": 70, "TP": 10}),
      "D": ("Berhubungan dengan siklus refrigerasi", {"TM": 10, "PM": 10, "TRIK": 10, "TP": 70})}),
    (22, "Saat belajar mandiri, kamu lebih suka...",
     {"A": ("Mengamati komponen mesin", {"TM": 70, "PM": 15, "TRIK": 10, "TP": 5}),
      "B": ("Menggambar skema desain", {"TM": 15, "PM": 60, "TRIK": 15, "TP": 10}),
      "C": ("Mencoba sensor dan board control", {"TM": 10, "PM": 10, "TRIK": 70, "TP": 10}),
      "D": ("Menguji sistem pendingin", {"TM": 5, "PM": 10, "TRIK": 15, "TP": 70})}),
    (23, "Aktivitas praktikum yang paling kamu sukai?",
     {"A": ("Bongkar pasang mesin", {"TM": 75, "PM": 10, "TRIK": 10, "TP": 5}),
      "B": ("Praktikum CAD dan fabrikasi", {"TM": 10, "PM": 75, "TRIK": 10, "TP": 5}),
      "C": ("Praktikum PLC dan sensor", {"TM": 10, "PM": 10, "TRIK": 75, "TP": 5}),
      "D": ("Praktikum refrigerasi", {"TM": 10, "PM": 5, "TRIK": 10, "TP": 75})}),
    (24, "Ketika melihat alat teknik, bagian apa yang kamu perhatikan?",
     {"A": ("Mekanik dan gerakan mesin", {"TM": 70, "PM": 15, "TRIK": 10, "TP": 5}),
      "B": ("Rancangan dan bentuk komponen", {"TM": 10, "PM": 70, "TRIK": 10, "TP": 10}),
      "C": ("Kabel, sensor, panel, control", {"TM": 10, "PM": 10, "TRIK": 70, "TP": 10}),
      "D": ("Pipa, evaporator, kondensor", {"TM": 5, "PM": 10, "TRIK": 10, "TP": 75})}),
    (25, "Kamu paling senang proyek seperti...",
     {"A": ("Merakit mesin atau alat mekanik", {"TM": 70, "PM": 20, "TRIK": 5, "TP": 5}),
      "B": ("Mendesain dan membuat prototipe", {"TM": 10, "PM": 75, "TRIK": 10, "TP": 5}),
      "C": ("Menyusun panel control", {"TM": 5, "PM": 10, "TRIK": 75, "TP": 10}),
      "D": ("Instalasi HVAC", {"TM": 10, "PM": 5, "TRIK": 10, "TP": 75})}),
    (26, "Kamu paling bisa memahami...",
     {"A": ("Gerak dan beban pada mesin", {"TM": 70, "PM": 20, "TRIK": 5, "TP": 5}),
      "B": ("Bentuk dan struktur desain", {"TM": 10, "PM": 75, "TRIK": 10, "TP": 5}),
      "C": ("Sistem kontrol otomatis", {"TM": 5, "PM": 10, "TRIK": 75, "TP": 10}),
      "D": ("Siklus pendinginan", {"TM": 5, "PM": 5, "TRIK": 10, "TP": 80})}),
    (27, "Kamu merasa paling cocok bekerja sebagai...",
     {"A": ("Teknisi atau mekanik mesin", {"TM": 80, "PM": 10, "TRIK": 5, "TP": 5}),
      "B": ("Desainer manufaktur", {"TM": 5, "PM": 80, "TRIK": 10, "TP": 5}),
      "C": ("Teknisi kontrol/otomasi", {"TM": 5, "PM": 5, "TRIK": 80, "TP": 10}),
      "D": ("Teknisi AC/Refrigerasi", {"TM": 5, "PM": 5, "TRIK": 10, "TP": 80})}),
    (28, "Kamu paling suka mengamati...",
     {"A": ("Pergerakan mesin bekerja", {"TM": 80, "PM": 10, "TRIK": 5, "TP": 5}),
      "B": ("Bagaimana desain dibuat", {"TM": 5, "PM": 80, "TRIK": 10, "TP": 5}),
      "C": ("Bagaimana sensor membaca data", {"TM": 5, "PM": 5, "TRIK": 80, "TP": 10}),
      "D": ("Pendinginan udara/logika refrigerasi", {"TM": 5, "PM": 5, "TRIK": 10, "TP": 80})}),
    (29, "Dalam kelompok, kamu sering menjadi...",
     {"A": ("Penggerak teknis(mekanik)", {"TM": 75, "PM": 10, "TRIK": 10, "TP": 5}),
      "B": ("Perancang/penggambar", {"TM": 5, "PM": 80, "TRIK": 10, "TP": 5}),
      "C": ("Penyambung alat control", {"TM": 5, "PM": 10, "TRIK": 75, "TP": 10}),
      "D": ("Penata peralatan pendingin", {"TM": 5, "PM": 5, "TRIK": 10, "TP": 80})}),
    (30, "Kamu lebih suka memecahkan masalah dengan...",
     {"A": ("Analisa mekanis", {"TM": 75, "PM": 15, "TRIK": 5, "TP": 5}),
      "B": ("Menganalisa desain", {"TM": 5, "PM": 80, "TRIK": 10, "TP": 5}),
      "C": ("Pengujian sensor dan control", {"TM": 5, "PM": 5, "TRIK": 80, "TP": 10}),
      "D": ("Uji tekanan/suhu refrigerasi", {"TM": 5, "PM": 5, "TRIK": 10, "TP": 80})}),
    (31, "Kamu paling percaya diri ketika...",
     {"A": ("Memperbaiki masalah mekanik", {"TM": 80, "PM": 10, "TRIK": 5, "TP": 5}),
      "B": ("Membuat konsep desain", {"TM": 10, "PM": 75, "TRIK": 10, "TP": 5}),
      "C": ("Mencoba rangkaian control", {"TM": 5, "PM": 10, "TRIK": 80, "TP": 5}),
      "D": ("Menganalisis kinerja pendingin", {"TM": 5, "PM": 5, "TRIK": 10, "TP": 80})}),
    (32, "Kamu paling suka berbicara tentang...",
     {"A": ("Mesin dan permesinan", {"TM": 80, "PM": 10, "TRIK": 5, "TP": 5}),
      "B": ("Desain dan manufaktur", {"TM": 10, "PM": 80, "TRIK": 5, "TP": 5}),
      "C": ("Kontrol dan otomasi", {"TM": 5, "PM": 5, "TRIK": 80, "TP": 10}),
      "D": ("AC, kulkas, pendingin industri", {"TM": 5, "PM": 5, "TRIK": 10, "TP": 80})}),
    (33, "Kamu paling menikmati tugas...",
     {"A": ("Memperbaiki atau merakit mesin", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Mendesain komponen", {"TM": 5, "PM": 85, "TRIK": 5, "TP": 5}),
      "C": ("Merakit panel control", {"TM": 3, "PM": 5, "TRIK": 85, "TP": 7}),
      "D": ("Memasang sistem pendingin", {"TM": 5, "PM": 5, "TRIK": 5, "TP": 85})}),
    (34, "Kamu lebih suka lingkungan yang...",
     {"A": ("Banyak suara mesin", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Penuh desain 2D/3D", {"TM": 5, "PM": 85, "TRIK": 5, "TP": 5}),
      "C": ("Banyak panel dan kabel", {"TM": 3, "PM": 5, "TRIK": 85, "TP": 7}),
      "D": ("Dingin karena pendingin", {"TM": 2, "PM": 5, "TRIK": 5, "TP": 88})}),
    (35, "Ketika melihat problem, kamu langsung...",
     {"A": ("Cek kondisi mesin", {"TM": 80, "PM": 10, "TRIK": 5, "TP": 5}),
      "B": ("Buat sketsa solusi", {"TM": 5, "PM": 80, "TRIK": 10, "TP": 5}),
      "C": ("Ukur arus/control", {"TM": 5, "PM": 5, "TRIK": 80, "TP": 10}),
      "D": ("Ukur tekanan/suhu", {"TM": 5, "PM": 5, "TRIK": 10, "TP": 80})}),
    (36, "Kamu merasa nyaman bekerja dengan...",
     {"A": ("Alat mekanik", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Software desain", {"TM": 5, "PM": 85, "TRIK": 5, "TP": 5}),
      "C": ("Alat sensor/control", {"TM": 3, "PM": 5, "TRIK": 85, "TP": 7}),
      "D": ("Alat pendingin", {"TM": 3, "PM": 5, "TRIK": 7, "TP": 85})}),
    (37, "Kamu lebih ingin memperdalam...",
     {"A": ("Mesin industri", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Desain manufaktur", {"TM": 5, "PM": 85, "TRIK": 5, "TP": 5}),
      "C": ("Kontrol otomatis", {"TM": 5, "PM": 5, "TRIK": 85, "TP": 5}),
      "D": ("Refrigerasi dan HVAC", {"TM": 5, "PM": 5, "TRIK": 5, "TP": 85})}),
    (38, "Kamu paling sering penasaran tentang...",
     {"A": ("Mesin bekerja bagaimana", {"TM": 80, "PM": 10, "TRIK": 5, "TP": 5}),
      "B": ("Desain dibuat di software apa", {"TM": 5, "PM": 80, "TRIK": 10, "TP": 5}),
      "C": ("Cara kerja PLC", {"TM": 5, "PM": 5, "TRIK": 80, "TP": 10}),
      "D": ("Kenapa AC bisa dingin", {"TM": 5, "PM": 5, "TRIK": 10, "TP": 80})}),
    (39, "Kamu paling menikmati saat...",
     {"A": ("Memegang komponen mesin", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Mendesain bentuk komponen", {"TM": 5, "PM": 85, "TRIK": 5, "TP": 5}),
      "C": ("Menyusun panel", {"TM": 3, "PM": 5, "TRIK": 85, "TP": 7}),
      "D": ("Mengatur pipa & sistem pendingin", {"TM": 3, "PM": 5, "TRIK": 7, "TP": 85})}),
    (40, "Kamu paling suka ketika tugas menuntut...",
     {"A": ("Perbaikan mekanik", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Perancangan", {"TM": 5, "PM": 85, "TRIK": 5, "TP": 5}),
      "C": ("Kontrol & wiring", {"TM": 3, "PM": 5, "TRIK": 85, "TP": 7}),
      "D": ("Pendingin", {"TM": 3, "PM": 5, "TRIK": 7, "TP": 85})}),
    (41, "Kamu paling bangga jika berhasil...",
     {"A": ("Menghidupkan mesin", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Menyelesaikan desain", {"TM": 5, "PM": 85, "TRIK": 5, "TP": 5}),
      "C": ("Mengaktifkan sistem control", {"TM": 3, "PM": 5, "TRIK": 85, "TP": 7}),
      "D": ("Mendinginkan ruangan/alat", {"TM": 3, "PM": 5, "TRIK": 7, "TP": 85})}),
    (42, "Dalam pekerjaan, kamu ingin jadi...",
     {"A": ("Ahli mesin", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Ahli desain", {"TM": 5, "PM": 85, "TRIK": 5, "TP": 5}),
      "C": ("Ahli otomasi", {"TM": 3, "PM": 5, "TRIK": 85, "TP": 7}),
      "D": ("Ahli pendingin", {"TM": 2, "PM": 5, "TRIK": 7, "TP": 86})}),
    (43, "Kamu merasa tipe yang...",
     {"A": ("Praktis & mekanis", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Detail & sistematis", {"TM": 10, "PM": 80, "TRIK": 5, "TP": 5}),
      "C": ("Teliti & logis(kontrol)", {"TM": 3, "PM": 5, "TRIK": 85, "TP": 7}),
      "D": ("Teliti & cekatan(pendingin)", {"TM": 3, "PM": 5, "TRIK": 7, "TP": 85})}),
    (44, "Kamu mengutamakan...",
     {"A": ("Perbaikan cepat & tepat", {"TM": 85, "PM": 10, "TRIK": 3, "TP": 2}),
      "B": ("Desain presisi", {"TM": 5, "PM": 85, "TRIK": 5, "TP": 5}),
      "C": ("Keakuratan kontrol", {"TM": 3, "PM": 5, "TRIK": 85, "TP": 7}),
      "D": ("Pendinginan efektif", {"TM": 3, "PM": 5, "TRIK": 7, "TP": 85})}),
    (45, "Kamu paling yakin masa depanmu di bidang...",
     {"A": ("Mesin & industri mekanik", {"TM": 90, "PM": 5, "TRIK": 3, "TP": 2}),
      "B": ("Desain & manufaktur", {"TM": 5, "PM": 90, "TRIK": 3, "TP": 2}),
      "C": ("Instrumentasi & control", {"TM": 3, "PM": 5, "TRIK": 90, "TP": 2}),
      "D": ("Pendingin & tata udara", {"TM": 3, "PM": 5, "TRIK": 2, "TP": 90})}),
]

# Isi ke DATA_JURUSAN
for no, q, choices in teknik_data:
    DATA_JURUSAN["teknik"]["pertanyaan"].append({"no": no, "pertanyaan": q, "pilihan": {k: {"text": v[0], "bobot": v[1]} for k, v in choices.items()}})

# === 3. ISI DATA KESEHATAN (24 pertanyaan) ===
kesehatan_data = [
    (1, "Saat ada kerabat sakit, peran utama yang Anda ambil?",
     {"A": ("Memberikan asuhan, kenyamanan, dan perawatan dasar.", {"KP": 70, "TLM": 20, "TREM": 10}),
      "B": ("Menganalisis kemungkinan penyakit dan tes yang dibutuhkan.", {"KP": 30, "TLM": 50, "TREM": 20}),
      "C": ("Memastikan alat bantu medis (termometer, nebulizer) berfungsi.", {"KP": 20, "TLM": 10, "TREM": 70})}),
    (2, "Kegiatan waktu luang yang paling Anda nikmati?",
     {"A": ("Berinteraksi untuk memberikan dukungan moral atau emosional.", {"KP": 70, "TLM": 15, "TREM": 15}),
      "B": ("Menganalisis data atau memecahkan masalah berbasis fakta.", {"KP": 15, "TLM": 70, "TREM": 15}),
      "C": ("Memperbaiki perangkat elektronik atau merangkai sistem.", {"KP": 15, "TLM": 15, "TREM": 70})}),
    (3, "Saat mengerjakan tugas, prioritas utama Anda?",
     {"A": ("Akurasi data dan kebenaran informasi yang disampaikan.", {"KP": 20, "TLM": 60, "TREM": 20}),
      "B": ("Kenyamanan dan suasana kolaborasi tim yang baik.", {"KP": 60, "TLM": 20, "TREM": 20})}),
    (4, "Di lab sains, yang paling menarik perhatian Anda?",
     {"A": ("Proses reaksi kimia dan perubahan zat.", {"KP": 10, "TLM": 80, "TREM": 10}),
      "B": ("Rangkaian sirkuit dan prinsip kerja alat listrik.", {"KP": 10, "TLM": 10, "TREM": 80})}),
    (5, "Anda lebih suka mempelajari manual tentang:",
     {"A": ("Prosedur komunikasi efektif dengan orang yang cemas.", {"KP": 70, "TLM": 15, "TREM": 15}),
      "B": ("Prosedur perawatan dan kalibrasi alat canggih.", {"KP": 15, "TLM": 15, "TREM": 70})}),
    (6, "Anda memilih lingkungan kerja yang:",
     {"A": ("Dinamis, banyak bergerak, dan berinteraksi intens.", {"KP": 70, "TLM": 15, "TREM": 15}),
      "B": ("Stabil, fokus pada objek/layar, dan minim gangguan.", {"KP": 15, "TLM": 50, "TREM": 35})}),
    (7, "Kapan Anda merasa paling berhasil?",
     {"A": ("Berhasil membuat pasien merasa aman dan didukung menuju kesembuhan.", {"KP": 60, "TLM": 20, "TREM": 20}),
      "B": ("Berhasil mengungkap penyebab penyakit melalui temuan data.", {"KP": 20, "TLM": 60, "TREM": 20}),
      "C": ("Berhasil memperbaiki instrumen penting yang rusak total.", {"KP": 20, "TLM": 20, "TREM": 60})}),
    (8, "Jika alat ukur(misal tensimeter) diragukan, tindakan Anda?",
     {"A": ("Mencari tahu prosedur kalibrasi agar alat kembali akurat.", {"KP": 10, "TLM": 20, "TREM": 70}),
      "B": ("Memastikan validitas data yang dihasilkan, karena ini vital.", {"KP": 35, "TLM": 45, "TREM": 20})}),
    (9, "Anda harus mengikuti prosedur langkah demi langkah yang sangat ketat.",
     {"A": ("Saya nyaman dan teliti dengan prosedur yang rigid(kaku).", {"KP": 15, "TLM": 65, "TREM": 20}),
      "B": ("Saya lebih suka prosedur yang adaptif sesuai kondisi lapangan.", {"KP": 65, "TLM": 20, "TREM": 15})}),
    (10, "Di Rumah Sakit, Anda lebih tertarik pada ruangan yang berisi:",
      {"A": ("Pasien dengan berbagai tingkat kebutuhan perawatan.", {"KP": 70, "TLM": 15, "TREM": 15}),
       "B": ("Peralatan canggih seperti ventilator atau mesin USG.", {"KP": 15, "TLM": 15, "TREM": 70})}),
    (11, "Mana yang lebih memicu rasa penasaran Anda?",
      {"A": ("Perilaku sel dan zat kimia sebagai respons terhadap penyakit.", {"KP": 20, "TLM": 65, "TREM": 15}),
       "B": ("Sinyal listrik dan mekanika yang menggerakkan alat medis.", {"KP": 15, "TLM": 20, "TREM": 65})}),
    (12, "Melihat seseorang kesulitan fisik dan butuh bantuan.",
      {"A": ("Insting Anda adalah langsung memberikan bantuan fisik yang aman.", {"KP": 70, "TLM": 15, "TREM": 15}),
       "B": ("Insting Anda adalah mencari tahu akar masalah medis dari kesulitan tersebut.", {"KP": 20, "TLM": 50, "TREM": 30})}),
    (13, "Anda tertarik pada isu efisiensi RS, terutama pada:",
      {"A": ("Ketahanan dan manajemen biaya pemeliharaan alat medis.", {"KP": 10, "TLM": 20, "TREM": 70}),
       "B": ("Optimalisasi alur pelayanan pasien agar tidak terjadi penundaan.", {"KP": 70, "TLM": 20, "TREM": 10})}),
    (14, "Anda harus sering memakai APD karena risiko paparan zat berbahaya/infeksi.",
      {"A": ("Saya siap, asalkan prosedur kerja saya menghasilkan data akurat.", {"KP": 15, "TLM": 70, "TREM": 15}),
       "B": ("Saya lebih siap menghadapi risiko cedera punggung akibat mengangkat pasien.", {"KP": 70, "TLM": 15, "TREM": 15})}),
    (15, "Mata pelajaran favorit Anda(nilai sempurna)?",
      {"A": ("Biologi(tubuh dan organ).", {"KP": 50, "TLM": 40, "TREM": 10}),
       "B": ("Kimia(zat dan reaksi).", {"KP": 10, "TLM": 50, "TREM": 40}),
       "C": ("Fisika(listrik dan mekanika).", {"KP": 10, "TLM": 10, "TREM": 80})}),
    (16, "Alarm alat infus pasien berbunyi. Respons Anda?",
      {"A": ("Segera ke sisi pasien dan kaji kondisinya.", {"KP": 75, "TLM": 15, "TREM": 10}),
       "B": ("Menganalisis kode error alat untuk mengetahui kerusakan teknis.", {"KP": 10, "TLM": 15, "TREM": 75})}),
    (17, "Mana yang Anda anggap pencapaian profesional terbesar?",
      {"A": ("Laporan diagnostik yang detail menjadi kunci keberhasilan pengobatan.", {"KP": 15, "TLM": 70, "TREM": 15}),
       "B": ("Asuhan yang diberikan sukses meningkatkan kualitas hidup pasien.", {"KP": 70, "TLM": 15, "TREM": 15}),
       "C": ("Peralatan vital yang rusak berhasil diperbaiki dan berfungsi optimal.", {"KP": 15, "TLM": 15, "TREM": 70})}),
    (18, "Anda harus menghadapi orang yang sangat cemas.",
      {"A": ("Saya siap mendengarkan dan memberikan edukasi yang menenangkan.", {"KP": 70, "TLM": 15, "TREM": 15}),
       "B": ("Saya fokus menyelesaikan tugas teknis yang menjadi tanggung jawab utama saya.", {"KP": 10, "TLM": 45, "TREM": 45})}),
    (19, "Anda harus mencatat setiap detail: jenis reagen, suhu, waktu, dll.",
      {"A": ("Saya menikmati dokumentasi detail dan prosedural.", {"KP": 15, "TLM": 70, "TREM": 15}),
       "B": ("Saya lebih fokus mencatat respons dan perkembangan kondisi pasien.", {"KP": 70, "TLM": 15, "TREM": 15})}),
    (20, "Pasien tiba-tiba jatuh. Reaksi Anda?",
      {"A": ("Memberikan pertolongan pertama dan menilai tingkat cedera.", {"KP": 75, "TLM": 15, "TREM": 10}),
       "B": ("Menganalisis faktor penyebab (kesehatan atau fungsi alat bantu).", {"KP": 20, "TLM": 40, "TREM": 40})}),
    (21, "Anda bekerja di ruangan suhu stabil/dingin untuk menjaga sampel/alat.",
      {"A": ("Saya nyaman dengan lingkungan kerja yang stabil dan tenang.", {"KP": 10, "TLM": 45, "TREM": 45}),
       "B": ("Saya lebih suka ruangan dengan suhu normal untuk kenyamanan interaksi.", {"KP": 80, "TLM": 10, "TREM": 10})}),
    (22, "Anda mahir memahami kode error atau instruksi teknis mesin.",
      {"A": ("Kemampuan ini sangat krusial dalam tugas harian saya.", {"KP": 15, "TLM": 20, "TREM": 65}),
       "B": ("Saya lebih mahir membaca bahasa tubuh dan ekspresi orang lain.", {"KP": 70, "TLM": 15, "TREM": 15})}),
    (23, "Ketelitian Anda paling dibutuhkan saat:",
      {"A": ("Pemberian obat agar dosis dan sasaran pasien tepat.", {"KP": 70, "TLM": 20, "TREM": 10}),
       "B": ("Pengukuran kadar zat dalam sampel agar hasil tidak meleset.", {"KP": 20, "TLM": 70, "TREM": 10})}),
    (24, "Anda presentasi soal teknologi kesehatan. Fokus utama Anda?",
      {"A": ("Inovasi perangkat keras(hardware) dan update alat terbaru.", {"KP": 10, "TLM": 10, "TREM": 70}),
       "B": ("Integrasi teknologi untuk meningkatkan asuhan langsung pasien.", {"KP": 60, "TLM": 10, "TREM": 30}),
       "C": ("Pengembangan metode tes cepat dan akurat untuk diagnosis dini.", {"KP": 10, "TLM": 60, "TREM": 30}),
       "D": ("Aspek etika dan kemanusiaan dalam penggunaan teknologi.", {"KP": 20, "TLM": 20, "TREM": 20})})
]

for no, q, choices in kesehatan_data:
    DATA_JURUSAN["kesehatan"]["pertanyaan"].append({"no": no, "pertanyaan": q, "pilihan": {k: {"text": v[0], "bobot": v[1]} for k, v in choices.items()}})

# === 4. ISI DATA INFORMATIKA (30 pertanyaan) ===
informatika_data = [
    (1, "Ketika membayangkan kerja di bidang teknologi, apa yang paling menarik buat kamu?",
     {"A": ("Menganalisis masalah dan mencari pola", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20}),
      "B": ("Mendesain solusi yang rapi dan terstruktur", {"SIKC": 20, "RPL": 35, "TRK": 15, "TI": 30}),
      "C": ("Memahami cara kerja perangkat/peralatan digital", {"SIKC": 20, "RPL": 10, "TRK": 45, "TI": 25}),
      "D": ("Belajar konsep dasar komputer dan jaringan secara umum", {"SIKC": 15, "RPL": 15, "TRK": 30, "TI": 40})}),
    (2, "Jika diminta menyelesaikan tugas kelompok, peran apa yang biasanya kamu ambil?",
     {"A": ("Mengatur alur kerja dan strategi tim", {"SIKC": 30, "RPL": 25, "TRK": 20, "TI": 25}),
      "B": ("Membuat rancangan step-by-step tugas", {"SIKC": 20, "RPL": 35, "TRK": 20, "TI": 25}),
      "C": ("Membantu bagian umum (input data, laporan, dll.)", {"SIKC": 25, "RPL": 25, "TRK": 25, "TI": 25})}),
    (3, "Jika menghadapi masalah, kamu lebih nyaman cara mana?",
     {"A": ("Observasi pola dan hubungan antar hal", {"SIKC": 35, "RPL": 25, "TRK": 15, "TI": 25}),
      "B": ("Membuat langkah-langkah secara runtut", {"SIKC": 25, "RPL": 30, "TRK": 20, "TI": 25}),
      "C": ("Mencari referensi dan mempelajari dasar-dasarnya dulu", {"SIKC": 25, "RPL": 25, "TRK": 25, "TI": 35})}),
    (4, "Kamu paling nyaman belajar dengan cara",
     {"A": ("Diskusi dan observasi kasus nyata", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20}),
      "B": ("Langkah-langkah teori yang runtut", {"SIKC": 20, "RPL": 35, "TRK": 20, "TI": 25}),
      "C": ("Melihat contoh lalu mempraktikkan", {"SIKC": 20, "RPL": 20, "TRK": 30, "TI": 30})}),
    (5, "Jika diminta mempelajari hal baru, kamu lebih",
     {"A": ("Mencari gambaran besarnya dulu", {"SIKC": 30, "RPL": 25, "TRK": 20, "TI": 25}),
      "B": ("Mencari struktur dan tahap belajarnya", {"SIKC": 20, "RPL": 30, "TRK": 25, "TI": 25}),
      "C": ("Mencoba langsung untuk mengetahui fungsinya", {"SIKC": 20, "RPL": 20, "TRK": 35, "TI": 25})}),
    (6, "Kamu lebih tertarik pada kegiatan yang",
     {"A": ("Melibatkan banyak data lapangan", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20}),
      "B": ("Melibatkan prosedur dan perencanaan", {"SIKC": 20, "RPL": 35, "TRK": 20, "TI": 25}),
      "C": ("Melibatkan alat elektronik atau perangkat", {"SIKC": 20, "RPL": 15, "TRK": 40, "TI": 25})}),
    (7, "Kamu cenderung teratur dalam hal apa?",
     {"A": ("Mengelola informasi dan membuat ringkasan (rangkuman)", {"SIKC": 30, "RPL": 25, "TRK": 20, "TI": 25}),
      "B": ("Membuat alur kerja", {"SIKC": 25, "RPL": 30, "TRK": 25, "TI": 20}),
      "C": ("Menyelesaikan tugas dasar secara konsisten", {"SIKC": 25, "RPL": 25, "TRK": 25, "TI": 25})}),
    (8, "Ketika diberi tugas baru, reaksi kamu?",
     {"A": ("Menanyakan apa tujuan keseluruhannya", {"SIKC": 30, "RPL": 25, "TRK": 20, "TI": 25}),
      "B": ("Langsung membayangkan langkah-langkahnya", {"SIKC": 20, "RPL": 30, "TRK": 25, "TI": 25}),
      "C": ("Membaca panduan dasarnya terlebih dahulu", {"SIKC": 25, "RPL": 25, "TRK": 25, "TI": 25})}),
    (9, "Lingkungan kerja seperti apa yang kamu bayangkan?",
     {"A": ("Tim yang memikirkan solusi dan prosedur", {"SIKC": 25, "RPL": 30, "TRK": 20, "TI": 25}),
      "B": ("Lingkungan dengan perangkat dan alat teknologi", {"SIKC": 20, "RPL": 20, "TRK": 35, "TI": 25})}),
    (10, "Ketika melihat sebuah masalah di lingkungan sekitar, kamu biasanya",
      {"A": ("Mencari tahu pola dan penyebab utamanya", {"SIKC": 35, "RPL": 20, "TRK": 20, "TI": 25}),
       "B": ("Membayangkan langkah-langkah perbaikan", {"SIKC": 20, "RPL": 35, "TRK": 20, "TI": 25}),
       "C": ("Mengecek alat/perlengkapan yang terkait", {"SIKC": 15, "RPL": 15, "TRK": 40, "TI": 30})}),
    (11, "Saat belajar hal baru, Bagian mana yang bikin kamu cepat paham saat belajar?",
      {"A": ("Penjelasan mengenai dampaknya pada masyarakat/lingkungan", {"SIKC": 35, "RPL": 25, "TRK": 20, "TI": 20}),
       "B": ("Urutan langkah-langkahnya", {"SIKC": 20, "RPL": 30, "TRK": 20, "TI": 30}),
       "C": ("Contoh langsung pada perangkat atau alat", {"SIKC": 20, "RPL": 15, "TRK": 40, "TI": 25})}),
    (12, "Kamu lebih suka proyek yang hasilnya",
      {"A": ("Bisa digunakan oleh masyarakat sekitar", {"SIKC": 30, "RPL": 25, "TRK": 20, "TI": 25}),
       "B": ("Bisa mempermudah alur kerja suatu organisasi", {"SIKC": 25, "RPL": 35, "TRK": 20, "TI": 20}),
       "C": ("Bisa berfungsi secara fisik", {"SIKC": 20, "RPL": 15, "TRK": 40, "TI": 25})}),
    (13, "Ketika belajar, kamu biasanya fokus pada",
      {"A": ('"Masalah apa yang mau diselesaikan?"', {"SIKC": 30, "RPL": 25, "TRK": 20, "TI": 25}),
       "B": ('"Bagaimana prosesnya dari awal sampai akhir?"', {"SIKC": 20, "RPL": 30, "TRK": 20, "TI": 30}),
       "C": ('"Alat atau perangkat apa saja yang diperlukan?"', {"SIKC": 20, "RPL": 20, "TRK": 35, "TI": 25}),
       "D": ('"Apa konsep dasarnya?"', {"SIKC": 25, "RPL": 25, "TRK": 25, "TI": 25})}),
    (14, "Saat membayangkan pekerjaan di masa depan, kamu ingin yang",
      {"A": ("Banyak berhubungan dengan data dan masyarakat", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20}),
       "B": ("Fokus pada perancangan solusi", {"SIKC": 30, "RPL": 25, "TRK": 20, "TI": 25}),
       "C": ("Berhubungan dengan perangkat dan alat teknologi", {"SIKC": 20, "RPL": 20, "TRK": 35, "TI": 25}),
       "D": ("Berbasis komputer dan jaringan", {"SIKC": 15, "RPL": 15, "TRK": 35, "TI": 35})}),
    (15, "Saat membaca berita/isu teknologi, apa yang paling kamu perhatikan?",
      {"A": ("Dampaknya pada masyarakat", {"SIKC": 35, "RPL": 20, "TRK": 20, "TI": 25}),
       "B": ("Bagaimana sistem itu bekerja", {"SIKC": 25, "RPL": 30, "TRK": 20, "TI": 25}),
       "C": ("Jenis perangkat atau infrastrukturnya", {"SIKC": 20, "RPL": 20, "TRK": 35, "TI": 25})}),
    (16, "Gaya berpikir kamu lebih dekat ke...",
      {"A": ("Logis dan berbasis bukti", {"SIKC": 35, "RPL": 25, "TRK": 15, "TI": 25}),
       "B": ("Sistematis dan bertahap", {"SIKC": 20, "RPL": 35, "TRK": 20, "TI": 25}),
       "C": ("Eksperimen mencoba langsung", {"SIKC": 20, "RPL": 20, "TRK": 35, "TI": 25})}),
    (17, "Saat belajar sesuatu yang rumit, kamu:",
      {"A": ("Membuat catatan langkah-langkah(step-by-step) dengan rapi", {"SIKC": 20, "RPL": 35, "TRK": 20, "TI": 25}),
       "B": ("Analisis pola dan konsepnya", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20})}),
    (18, "Apa gelar yang ingin kamu dapatkan?",
      {"A": ("Ahli Madya(A.Md)", {"SIKC": 10, "RPL": 10, "TRK": 10, "TI": 70}),
       "B": ("Sarjana Terapan(S.Tr)", {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 10})}),
    (19, "Mengenai teknologi, kamu lebih penasaran tentang ...",
      {"A": ("Bagaimana internet atau jaringan itu bisa berjalan?", {"SIKC": 20, "RPL": 20, "TRK": 25, "TI": 35}),
       "B": ("Bagaimana cara membuat suatu aplikasi?", {"SIKC": 25, "RPL": 35, "TRK": 10, "TI": 25}),
       "C": ("Bagaimana cara kerja suatu sensor yang bisa mendeteksi?", {"SIKC": 25, "RPL": 10, "TRK": 40, "TI": 25}),
       "D": ("Bagaimana komputer bisa memiliki kecerdasan layaknya manusia?", {"SIKC": 25, "RPL": 25, "TRK": 25, "TI": 25})}),
    (20, "Kamu lebih memilih...",
      {"A": ("Belajar 3 tahun(D3) dan cepat masuk dunia kerja.", {"SIKC": 10, "RPL": 10, "TRK": 10, "TI": 70}),
       "B": ("Belajar 4 tahun(D4) untuk pendalaman keahlian dan jenjang karir lebih tinggi.", {"SIKC": 30, "RPL": 30, "TRK": 30, "TI": 10})}),
    (21, "Kamu lebih suka bekerja dengan...",
      {"A": ("Data dan angka untuk mencari tahu tren dan dampaknya di masyarakat/bisnis.", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20}),
       "B": ("Perangkat lunak dan coding untuk membangun aplikasi yang fungsional.", {"SIKC": 25, "RPL": 40, "TRK": 10, "TI": 25}),
       "C": ("Perangkat keras dan jaringan untuk memastikan koneksi berjalan aman dan cepat.", {"SIKC": 20, "RPL": 10, "TRK": 40, "TI": 20})}),
    (22, "Kamu lebih nyaman bekerja dengan metode yang...",
      {"A": ("Sistematis, terencana, dan punya tahapan yang wajib diikuti(seperti membuat jadwal rapi).", {"SIKC": 25, "RPL": 35, "TRK": 20, "TI": 20}),
       "B": ("Fleksibel dan bisa langsung mencoba-coba sambil diperbaiki(trial and error).", {"SIKC": 20, "RPL": 20, "TRK": 35, "TI": 25})}),
    (23, "Mata kuliah apa yang paling kamu ingin pelajari lebih dalam?",
      {"A": ("Rekayasa Perangkat Lunak, Pengujian Perangkat Lunak (Software Testing).", {"SIKC": 25, "RPL": 40, "TRK": 15, "TI": 20}),
       "B": ("Sistem Informasi Manajemen, Analisis Bisnis, Business Intelligence.", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20}),
       "C": ("Internet of Things(IoT), Sistem Tertanam, Kriptografi.", {"SIKC": 25, "RPL": 10, "TRK": 40, "TI": 25}),
       "D": ("Algoritma, Basis Data, Administrasi Sistem dan Jaringan Dasar.", {"SIKC": 20, "RPL": 20, "TRK": 20, "TI": 40})}),
    (24, "Kamu melihat jaringan komputer sebagai...",
      {"A": ("Alat komunikasi yang menghubungkan sistem informasi dalam organisasi.", {"SIKC": 40, "RPL": 25, "TRK": 10, "TI": 25}),
       "B": ("Infrastruktur fisik yang harus dirancang, dipasang, dan diamankan secara ketat.", {"SIKC": 20, "RPL": 15, "TRK": 40, "TI": 25})}),
    (25, "Kamu lebih tertarik pada otomatisasi yang ...",
      {"A": ("Menggantikan proses manual di belakang layar (back-end atau system process).", {"SIKC": 25, "RPL": 35, "TRK": 15, "TI": 25}),
       "B": ("Mengontrol alat fisik (misalnya robot, pintu otomatis, atau sensor).", {"SIKC": 20, "RPL": 15, "TRK": 40, "TI": 25})}),
    (26, "Jika diminta melakukan penelitian (riset), kamu lebih tertarik pada...",
      {"A": ("Riset tentang metode terbaik untuk mengembangkan sebuah software.", {"SIKC": 25, "RPL": 40, "TRK": 10, "TI": 25}),
       "B": ("Riset tentang analisis data untuk memecahkan masalah di lingkungan/organisasi.", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20}),
       "C": ("Riset tentang cara kerja sebuah alat atau sistem yang terhubung.", {"SIKC": 20, "RPL": 20, "TRK": 40, "TI": 20})}),
    (27, "Ketika menggunakan aplikasi(seperti game atau media sosial), mana yang kamu anggap paling penting?",
      {"A": ("Tampilan yang keren, warna yang bagus, dan mudah digunakan.", {"SIKC": 25, "RPL": 35, "TRK": 15, "TI": 25}),
       "B": ("Fungsi yang berjalan cepat dan sistem di belakangnya yang stabil.", {"SIKC": 25, "RPL": 35, "TRK": 15, "TI": 25}),
       "C": ("Kombinasi keduanya (tampilan dan fungsi)", {"SIKC": 25, "RPL": 25, "TRK": 25, "TI": 25})}),
    (28, "Jika kamu punya ide bisnis teknologi, kamu akan fokus pada...",
      {"A": ("Menciptakan aplikasi atau platform baru yang belum ada.", {"SIKC": 25, "RPL": 35, "TRK": 15, "TI": 25}),
       "B": ("Menyediakan jasa pemasangan dan pemeliharaan alat/jaringan.", {"SIKC": 15, "RPL": 15, "TRK": 40, "TI": 30}),
       "C": ("Menganalisis pasar dan membuat platform yang fokus pada informasi bisnis/publik.", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20})}),
    (29, "Menurut kamu, data yang terkumpul itu paling berguna untuk...",
      {"A": ("Membuat kebijakan atau keputusan yang lebih baik di perusahaan atau lingkungan sekitar.", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20}),
       "B": ("Membuat software lebih canggih(misalnya, membuat program bisa memprediksi sesuatu).", {"SIKC": 25, "RPL": 30, "TRK": 20, "TI": 25})}),
    (30, "Dalam Pelajaran Matematika: Kamu paling suka jika diminta...",
      {"A": ("Mengerjakan soal cerita yang harus dianalisis polanya.", {"SIKC": 40, "RPL": 20, "TRK": 20, "TI": 20}),
       "B": ("Mengerjakan soal yang prosedural(harus ikut rumus step-by-step).", {"SIKC": 20, "RPL": 35, "TRK": 25, "TI": 20})})
]

for no, q, choices in informatika_data:
    DATA_JURUSAN["informatika"]["pertanyaan"].append({"no": no, "pertanyaan": q, "pilihan": {k: {"text": v[0], "bobot": v[1]} for k, v in choices.items()}})

# === TRAIT CONTEXT ===
TRAIT_CONTEXT = {
    "TM": "Siswa praktis, suka mekanika fisik, hands-on mesin.",
    "PM": "Siswa perancang, suka presisi desain, gambar teknik, manufaktur.",
    "TRIK": "Siswa logis sistem, suka otorisasi, sensor, kendali otomatis.",
    "TP": "Siswa spesifik HVAC, termodinamika aplikasi, instalasi pendingin.",
    "KP": "Siswa empatik, humanis, care-giver, pelayanan langsung pasien.",
    "TLM": "Siswa analitis, suka detail laboratorium, riset penyakit, data medis.",
    "TREM": "Siswa teknis-medis, suka hardware kedokteran, maintenance alat RS.",
    "TI": "Siswa generalis IT, infrastruktur jaringan, admin sistem.",
    "RPL": "Siswa creator, coding logic, problem solver via software.",
    "SIKC": "Siswa visioner, smart city, integrasi data sosial & teknologi.",
    "TRK": "Siswa hardware-software integrator, IoT, embedded system."
}

def kirim_ke_gemini(prodi_nama, tema_jawaban, rank=1):
    """Versi optimized dengan prompt yang lebih detail tapi tetap cepat"""
    
    # Debug: print untuk melihat input
    print(f"\n=== DEBUG AI REQUEST ===")
    print(f"Rank: {rank}")
    print(f"Prodi: {prodi_nama}")
    print(f"Tema: {tema_jawaban[:100]}...")
    
    if rank == 1:
        prompt = f"""Kamu adalah konselor akademik Politeknik Negeri Indramayu.

Seorang siswa mengikuti kuis minat dan menjawab dengan pola berikut:
{tema_jawaban}

Berdasarkan analisis sistem, rekomendasi utama adalah: {prodi_nama}

    TUGAS:
    - Jelaskan **mengapa prodi ini relevan** dengan jawaban yang dipilih (contohkan 1–2 poin).
    - Berikan **saran konkret** tentang hal yang sebaiknya dipelajari atau dikembangkan di prodi ini.
    - Gunakan **gaya Dicoding**: maksimal 2 kalimat, langsung ke inti, tanpa menyebut persentase.
    - Jangan gunakan kata "kamu" berulang. Hindari kalimat klise seperti "sangat cocok".
Format: Langsung jawab tanpa pembukaan. Gunakan bahasa yang ramah dan motivatif."""
    
    else:
        prompt = f"""Berdasarkan pola minat siswa: {tema_jawaban}

Prodi alternatif ke-{rank}: {prodi_nama}

Jelaskan dalam 2 kalimat singkat mengapa prodi ini bisa menjadi pilihan alternatif yang baik untuk siswa ini."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 250,
            "temperature": 0.8,
            "topP": 0.95,
            "topK": 40
        }
    }

    try:
        print(f"Mengirim request ke Gemini...")
        response = requests.post(
            GEMINI_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        print(f"Status code: {response.status_code}")

        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return f"Prodi ini sesuai dengan minat kamu di bidang {prodi_nama.split()[-1].lower()}."

        data = response.json()
        print(f"Response data keys: {data.keys()}")
        
        if "candidates" not in data or not data["candidates"]:
            print(f"No candidates in response")
            return f"Berdasarkan jawaban kamu, prodi ini cocok untuk mengembangkan karir di bidang terkait."

        candidate = data["candidates"][0]
        print(f"Candidate keys: {candidate.keys()}")
        
        parts = candidate.get("content", {}).get("parts") or candidate.get("parts")
        
        if not parts:
            print(f"No parts found")
            return f"Prodi ini sesuai dengan pola minat dan bakat kamu."

        text = parts[0].get("text", "").strip()
        print(f"AI Response: {text[:200]}...")
        
        if not text:
            print(f"Empty text response")
            return f"Berdasarkan evaluasi, prodi ini sangat sesuai dengan profil minat kamu."

        # Batasi maksimal 3 kalimat
        sentences = [s.strip() + "." for s in text.split(".") if s.strip()]
        result = " ".join(sentences[:3])
        print(f"Final result: {result[:200]}...")
        return result

    except requests.Timeout:
        print(f"Request timeout after 15 seconds")
        return f"Prodi ini cocok dengan hasil evaluasi minat kamu di area {prodi_nama.split()[-2].lower() if len(prodi_nama.split()) > 2 else 'teknologi'}."
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return f"Prodi ini sesuai dengan profil dan minat kamu berdasarkan hasil kuis."

# === 4. FUNGSI UTAMA ===
def sistem_rekomendasi_prodi():
    print("\n" + "="*70)
    print("🎓  SISTEM PAKAR REKOMENDASI PRODI - POLITEKNIK NEGERI INDRAMAYU  🎓")
    print("="*70 + "\n")

    jawaban_user = []

    # Pilih jurusan
    print("Pilih Rumpun Jurusan:")
    print("1. Teknik (Mesin, Manufaktur, Pendingin)")
    print("2. Kesehatan (Keperawatan, Medis)")
    print("3. Informatika (Komputer, Software)")
    while True:
        choice = input(">> Masukkan pilihan (1/2/3): ").strip()
        map_j = {"1": "teknik", "2": "kesehatan", "3": "informatika"}
        if choice in map_j:
            jurusan = map_j[choice]
            break
        print("❌ Input salah. Ketik 1, 2, atau 3.")

    # Ambil data soal dan daftar prodi
    semua_soal = DATA_JURUSAN[jurusan]["pertanyaan"]
    prodi_list = DATA_JURUSAN[jurusan]["prodi"]

    # Pilih jumlah pertanyaan: 10, 15, 20
    print(f"\nRumpun '{jurusan.upper()}' memiliki {len(semua_soal)} pertanyaan.")
    print("Pilih jumlah pertanyaan yang ingin dijawab:")
    print("A. 10 soal")
    print("B. 15 soal")
    print("C. 20 soal")
    while True:
        pilih_jumlah = input(">> Pilih (A/B/C): ").strip().upper()
        if pilih_jumlah == "A":
            n_soal = 10
            break
        elif pilih_jumlah == "B":
            n_soal = 15
            break
        elif pilih_jumlah == "C":
            n_soal = 20
            break
        else:
            print("❌ Pilih A, B, atau C.")

    # Cek apakah cukup soal tersedia
    if n_soal > len(semua_soal):
        n_soal = len(semua_soal)
        print(f"⚠️  Hanya tersedia {n_soal} soal. Menggunakan semua soal.")

    # Acak dan ambil n_soal soal tanpa duplikat
    soal_acak = random.sample(semua_soal, n_soal)

    # Inisialisasi skor
    skor = {p: 0 for p in prodi_list}

    # Mulai kuis
    print(f"\n🧠 Mulai kuis {n_soal} soal (acak)...")
    for i, item in enumerate(soal_acak, 1):
        print(f"\n[{i}/{n_soal}] {item['pertanyaan']}")
        opts = item['pilihan']
        for k, v in opts.items():
            print(f"    {k}. {v['text']}")

        # Validasi input jawaban
        while True:
            ans = input("    Jawab (A/B/C/D): ").strip().upper()
            if ans in opts:
                break
            print("    ❌ Harap pilih opsi yang tersedia.")

        # Perbarui skor & tampilkan log
        print(f"    ------------------------------------------------")
        print(f"    📝 LOG PERHITUNGAN BOBOT (Soal {i}):")
        bobot_pilihan = opts[ans]['bobot']
        jawaban_user.append({
            "soal": item['pertanyaan'],
            "pilihan": opts[ans]['text'],
            "bobot": bobot_pilihan
        })
        for p_code in prodi_list:
            tambah = bobot_pilihan.get(p_code, 0)
            skor_lama = skor[p_code]
            skor[p_code] += tambah
            if tambah > 0:
                print(f"    ► {p_code.ljust(5)} : {str(skor_lama).rjust(3)} +{str(tambah).ljust(3)} → Total: {skor[p_code]}")
        print(f"    ------------------------------------------------")
        time.sleep(0.3)

    # Hitung persentase akurasi
    total_skor = sum(skor.values())
    if total_skor == 0:
        print("\n❌ Tidak ada skor terkumpul. Mungkin semua jawaban tidak relevan.")
        return

    hasil_akhir = []
    for p_code, val in skor.items():
        persen = round((val / total_skor) * 100, 1)
        hasil_akhir.append((p_code, persen))
    hasil_akhir.sort(key=lambda x: x[1], reverse=True)

    # Ambil rekomendasi utama
    top_kode, top_persen = hasil_akhir[0]
    top_nama = DATA_JURUSAN[jurusan]["prodi_nama"][top_kode]
    top_link = DATA_JURUSAN[jurusan]["prodi_link"][top_kode]

       # Tampilkan ranking semua prodi (hasil sistem)
    print("\n" + "="*70)
    print("📊 HASIL EVALUASI SISTEM")
    print("="*70)
    for rank, (k, p) in enumerate(hasil_akhir, 1):
        nama_prodi = DATA_JURUSAN[jurusan]["prodi_nama"][k]
        marker = "✅ REKOMENDASI UTAMA" if rank == 1 else ""
        print(f"{rank}. {nama_prodi}\t: {p}% {marker}")

    # Ambil rekomendasi utama
    top_kode, top_persen = hasil_akhir[0]
    top_nama = DATA_JURUSAN[jurusan]["prodi_nama"][top_kode]
    top_link = DATA_JURUSAN[jurusan]["prodi_link"][top_kode]

    # Kirim ke Gemini untuk summary singkat
    print("\n🤖 Menghubungi AI untuk rekomendasi singkat...")
    data_top = {
        "prodi_nama": top_nama,
        "persen": top_persen,
        "link": top_link
    }
    
    # Ringkas jawaban user jadi kalimat naratif (ambil 3 contoh teratas)
    ringkasan_jawaban = "Berdasarkan jawaban kamu: "
    contoh = []
    for jwb in jawaban_user[:3]:  # ambil 3 jawaban pertama
        contoh.append(jwb['pilihan'])
    ringkasan_jawaban += "; ".join(contoh) + "."

    summary = kirim_ke_gemini(jurusan, data_top, ringkasan_jawaban)

    # Potong jadi maks 2 kalimat
    sentences = [s.strip() for s in summary.split(".") if s.strip()]
    short_summary = ". ".join(sentences[:2]) + "."
    if "Kesalahan" in summary or "error" in summary.lower():
        short_summary = "AI sedang sibuk. Tapi tenang, rekomendasi ini sudah sesuai minat dan jawabanmu!"

    # Tampilkan rekomendasi ala Dicoding
    print("\n" + "="*70)
    print("🎓 REKOMENDASI AKADEMIK")
    print("="*70)
    print(f"Berdasarkan hasil evaluasi, kamu paling cocok masuk ke:\n{top_nama}.\n")
    print(short_summary + "\n")
    print("Lihat informasi prodi lengkap di sini:")
    print(top_link)
    print("="*70)

# === FUNGSI PROSES REKOMENDASI (versi API) ===
def proses_rekomendasi_api(jurusan, jawaban_list, n_soal=10):
    if jurusan not in DATA_JURUSAN:
        return {"error": "Jurusan tidak valid."}
    
    semua_soal = DATA_JURUSAN[jurusan]["pertanyaan"]
    prodi_list = DATA_JURUSAN[jurusan]["prodi"]
    soal_acak = random.sample(semua_soal, min(n_soal, len(semua_soal)))
    skor = {p: 0 for p in prodi_list}
    jawaban_user = []
    
    for i, item in enumerate(soal_acak):
        if i >= len(jawaban_list):
            break
        ans = jawaban_list[i].upper()
        if ans not in item["pilihan"]:
            continue
        bobot_pilihan = item["pilihan"][ans]["bobot"]
        jawaban_user.append({
            "soal": item["pertanyaan"],
            "pilihan": item["pilihan"][ans]["text"],
            "bobot": bobot_pilihan
        })
        for p_code in prodi_list:
            skor[p_code] += bobot_pilihan.get(p_code, 0)
    
    total_skor = sum(skor.values())
    if total_skor == 0:
        return {"error": "Tidak ada skor terkumpul."}
    
    hasil_akhir = []
    for p_code, val in skor.items():
        persen = round((val / total_skor) * 100, 1)
        hasil_akhir.append({
            "kode": p_code,
            "nama": DATA_JURUSAN[jurusan]["prodi_nama"][p_code],
            "persen": persen
        })
    hasil_akhir.sort(key=lambda x: x["persen"], reverse=True)
    
    top = hasil_akhir[0]
    # Ambil soal + jawaban spesifik
    # Buat ringkasan spesifik: soal + jawaban
    ringkasan_parts = []
    for jwb in jawaban_user[:3]:
        soal = jwb['soal'].replace('"', "'")  # hindari bentrok quote
        pilihan = jwb['pilihan']
        ringkasan_parts.append(f'"{soal}" → "{pilihan}"')
    ringkasan = "Jawaban kamu mencakup: " + "; ".join(ringkasan_parts) + "."
    ai_summary = kirim_ke_gemini(jurusan, {
        "prodi_nama": top["nama"],
        "link": DATA_JURUSAN[jurusan]["prodi_link"][top["kode"]]
    }, ringkasan)
    
    return {
        "ranking": hasil_akhir,
        "rekomendasi_utama": {
            "kode": top["kode"],
            "nama": top["nama"],
            "link": DATA_JURUSAN[jurusan]["prodi_link"][top["kode"]],
            "summary": ai_summary
        }
    }

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "http://10.0.173.172:5173",
    "http://192.168.153.1:5173",
    "http://192.168.102.1:5173"
])

@app.route("/api/get-questions", methods=["POST"])
def get_questions():
    try:
        data = request.get_json()
        jurusan = data.get("jurusan")
        n_soal = data.get("n_soal", 10)
        
        if jurusan not in DATA_JURUSAN:
            return jsonify({"error": "Jurusan tidak valid."}), 400
        
        semua_soal = DATA_JURUSAN[jurusan]["pertanyaan"]
        soal_acak = random.sample(semua_soal, min(n_soal, len(semua_soal)))
        
        soal_formatted = []
        for item in soal_acak:
            soal_formatted.append({
                "pertanyaan": item["pertanyaan"],
                "pilihan": {k: v["text"] for k, v in item["pilihan"].items()}
            })
        
        return jsonify({"soal": soal_formatted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/rekomendasi", methods=["POST"])
def api_rekomendasi():
    try:
        data = request.get_json()
        jurusan = data.get("jurusan")
        jawaban = data.get("jawaban", [])
        n_soal = data.get("n_soal", 10)
        
        if not jurusan or not isinstance(jawaban, list):
            return jsonify({"error": "Data tidak lengkap."}), 400
        
        if jurusan not in DATA_JURUSAN:
            return jsonify({"error": "Jurusan tidak valid."}), 400
        
        semua_soal = DATA_JURUSAN[jurusan]["pertanyaan"]
        prodi_list = DATA_JURUSAN[jurusan]["prodi"]
        soal_acak = random.sample(semua_soal, min(n_soal, len(semua_soal)))
        skor = {p: 0 for p in prodi_list}
        jawaban_user = []
        
        for i, item in enumerate(soal_acak):
            if i >= len(jawaban):
                break
            ans = jawaban[i].upper()
            if ans not in item["pilihan"]:
                continue
            bobot_pilihan = item["pilihan"][ans]["bobot"]
            jawaban_user.append({
                "soal": item["pertanyaan"],
                "pilihan": item["pilihan"][ans]["text"],
                "bobot": bobot_pilihan
            })
            for p_code in prodi_list:
                skor[p_code] += bobot_pilihan.get(p_code, 0)
        
        total_skor = sum(skor.values())
        if total_skor == 0:
            return jsonify({"error": "Tidak ada skor terkumpul."}), 400
        
        hasil_akhir = []
        for p_code, val in skor.items():
            hasil_akhir.append({
                "kode": p_code,
                "nama": DATA_JURUSAN[jurusan]["prodi_nama"][p_code],
                "link": DATA_JURUSAN[jurusan]["prodi_link"][p_code],
                "skor": val
            })
        hasil_akhir.sort(key=lambda x: x["skor"], reverse=True)
        
        # Generate summary untuk SEMUA prodi dengan detail berbeda
        summaries = []
        
        print(f"\n=== GENERATING SUMMARIES ===")
        print(f"Total jawaban user: {len(jawaban_user)}")
        
        for rank, prodi in enumerate(hasil_akhir, 1):
            # Buat ringkasan jawaban yang lebih deskriptif
            tema_parts = []
            
            # Ambil 3-4 jawaban yang paling relevan
            if len(jawaban_user) >= 3:
                for i, jwb in enumerate(jawaban_user[:4], 1):
                    tema_parts.append(f"- {jwb['pilihan']}")
            else:
                tema_parts.append("Berbagai aspek yang menunjukkan minat di bidang ini")
            
            tema_lengkap = "\n".join(tema_parts)
            
            print(f"\nProdi #{rank}: {prodi['nama']}")
            print(f"Tema: {tema_lengkap[:150]}...")
            
            ai_summary = kirim_ke_gemini(prodi["nama"], tema_lengkap, rank)
            
            summaries.append({
                "rank": rank,
                "nama": prodi["nama"],
                "kode": prodi["kode"],
                "link": prodi["link"],
                "summary": ai_summary
            })
            
            # Jeda kecil antar request untuk menghindari rate limit
            if rank < len(hasil_akhir):
                time.sleep(0.5)
        
        print(f"\n=== SUMMARIES COMPLETED ===")
        return jsonify({"rekomendasi": summaries})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ Polindra Rekomendasi API - Optimized Version!"

if __name__ == "__main__":
    app.run(debug=True, port=5000)