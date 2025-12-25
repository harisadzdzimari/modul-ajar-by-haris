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
# 1. STYLE SKEUOMORPHISM & UI COMPONENTS
# ==========================================
st.markdown("""
<style>
    /* Mengubah Warna Background Utama */
    .stApp {
        background-color: #e0e5ec;
        font-family: 'Segoe UI', sans-serif;
    }

    /* KELAS CSS KHUSUS SKEUOMORPHISM */
    
    /* Kotak Timbul (Card) */
    .skeuo-card {
        border-radius: 20px;
        background: #e0e5ec;
        box-shadow:  9px 9px 16px rgb(163,177,198,0.6), 
                    -9px -9px 16px rgba(255,255,255, 0.5);
        padding: 25px;
        margin-bottom: 20px;
        color: #4d4d4d;
    }

    /* Style Input Fields (Efek Tenggelam/Engraved) */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div {
        background-color: #e0e5ec !important;
        border-radius: 10px;
        border: none;
        box-shadow: inset 4px 4px 8px #bebebe, 
                    inset -4px -4px 8px #ffffff !important;
        color: #333 !important;
        padding: 10px;
    }
    
    /* Label Input */
    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stDateInput > label {
        color: #444 !important;
        font-weight: bold;
    }

    /* Style Tombol (Timbul & Efek Tekan) */
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
    
    .stButton > button:active {
        background: #e0e5ec;
        box-shadow: inset 4px 4px 8px #bebebe, 
                    inset -4px -4px 8px #ffffff;
        transform: translateY(2px);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #e0e5ec;
        border-right: 1px solid #d1d9e6;
    }

    /* HEADER & FOOTER CUSTOM */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #e0e5ec;
        padding: 15px 20px;
        border-radius: 15px;
        box-shadow:  5px 5px 10px #bebebe, -5px -5px 10px #ffffff;
        margin-bottom: 25px;
        border: 1px solid #ffffff;
    }
    
    .running-text {
        width: 70%;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        color: #2c3e50;
        font-size: 16px;
    }
    
    .live-clock {
        width: 25%;
        text-align: right;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #0d47a1;
        background: #e0e5ec;
        padding: 5px 15px;
        border-radius: 8px;
        box-shadow: inset 3px 3px 6px #bebebe, inset -3px -3px 6px #ffffff;
    }

    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #e0e5ec;
        color: #555;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0px -4px 10px rgba(0,0,0,0.1);
        z-index: 999;
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
# 2. LOGIKA HEADER & CLOCK (JS)
# ==========================================
def render_header():
    st.markdown("""
        <div class="header-container">
            <div class="running-text">
                <marquee direction="left" scrollamount="6">
                    🚀 SELAMAT DATANG DI SISTEM MODUL AJAR SULTAN AI - SD MUHAMMADIYAH 8 TULANGAN - "Mewujudkan Generasi Cerdas & Berakhlak Mulia" 🚀
                </marquee>
            </div>
            <div id="clock" class="live-clock">Loading...</div>
        </div>
        
        <script>
            function updateTime() {
                const now = new Date();
                const optionsDate = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                const dateStr = now.toLocaleDateString('id-ID', optionsDate);
                const timeStr = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                
                document.getElementById('clock').innerHTML = dateStr + '<br>' + timeStr + ' WIB';
            }
            setInterval(updateTime, 1000);
            updateTime();
        </script>
        
        <div class="footer">
            Aplikasi By Haris Adz Dzimari &copy; 2025 | Sultan AI Pro v2.0
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. FUNGSI LOGIKA (TETAP SAMA)
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
        r.cells[0].text = k; r.cells[0].paragraphs[0].runs[0].bold = True; r.cells[1].text = v

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
# 4. HALAMAN LOGIN
# ==========================================
def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
        <div class='login-container'>
            <h2 style='color: #444; margin-bottom: 0;'>🔐 LOGIN</h2>
            <p style='color: #777;'>Sistem Perangkat Ajar</p>
            <hr style="border: 0; border-top: 1px solid #d1d9e6;">
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Masukkan ID Guru")
        password = st.text_input("Password", type="password", placeholder="Masukkan Kata Sandi")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("MASUK SISTEM", type="primary", use_container_width=True):
            if username == "guru" and password == "123":
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = "Guru Hebat"
                st.rerun()
            elif username == "admin" and password == "admin":
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = "Administrator"
                st.rerun()
            else:
                st.error("Username / Password Salah! (Coba: guru / 123)")

# ==========================================
# 5. APLIKASI UTAMA
# ==========================================
def main_app():
    # Render Header Berjalan & Jam
    render_header()

    # Judul Halaman dalam Card Skeuomorphism
    st.markdown("""
        <div class='skeuo-card' style='text-align: center;'>
            <h1 style='color: #0d47a1; margin:0; text-shadow: 1px 1px 2px #fff;'>💎 SULTAN AI PRO</h1>
            <p style='margin:0; font-weight:bold;'>Generator Modul Ajar (Skeuomorphism Edition)</p>
        </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<div class='skeuo-card' style='text-align:center;'>👤 Login: <b>{st.session_state.get('user_name', 'Guru')}</b></div>", unsafe_allow_html=True)
        
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.divider()
        st.header("🤖 Konfigurasi AI")
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ Terhubung (Cloud)")
        else:
            api_key = st.text_input("Gemini API Key", type="password")
            st.info("💡 Masukkan API Key Manual")

        st.divider()
        st.header("⚙️ Data Sekolah")
        uploaded_logo = st.file_uploader("Upload Logo", type=['png', 'jpg'])
        nama_sekolah = st.text_input("Nama Sekolah", value="SD MUHAMMADIYAH 8 TULANGAN")
        alamat_sekolah = st.text_area("Alamat", value="Jl. Raya Kenongo RT. 02 RW. 01 Tulangan Sidoarjo")
        kepsek = st.text_input("Kepala Sekolah", value="MUHAMMAD SAIFUDIN ZUHRI, M.Pd.")
        nip_kepsek = st.text_input("NIP/NBM", value="-")

    # --- TABS ---
    t1, t2, t3, t4, t5 = st.tabs(["1️⃣ Identitas", "2️⃣ Inti (AI)", "3️⃣ Bahan (AI)", "4️⃣ Asesmen", "5️⃣ 📥 DOWNLOAD"])

    with t1:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            nama_guru = st.text_input("Nama Guru", placeholder="Nama Lengkap & Gelar")
            mapel = st.text_input("Mapel", placeholder="Contoh: IPAS")
            fase = st.selectbox("Fase", ["Fase A", "Fase B", "Fase C"])
        with c2:
            kelas = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"])
            tanggal = st.date_input("Tanggal", datetime.date.today())
            alokasi = st.text_input("Alokasi Waktu", value="2 JP (2 x 35 Menit)")
        
        st.markdown("<hr style='border-top: 1px solid #d1d9e6;'>", unsafe_allow_html=True)
        cp_text = st.text_area("Capaian Pembelajaran (CP):", height=80, placeholder="Salin CP dari dokumen resmi...")
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        topik = st.text_input("Topik / Bab", placeholder="Contoh: Rantai Makanan")
        model = st.selectbox("Model Pembelajaran", ["Deep Learning", "PjBL", "PBL", "Discovery Learning", "Inquiry"])
        
        c_ai, c_res = st.columns([1, 3])
        with c_ai:
            st.write("") 
            st.write("") 
            if st.button("✨ Auto Tujuan"):
                if not topik: st.warning("Isi Topik!")
                else:
                    with st.spinner("AI Sedang Berpikir..."):
                        p = f"Buatkan 3 Tujuan Pembelajaran mapel {mapel} topik {topik} kelas {kelas} model {model}."
                        st.session_state['tujuan_val'] = tanya_gemini(api_key, p)
        with c_res:
            tujuan = st.text_area("Tujuan Pembelajaran:", value=st.session_state.get('tujuan_val', ''), height=100)
            
        pemantik = st.text_input("Pertanyaan Pemantik")
        dimensi = st.multiselect("Profil Pelajar:", ["Keimanan", "Kewargaan", "Bernalar Kritis", "Kreativitas", "Kolaborasi", "Kemandirian"], default=["Bernalar Kritis", "Kolaborasi"])
        
        st.markdown("<hr style='border-top: 1px solid #d1d9e6;'>", unsafe_allow_html=True)
        c_dif1, c_dif2 = st.columns(2)
        with c_dif1: remedial = st.text_area("Remedial:", value="Pendampingan individu.", height=60)
        with c_dif2: pengayaan = st.text_area("Pengayaan:", value="Tugas proyek tambahan.", height=60)
        st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("✨ Auto Materi & Soal"):
            if not topik: st.warning("Isi Topik!")
            else:
                with st.spinner("AI Menulis..."):
                    st.session_state['materi_val'] = tanya_gemini(api_key, f"Ringkasan materi {topik} SD kelas {kelas}.")
                    st.session_state['soal_val'] = tanya_gemini(api_key, f"5 soal essay {topik} dan kunci jawaban.")
        
        bahan = st.text_area("Materi Singkat:", value=st.session_state.get('materi_val', ''), height=150)
        lkpd_instruksi = st.text_area("Instruksi LKPD:")
        soal = st.text_area("Soal & Kunci:", value=st.session_state.get('soal_val', ''), height=150)
        st.markdown("</div>", unsafe_allow_html=True)

    with t4:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        st.info("📊 Tabel Rubrik Penilaian akan otomatis dibuat di file Word.")
        df_rubrik = pd.DataFrame({"Dimensi": dimensi, "Kriteria": ["Membudaya (Skor 4)" for _ in dimensi]})
        st.table(df_rubrik)
        st.markdown("</div>", unsafe_allow_html=True)

    with t5:
        st.markdown("<div class='skeuo-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.success("✅ Dokumen Siap Diunduh")
        
        data_modul = {
            'logo': uploaded_logo, 'sekolah': nama_sekolah, 'alamat': alamat_sekolah, 'kepsek': kepsek, 'nip': nip_kepsek,
            'guru': nama_guru, 'tanggal': tanggal, 'fase': fase, 'kelas': kelas, 'mapel': mapel, 'alokasi': alokasi,
            'cp': cp_text, 'topik': topik, 'model': model, 'tujuan': tujuan, 'pemantik': pemantik,
            'dimensi': dimensi, 'bahan': bahan, 'lkpd': lkpd_instruksi, 'soal': soal
        }

        col_w, col_p = st.columns(2)
        with col_w:
            if st.button("📄 DOWNLOAD WORD (.DOCX)"):
                if not nama_guru or not topik: st.error("Lengkapi Data!")
                else:
                    docx = create_docx(data_modul)
                    st.download_button("⬇️ Simpan Word", docx, f"Modul_{topik}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with col_p:
            if st.button("📕 DOWNLOAD PDF"):
                if not nama_guru or not topik: st.error("Lengkapi Data!")
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
