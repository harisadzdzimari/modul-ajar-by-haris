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

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Generator Modul Ajar by Haris", layout="wide", page_icon="🏫")

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
    }

    /* Input Fields (Efek Tenggelam) */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        background-color: #e0e5ec !important;
        border-radius: 10px;
        border: none;
        box-shadow: inset 4px 4px 8px #bebebe, 
                    inset -4px -4px 8px #ffffff !important;
        color: #333 !important;
        padding: 10px;
    }
    
    /* Label Input */
    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stNumberInput > label {
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
    
    .stButton > button:active {
        background: #e0e5ec;
        box-shadow: inset 4px 4px 8px #bebebe, 
                    inset -4px -4px 8px #ffffff;
        transform: translateY(2px);
    }

    /* HEADER & FOOTER */
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
            Aplikasi By Haris Adz Dzimari &copy; 2025 | Sultan AI Pro v3.0 (Absensi Added)
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# --- FUNGSI LOGIKA (AI, DOCX, PDF) ---
def tanya_gemini(api_key, prompt):
    if not api_key:
        return "⚠️ Masukkan API Key di Sidebar terlebih dahulu!"
    try:
        genai.configure(api_key=api_key)
        
        # PERBAIKAN: Gunakan model 'gemini-1.5-flash' yang stabil
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
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

    # Header
    if data['logo'] is not None:
        try: doc.add_picture(data['logo'], width=Inches(0.8))
        except: pass

    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header.add_run(f"MODUL AJAR KURIKULUM MERDEKA\n{data['sekolah']}\n")
    run.bold = True; run.font.size = Pt(14)
    header.add_run(f"{data['alamat']}").font.size = Pt(10)
    doc.add_paragraph("_"*85)

    # I. Info Umum
    doc.add_heading('I. INFORMASI UMUM', level=1)
    table = doc.add_table(rows=0, cols=2); table.style = 'Table Grid'
    infos = [("Penyusun", data['guru']), ("Tahun", str(data['tanggal'].year)), 
             ("Jenjang/Kelas", f"SD / {data['kelas']} ({data['fase']})"), 
             ("Mata Pelajaran", data['mapel']), ("Topik", data['topik']), 
             ("Alokasi Waktu", data['alokasi']), ("Model", data['model'])]
    
    for k, v in infos:
        r = table.add_row()
        r.cells[0].text = k; r.cells[0].paragraphs[0].runs[0].bold = True; r.cells[1].text = v

    doc.add_paragraph(f"\nCapaian Pembelajaran (CP): {data['cp']}")
    doc.add_paragraph(f"Profil Pelajar: {', '.join(data['dimensi'])}")

    # II. Komponen Inti
    doc.add_heading('II. KOMPONEN INTI', level=1)
    doc.add_heading('A. Tujuan Pembelajaran', level=2); doc.add_paragraph(data['tujuan'])
    doc.add_heading('B. Pemantik', level=2); doc.add_paragraph(data['pemantik'])
    
    # III. Lampiran
    doc.add_page_break()
    doc.add_heading('III. LAMPIRAN', level=1)
    doc.add_heading('1. Bahan Ajar', level=2); doc.add_paragraph(data['bahan'])
    doc.add_heading('2. LKPD', level=2); doc.add_paragraph(data['lkpd'])
    doc.add_heading('3. Soal Evaluasi', level=2); doc.add_paragraph(data['soal'])
    
    # IV. Rubrik & Absensi
    doc.add_heading('4. Rubrik Penilaian Sikap', level=2)
    t_rubrik = doc.add_table(rows=1, cols=5); t_rubrik.style = 'Table Grid'
    hdr = t_rubrik.rows[0].cells
    for i, h in enumerate(['Dimensi', '4 (Sangat Baik)', '3 (Baik)', '2 (Cukup)', '1 (Kurang)']):
        hdr[i].text = h; hdr[i].paragraphs[0].runs[0].bold = True
    for dim in data['dimensi']:
        row = t_rubrik.add_row().cells
        row[0].text = dim; row[1].text = "Membudaya"; row[2].text = "Berkembang"; row[3].text = "Mulai Terlihat"; row[4].text = "Belum Terlihat"

    # FITUR BARU: GENERATOR TABEL ABSENSI
    doc.add_page_break()
    doc.add_heading('V. LEMBAR PRESENSI SISWA', level=1)
    doc.add_paragraph(f"Kelas: {data['kelas']} | Mata Pelajaran: {data['mapel']} | Tanggal: {data['tanggal'].strftime('%d %B %Y')}")
    
    # Tabel Absensi Otomatis
    jml_siswa = data['jml_siswa']
    t_absen = doc.add_table(rows=1, cols=6); t_absen.style = 'Table Grid'
    
    # Header Tabel Absen
    hdr_absen = t_absen.rows[0].cells
    headers_absen = ["No", "Nama Siswa", "H (Hadir)", "S (Sakit)", "I (Izin)", "A (Alpha)"]
    for i, h in enumerate(headers_absen):
        hdr_absen[i].text = h
        hdr_absen[i].paragraphs[0].runs[0].bold = True
        
    # Isi Baris Kosong Sesuai Jumlah Siswa
    for i in range(1, jml_siswa + 1):
        row = t_absen.add_row().cells
        row[0].text = str(i) # Nomor urut
        row[1].text = "" # Nama kosong untuk ditulis tangan
        # Kolom ceklis kosong

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
    pdf.cell(0, 10, "Lembar Presensi:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, f"Telah disiapkan tabel presensi untuk {data['jml_siswa']} siswa di versi Word (.docx). Silakan download versi Word untuk hasil cetak tabel yang sempurna.")
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
        
        username = st.text_input("Username", placeholder="ID Guru")
        password = st.text_input("Password", type="password", placeholder="Kata Sandi")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("LOGIN", use_container_width=True):
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
    render_header()

    st.markdown("""
        <div class='skeuo-card' style='text-align: center;'>
            <h1 style='color: #0d47a1; margin:0; text-shadow: 1px 1px 2px #fff;'>💎 GENERATOR MODUL AJAR</h1>
            <p style='margin:0; font-weight:bold;'>by Haris Adz Dzimari</p>
        </div>
    """, unsafe_allow_html=True)

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
        uploaded_logo = st.file_uploader("Logo", type=['png','jpg'])
        nama_sekolah = st.text_input("Sekolah", value="SD MUHAMMADIYAH 8 TULANGAN")
        alamat_sekolah = st.text_area("Alamat", value="Jl. Raya Kenongo RT. 02 RW. 01 Tulangan Sidoarjo")
        kepsek = st.text_input("Kepala Sekolah", value="Muhammad Saifudin Zuhri, M.Pd.")
        nip_kepsek = st.text_input("NIP", value="-")

    t1, t2, t3, t4, t5 = st.tabs(["1️⃣ Identitas", "2️⃣ Inti (AI)", "3️⃣ Bahan (AI)", "4️⃣ Asesmen & Absen", "5️⃣ 📥 DOWNLOAD"])

    with t1:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
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
        cp_text = st.text_area("Capaian Pembelajaran (CP):", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        topik = st.text_input("Topik Materi")
        model = st.selectbox("Model Pembelajaran", ["Deep Learning", "PjBL", "PBL", "Discovery"])
        c_btn, c_tp = st.columns([1,3])
        with c_btn:
            st.write(""); st.write("")
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
        st.markdown("<hr style='border-top: 1px solid #d1d9e6;'>", unsafe_allow_html=True)
        c_dif1, c_dif2 = st.columns(2)
        with c_dif1: remedial = st.text_area("Remedial:", value="Pendampingan individu.")
        with c_dif2: pengayaan = st.text_area("Pengayaan:", value="Tugas proyek tambahan.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 3 DENGAN MENU BARU ---
    with t3:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        st.subheader("🛠️ Generator Bahan Ajar")
        
        # Menu Pilihan
        st.write("Pilih komponen yang ingin dibuatkan AI:")
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            inc_lkpd = st.checkbox("✅ Buat LKPD Otomatis", value=True)
            inc_rubrik = st.checkbox("✅ Buat Rubrik Penilaian", value=True)
        with col_opt2:
            inc_glosarium = st.checkbox("✅ Sertakan Glosarium", value=False)
            inc_media = st.checkbox("✅ Ide Media Pembelajaran", value=False)
        
        st.divider()

        if st.button("✨ Generate Bahan Ajar Lengkap"):
            if not topik: 
                st.warning("⚠️ Harap isi 'Topik Materi' di Tab 2 terlebih dahulu!")
            else:
                with st.spinner("⏳ AI sedang menyusun materi, LKPD, dan soal..."):
                    
                    # 1. PROMPT MATERI
                    prompt_materi = f"Buatkan Ringkasan materi {topik} untuk siswa SD kelas {kelas} dengan bahasa yang mudah dipahami."
                    if inc_glosarium: prompt_materi += "\n- Tambahkan bagian 'Glosarium' untuk istilah-istilah sulit."
                    if inc_media: prompt_materi += "\n- Berikan 3 ide media pembelajaran kreatif/alat peraga sederhana untuk materi ini."
                    
                    st.session_state['bahan'] = tanya_gemini(api_key, prompt_materi)

                    # 2. PROMPT LKPD
                    if inc_lkpd:
                        prompt_lkpd = f"Buatkan rancangan Lembar Kerja Peserta Didik (LKPD) untuk topik {topik} kelas {kelas}. Berikan instruksi langkah demi langkah aktivitas siswa yang menarik."
                        st.session_state['lkpd_ai'] = tanya_gemini(api_key, prompt_lkpd)
                    else:
                        st.session_state['lkpd_ai'] = ""

                    # 3. PROMPT SOAL & RUBRIK
                    prompt_soal = f"Buatkan 5 soal essay HOTS tentang {topik} beserta kunci jawabannya."
                    if inc_rubrik: prompt_soal += "\n- Sertakan tabel Rubrik Penilaian untuk soal tersebut (Skor 4,3,2,1)."
                    
                    st.session_state['soal'] = tanya_gemini(api_key, prompt_soal)
                    st.success("Selesai! Silakan cek kolom di bawah.")

        # Input text areas
        bahan = st.text_area("📚 Bahan Ajar & Materi:", value=st.session_state.get('bahan', ''), height=200)
        lkpd = st.text_area("📝 Instruksi LKPD:", value=st.session_state.get('lkpd_ai', ''), height=150)
        soal = st.text_area("❓ Soal, Kunci & Rubrik:", value=st.session_state.get('soal', ''), height=200)
        st.markdown("</div>", unsafe_allow_html=True)

    with t4:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        
        # FITUR ABSENSI
        st.subheader("📅 Generator Presensi Siswa")
        st.info("Pilih jumlah siswa untuk membuat Tabel Absensi otomatis di file Word.")
        
        c_absen1, c_absen2 = st.columns([1, 3])
        with c_absen1:
            jml_siswa = st.number_input("Jumlah Siswa", min_value=1, max_value=50, value=25)
        with c_absen2:
            st.write("**Preview Tabel Absensi (5 Baris Pertama):**")
            df_preview = pd.DataFrame({
                "No": [1, 2, 3, 4, 5],
                "Nama Siswa": ["...", "...", "...", "...", "..."],
                "Hadir": ["⬜", "⬜", "⬜", "⬜", "⬜"],
                "Sakit": ["⬜", "⬜", "⬜", "⬜", "⬜"],
                "Izin": ["⬜", "⬜", "⬜", "⬜", "⬜"],
                "Alpha": ["⬜", "⬜", "⬜", "⬜", "⬜"]
            })
            st.table(df_preview)
            
        st.markdown("<hr style='border-top: 1px solid #d1d9e6;'>", unsafe_allow_html=True)
        
        st.subheader("📊 Rubrik Penilaian")
        st.write("Otomatis dibuat berdasarkan Dimensi Profil Pelajar yang dipilih.")
        st.table(pd.DataFrame({"Dimensi": dimensi, "Kriteria": ["Membudaya (Skor 4)" for _ in dimensi]}))
        st.markdown("</div>", unsafe_allow_html=True)

    with t5:
        st.markdown("<div class='skeuo-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.success("✅ Dokumen Siap Diunduh")
        
        data_modul = {
            'logo': uploaded_logo, 'sekolah': nama_sekolah, 'alamat': alamat_sekolah, 'kepsek': kepsek, 'nip': nip_kepsek,
            'guru': nama_guru, 'tanggal': tanggal, 'fase': fase, 'kelas': kelas, 'mapel': mapel, 'alokasi': alokasi,
            'cp': cp_text, 'topik': topik, 'model': model, 'tujuan': tujuan, 'pemantik': pemantik,
            'dimensi': dimensi, 'bahan': bahan, 'lkpd': lkpd, 'soal': soal, 'jml_siswa': jml_siswa
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

if __name__ == "__main__":
    if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
    if not st.session_state['logged_in']: login_page()
    else: main_app()
