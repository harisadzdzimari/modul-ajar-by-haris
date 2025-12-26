import streamlit as st
import datetime
import pandas as pd
import os
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Administrasi Guru Sultan AI", layout="wide", page_icon="🏫")

# ==========================================
# 1. DATABASE TEMPLATE (KONTEN)
# ==========================================
def generate_content_template(jenis, mapel, topik, fase, kelas, model):
    if jenis == "tujuan":
        return (f"Peserta didik mampu memahami konsep {topik} melalui diskusi dan pengamatan.\n"
                f"Peserta didik mampu menganalisis karakteristik {topik} dalam kehidupan sehari-hari.\n"
                f"Peserta didik mampu menyajikan hasil karya terkait {topik} dengan percaya diri.")
    elif jenis == "pemantik":
        return (f"1. Pernahkah kalian melihat {topik} di lingkungan sekitar?\n"
                f"2. Mengapa {topik} penting bagi kehidupan kita?\n"
                f"3. Bagaimana solusi jika terjadi masalah pada {topik}?")
    elif jenis == "materi":
        return (f"A. Pengertian {topik}\n"
                f"   {topik} merupakan konsep dasar dalam {mapel} yang mempelajari tentang...\n\n"
                f"B. Karakteristik Utama\n"
                f"   1. Memiliki ciri khusus...\n   2. Berdampak pada...\n\n"
                f"C. Penerapan\n   Dapat diterapkan dalam situasi...")
    elif jenis == "lkpd":
        return (f"1. Bentuk kelompok 4-5 orang.\n"
                f"2. Amati studi kasus tentang {topik} yang diberikan guru.\n"
                f"3. Diskusikan: Apa penyebab masalah? Bagaimana solusinya?\n"
                f"4. Tulis hasil diskusi di lembar kerja.\n"
                f"5. Presentasikan di depan kelas.")
    elif jenis == "soal":
        return (f"1. Jelaskan definisi {topik} menurut pemahamanmu!\n"
                f"2. Sebutkan 3 contoh penerapan {topik}!\n"
                f"3. Analisislah dampak positif dari {topik}!\n"
                f"4. Buatlah skema sederhana tentang {topik}!\n"
                f"5. Simpulkan manfaat mempelajari {topik}!")
    elif jenis == "kunci":
        return (f"1. Definisi: [Jelaskan sesuai buku teks]\n"
                f"2. Contoh: [Sebutkan 3 contoh relevan]\n"
                f"3. Dampak: [Jelaskan dampak positif]\n"
                f"4. Skema: [Gambar/Alur]\n"
                f"5. Kesimpulan: [Inti sari materi]")
    return "-"

# ==========================================
# 2. SISTEM PELACAKAN & WAKTU
# ==========================================
STATS_FILE = "daily_stats.csv"

def get_jakarta_time():
    utc_now = datetime.datetime.utcnow()
    jakarta_time = utc_now + datetime.timedelta(hours=7)
    return jakarta_time

def manage_stats(action=None):
    now_jakarta = get_jakarta_time()
    today_str = now_jakarta.strftime("%Y-%m-%d")
    
    if not os.path.exists(STATS_FILE):
        df = pd.DataFrame(columns=["date", "login_count", "gen_count"])
        df.to_csv(STATS_FILE, index=False)
    
    df = pd.read_csv(STATS_FILE)
    if today_str not in df['date'].values:
        new_row = pd.DataFrame({"date": [today_str], "login_count": [0], "gen_count": [0]})
        df = pd.concat([df, new_row], ignore_index=True)
    
    if action == 'login': df.loc[df['date'] == today_str, 'login_count'] += 1
    elif action == 'generate': df.loc[df['date'] == today_str, 'gen_count'] += 1
        
    df.to_csv(STATS_FILE, index=False)
    today_data = df.loc[df['date'] == today_str].iloc[0]
    return today_data['login_count'], today_data['gen_count'], df

# ==========================================
# 3. ENGINE DOCX PROFESIONAL (MIRIP PDF)
# ==========================================
def set_col_widths(table, widths):
    for row in table.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = width

def create_modul_docx_pro(data):
    doc = Document()
    
    # Atur Margin (Standar A4)
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.0)

    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(11)

    # --- HALAMAN 1: COVER ---
    if data['logo']:
        try:
            doc.add_picture(data['logo'], width=Inches(1.2))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        except: pass
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"\nMODUL AJAR KURIKULUM MERDEKA\n")
    run.bold = True; run.font.size = Pt(14)
    run = p.add_run(f"MATA PELAJARAN: {data['mapel'].upper()}\n")
    run.bold = True; run.font.size = Pt(12)
    run = p.add_run(f"{data['fase'].upper()} KELAS {data['kelas']} SEMESTER {data['semester']}\n")
    run.bold = True; run.font.size = Pt(12)
    run = p.add_run(f"{data['sekolah'].upper()}\n\n")
    run.bold = True; run.font.size = Pt(14)

    # Box Isi Perangkat
    table_isi = doc.add_table(rows=1, cols=1)
    table_isi.style = 'Table Grid'
    cell = table_isi.rows[0].cells[0]
    p_isi = cell.paragraphs[0]
    p_isi.add_run("Isi Perangkat:\n").bold = True
    isi_list = ["1. Modul Ajar", "2. LKPD", "3. Asesmen Penilaian", "4. Pengayaan Dan Remedial", 
                "5. Bahan Bacaan", "6. Media Pembelajaran", "7. Jurnal Refleksi Guru", 
                "8. Lembar Survey Guru", "9. Instrumen Penilaian"]
    for item in isi_list: p_isi.add_run(f"{item}\n")

    doc.add_paragraph("\n\n")
    p_bawah = doc.add_paragraph()
    p_bawah.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bawah.add_run("Disusun Oleh:\n").italic = True
    p_bawah.add_run(f"{data['guru']}\n").bold = True
    if data['nim']: p_bawah.add_run(f"NIM/No Peserta: {data['nim']}\n")
    p_bawah.add_run(f"\n{data['instansi_pendidikan']}\n").bold = True
    p_bawah.add_run(f"TAHUN {data['tanggal'].year}")
    
    doc.add_page_break()

    # --- HALAMAN 2: MODUL AJAR (TABEL IDENTITAS) ---
    doc.add_heading('A. IDENTITAS DAN INFORMASI UMUM', level=1)
    
    table_id = doc.add_table(rows=0, cols=3)
    table_id.style = 'Table Grid'
    # Set lebar kolom manual
    
    infos = [
        ("Penyusun", ":", data['guru']),
        ("Jenjang Sekolah", ":", "Sekolah Dasar (SD) / MI"),
        ("Fase/Kelas", ":", f"{data['fase']} / {data['kelas']}"),
        ("Mata Pelajaran", ":", data['mapel']),
        ("Elemen / Topik", ":", data['topik']),
        ("Alokasi Waktu", ":", data['alokasi']),
        ("Profil Pelajar", ":", ", ".join(data['profil'])),
        ("Model Pembelajaran", ":", data['model']),
        ("Metode", ":", "Diskusi, Tanya Jawab, Presentasi"),
        ("Sarana Prasarana", ":", "Laptop, LCD, LKPD, Buku Paket")
    ]
    for k, s, v in infos:
        row = table_id.add_row()
        row.cells[0].text = k
        row.cells[1].text = s
        row.cells[2].text = v
    
    doc.add_paragraph("\n")
    
    # --- LANGKAH PEMBELAJARAN (MATRIKS) ---
    doc.add_heading('B. LANGKAH-LANGKAH PEMBELAJARAN', level=1)
    doc.add_paragraph(f"Tujuan Pembelajaran: {data['tujuan']}")
    doc.add_paragraph(f"Pemantik: {data['pemantik']}")
    
    t_keg = doc.add_table(rows=1, cols=4)
    t_keg.style = 'Table Grid'
    hdr = t_keg.rows[0].cells
    hdr[0].text = "TAHAP"; hdr[1].text = "KEGIATAN"; hdr[2].text = "MUATAN (4C/P5)"; hdr[3].text = "WAKTU"
    
    # Isi Kegiatan (Template Manual agar rapi)
    # 1. Pendahuluan
    r1 = t_keg.add_row().cells
    r1[0].text = "Pendahuluan"
    r1[1].text = "1. Guru memberi salam dan menyapa siswa.\n2. Doa bersama.\n3. Menyanyikan lagu wajib.\n4. Apersepsi materi sebelumnya.\n5. Menyampaikan Tujuan Pembelajaran."
    r1[2].text = "Religius\nNasionalisme\nCommunication"
    r1[3].text = "10 Menit"
    
    # 2. Inti
    r2 = t_keg.add_row().cells
    r2[0].text = "Inti"
    r2[1].text = (f"Sintaks {data['model']}:\n"
                  "1. Orientasi Masalah: Siswa mengamati materi/video.\n"
                  "2. Organisasi Belajar: Siswa membentuk kelompok.\n"
                  "3. Penyelidikan: Mengerjakan LKPD secara diskusi.\n"
                  "4. Penyajian: Presentasi hasil diskusi kelompok.\n"
                  "5. Evaluasi: Guru memberi penguatan dan kuis.")
    r2[2].text = "Critical Thinking\nCollaboration\nCreativity"
    r2[3].text = "50 Menit"
    
    # 3. Penutup
    r3 = t_keg.add_row().cells
    r3[0].text = "Penutup"
    r3[1].text = "1. Siswa dan guru menyimpulkan materi.\n2. Refleksi perasaan siswa.\n3. Penyampaian materi esok.\n4. Doa penutup."
    r3[2].text = "Mandiri\nReligius"
    r3[3].text = "10 Menit"

    doc.add_paragraph("\n")
    
    # --- REFLEKSI & PENGAYAAN ---
    doc.add_heading('C. REFLEKSI & PENGAYAAN', level=1)
    doc.add_paragraph("Refleksi Guru:")
    doc.add_paragraph(data['ref_guru'])
    doc.add_paragraph("\nPengayaan:")
    doc.add_paragraph(data['pengayaan'])
    doc.add_paragraph("\nRemedial:")
    doc.add_paragraph(data['remedial'])

    # --- TANDA TANGAN ---
    doc.add_paragraph("\n\n")
    ttd = doc.add_table(rows=1, cols=2)
    ttd.rows[0].cells[0].text = f"Mengetahui,\nKepala Sekolah\n\n\n\n( {data['kepsek']} )\nNIP. -"
    ttd.rows[0].cells[1].text = f"Sidoarjo, {data['tanggal'].strftime('%d %B %Y')}\nGuru Mata Pelajaran\n\n\n\n( {data['guru']} )\nNIM. {data['nim']}"
    ttd.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # --- LAMPIRAN 1: LKPD ---
    doc.add_page_break()
    doc.add_heading('LAMPIRAN 1: LKPD', level=1)
    doc.add_paragraph(f"Nama Kelompok: ....................\nKelas: {data['kelas']}\n")
    doc.add_paragraph("Petunjuk:")
    doc.add_paragraph(data['lkpd'])
    doc.add_paragraph("\nSoal Diskusi:")
    doc.add_paragraph("1. ...................................................................................")
    doc.add_paragraph("2. ...................................................................................")

    # --- LAMPIRAN 2: RUBRIK PENILAIAN ---
    doc.add_page_break()
    doc.add_heading('LAMPIRAN 2: INSTRUMEN PENILAIAN', level=1)
    
    doc.add_heading('1. Penilaian Sikap (Observasi)', level=2)
    t_sikap = doc.add_table(rows=1, cols=5); t_sikap.style = 'Table Grid'
    sh = t_sikap.rows[0].cells
    sh[0].text = "No"; sh[1].text = "Nama Siswa"; sh[2].text = "Disiplin"; sh[3].text = "Kerjasama"; sh[4].text = "Tanggung Jawab"
    for i in range(1, 6): # Contoh 5 baris
        r = t_sikap.add_row().cells; r[0].text=str(i)

    doc.add_paragraph("\n")
    doc.add_heading('2. Rubrik Penilaian Kinerja (Presentasi)', level=2)
    t_rub = doc.add_table(rows=1, cols=5); t_rub.style = 'Table Grid'
    rh = t_rub.rows[0].cells
    rh[0].text = "Aspek"; rh[1].text = "Sangat Baik (4)"; rh[2].text = "Baik (3)"; rh[3].text = "Cukup (2)"; rh[4].text = "Kurang (1)"
    
    ra = t_rub.add_row().cells
    ra[0].text = "Isi Materi"
    ra[1].text = "Lengkap, akurat, mendalam"
    ra[2].text = "Lengkap, cukup akurat"
    ra[3].text = "Kurang lengkap"
    ra[4].text = "Tidak sesuai"

    rb = t_rub.add_row().cells
    rb[0].text = "Penyampaian"
    rb[1].text = "Percaya diri, suara jelas"
    rb[2].text = "Cukup percaya diri"
    rb[3].text = "Kurang percaya diri"
    rb[4].text = "Tidak berani tampil"

    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# ==========================================
# 4. CSS SKEUOMORPHISM & STYLE
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #e0e5ec; color: #4d4d4d; font-family: 'Segoe UI', sans-serif; }
    .skeuo-card {
        border-radius: 20px; background: #e0e5ec;
        box-shadow:  9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5);
        padding: 25px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2);
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background-color: #e0e5ec !important; border-radius: 10px; border: none;
        box-shadow: inset 4px 4px 8px #bebebe, inset -4px -4px 8px #ffffff !important;
        color: #333 !important; padding: 10px;
    }
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
    .header-container {
        display: flex; justify-content: space-between; align-items: center;
        background: #e0e5ec; padding: 15px 20px; border-radius: 15px;
        box-shadow: 5px 5px 10px #bebebe, -5px -5px 10px #ffffff; margin-bottom: 25px;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #e0e5ec; color: #555; text-align: center;
        padding: 10px; font-weight: bold; box-shadow: 0px -4px 10px rgba(0,0,0,0.1); z-index: 9999; font-size: 14px;
    }
    h3 { color: #0d47a1; font-weight: bold; margin-bottom: 15px; }
    h4 { color: #333; font-weight: bold; margin-bottom: 10px; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. HEADER & JAM (JS)
# ==========================================
def render_header():
    st.markdown("""
        <div class="header-container">
            <div style="width: 65%; font-family: 'Courier New', monospace; font-weight: bold; color: #2c3e50; font-size: 16px;">
                <marquee direction="left" scrollamount="6">🚀 SISTEM PERANGKAT AJAR TERPADU - SD MUHAMMADIYAH 8 TULANGAN 🚀</marquee>
            </div>
            <div id="clock" style="font-weight:bold; color:#0d47a1;">Loading...</div>
        </div>
        <script>
            function updateTime() {
                const now = new Date();
                const optionsDate = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                document.getElementById('clock').innerHTML = now.toLocaleDateString('id-ID', optionsDate) + '<br>' + now.toLocaleTimeString('id-ID', {hour:'2-digit', minute:'2-digit', second:'2-digit'}) + ' WIB';
            }
            setInterval(updateTime, 1000); updateTime();
        </script>
        <div class="footer">Aplikasi by Haris Adz Dzimari &copy; 2025</div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. APLIKASI UTAMA (MAIN APP)
# ==========================================
def main_app():
    render_header()
    logins, gens, df_stats = manage_stats() 
    utc_now = datetime.datetime.utcnow(); jakarta_time = utc_now + datetime.timedelta(hours=7)
    today_date = jakarta_time.strftime("%d %B %Y"); now_time = jakarta_time.strftime("%H:%M WIB")

    st.markdown("<div class='skeuo-card' style='text-align:center;'><h1 style='color:#0d47a1; margin:0;'>💎 SUPER APP GURU</h1></div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<div class='skeuo-card' style='text-align:center;'>⚙️ <b>NAVIGASI</b></div>", unsafe_allow_html=True)
        menu = st.radio("Pilih Alat:", ["📂 Modul Ajar", "🗺️ Generator ATP", "📅 Generator Prota"])
        
        st.markdown(f"""
        <div style='background:#f0f2f6; padding:10px; border-radius:10px; margin:15px 0; text-align:center;'>
            <h4 style='margin:0;'>📊 Statistik</h4>
            <p style='font-size:12px; margin-bottom:5px;'>{today_date} | {now_time}</p>
            <p style='margin:0;'>Login: <b>{logins}</b> | Dokumen: <b>{gens}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik
        if not df_stats.empty:
            st.caption("Tren Aktivitas (7 Hari)")
            st.bar_chart(df_stats.tail(7).set_index('date')['gen_count'])

        if menu == "📂 Modul Ajar":
            if st.button("🔄 Reset Modul"):
                keys = ['tujuan_ai', 'materi_ai', 'lkpd_ai', 'media_ai', 'soal_ai', 'kunci_ai']; 
                for k in keys: 
                    if k in st.session_state: del st.session_state[k]
                st.rerun()

        st.divider()
        st.write("<b>Identitas Sekolah:</b>", unsafe_allow_html=True)
        uploaded_logo = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
        nama_sekolah = st.text_input("Sekolah", value="SD MUHAMMADIYAH 8 TULANGAN")
        alamat_sekolah = st.text_area("Alamat", value="Jl. Raya Kenongo RT. 02 RW. 01 Tulangan Sidoarjo")
        instansi_pendidikan = st.text_input("Yayasan/Dinas", value="MAJELIS DIKDASMEN MUHAMMADIYAH")
        kepsek = st.text_input("Kepala Sekolah", value="Muhammad Saifudin Zuhri, M.Pd.")
        
        if st.button("Logout"): 
            st.session_state['logged_in'] = False; st.query_params.clear(); st.rerun()

    if menu == "📂 Modul Ajar":
        menu_modul_ajar(nama_sekolah, alamat_sekolah, kepsek, uploaded_logo, instansi_pendidikan)
    else:
        st.info("Fitur ATP dan Prota tersedia di menu ini (Kode disederhanakan).")

def menu_modul_ajar(nama_sekolah, alamat_sekolah, kepsek, uploaded_logo, instansi_pendidikan):
    st.subheader("📂 Generator Modul Ajar (Format PDF Profesional)")
    st.info("💡 Mode Template aktif: Menghasilkan format baku lengkap dengan tabel dan lampiran sesuai standar akreditasi.")
    
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(["1️⃣ Identitas", "2️⃣ Inti", "3️⃣ Bahan & LKPD", "4️⃣ Evaluasi", "5️⃣ Asesmen", "6️⃣ Glosarium", "7️⃣ Refleksi"])

    with t1:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: 
            nama_guru = st.text_input("Nama Guru", value=st.session_state.get('nama_guru', ''))
            nim = st.text_input("NIP / NBM / NIM", placeholder="Opsional")
            tanggal = st.date_input("Tanggal")
            mapel = st.text_input("Mapel", value=st.session_state.get('mapel', ''), placeholder="Contoh: IPAS")
        with c2: 
            fase = st.selectbox("Fase", ["Fase A (Kls 1-2)", "Fase B (Kls 3-4)", "Fase C (Kls 5-6)", "Fase D (SMP)"])
            kelas = st.selectbox("Kelas", ["1","2","3","4","5","6","7","8","9"])
            semester = st.selectbox("Semester", ["I (Ganjil)", "II (Genap)"])
            alokasi = st.text_input("Alokasi Waktu", value="2 JP")
        cp = st.text_area("Capaian Pembelajaran (CP):", height=100)
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        col_inti_1, col_inti_2 = st.columns(2)
        with col_inti_1:
            st.markdown("### 📚 Materi & Tujuan")
            topik = st.text_input("Topik / Bab", value=st.session_state.get('topik', ''))
            model = st.selectbox("Model", ["Problem Based Learning (PBL)", "Project Based Learning (PjBL)", "Discovery Learning", "Inquiry"])
            
            if st.button("⚡ Generate Tujuan Otomatis"):
                manage_stats('generate')
                st.session_state['tujuan_ai'] = generate_content_template("tujuan", mapel, topik, fase, kelas, model)
                st.session_state['pemantik_ai'] = generate_content_template("pemantik", mapel, topik, fase, kelas, model)
                st.success("Tujuan berhasil dibuat!")
                
            tujuan = st.text_area("Tujuan Pembelajaran (TP)", value=st.session_state.get('tujuan_ai', ''), height=150)
            pemantik = st.text_input("Pemantik", value=st.session_state.get('pemantik_ai', ''))

        with col_inti_2:
            st.markdown("### 👤 Profil & Diferensiasi")
            profil = st.multiselect("Profil Pelajar", ["Beriman", "Mandiri", "Bernalar Kritis", "Kreatif", "Gotong Royong"], default=["Mandiri", "Bernalar Kritis"])
            remedial = st.text_area("Remedial:", value="Bimbingan perorangan ulang untuk siswa yang belum tuntas.", height=80)
            pengayaan = st.text_area("Pengayaan:", value="Tugas proyek tambahan menganalisis studi kasus.", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("⚡ Generate Materi & LKPD Otomatis"):
            manage_stats('generate')
            st.session_state['materi_ai'] = generate_content_template("materi", mapel, topik, fase, kelas, model)
            st.session_state['lkpd_ai'] = generate_content_template("lkpd", mapel, topik, fase, kelas, model)
            st.success("Materi & LKPD siap!")
            
        bahan = st.text_area("Materi Ringkas:", value=st.session_state.get('materi_ai', ''), height=200)
        lkpd = st.text_area("Langkah LKPD:", value=st.session_state.get('lkpd_ai', ''), height=200)
        media = st.text_area("Media Ajar:", value="Laptop, LCD Proyektor, Video Pembelajaran, Kertas Karton", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    with t4:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("⚡ Generate Soal Otomatis"):
            manage_stats('generate')
            st.session_state['soal_ai'] = generate_content_template("soal", mapel, topik, fase, kelas, model)
            st.session_state['kunci_ai'] = generate_content_template("kunci", mapel, topik, fase, kelas, model)
            st.success("Soal siap!")
            
        c_ev1, c_ev2 = st.columns(2)
        with c_ev1: soal = st.text_area("Soal Evaluasi:", value=st.session_state.get('soal_ai', ''), height=250)
        with c_ev2: kunci = st.text_area("Kunci Jawaban:", value=st.session_state.get('kunci_ai', ''), height=250)
        st.markdown("</div>", unsafe_allow_html=True)

    with t5:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        teknik_nilai = st.multiselect("Teknik Penilaian", ["Tes Tulis", "Observasi", "Unjuk Kerja"], default=["Tes Tulis", "Observasi"])
        st.write("Daftar Siswa (Copy-Paste dari Excel untuk Absensi Otomatis):")
        raw_siswa = st.text_area("Nama Siswa:", height=150)
        siswa_list = [x for x in raw_siswa.split('\n') if x.strip()]
        st.markdown("</div>", unsafe_allow_html=True)

    with t6:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        pustaka = st.text_area("Daftar Pustaka:", value="Buku Kemdikbud, Youtube", height=100)
        glosarium = st.text_area("Glosarium:", height=100)
        st.markdown("</div>", unsafe_allow_html=True)

    with t7:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        c_ref1, c_ref2 = st.columns(2)
        with c_ref1: ref_guru = st.text_area("Refleksi Guru:", height=100)
        with c_ref2: ref_siswa = st.text_area("Refleksi Siswa:", height=100)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DOWNLOAD ---
    st.success("✅ Dokumen Siap Unduh")
    data_export = {
        'logo': uploaded_logo, 'sekolah': nama_sekolah, 'alamat': alamat_sekolah, 'kepsek': kepsek,
        'guru': nama_guru, 'nim': nim, 'instansi_pendidikan': instansi_pendidikan,
        'mapel': mapel, 'kelas': kelas, 'fase': fase, 'semester': semester, 'tanggal': tanggal, 'alokasi': alokasi,
        'cp': cp, 'topik': topik, 'model': model, 'tujuan': tujuan, 'pemantik': pemantik,
        'profil': profil, 'remedial': remedial, 'pengayaan': pengayaan,
        'bahan': bahan, 'lkpd': lkpd, 'media': media, 'soal': soal, 'kunci': kunci,
        'teknik_nilai': teknik_nilai,
        'siswa_list': siswa_list, 'pustaka': pustaka, 'glosarium': glosarium, 
        'ref_guru': ref_guru, 'ref_siswa': ref_siswa
    }
    
    st.download_button("📄 DOWNLOAD MODUL AJAR RESMI (.DOCX)", create_modul_docx_pro(data_export), f"Modul_Ajar_{topik}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# LOGIN
if "auth" in st.query_params and st.query_params["auth"] == "true": st.session_state['logged_in'] = True
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    render_header()
    st.markdown("<br><br><div class='skeuo-card' style='max-width:400px; margin:auto; text-align:center;'><h2>🔐 LOGIN</h2><hr></div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        u = st.text_input("User"); p = st.text_input("Pass", type="password")
        if st.button("MASUK"): 
            if u=="guru" and p=="123": 
                manage_stats('login'); st.session_state['logged_in'] = True; st.query_params["auth"] = "true"; st.rerun()
            else: st.error("Gagal")
else: main_app()
