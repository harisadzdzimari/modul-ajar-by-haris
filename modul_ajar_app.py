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
# 1. CSS SKEUOMORPHISM & ANIMASI
# ==========================================
st.markdown("""
<style>
    /* Latar Belakang */
    .stApp {
        background-color: #e0e5ec;
        font-family: 'Segoe UI', sans-serif;
        color: #4d4d4d;
    }

    /* Card Skeuomorphism */
    .skeuo-card {
        border-radius: 20px;
        background: #e0e5ec;
        box-shadow:  9px 9px 16px rgb(163,177,198,0.6), 
                     -9px -9px 16px rgba(255,255,255, 0.5);
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* Input Fields */
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

    /* Tombol */
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

    /* HEADER STYLE */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #e0e5ec;
        padding: 15px 20px;
        border-radius: 15px;
        box-shadow:  5px 5px 10px #bebebe, -5px -5px 10px #ffffff;
        margin-bottom: 25px;
    }
    .running-text {
        width: 65%;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        color: #2c3e50;
        font-size: 16px;
    }
    .live-clock {
        width: 30%;
        text-align: right;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #0d47a1;
        background: #e0e5ec;
        padding: 5px 15px;
        border-radius: 8px;
        box-shadow: inset 3px 3px 6px #bebebe, inset -3px -3px 6px #ffffff;
        font-size: 14px;
    }

    /* FOOTER */
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
    
    /* Subheader Style */
    .custom-subheader {
        color: #0d47a1;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA HEADER & CLOCK (JAVASCRIPT)
# ==========================================
def render_header():
    st.markdown("""
        <div class="header-container">
            <div class="running-text">
                <marquee direction="left" scrollamount="6">
                    🚀 SELAMAT DATANG DI SISTEM MODUL AJAR SULTAN AI - "Mewujudkan Generasi Cerdas & Berakhlak Mulia" 🚀
                </marquee>
            </div>
            <div id="clock" class="live-clock">Loading Waktu...</div>
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
            Aplikasi by Haris Adz Dzimari
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. FUNGSI AI & EXPORT DOKUMEN
# ==========================================
def tanya_gemini(api_key, prompt):
    if not api_key: return "⚠️ Masukkan API Key dulu!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro') 
        return model.generate_content(prompt).text
    except Exception as e: return f"Error: {str(e)}"

# --- EXPORT WORD (.DOCX) ---
def create_docx(data):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.54); section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54); section.right_margin = Cm(2.54)

    # Header
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"MODUL AJAR KURIKULUM MERDEKA\n{data['sekolah']}\n")
    r.bold = True; r.font.size = Pt(14)
    p.add_run(f"{data['alamat']}").font.size = Pt(10)
    doc.add_paragraph("_"*85)

    # I. Info Umum
    doc.add_heading('I. INFORMASI UMUM', level=1)
    table = doc.add_table(rows=0, cols=2); table.style = 'Table Grid'
    infos = [("Penyusun", data['guru']), ("Tahun", str(data['tanggal'].year)), 
             ("Kelas", data['kelas']), ("Mapel", data['mapel']), 
             ("Topik", data['topik']), ("Model", data['model'])]
    for k, v in infos:
        r = table.add_row()
        r.cells[0].text = k; r.cells[0].paragraphs[0].runs[0].bold = True; r.cells[1].text = v

    doc.add_paragraph(f"\nCP: {data['cp']}")

    # II. Komponen Inti
    doc.add_heading('II. KOMPONEN INTI', level=1)
    doc.add_heading('A. Tujuan', level=2); doc.add_paragraph(data['tujuan'])
    doc.add_heading('B. Pemantik', level=2); doc.add_paragraph(data['pemantik'])
    
    # III. Kegiatan (STRUKTUR BARU)
    doc.add_heading('III. KEGIATAN PEMBELAJARAN', level=1)
    doc.add_heading('1. Ringkasan Bahan Ajar', level=2)
    doc.add_paragraph(data['bahan'])
    
    doc.add_heading('2. Desain LKPD', level=2)
    doc.add_paragraph("Petunjuk Pengerjaan:")
    doc.add_paragraph(data['lkpd'])
    doc.add_paragraph("\nMedia Ajar:")
    doc.add_paragraph(data['media'])
    
    # IV. Evaluasi
    doc.add_heading('IV. EVALUASI', level=1)
    doc.add_paragraph(data['soal'])
    
    # V. Absensi (NAMA SISWA OTOMATIS)
    doc.add_page_break()
    doc.add_heading('V. DAFTAR HADIR SISWA', level=1)
    doc.add_paragraph(f"Kelas: {data['kelas']} | Tanggal: {data['tanggal'].strftime('%d-%m-%Y')}")
    
    # Logic Tabel Nama Siswa
    siswa_list = data['siswa_list']
    if not siswa_list: # Kalau kosong, bikin 25 baris kosong
        jml = 25
        t_absen = doc.add_table(rows=1, cols=5); t_absen.style = 'Table Grid'
        hdr = t_absen.rows[0].cells
        hdr[0].text = "No"; hdr[1].text = "Nama Siswa"; hdr[2].text = "Hadir"; hdr[3].text = "Sakit/Izin"; hdr[4].text = "Ket"
        for i in range(jml):
            row = t_absen.add_row().cells
            row[0].text = str(i+1); row[1].text = ""
    else:
        # Kalau ada nama siswa
        t_absen = doc.add_table(rows=1, cols=5); t_absen.style = 'Table Grid'
        hdr = t_absen.rows[0].cells
        hdr[0].text = "No"; hdr[1].text = "Nama Siswa"; hdr[2].text = "Hadir"; hdr[3].text = "Sakit/Izin"; hdr[4].text = "Ket"
        for i, nama in enumerate(siswa_list):
            row = t_absen.add_row().cells
            row[0].text = str(i+1)
            row[1].text = nama.strip()

    # VI. Lampiran
    doc.add_paragraph("\n")
    doc.add_heading('VI. LAMPIRAN', level=1)
    doc.add_heading('A. Daftar Pustaka', level=2); doc.add_paragraph(data['pustaka'])
    doc.add_heading('B. Glosarium', level=2); doc.add_paragraph(data['glosarium'])
    doc.add_heading('C. Refleksi', level=2); doc.add_paragraph(data['refleksi'])

    # TTD
    doc.add_paragraph("\n\n")
    ttd = doc.add_table(rows=1, cols=2)
    ttd.rows[0].cells[0].text = f"Mengetahui,\nKepala Sekolah\n\n\n( {data['kepsek']} )"
    ttd.rows[0].cells[1].text = f"Sidoarjo, {data['tanggal'].strftime('%d %B %Y')}\nGuru Kelas\n\n\n( {data['guru']} )"
    
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- EXPORT PDF (.PDF) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'MODUL AJAR KURIKULUM MERDEKA', 0, 1, 'C')
        self.ln(5)

def create_pdf(data):
    pdf = PDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
    
    def safe_text(txt): 
        return txt.encode('latin-1', 'replace').decode('latin-1')

    pdf.cell(0, 10, safe_text(f"Sekolah: {data['sekolah']}"), ln=True)
    pdf.cell(0, 10, safe_text(f"Guru: {data['guru']} | Kelas: {data['kelas']}"), ln=True)
    pdf.cell(0, 10, safe_text(f"Model: {data['model']}"), ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11); pdf.cell(0, 10, "1. RINGKASAN MATERI:", ln=True)
    pdf.set_font("Arial", size=11); pdf.multi_cell(0, 6, safe_text(data['bahan'][:800] + "...")); pdf.ln(3)

    pdf.set_font("Arial", 'B', 11); pdf.cell(0, 10, "2. PETUNJUK LKPD:", ln=True)
    pdf.set_font("Arial", size=11); pdf.multi_cell(0, 6, safe_text(data['lkpd'])); pdf.ln(3)

    pdf.set_font("Arial", 'B', 11); pdf.cell(0, 10, "3. DAFTAR HADIR:", ln=True)
    pdf.set_font("Arial", size=11)
    
    # Render Nama Siswa di PDF
    siswa_list = data['siswa_list']
    if not siswa_list:
        pdf.cell(0, 10, safe_text("(Daftar siswa kosong, silakan isi di Tab Asesmen)"), ln=True)
    else:
        for i, nama in enumerate(siswa_list):
             pdf.cell(0, 8, safe_text(f"{i+1}. {nama}"), ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ==========================================
# 4. HALAMAN LOGIN
# ==========================================
def login_page():
    render_header()
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("""
        <div class='login-container' style='background:#e0e5ec; padding:40px; border-radius:30px; box-shadow: 15px 15px 30px #bebebe, -15px -15px 30px #ffffff; text-align:center;'>
            <h2 style='color:#444;'>🔐 LOGIN GURU</h2>
            <hr>
        </div>
        """, unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("MASUK"):
            if username == "guru" and password == "123":
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("Salah sandi!")

# ==========================================
# 5. APLIKASI UTAMA
# ==========================================
def main_app():
    render_header()
    
    st.markdown("""
        <div class='skeuo-card' style='text-align:center;'>
            <h1 style='color:#0d47a1; margin:0;'>💎 GENERATOR MODUL AJAR</h1>
            <p>SD MUHAMMADIYAH 8 TULANGAN</p>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<div class='skeuo-card' style='text-align:center;'>⚙️ <b>MENU</b></div>", unsafe_allow_html=True)
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ AI Terhubung")
        else:
            api_key = st.text_input("API Key", type="password")
        
        st.divider()
        st.write("<b>Data Sekolah:</b>", unsafe_allow_html=True)
        nama_sekolah = st.text_input("Sekolah", value="SD MUHAMMADIYAH 8 TULANGAN")
        alamat_sekolah = st.text_area("Alamat", value="Jl. Raya Kenongo, Sidoarjo")
        kepsek = st.text_input("Kepala Sekolah", value="Muhammad Saifudin Zuhri, M.Pd.")
        
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    # --- TABS ---
    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "1️⃣ Identitas", "2️⃣ Inti (AI)", "3️⃣ Bahan & LKPD (AI)", 
        "4️⃣ Evaluasi", "5️⃣ Asesmen", "6️⃣ Glosarium", "7️⃣ Refleksi"
    ])

    with t1:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            nama_guru = st.text_input("Guru", placeholder="Nama Lengkap")
            mapel = st.text_input("Mapel", placeholder="Contoh: IPAS")
        with c2:
            kelas = st.selectbox("Kelas", ["1", "2", "3", "4", "5", "6"])
            tanggal = st.date_input("Tanggal")
        cp = st.text_area("Capaian Pembelajaran (CP):", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        topik = st.text_input("Topik Materi")
        
        # --- PERMINTAAN: 4 MODEL SPESIFIK ---
        model_opsi = [
            "Problem-Based Learning (PBL)", 
            "Project-Based Learning (PjBL)", 
            "Discovery Learning (DL)", 
            "Inquiry Learning (IL)"
        ]
        model = st.selectbox("Model Pembelajaran", model_opsi)
        
        if st.button("✨ Auto Tujuan"):
            if not api_key: st.error("API Key Kosong")
            else:
                with st.spinner("AI Bekerja..."):
                    p = f"Buatkan tujuan pembelajaran & pemantik mapel {mapel} topik {topik} kelas {kelas} model {model}."
                    st.session_state['tujuan_ai'] = tanya_gemini(api_key, p)
        
        tujuan = st.text_area("Tujuan:", value=st.session_state.get('tujuan_ai', ''), height=150)
        pemantik = st.text_input("Pemantik")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 3: BAHAN, LKPD, MEDIA ---
    with t3:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("✨ Auto Materi & LKPD"):
             if not api_key: st.error("API Key Kosong")
             else:
                with st.spinner("Menyusun..."):
                    st.session_state['materi_ai'] = tanya_gemini(api_key, f"Ringkasan materi {topik} SD kelas {kelas}.")
                    st.session_state['lkpd_ai'] = tanya_gemini(api_key, f"Buatkan langkah-langkah aktivitas siswa untuk LKPD topik {topik}.")
                    st.session_state['media_ai'] = tanya_gemini(api_key, f"Sebutkan 3 media ajar/alat peraga sederhana untuk topik {topik}.")
        
        # BAGIAN 1: RINGKASAN
        st.markdown("<div class='custom-subheader'>📖 Ringkasan Bahan Ajar</div>", unsafe_allow_html=True)
        bahan = st.text_area("Ringkasan Materi:", value=st.session_state.get('materi_ai', ''), height=200)
        
        st.divider()
        
        # BAGIAN 2: DESAIN LKPD
        st.markdown("<div class='custom-subheader'>📝 Desain LKPD</div>", unsafe_allow_html=True)
        lkpd = st.text_area("Petunjuk LKPD:", value=st.session_state.get('lkpd_ai', ''), height=200)
        
        # MEDIA AJAR (INPUT BARU)
        media = st.text_area("Media Ajar (Alat & Bahan):", value=st.session_state.get('media_ai', ''), placeholder="Contoh: Video Youtube, Kertas Karton, Spidol...")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with t4:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("✨ Auto Soal"):
             if not api_key: st.error("API Key Kosong")
             else:
                 st.session_state['soal_ai'] = tanya_gemini(api_key, f"5 Soal Essay HOTS {topik} & Kunci Jawaban.")
        soal = st.text_area("Soal & Kunci", value=st.session_state.get('soal_ai', ''), height=200)
        st.markdown("</div>", unsafe_allow_html=True)

    with t5:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        st.subheader("📊 Daftar Hadir Siswa")
        
        # --- PERMINTAAN: KETIK NAMA SISWA LANGSUNG ---
        st.info("Ketik/Paste nama siswa di bawah ini (Satu nama per baris). Tabel Absensi di Word akan otomatis terisi.")
        raw_siswa = st.text_area("Daftar Nama Siswa:", height=200, placeholder="Ahmad\nBudi\nCitra\n...")
        
        # Proses String menjadi List
        siswa_list = raw_siswa.split('\n') if raw_siswa else []
        siswa_list = [nama for nama in siswa_list if nama.strip()] # Hapus baris kosong
        
        st.write(f"Terdeteksi: **{len(siswa_list)} Siswa**")
        
        st.divider()
        st.write("Rubrik Penilaian Sikap:")
        profil = st.multiselect("Dimensi", ["Mandiri", "Bernalar Kritis", "Gotong Royong", "Kreatif"], default=["Mandiri"])
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 6: GLOSARIUM & PUSTAKA ---
    with t6:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        
        st.markdown("<div class='custom-subheader'>📚 Daftar Pustaka</div>", unsafe_allow_html=True)
        pustaka = st.text_area("Sumber Belajar:", value=f"1. Buku Paket Kemdikbud Kelas {kelas}\n2. Video Pembelajaran Youtube", height=100)
        
        st.divider()
        
        st.markdown("<div class='custom-subheader'>🔤 Glosarium</div>", unsafe_allow_html=True)
        glosarium = st.text_area("Istilah Sulit:", placeholder="Contoh: Ekosistem adalah...", height=150)
        
        st.markdown("</div>", unsafe_allow_html=True)

    with t7:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        refleksi = st.text_area("Refleksi", placeholder="Catatan refleksi guru & siswa...", height=150)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DOWNLOAD AREA ---
    st.markdown("<div class='skeuo-card' style='text-align:center;'>", unsafe_allow_html=True)
    st.success("✅ Dokumen Siap Unduh")
    
    data = {
        'sekolah': nama_sekolah, 'alamat': alamat_sekolah, 'kepsek': kepsek,
        'guru': nama_guru, 'mapel': mapel, 'kelas': kelas, 'tanggal': tanggal,
        'cp': cp, 'topik': topik, 'model': model, 'tujuan': tujuan, 'pemantik': pemantik,
        'bahan': bahan, 'lkpd': lkpd, 'media': media, 'soal': soal,
        'siswa_list': siswa_list, # List nama siswa dikirim ke fungsi docx
        'pustaka': pustaka, 'glosarium': glosarium, 'refleksi': refleksi
    }
    
    c_dl1, c_dl2 = st.columns(2)
    with c_dl1:
        docx = create_docx(data)
        st.download_button("📄 DOWNLOAD WORD (.DOCX)", docx, f"Modul_{topik}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with c_dl2:
        pdf = create_pdf(data)
        st.download_button("📕 DOWNLOAD PDF", pdf, f"Modul_{topik}.pdf", "application/pdf")
        
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
    if st.session_state['logged_in']: main_app()
    else: login_page()
