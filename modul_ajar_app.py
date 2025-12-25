import streamlit as st
import datetime
import time
import pandas as pd
import google.generativeai as genai
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
import streamlit.components.v1 as components

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sultan AI - Skeuomorphism", layout="wide", page_icon="🏫")

# ==========================================
# 1. STYLE SKEUOMORPHISM (TAMPILAN NYATA)
# ==========================================
st.markdown("""
<style>
    /* Latar Belakang Utama */
    .stApp {
        background-color: #e0e5ec;
        color: #4d4d4d;
    }

    /* Container Skeuomorphism (Kotak Timbul) */
    .skeuo-box {
        border-radius: 20px;
        background: #e0e5ec;
        box-shadow:  9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5);
        padding: 25px;
        margin-bottom: 20px;
    }

    /* Header Bar */
    .header-bar {
        border-radius: 15px;
        background: #e0e5ec;
        box-shadow: inset 5px 5px 10px #bebebe, inset -5px -5px 10px #ffffff;
        padding: 15px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #d1d9e6;
    }

    /* Tombol Skeuomorphism */
    .stButton>button {
        width: 100%;
        border: none;
        border-radius: 10px;
        background: linear-gradient(145deg, #f0f0f3, #cacaca);
        box-shadow:  5px 5px 10px #bebebe, -5px -5px 10px #ffffff;
        color: #444;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    
    /* Efek Tombol Ditekan */
    .stButton>button:active {
        background: #e0e5ec;
        box-shadow: inset 5px 5px 10px #bebebe, inset -5px -5px 10px #ffffff;
    }

    /* Input Fields (Tenggelam) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #e0e5ec;
        border-radius: 10px;
        border: none;
        box-shadow: inset 3px 3px 6px #bebebe, inset -3px -3px 6px #ffffff;
        color: #333;
    }
    
    /* Login Box Spesifik */
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 40px;
        border-radius: 30px;
        background: #e0e5ec;
        box-shadow: 15px 15px 30px #bebebe, -15px -15px 30px #ffffff;
        text-align: center;
    }

    /* Footer */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #e0e5ec;
        box-shadow: 0px -5px 10px rgba(0,0,0,0.1);
        color: #555;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI LOGIKA (AI, DOCX, PDF) - TETAP
# ==========================================

def tanya_gemini(api_key, prompt):
    if not api_key:
        return "⚠️ Masukkan API Key di Sidebar terlebih dahulu!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def create_docx(data):
    doc = Document()
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.54); section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54); section.right_margin = Cm(2.54)

    if data['logo'] is not None:
        try: doc.add_picture(data['logo'], width=Inches(0.8))
        except: pass

    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header.add_run(f"MODUL AJAR KURIKULUM MERDEKA\n{data['sekolah']}\n")
    run.bold = True; run.font.size = Pt(14)
    header.add_run(f"{data['alamat']}").font.size = Pt(10)
    doc.add_paragraph("_"*85)

    doc.add_heading('I. INFORMASI UMUM', level=1)
    table = doc.add_table(rows=0, cols=2)
    table.style = 'Table Grid'
    infos = [("Penyusun", data['guru']), ("Tahun", str(data['tanggal'].year)), 
             ("Jenjang/Kelas", f"SD / {data['kelas']} ({data['fase']})"), 
             ("Mata Pelajaran", data['mapel']), ("Topik", data['topik']), 
             ("Alokasi Waktu", data['alokasi']), ("Model", data['model'])]
    
    for k, v in infos:
        r = table.add_row()
        r.cells[0].text = k
        r.cells[0].paragraphs[0].runs[0].bold = True
        r.cells[1].text = v

    doc.add_paragraph(f"\nCapaian Pembelajaran (CP): {data['cp']}")
    doc.add_paragraph(f"Profil Pelajar: {', '.join(data['dimensi'])}")

    doc.add_heading('II. KOMPONEN INTI', level=1)
    doc.add_heading('A. Tujuan Pembelajaran', level=2); doc.add_paragraph(data['tujuan'])
    doc.add_heading('B. Pemantik', level=2); doc.add_paragraph(data['pemantik'])
    
    doc.add_page_break()
    doc.add_heading('III. LAMPIRAN', level=1)
    doc.add_heading('1. Bahan Ajar', level=2); doc.add_paragraph(data['bahan'])
    doc.add_heading('2. LKPD', level=2); doc.add_paragraph(data['lkpd'])
    doc.add_heading('3. Soal Evaluasi', level=2); doc.add_paragraph(data['soal'])
    
    doc.add_heading('4. Rubrik Penilaian Sikap', level=2)
    t_rubrik = doc.add_table(rows=1, cols=5); t_rubrik.style = 'Table Grid'
    hdr = t_rubrik.rows[0].cells
    for i, h in enumerate(['Dimensi', 'Sangat Baik (4)', 'Baik (3)', 'Cukup (2)', 'Kurang (1)']):
        hdr[i].text = h; hdr[i].paragraphs[0].runs[0].bold = True
    for dim in data['dimensi']:
        row = t_rubrik.add_row().cells
        row[0].text = dim; row[1].text = "Membudaya"; row[2].text = "Berkembang"; row[3].text = "Mulai Terlihat"; row[4].text = "Belum Terlihat"

    doc.add_paragraph("\n\n")
    ttd = doc.add_table(rows=1, cols=2)
    ttd.rows[0].cells[0].text = f"Mengetahui,\nKepala Sekolah\n\n\n( {data['kepsek']} )\nNIP. {data['nip']}"
    ttd.rows[0].cells[1].text = f"Sidoarjo, {data['tanggal'].strftime('%d %B %Y')}\nGuru Mata Pelajaran\n\n\n( {data['guru']} )"
    ttd.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'MODUL AJAR KURIKULUM MERDEKA', 0, 1, 'C')
        self.ln(5)

def create_pdf(data):
    pdf = PDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Sekolah: {data['sekolah']}", ln=True)
    pdf.cell(0, 10, f"Guru: {data['guru']} | Kelas: {data['kelas']}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 7, f"Topik: {data['topik']}\nTujuan: {data['tujuan']}")
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "Bahan Ajar Ringkas:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, data['bahan'])
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 7, "*Catatan: Download versi Word (.docx) untuk melihat tabel penilaian lengkap.")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ==========================================
# 3. HEADER & FOOTER KHUSUS (JS Injection)
# ==========================================
def render_header_footer():
    # Menampilkan Header Berjalan & Jam Digital via HTML/JS
    st.markdown("""
        <div class="header-bar">
            <div style="width: 70%; font-family: monospace; font-size: 16px; color: #333;">
                <marquee direction="left">
                    🚀 Selamat Datang di Sistem Modul Ajar Sultan AI - SD Muhammadiyah 8 Tulangan - "Mewujudkan Generasi Cerdas & Berakhlak"
                </marquee>
            </div>
            <div id="clock" style="width: 25%; text-align: right; font-weight: bold; font-family: sans-serif; color: #0d47a1;">
                Loading Time...
            </div>
        </div>
        
        <script>
            function updateClock() {
                var now = new Date();
                var d = now.toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
                var t = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                var clockDiv = document.getElementById("clock");
                if (clockDiv) {
                    clockDiv.innerHTML = d + " | " + t + " WIB";
                }
            }
            setInterval(updateClock, 1000);
            updateClock();
        </script>
        
        <div class="footer">
            Aplikasi By Haris Adz Dzimari &copy; 2025 | Sultan AI Pro
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. HALAMAN LOGIN
# ==========================================
def login_page():
    # Header kosong untuk layout
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <h2 style="color:#444; margin-bottom: 0;">🔐 LOGIN</h2>
            <p style="color:#777;">Sistem Perangkat Ajar</p>
            <hr style="border-top: 1px solid #d1d9e6;">
        </div>
        """, unsafe_allow_html=True)
        
        # Input form (tampilannya sudah diubah lewat CSS di atas)
        username = st.text_input("Username", placeholder="ID Guru")
        password = st.text_input("Password", type="password", placeholder="Kata Sandi")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("MASUK SISTEM", use_container_width=True):
            if username == "guru" and password == "123":
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = "Guru Hebat"
                st.rerun()
            elif username == "admin" and password == "admin":
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = "Administrator"
                st.rerun()
            else:
                st.error("Username/Password Salah!")

# ==========================================
# 5. APLIKASI UTAMA
# ==========================================
def main_app():
    # Panggil Header Berjalan
    render_header_footer()

    # Judul Utama dalam Box Skeuomorphism
    st.markdown("""
        <div class="skeuo-box" style="text-align: center;">
            <h1 style="color: #0d47a1; margin:0;">💎 SULTAN AI PRO</h1>
            <p style="margin:0;">Generator Modul Ajar (Skeuomorphism Edition)</p>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<div class='skeuo-box'>👤 User: <b>{st.session_state.get('user_name', 'Guru')}</b></div>", unsafe_allow_html=True)
        if st.button("Logout"): 
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.divider()
        st.header("🤖 Konfigurasi AI")
        
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ Terhubung Cloud")
        else:
            api_key = st.text_input("API Key", type="password", placeholder="Isi API Key...")

        st.divider()
        st.header("⚙️ Data Sekolah")
        uploaded_logo = st.file_uploader("Logo", type=['png','jpg'])
        nama_sekolah = st.text_input("Sekolah", value="SD MUHAMMADIYAH 8 TULANGAN")
        alamat_sekolah = st.text_area("Alamat", value="Jl. Raya Kenongo RT. 02 RW. 01 Tulangan Sidoarjo")
        kepsek = st.text_input("Kepala Sekolah", value="MUHAMMAD SAIFUDIN ZUHRI, M.Pd.")
        nip_kepsek = st.text_input("NIP", value="-")

    # TABS MENU
    t1, t2, t3, t4, t5 = st.tabs(["1️⃣ Identitas", "2️⃣ Inti (AI)", "3️⃣ Bahan (AI)", "4️⃣ Asesmen", "5️⃣ 📥 DOWNLOAD"])

    with t1:
        st.markdown("<div class='skeuo-box'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            nama_guru = st.text_input("Nama Guru", placeholder="Nama Lengkap")
            mapel = st.text_input("Mapel", placeholder="Contoh: IPAS")
            fase = st.selectbox("Fase", ["Fase A", "Fase B", "Fase C"])
        with c2:
            kelas = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"])
            tanggal = st.date_input("Tanggal", datetime.date.today())
            alokasi = st.text_input("Alokasi Waktu", value="2 JP")
        
        st.divider()
        cp_text = st.text_area("Capaian Pembelajaran (CP):", placeholder="Paste CP di sini...")
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='skeuo-box'>", unsafe_allow_html=True)
        topik = st.text_input("Topik Materi")
        model = st.selectbox("Model Pembelajaran", ["Deep Learning", "PjBL", "PBL", "Discovery"])
        
        c_btn, c_tp = st.columns([1,3])
        with c_btn:
            st.write("") 
            st.write("") 
            if st.button("✨ Auto Tujuan"):
                if not topik: st.warning("Isi Topik!")
                else:
                    with st.spinner("AI Bekerja..."):
                        p = f"Buatkan tujuan pembelajaran {mapel} topik {topik} kelas {kelas} model {model}."
                        st.session_state['tujuan'] = tanya_gemini(api_key, p)
        with c_tp:
            tujuan = st.text_area("Tujuan Pembelajaran:", value=st.session_state.get('tujuan', ''))
        
        pemantik = st.text_input("Pertanyaan Pemantik")
        dimensi = st.multiselect("Profil Pelajar:", ["Beriman", "Mandiri", "Bernalar Kritis", "Kreatif", "Gotong Royong"], default=["Bernalar Kritis"])
        st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        st.markdown("<div class='skeuo-box'>", unsafe_allow_html=True)
        if st.button("✨ Auto Materi & Soal"):
            if not topik: st.warning("Isi Topik!")
            else:
                with st.spinner("AI Menulis..."):
                    st.session_state['bahan'] = tanya_gemini(api_key, f"Ringkasan materi {topik} SD kelas {kelas}.")
                    st.session_state['soal'] = tanya_gemini(api_key, f"5 soal essay {topik} beserta kunci jawaban.")
        
        bahan = st.text_area("Bahan Ajar:", value=st.session_state.get('bahan', ''), height=150)
        lkpd = st.text_area("Instruksi LKPD:")
        soal = st.text_area("Soal & Kunci:", value=st.session_state.get('soal', ''), height=150)
        st.markdown("</div>", unsafe_allow_html=True)

    with t4:
        st.markdown("<div class='skeuo-box'>", unsafe_allow_html=True)
        st.info("📊 Rubrik Penilaian otomatis dibuat di file Word.")
        st.table(pd.DataFrame({"Dimensi": dimensi, "Kriteria": ["Membudaya" for _ in dimensi]}))
        st.markdown("</div>", unsafe_allow_html=True)

    with t5:
        st.markdown("<div class='skeuo-box' style='text-align:center;'>", unsafe_allow_html=True)
        st.success("✅ Dokumen Siap Diunduh")
        
        data_modul = {
            'logo': uploaded_logo, 'sekolah': nama_sekolah, 'alamat': alamat_sekolah, 'kepsek': kepsek, 'nip': nip_kepsek,
            'guru': nama_guru, 'tanggal': tanggal, 'fase': fase, 'kelas': kelas, 'mapel': mapel, 'alokasi': alokasi,
            'cp': cp_text, 'topik': topik, 'model': model, 'tujuan': tujuan, 'pemantik': pemantik,
            'dimensi': dimensi, 'bahan': bahan, 'lkpd': lkpd, 'soal': soal
        }

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 DOWNLOAD WORD (.DOCX)"):
                if not nama_guru or not topik: st.error("Data Belum Lengkap")
                else:
                    docx = create_docx(data_modul)
                    st.download_button("⬇️ Simpan Word", docx, f"Modul_{topik}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with col2:
            if st.button("📕 DOWNLOAD PDF"):
                if not nama_guru or not topik: st.error("Data Belum Lengkap")
                else:
                    pdf = create_pdf(data_modul)
                    st.download_button("⬇️ Simpan PDF", pdf, f"Modul_{topik}.pdf", "application/pdf")
        st.markdown("</div>", unsafe_allow_html=True)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login_page()
    else:
        main_app()
