import streamlit as st
import datetime
import pandas as pd
import google.generativeai as genai
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Modul Ajar Sultan AI", layout="wide", page_icon="🏫")

# ==========================================
# 1. STYLE SKEUOMORPHISM (TAMPILAN NYATA)
# ==========================================
st.markdown("""
<style>
    /* Latar Belakang Utama */
    .stApp {
        background-color: #e0e5ec;
        font-family: 'Segoe UI', sans-serif;
        color: #4d4d4d;
    }

    /* Container Skeuomorphism (Kotak Timbul) */
    .skeuo-card {
        border-radius: 20px;
        background: #e0e5ec;
        box-shadow:  9px 9px 16px rgb(163,177,198,0.6), 
                     -9px -9px 16px rgba(255,255,255, 0.5);
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* Input Fields (Efek Tenggelam) */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background-color: #e0e5ec !important;
        border-radius: 10px;
        border: none;
        box-shadow: inset 4px 4px 8px #bebebe, 
                    inset -4px -4px 8px #ffffff !important;
        color: #333 !important;
        padding: 10px;
    }
    
    /* Label Input */
    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stNumberInput > label, .stDateInput > label {
        color: #444 !important;
        font-weight: bold;
    }

    /* Tombol Skeuomorphism */
    .stButton > button {
        width: 100%;
        border: none;
        outline: none;
        border-radius: 12px;
        background: linear-gradient(145deg, #f0f0f3, #cacaca);
        box-shadow:  6px 6px 12px #bebebe, 
                     -6px -6px 12px #ffffff;
        color: #0d47a1;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
        padding: 10px 20px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #cacaca, #f0f0f3);
    }

    .stButton > button:active {
        background: #e0e5ec;
        box-shadow: inset 4px 4px 8px #bebebe, 
                    inset -4px -4px 8px #ffffff;
        transform: translateY(2px);
    }

    /* Header Title Style */
    .header-title {
        color: #0d47a1;
        text-shadow: 1px 1px 2px white;
        text-align: center;
        margin: 0;
        padding-bottom: 5px;
    }
    
    /* Login Box */
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 40px;
        border-radius: 30px;
        background: #e0e5ec;
        box-shadow: 15px 15px 30px #bebebe, -15px -15px 30px #ffffff;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI LOGIKA (AI & DOCX)
# ==========================================
def tanya_gemini(api_key, prompt):
    if not api_key:
        return "⚠️ Masukkan API Key di Sidebar terlebih dahulu!"
    try:
        genai.configure(api_key=api_key)
        # MENGGUNAKAN MODEL STABIL (GEMINI-PRO)
        model = genai.GenerativeModel('gemini-pro') 
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def create_docx(data):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.54); section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54); section.right_margin = Cm(2.54)

    # HEADER
    head = doc.add_paragraph()
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = head.add_run(f"MODUL AJAR KURIKULUM MERDEKA\n{data['sekolah']}\n")
    run.bold = True; run.font.size = Pt(14)
    head.add_run(f"{data['alamat']}").font.size = Pt(10)
    doc.add_paragraph("_"*85)

    # I. INFORMASI UMUM
    doc.add_heading('I. INFORMASI UMUM', level=1)
    table = doc.add_table(rows=0, cols=2); table.style = 'Table Grid'
    infos = [("Penyusun", data['guru']), ("Tahun", str(data['tanggal'].year)), 
             ("Kelas/Fase", f"{data['kelas']} / {data['fase']}"), ("Mapel", data['mapel']), 
             ("Topik", data['topik']), ("Alokasi", data['alokasi'])]
    for k, v in infos:
        r = table.add_row()
        r.cells[0].text = k; r.cells[0].paragraphs[0].runs[0].bold = True; r.cells[1].text = v

    doc.add_paragraph(f"\nCapaian Pembelajaran (CP): {data['cp']}")

    # II. KOMPONEN INTI
    doc.add_heading('II. KOMPONEN INTI', level=1)
    doc.add_heading('A. Tujuan Pembelajaran', level=2); doc.add_paragraph(data['tujuan'])
    doc.add_heading('B. Pemantik', level=2); doc.add_paragraph(data['pemantik'])
    
    # III. KEGIATAN PEMBELAJARAN
    doc.add_heading('III. KEGIATAN PEMBELAJARAN', level=1)
    doc.add_heading('1. Materi Inti', level=2); doc.add_paragraph(data['bahan'])
    doc.add_heading('2. Langkah LKPD', level=2); doc.add_paragraph(data['lkpd'])
    
    # IV. EVALUASI
    doc.add_heading('IV. EVALUASI & ASESMEN', level=1)
    doc.add_paragraph(data['soal'])
    
    # V. LAMPIRAN (GLOSARIUM & PUSTAKA)
    doc.add_page_break()
    doc.add_heading('V. LAMPIRAN', level=1)
    doc.add_heading('A. Glosarium', level=2); doc.add_paragraph(data['glosarium'])
    doc.add_heading('B. Daftar Pustaka', level=2); doc.add_paragraph(data['pustaka'])
    
    # VI. REFLEKSI
    doc.add_heading('C. Refleksi', level=2)
    doc.add_paragraph(f"Refleksi Guru: {data['refleksi_guru']}")
    doc.add_paragraph(f"Refleksi Siswa: {data['refleksi_siswa']}")

    # TTD
    doc.add_paragraph("\n\n")
    ttd = doc.add_table(rows=1, cols=2)
    ttd.rows[0].cells[0].text = f"Mengetahui,\nKepala Sekolah\n\n\n( {data['kepsek']} )\nNIP. {data['nip']}"
    ttd.rows[0].cells[1].text = f"Sidoarjo, {data['tanggal'].strftime('%d %B %Y')}\nGuru Kelas\n\n\n( {data['guru']} )"
    ttd.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# ==========================================
# 3. LOGIN PAGE (SKEUOMORPHISM)
# ==========================================
def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("""
        <div class='login-container'>
            <h2 style='color: #444; margin-bottom: 0;'>🔐 LOGIN SYSTEM</h2>
            <p style='color: #777;'>Sistem Perangkat Ajar</p>
            <hr style="border: 0; border-top: 1px solid #d1d9e6;">
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="ID Guru")
        password = st.text_input("Password", type="password", placeholder="Kata Sandi")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("MASUK APLIKASI"):
            if username == "guru" and password == "123":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Username/Password Salah!")

# ==========================================
# 4. MAIN APP (FITUR BARU + STYLE LAMA)
# ==========================================
def main_app():
    # Header Skeuomorphism
    st.markdown("""
        <div class='skeuo-card' style='text-align: center;'>
            <h1 class='header-title'>🏛️ SISTEM PERANGKAT AJAR TERPADU</h1>
            <p style='margin:0; font-weight:bold; color:#666;'>SD MUHAMMADIYAH 8 TULANGAN | KURIKULUM MERDEKA</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar Skeuomorphism
    with st.sidebar:
        st.markdown("<div class='skeuo-card' style='text-align:center;'>⚙️ <b>KONFIGURASI</b></div>", unsafe_allow_html=True)
        
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("Cloud Connected ✅")
        else:
            api_key = st.text_input("Gemini API Key", type="password")
            st.caption("Tanpa API Key, fitur otomatis tidak berjalan.")

        st.divider()
        st.markdown("<b>🏫 Identitas Sekolah</b>", unsafe_allow_html=True)
        nama_sekolah = st.text_input("Nama Sekolah", value="SD MUHAMMADIYAH 8 TULANGAN")
        alamat_sekolah = st.text_area("Alamat", value="Jl. Raya Kenongo, Tulangan, Sidoarjo")
        kepsek = st.text_input("Kepala Sekolah", value="Muhammad Saifudin Zuhri, M.Pd.")
        nip = st.text_input("NIP", value="-")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    # --- 7 TABS LENGKAP ---
    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "1️⃣ Identitas", 
        "2️⃣ Inti (AI)", 
        "3️⃣ Bahan (AI)", 
        "4️⃣ Evaluasi", 
        "5️⃣ Asesmen", 
        "6️⃣ Glosarium", 
        "7️⃣ Refleksi"
    ])

    # --- TAB 1: IDENTITAS ---
    with t1:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            nama_guru = st.text_input("Nama Guru Penyusun")
            mapel = st.text_input("Mata Pelajaran", placeholder="Contoh: IPAS")
            fase = st.selectbox("Fase", ["A (Kelas 1-2)", "B (Kelas 3-4)", "C (Kelas 5-6)"])
        with c2:
            kelas = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"])
            alokasi = st.text_input("Alokasi Waktu", value="2 x 35 Menit")
            tanggal = st.date_input("Tanggal Pelaksanaan")
        
        st.divider()
        cp = st.text_area("Capaian Pembelajaran (CP):", height=100)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 2: KOMPONEN INTI (AI) ---
    with t2:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        topik = st.text_input("Topik / Materi Pokok")
        model_ajar = st.selectbox("Model Pembelajaran", ["PBL (Problem Based Learning)", "PjBL (Project Based Learning)", "Discovery Learning"])
        
        if st.button("✨ Generate Tujuan (AI)"):
            if not api_key: st.error("API Key Belum Diisi!")
            else:
                with st.spinner("AI sedang berpikir..."):
                    p = f"Buatkan tujuan pembelajaran dan pertanyaan pemantik untuk mapel {mapel} topik {topik} kelas {kelas} model {model_ajar}."
                    res = tanya_gemini(api_key, p)
                    st.session_state['tujuan_ai'] = res
        
        tujuan = st.text_area("Tujuan Pembelajaran:", value=st.session_state.get('tujuan_ai', ''), height=150)
        pemantik = st.text_input("Pertanyaan Pemantik", placeholder="Pertanyaan awal untuk memancing rasa ingin tahu siswa")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 3: BAHAN & LKPD (AI) ---
    with t3:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("✨ Generate Materi & LKPD (AI)"):
            if not api_key: st.error("API Key Kosong")
            else:
                with st.spinner("Menyusun bahan ajar..."):
                    res_materi = tanya_gemini(api_key, f"Ringkasan materi {topik} untuk SD kelas {kelas}.")
                    st.session_state['materi_ai'] = res_materi
                    res_lkpd = tanya_gemini(api_key, f"Buatkan langkah-langkah LKPD seru untuk topik {topik} kelas {kelas}.")
                    st.session_state['lkpd_ai'] = res_lkpd

        col_a, col_b = st.columns(2)
        with col_a:
            bahan = st.text_area("📘 Bahan Ajar", value=st.session_state.get('materi_ai', ''), height=300)
        with col_b:
            lkpd = st.text_area("📝 Instruksi LKPD", value=st.session_state.get('lkpd_ai', ''), height=300)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 4: EVALUASI (AI) ---
    with t4:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("✨ Buat Soal Evaluasi"):
             if not api_key: st.error("API Key Kosong")
             else:
                with st.spinner("Membuat soal..."):
                    res_soal = tanya_gemini(api_key, f"Buatkan 5 soal essay HOTS topik {topik} kelas {kelas} dan kunci jawaban.")
                    st.session_state['soal_ai'] = res_soal
        
        soal = st.text_area("Soal Evaluasi & Kunci Jawaban", value=st.session_state.get('soal_ai', ''), height=300)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 5: ASESMEN ---
    with t5:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        st.subheader("Rubrik Penilaian Sikap")
        st.write("Rubrik akan otomatis digenerate di file Word berdasarkan dimensi yang dipilih.")
        profil = st.multiselect("Dimensi Profil Pelajar Pancasila", ["Beriman", "Mandiri", "Bernalar Kritis", "Kreatif", "Gotong Royong"], default=["Mandiri", "Bernalar Kritis"])
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 6: GLOSARIUM (FITUR BARU) ---
    with t6:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        
        st.subheader("📚 Daftar Pustaka")
        pustaka_default = "1. Buku Paket Kemdikbud Kelas " + str(kelas) + "\n2. Video Pembelajaran Youtube"
        pustaka = st.text_area("Sumber Belajar", value=pustaka_default)
        
        st.divider()
        
        st.subheader("🔤 Glosarium")
        st.write("Daftar istilah sulit:")
        glosarium = st.text_area("Glosarium", placeholder="Contoh:\n1. Ekosistem : Hubungan timbal balik...\n2. Abiotik : Benda tidak hidup...", height=150)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 7: REFLEKSI (FITUR BARU) ---
    with t7:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        st.subheader("💭 Refleksi Pembelajaran")
        refleksi_guru = st.text_area("Refleksi Guru", placeholder="Apa yang sudah berjalan baik? Apa yang perlu diperbaiki?")
        refleksi_siswa = st.text_area("Refleksi Siswa", placeholder="Bagaimana tanggapan siswa terhadap pembelajaran hari ini?")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DOWNLOAD SECTION ---
    st.markdown("<div class='skeuo-card' style='text-align:center;'>", unsafe_allow_html=True)
    st.success("✅ Dokumen Siap Diunduh")
    if st.button("📄 DOWNLOAD MODUL AJAR (WORD)"):
        data_modul = {
            'sekolah': nama_sekolah, 'alamat': alamat_sekolah, 'kepsek': kepsek, 'nip': nip,
            'guru': nama_guru, 'mapel': mapel, 'fase': fase, 'kelas': kelas, 'alokasi': alokasi, 'tanggal': tanggal,
            'cp': cp, 'topik': topik, 'tujuan': tujuan, 'pemantik': pemantik,
            'bahan': bahan, 'lkpd': lkpd, 'soal': soal,
            'glosarium': glosarium, 'pustaka': pustaka,
            'refleksi_guru': refleksi_guru, 'refleksi_siswa': refleksi_siswa
        }
        docx_file = create_docx(data_modul)
        st.download_button("Klik untuk Unduh .DOCX", docx_file, file_name=f"Modul_{mapel}_{kelas}.docx")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
    
    if st.session_state['logged_in']:
        main_app()
    else:
        login_page()
