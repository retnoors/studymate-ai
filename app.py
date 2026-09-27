"""
StudyMate AI — Chatbot Edukasi Berbasis Gemini
================================================
Final Project - Pelatihan Maju Bareng AI Data Science Hacktiv8

Use case: Study/education assistant untuk siswa & mahasiswa Indonesia.

Parameter kreatif yang diimplementasikan:
- Gaya bahasa (Santai / Formal)  -> mengubah system_instruction secara dinamis
- Fokus materi (domain pengetahuan tertentu)
- Temperature (tingkat kreativitas jawaban)
- Memory percakapan (st.session_state + Gemini chat session)
- Integrasi API eksternal (Crossref) sebagai tool pencari referensi akademik
- Fitur tambahan: quick-action buttons (jelaskan lebih sederhana, buat quiz, rangkum)
"""

import os
import time
import requests
import streamlit as st
from google import genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="StudyMate AI", page_icon="🎓")


# ── 0. Tool: Integrasi API Eksternal (Crossref) ───────────────────────────
def cari_referensi_akademik(topik: str) -> str:
    """Mencari referensi akademik (jurnal/paper ilmiah) yang relevan dengan sebuah topik lewat Crossref API.

    Gunakan fungsi ini setiap kali user menanyakan fakta, definisi, tokoh,
    peristiwa, atau topik pengetahuan umum yang butuh referensi ilmiah yang
    bisa dicitasi secara formal — bukan hanya mengandalkan ingatan model.

    Args:
        topik: kata kunci atau nama topik yang ingin dicari referensi akademiknya.

    Returns:
        Daftar hingga 3 referensi akademik (judul, penulis, jurnal, tahun, link DOI)
        yang paling relevan dengan topik.
    """
    print(f" - TOOL CALL: cari_referensi_akademik('{topik}')")
    try:
        response = requests.get(
            "https://api.crossref.org/works",
            params={"query": topik, "rows": 3},
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get("message", {}).get("items", [])

        if not items:
            return f"Tidak ditemukan referensi akademik untuk topik '{topik}'."

        hasil = []
        for item in items:
            judul = item.get("title", ["(tanpa judul)"])[0]
            penulis_list = item.get("author", [])
            penulis = ", ".join(
                f"{p.get('given', '')} {p.get('family', '')}".strip()
                for p in penulis_list[:3]
            ) or "Penulis tidak diketahui"
            jurnal = item.get("container-title", ["-"])[0] if item.get("container-title") else "-"
            tahun = item.get("published", {}).get("date-parts", [[None]])[0][0] or "-"
            doi = item.get("DOI", "")
            link = f"https://doi.org/{doi}" if doi else "-"
            hasil.append(f"- {judul} ({penulis}, {jurnal}, {tahun}) — {link}")

        return "\n".join(hasil)
    except Exception as e:
        return f"Terjadi error saat mencari referensi akademik: {e}"


# ── 1. Header ──────────────────────────────────────────────────────────────
st.title("🎓 StudyMate AI")
st.caption(
    "Asisten belajar berbasis Google Gemini — atur gaya bahasa dan fokus materi "
    "sesuai kebutuhanmu di sidebar, lalu mulai bertanya!"
)

# ── 2. Sidebar: Pengaturan & Parameter Kreatif ───────────────────────────────
with st.sidebar:
    st.subheader("Pengaturan")

    google_api_key = st.text_input(
        "Google AI API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),  # auto-isi dari .env kalau ada
    )

    st.markdown("---")
    st.subheader("Parameter Kreatif")

    gaya_bahasa = st.selectbox("Gaya Bahasa", ["Santai", "Formal"])

    fokus_materi = st.selectbox(
        "Fokus Materi",
        ["Umum", "Matematika", "Bahasa Inggris", "Sains", "Sejarah", "Pemrograman"],
    )

    kreativitas = st.slider(
        "Tingkat Kreativitas (temperature)", 0.0, 1.0, 0.4, 0.1,
        help="Nilai rendah = jawaban lebih konsisten/faktual. Nilai tinggi = jawaban lebih variatif."
    )

    st.markdown("---")
    reset_button = st.button("Reset Percakapan", help="Hapus riwayat chat dan mulai dari awal")

    st.markdown("---")
    st.caption("🔎 Terintegrasi dengan Wikipedia API untuk jawaban berbasis fakta")

# ── 3. Validasi API Key ───────────────────────────────────────────────────
if not google_api_key:
    st.info("Masukkan Google AI API Key di sidebar untuk mulai chat.", icon="🔑")
    st.caption("Belum punya API key? Dapatkan gratis di https://aistudio.google.com")
    st.stop()

# ── 4. System instruction dinamis berdasarkan pilihan user ───────────────
GAYA_BAHASA_MAP = {
    "Santai": (
        "Gunakan bahasa Indonesia yang santai, ramah, dan hangat seperti teman sebaya yang "
        "sedang membantu belajar. Boleh sesekali pakai emoji secukupnya, tapi tetap jelas."
    ),
    "Formal": (
        "Gunakan bahasa Indonesia yang formal, sopan, dan terstruktur, seperti guru atau "
        "tutor profesional. Hindari singkatan gaul dan emoji."
    ),
}

SYSTEM_INSTRUCTION = f"""
Kamu adalah StudyMate AI, asisten belajar untuk siswa dan mahasiswa di Indonesia.

Gaya bicara: {GAYA_BAHASA_MAP[gaya_bahasa]}

Fokus materi utama kamu saat ini: {fokus_materi}.
- Jika user bertanya hal di luar topik akademik/belajar, tetap jawab dengan ramah,
  lalu arahkan kembali ke topik belajar.
- Kamu punya akses ke tool cari_referensi_akademik untuk mencari referensi
  jurnal/paper ilmiah yang bisa dicitasi secara formal. Gunakan tool ini kalau
  pertanyaan user butuh referensi akurat, jangan hanya mengarang dari ingatanmu.
- Selalu berikan penjelasan yang mudah dipahami, gunakan analogi atau contoh konkret
  bila memungkinkan.
- Jika diminta membuat quiz, buat 3-5 soal pilihan ganda beserta kunci jawaban di
  bagian akhir (jangan taruh kunci jawaban di tengah soal).
- Jika diminta merangkum, gunakan format bullet points yang ringkas.
- Jujur kalau tidak yakin dengan suatu jawaban, jangan mengarang informasi.
"""

# Memory dan konfigurasi chatbot
config_key = f"{google_api_key}|{gaya_bahasa}|{fokus_materi}|{kreativitas}"

if ("genai_client" not in st.session_state) or (st.session_state.get("_config_key") != config_key):
    try:
        st.session_state.genai_client = genai.Client(api_key=google_api_key)
        st.session_state._config_key = config_key
        st.session_state.chat = st.session_state.genai_client.chats.create(
            model="gemini-3.7-flash",
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "temperature": kreativitas,
                "tools": [cari_referensi_akademik],  # daftarkan tool integrasi API eksternal
            },
        )

        st.session_state.messages = []
    except Exception as e:
        st.error(f"API Key tidak valid atau terjadi error saat inisialisasi: {e}")
        st.stop()

# ── 5. Tombol Reset ───────────────────────────────────────────────────────
if reset_button:
    st.session_state.pop("chat", None)
    st.session_state.pop("messages", None)
    st.session_state.pop("_config_key", None)
    st.rerun()

# ── 6. Tampilkan riwayat percakapan ───────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 7. Fitur tambahan: Quick Action Buttons ───────────────────────────────
st.markdown("**Aksi cepat:**")
col1, col2, col3 = st.columns(3)
quick_prompt = None

with col1:
    if st.button("💡 Jelaskan lebih sederhana", use_container_width=True):
        quick_prompt = (
            "Tolong jelaskan ulang jawaban terakhirmu dengan lebih sederhana, "
            "seolah-olah menjelaskan ke anak SD."
        )
with col2:
    if st.button("📝 Buatkan quiz", use_container_width=True):
        quick_prompt = (
            "Buatkan quiz singkat (3-5 soal pilihan ganda) dari materi yang baru saja "
            "kita bahas, lengkap dengan kunci jawaban di bagian akhir."
        )
with col3:
    if st.button("📌 Rangkum percakapan", use_container_width=True):
        quick_prompt = (
            "Rangkum poin-poin penting dari percakapan kita sejauh ini dalam bentuk "
            "bullet points singkat."
        )

# ── 8. Input chat biasa ────────────────────────────────────────────────────
prompt = st.chat_input("Tanyakan sesuatu tentang materi belajarmu...")

final_prompt = quick_prompt or prompt

if final_prompt:
    # Tampilkan & simpan pesan user
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    answer = None
    max_retries = 3

    # Kirim ke Gemini dengan Auto-Retry jika terkena error 503 (server sibuk)
    with st.chat_message("assistant"):
        with st.spinner("Sedang berpikir..."):
            for attempt in range(max_retries):
                try:
                    response = st.session_state.chat.send_message(final_prompt)
                    answer = response.text if hasattr(response, "text") else str(response)
                    break
                except Exception as e:
                    err_msg = str(e)
                    if ("503" in err_msg or "UNAVAILABLE" in err_msg) and attempt < max_retries - 1:
                        time.sleep(2)  # Tunggu 2 detik lalu coba lagi otomatis
                        continue

                    # Jika tetap gagal setelah retry
                    st.error(
                        "⚠️ Server Gemini sedang sangat sibuk (Error 503). "
                        "Silakan coba klik tombol atau kirim pesanmu lagi dalam beberapa detik!"
                    )
                    # Hapus pesan user terakhir agar riwayat memory chat tidak rusak
                    st.session_state.messages.pop()
                    break

        if answer:
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})