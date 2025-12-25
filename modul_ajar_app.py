import streamlit as st
import datetime
import pandas as pd
import google.generativeai as genai
from io import BytesIO
import tempfile
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Modul Ajar Sultan AI", layout="wide", page_icon="🏫")

# ==========================================
# 1. CSS SKEUOMORPHISM & STYLE
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #e0e5ec; color: #4d4d4d; font-family: 'Segoe UI', sans-serif; }
    
    /* Card Style */
    .skeuo-card {
        border-radius: 20px;
        background: #e0e5ec;
        box-shadow:  9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5);
        padding: 25px; margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Input Style */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background-color: #e0e5ec !important;
        border-radius: 10px; border: none;
        box-shadow: inset 4px 4px 8px #bebebe, inset -4px -4px 8px #ffffff !important;
        color: #333 !important; padding: 10px;
    }
    
    /* Button Style */
    .stButton>button {
        width: 100%; border: none; outline: none; border-radius: 12px;
        background: linear-gradient(145deg, #f0f0f3, #cacaca);
        box-shadow:  6px 6px 12px #bebebe, -6px -6px 12px #ffffff;
        color: #0d47a1; font-weight: bold; padding: 10px 20px;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:active {
        background: #e0e5ec;
        box-shadow: inset 4px 4px 8px #bebebe, inset -4px -4px 8px #ffffff;
        transform: translateY(2px);
    }
    
    /* Header & Footer */
    .header-container {
        display: flex; justify-content: space-between; align-items: center;
        background: #e0e5ec; padding: 15px 20px; border-radius: 15px;
        box-shadow: 5px 5px 10px #bebebe, -5px -5px 10px #ffffff; margin-bottom: 25px;
    }
    .live-clock {
        background: #e0e5ec; padding: 5px 15px; border-radius: 8px;
        box-shadow: inset 3px 3px 6px #bebebe, inset -3px -3px 6px #ffffff;
        color: #0d47a1; font-weight: bold; font-size: 14px; text-align: right;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #e0e5ec; color: #555; text-align: center;
        padding: 10px; font-weight: bold; box-shadow: 0px -4px 10px rgba(0,0,0,0.1); z-index: 999;
    }
    
    /* Headings */
    h3 { color: #0d47a1; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HEADER & JAM (JS)
# ==========================================
def render_header():
    st.markdown("""
        <div class="header-container">
            <div style="width: 65%; font-family: 'Courier New', monospace; font-weight: bold; color: #2c3e50; font-size: 16px;">
                <marquee direction="left" scrollamount="6">🚀 SISTEM PERANGKAT AJAR TERPADU - SD MUHAMMADIYAH 8 TULANGAN 🚀</marquee>
            </div>
            <div id="clock" class="live-clock">Loading...</div>
        </div>
        <script>
            function updateTime() {
                const now = new Date();
                document.getElementById('clock').innerHTML = now.toLocaleDateString('id-ID', {weekday:'long', year:'numeric', month:'long', day:'numeric'}) + '<br>' + now.toLocaleTimeString('id-ID', {hour:'2-digit', minute:'2-digit', second:'2-digit'}) + ' WIB';
            }
            setInterval(updateTime, 1000); updateTime();
        </script>
        <div class="footer">Aplikasi by Haris Adz Dzimari</div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. FUNGSI LOGIKA (AI & DOKUMEN)
# ==========================================
def tanya_gemini(api_key, prompt):
    if not api_key: return "⚠️ Masukkan API Key!"
    try:
        genai.configure(api_key=api_key)
        # Menggunakan model flash yang lebih baru dan stabil
        model = genai.GenerativeModel('gemini-1.5-flash') 
        return model.generate_content(prompt).text
    except Exception as e: return f"Error: {str(e)}"

def create_docx(data):
    doc = Document()
    for s in doc.sections: s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Cm(2.54)

    # HEADER DENGAN LOGO
    if data['logo']:
        try:
            doc.add_picture(data['logo'], width=Inches(1.0))
            last_paragraph = doc.paragraphs[-1] 
            last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except: pass

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"MODUL AJAR KURIKULUM MERDEKA\n{data['sekolah']}\n")
    r.bold = True; r.font.size = Pt(14)
    p.add_run(f"{data['alamat']}").font.size = Pt(10)
    doc.add_paragraph("_"*85)

    # I. INFO UMUM
    doc.add_heading('I. INFORMASI UMUM', 1)
    table = doc.add_table(rows=0, cols=2); table.style = 'Table Grid'
    info = [("Penyusun", data['guru']), ("Tahun", str(data['tanggal'].year)), ("Kelas", data['kelas']), 
            ("Mapel", data['mapel']), ("Topik", data['topik']), ("Model", data['model'])]
    for k,v in info:
        row = table.add_row()
        row.cells[0].text = k; row.cells[0].paragraphs[0].runs[0].bold = True; row.cells[1].text = v
    doc.add_paragraph(f"\nCP: {data['cp']}")

    # II. INTI
    doc.add_heading('II. KOMPONEN INTI', 1)
    doc.add_heading('A. Tujuan', 2); doc.add_paragraph(data['tujuan'])
    doc.add_heading('B. Pemantik', 2); doc.add_paragraph(data['pemantik'])

    # III. KEGIATAN
    doc.add_heading('III. KEGIATAN PEMBELAJARAN', 1)
    doc.add_heading('1. Ringkasan Materi', 2); doc.add_paragraph(data['bahan'])
    doc.add_heading('2. Langkah LKPD', 2); doc.add_paragraph(data['lkpd'])
    doc.add_heading('3. Media Ajar', 2); doc.add_paragraph(data['media'])

    # IV. EVALUASI (SPLIT)
    doc.add_heading('IV. EVALUASI', 1)
    doc.add_heading('A. Soal Latihan', 2); doc.add_paragraph(data['soal'])
    doc.add_heading('B. Kunci Jawaban', 2); doc.add_paragraph(data['kunci'])

    # V. ABSENSI
    doc.add_page_break(); doc.add_heading('V. DAFTAR HADIR', 1)
    doc.add_paragraph(f"Kelas: {data['kelas']} | Tanggal: {data['tanggal'].strftime('%d-%m-%Y')}")
    t_absen = doc.add_table(rows=1, cols=5); t_absen.style = 'Table Grid'
    hdr = t_absen.rows[0].cells; hdr[0].text="No"; hdr[1].text="Nama"; hdr[2].text="Hadir"; hdr[3].text="Ket"
    
    siswa = data['siswa_list'] if data['siswa_list'] else [""]*25
    for i, nm in enumerate(siswa):
        r = t_absen.add_row().cells; r[0].text=str(i+1); r[1].text=nm.strip()

    # VI. LAMPIRAN
    doc.add_paragraph("\n"); doc.add_heading('VI. LAMPIRAN', 1)
    doc.add_heading('Daftar Pustaka', 2); doc.add_paragraph(data['pustaka'])
    doc.add_heading('Glosarium', 2); doc.add_paragraph(data['glosarium'])
    
    # VII. REFLEKSI (SPLIT)
    doc.add_heading('Refleksi', 1)
    doc.add_heading('Refleksi Guru', 2); doc.add_paragraph(data['ref_guru'])
    doc.add_heading('Refleksi Siswa', 2); doc.add_paragraph(data['ref_siswa'])

    # TTD
    doc.add_paragraph("\n\n")
    ttd = doc.add_table(rows=1, cols=2)
    ttd.rows[0].cells[0].text = f"Mengetahui,\nKepala Sekolah\n\n\n( {data['kepsek']} )"
    ttd.rows[0].cells[1].text = f"Sidoarjo, {data['tanggal'].strftime('%d %B %Y')}\nGuru Kelas\n\n\n( {data['guru']} )"

    buf = BytesIO(); doc.save(buf); buf.seek(0)
    return buf

def create_pdf(data):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
    def safe(txt): return txt.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_font("Arial", 'B', 14); pdf.cell(0,10, "MODUL AJAR", 0, 1, 'C'); pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, safe(f"Sekolah: {data['sekolah']}"), ln=True)
    pdf.cell(0, 8, safe(f"Guru: {data['guru']}"), ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11); pdf.cell(0, 8, "TUJUAN:", ln=True)
    pdf.set_font("Arial", size=11); pdf.multi_cell(0, 6, safe(data['tujuan'])); pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 11); pdf.cell(0, 8, "SOAL LATIHAN:", ln=True)
    pdf.set_font("Arial", size=11); pdf.multi_cell(0, 6, safe(data['soal'])); pdf.ln(3)

    return pdf.output(dest='S').encode('latin-1', 'replace')

# ==========================================
# 4. APLIKASI UTAMA
# ==========================================
def main_app():
    render_header()
    st.markdown("<div class='skeuo-card' style='text-align:center;'><h1 style='color:#0d47a1; margin:0;'>💎 GENERATOR MODUL AJAR</h1></div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<div class='skeuo-card' style='text-align:center;'>⚙️ <b>MENU</b></div>", unsafe_allow_html=True)
        api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else st.text_input("API Key", type="password")
        if api_key: st.success("✅ AI Ready")
        
        st.divider()
        st.write("<b>Data Sekolah:</b>", unsafe_allow_html=True)
        # --- FITUR UPLOAD LOGO ---
        uploaded_logo = st.file_uploader("Upload Logo Sekolah", type=['png', 'jpg', 'jpeg'])
        nama_sekolah = st.text_input("Sekolah", value="SD MUHAMMADIYAH 8 TULANGAN")
        alamat_sekolah = st.text_area("Alamat", value="Jl. Raya Kenongo, Sidoarjo")
        kepsek = st.text_input("Kepala Sekolah", value="Muhammad Saifudin Zuhri, M.Pd.")
        
        if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()

    t1, t2, t3, t4, t5, t6, t7 = st.tabs(["1️⃣ Identitas", "2️⃣ Inti", "3️⃣ Bahan & LKPD", "4️⃣ Evaluasi", "5️⃣ Asesmen", "6️⃣ Glosarium", "7️⃣ Refleksi"])

    with t1: # Identitas
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: nama_guru = st.text_input("Guru", placeholder="Nama Lengkap"); mapel = st.text_input("Mapel", placeholder="Contoh: IPAS")
        with c2: kelas = st.selectbox("Kelas", ["1","2","3","4","5","6"]); tanggal = st.date_input("Tanggal")
        cp = st.text_area("Capaian Pembelajaran (CP):", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    with t2: # Inti
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        topik = st.text_input("Topik Materi")
        model = st.selectbox("Model Pembelajaran", ["Problem-Based Learning (PBL)", "Project-Based Learning (PjBL)", "Discovery Learning (DL)", "Inquiry Learning (IL)"])
        if st.button("✨ Auto Tujuan"):
            if not api_key: st.error("API Key Kosong")
            else:
                with st.spinner("AI Bekerja..."):
                    st.session_state['tujuan_ai'] = tanya_gemini(api_key, f"Buatkan tujuan pembelajaran & pemantik mapel {mapel} topik {topik} kelas {kelas} model {model}.")
        tujuan = st.text_area("Tujuan:", value=st.session_state.get('tujuan_ai', ''), height=150)
        pemantik = st.text_input("Pemantik")
        st.markdown("</div>", unsafe_allow_html=True)

    with t3: # Bahan & LKPD
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("✨ Auto Materi & LKPD"):
             if not api_key: st.error("API Key Kosong")
             else:
                with st.spinner("Menyusun..."):
                    st.session_state['materi_ai'] = tanya_gemini(api_key, f"Ringkasan materi {topik} SD kelas {kelas}.")
                    st.session_state['lkpd_ai'] = tanya_gemini(api_key, f"Buatkan petunjuk LKPD aktivitas siswa topik {topik}.")
                    st.session_state['media_ai'] = tanya_gemini(api_key, f"List media ajar untuk topik {topik}.")
        
        st.write("📖 **Ringkasan Bahan Ajar**"); bahan = st.text_area("Materi:", value=st.session_state.get('materi_ai', ''), height=200)
        st.divider()
        st.write("📝 **Desain LKPD**"); lkpd = st.text_area("Petunjuk LKPD:", value=st.session_state.get('lkpd_ai', ''), height=200)
        media = st.text_area("Media Ajar:", value=st.session_state.get('media_ai', ''), height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    with t4: # Evaluasi (SPLIT KOLOM)
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("✨ Auto Soal & Kunci"):
             if not api_key: st.error("API Key Kosong")
             else:
                 with st.spinner("Membuat Soal..."):
                     st.session_state['soal_ai'] = tanya_gemini(api_key, f"Buatkan 5 Soal Essay {topik}.")
                     st.session_state['kunci_ai'] = tanya_gemini(api_key, f"Buatkan Kunci Jawaban untuk soal essay topik {topik}.")
        
        c_ev1, c_ev2 = st.columns(2)
        with c_ev1:
            st.write("❓ **Soal Latihan**")
            soal = st.text_area("Daftar Soal:", value=st.session_state.get('soal_ai', ''), height=250)
        with c_ev2:
            st.write("🔑 **Kunci Jawaban**")
            kunci = st.text_area("Kunci Jawaban:", value=st.session_state.get('kunci_ai', ''), height=250)
        st.markdown("</div>", unsafe_allow_html=True)

    with t5: # Asesmen & Absen
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        st.info("Ketik nama siswa (1 nama per baris) untuk mengisi Tabel Absensi otomatis.")
        raw_siswa = st.text_area("Daftar Nama Siswa:", height=150, placeholder="Adi\nBudi\nCici...")
        siswa_list = [x for x in raw_siswa.split('\n') if x.strip()]
        st.write(f"Terdeteksi: **{len(siswa_list)} Siswa**")
        st.markdown("</div>", unsafe_allow_html=True)

    with t6: # Glosarium
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        pustaka = st.text_area("📚 Daftar Pustaka:", value=f"1. Buku Paket Kemdikbud Kelas {kelas}", height=100)
        glosarium = st.text_area("🔤 Glosarium:", placeholder="Istilah sulit...", height=100)
        st.markdown("</div>", unsafe_allow_html=True)

    with t7: # Refleksi (SPLIT)
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        c_ref1, c_ref2 = st.columns(2)
        with c_ref1:
            st.write("👨‍🏫 **Refleksi Guru**")
            ref_guru = st.text_area("Catatan Guru:", placeholder="Kendala, keberhasilan...", height=150)
        with c_ref2:
            st.write("🧒 **Refleksi Siswa**")
            ref_siswa = st.text_area("Catatan Siswa:", placeholder="Respon siswa...", height=150)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DOWNLOAD ---
    st.markdown("<div class='skeuo-card' style='text-align:center;'>", unsafe_allow_html=True)
    st.success("✅ Dokumen Siap Unduh")
    data = {
        'logo': uploaded_logo, 'sekolah': nama_sekolah, 'alamat': alamat_sekolah, 'kepsek': kepsek,
        'guru': nama_guru, 'mapel': mapel, 'kelas': kelas, 'tanggal': tanggal,
        'cp': cp, 'topik': topik, 'model': model, 'tujuan': tujuan, 'pemantik': pemantik,
        'bahan': bahan, 'lkpd': lkpd, 'media': media, 'soal': soal, 'kunci': kunci,
        'siswa_list': siswa_list, 'pustaka': pustaka, 'glosarium': glosarium, 
        'ref_guru': ref_guru, 'ref_siswa': ref_siswa
    }
    c_dl1, c_dl2 = st.columns(2)
    with c_dl1:
        st.download_button("📄 DOWNLOAD WORD (.DOCX)", create_docx(data), f"Modul_{topik}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with c_dl2:
        st.download_button("📕 DOWNLOAD PDF", create_pdf(data), f"Modul_{topik}.pdf", "application/pdf")
    st.markdown("</div>", unsafe_allow_html=True)

# LOGIN
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if not st.session_state['logged_in']:
    render_header(); st.markdown("<br><br><div class='skeuo-card' style='max-width:400px; margin:auto; text-align:center;'><h2>🔐 LOGIN</h2><hr></div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        u = st.text_input("User"); p = st.text_input("Pass", type="password")
        if st.button("MASUK"): 
            if u=="guru" and p=="123": st.session_state['logged_in']=True; st.rerun()
            else: st.error("Gagal")
else: main_app()
