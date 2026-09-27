# 🎓 StudyMate AI

Chatbot edukasi berbasis **Google Gemini**, dibuat sebagai final project pelatihan
*Maju Bareng AI — Data Science Hacktiv8*.

## Use Case

**Study/education assistant** untuk siswa dan mahasiswa di Indonesia — membantu
menjelaskan materi pelajaran, membuat quiz latihan, dan merangkum diskusi belajar.

## Parameter Kreatif

| Parameter | Deskripsi |
|---|---|
| **Gaya bahasa** | Santai (seperti teman) atau Formal (seperti guru/tutor) — mengubah `system_instruction` secara dinamis |
| **Fokus materi** | Umum, Matematika, Bahasa Inggris, Sains, Sejarah, atau Pemrograman |
| **Temperature** | Slider 0.0–1.0 untuk mengatur tingkat kreativitas/variasi jawaban |
| **Memory** | Riwayat percakapan disimpan lewat `st.session_state` + Gemini chat session, jadi bot ingat konteks sebelumnya |
| **Integrasi API eksternal** | Tool `cari_referensi_akademik()` menggunakan Crossref API untuk mencari hingga 3 referensi akademik yang relevan berdasarkan topik pertanyaan |
| **Fitur tambahan** | Tombol aksi cepat: "Jelaskan lebih sederhana", "Buatkan quiz", "Rangkum percakapan" |

## Struktur Proyek

```
.
├── app.py             # Aplikasi Streamlit utama
├── requirements.txt   # Dependencies
├── .env.example       # Template untuk API key (copy jadi .env)
├── .gitignore
└── README.md
```

## Cara Menjalankan

### 1. Lokal

```bash
git clone https://github.com/retnoors/studymate-ai.git
cd studymate-ai
pip install -r requirements.txt
```

**(Opsional, agar tidak perlu mengetik API key tiap run)** — copy `.env.example` jadi `.env`,
lalu isi dengan API key kamu:

```bash
Copy file `.env.example` menjadi `.env`, lalu isi dengan API key kamu:
GOOGLE_API_KEY=key_asli_kamu
```

File `.env` sudah masuk `.gitignore`, jadi key kamu **tidak akan ikut ter-push** ke GitHub.

```bash
streamlit run app.py
```

Browser akan otomatis kebuka di `http://localhost:8501`. Kalau sudah isi `.env`, kotak
API Key di sidebar bakal otomatis terisi. Kalau tidak, tinggal ketik manual di sana.

### 2. Deploy online gratis (Streamlit Community Cloud)

Biar bisa diakses lewat URL publik tanpa harus running di komputer sendiri:

1. Pastikan `app.py` dan `requirements.txt` sudah ke-push ke GitHub (repo public)
2. Buka https://share.streamlit.io → login pakai akun GitHub
3. Klik **New app** → pilih repo kamu → branch `main` → main file path `app.py`
4. Klik **Deploy**

Setelah live, kamu tinggal masukkan API key di sidebar app yang online itu — tidak perlu Colab atau ngrok sama sekali.

## Cara Mendapatkan Google AI API Key

1. Buka https://aistudio.google.com
2. Klik **Get API Key** → **Create API Key**
3. Copy key-nya dan paste ke kotak "Google AI API Key" di sidebar app

## Screenshot
<img width="1919" height="951" alt="image" src="https://github.com/user-attachments/assets/614fcd26-2920-476c-b8d9-e9fe5dabd564" />



