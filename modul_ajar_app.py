import streamlit as st
import datetime
import pandas as pd
import os
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Administrasi Guru (Offline Mode)", layout="wide", page_icon="🏫")

# ==========================================
# 1. DATABASE TEMPLATE (PENGGANTI AI)
# ==========================================
def generate_content_template(jenis, mapel, topik, fase, kelas, model):
    """
    Fungsi ini menggantikan AI. Menghasilkan teks berdasarkan logika template.
    """
    if jenis == "tujuan":
        return (f"Peserta didik mampu memahami konsep dasar {topik} melalui pengamatan dan diskusi.\n"
                f"Peserta didik mampu mengidentifikasi karakteristik utama {topik} dalam kehidupan sehari-hari.\n"
                f"Peserta didik mampu menyajikan hasil analisis sederhana tentang {topik} dengan percaya diri.")
    
    elif jenis == "pemantik":
        return (f"1. Pernahkah kalian melihat {topik} di sekitar kalian?\n"
                f"2. Menurut kalian, seberapa penting {topik} bagi kehidupan kita?\n"
                f"3. Apa yang akan terjadi jika tidak ada {topik}?")
    
    elif jenis == "materi":
        return (f"Rangkuman Materi: {topik}\n\n"
                f"1. Pengertian {topik}\n"
                f"   {topik} adalah salah satu konsep penting dalam mata pelajaran {mapel}. "
                f"Pemahaman tentang {topik} membantu siswa dalam mengenali fenomena di lingkungan sekitar.\n\n"
                f"2. Karakteristik {topik}\n"
                f"   - Memiliki ciri khusus yang dapat diamati.\n"
                f"   - Berhubungan erat dengan kehidupan sehari-hari.\n\n"
                f"3. Manfaat Mempelajari {topik}\n"
                f"   Siswa dapat menerapkan pengetahuan ini untuk memecahkan masalah sederhana.")
    
    elif jenis == "lkpd":
        return (f"LEMBAR KERJA PESERTA DIDIK (LKPD)\n"
                f"Topik: {topik}\n\n"
                f"Langkah Kegiatan ({model}):\n"
                f"1. Orientasi: Amati gambar/video tentang {topik} yang ditayangkan guru.\n"
                f"2. Organisasi: Bentuk kelompok terdiri dari 4-5 orang.\n"
                f"3. Penyelidikan: Diskusikan ciri-ciri {topik} berdasarkan pengamatan.\n"
                f"4. Penyajian: Tuliskan hasil diskusi di lembar kerja dan presentasikan.\n"
                f"5. Evaluasi: Simpulkan apa yang telah dipelajari hari ini.")
    
    elif jenis == "soal":
        return (f"Jawablah pertanyaan berikut dengan tepat!\n\n"
                f"1. Jelaskan apa yang dimaksud dengan {topik}?\n"
                f"2. Sebutkan 3 contoh {topik} yang ada di sekitarmu!\n"
                f"3. Mengapa {topik} penting untuk kita pelajari?\n"
                f"4. Bagaimana cara menerapkan konsep {topik} di rumah?\n"
                f"5. Apa perbedaan antara {topik} dengan materi sebelumnya?")
    
    elif jenis == "kunci":
        return (f"Kunci Jawaban (Perkiraan):\n\n"
                f"1. {topik} adalah [Definisi konsep sesuai buku paket].\n"
                f"2. Contohnya: [Contoh 1], [Contoh 2], [Contoh 3].\n"
                f"3. Karena membantu kita memahami [Manfaat utama].\n"
                f"4. Dengan cara mempraktikkannya saat [Situasi relevan].\n"
                f"5. Perbedaannya terletak pada [Ciri khas utama].")
    
    elif jenis == "atp":
        return (f"ALUR TUJUAN PEMBELAJARAN (ATP)\n"
                f"Mapel: {mapel} | Fase: {fase} | Kelas: {kelas}\n\n"
                f"| No | Elemen | Tujuan Pembelajaran (TP) | Alokasi |\n"
                f"|----|--------|--------------------------|---------|\n"
                f"| 1  | Pemahaman | Memahami konsep {topik} dasar | 4 JP |\n"
                f"| 2  | Penerapan | Menerapkan {topik} dalam kasus nyata | 4 JP |\n"
                f"| 3  | Analisis  | Menganalisis hubungan {topik} dengan lingkungan | 4 JP |")
    
    elif jenis == "prota":
        return (f"PROGRAM TAHUNAN (PROTA)\n"
                f"Mapel: {mapel} | Kelas: {kelas}\n\n"
                f"SEMESTER 1:\n"
                f"1. {topik} (Pendahuluan) - 8 JP\n"
                f"2. Pendalaman {topik} - 12 JP\n"
                f"3. Proyek {topik} - 10 JP\n\n"
                f"SEMESTER 2:\n"
                f"1. Penerapan Lanjut {topik} - 8 JP\n"
                f"2. Evaluasi dan Refleksi - 4 JP")
    
    return "Konten belum tersedia."

# ==========================================
# 2. SISTEM PELACAKAN (TRACKER)
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
    
    if action == 'login':
        df.loc[df['date'] == today_str, 'login_count'] += 1
    elif action == 'generate':
        df.loc[df['date'] == today_str, 'gen_count'] += 1
        
    df.to_csv(STATS_FILE, index=False)
    today_data = df.loc[df['date'] == today_str].iloc[0]
    return today_data['login_count'], today_data['gen_count'], df

# ==========================================
# 3. CSS STYLE
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #e0e5ec; color: #4d4d4d; font-family: 'Segoe UI', sans-serif; }
    .skeuo-card {
        border-radius: 20px; background: #e0e5ec;
        box-shadow:  9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5);
        padding: 25px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2);
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #e0e5ec !important; border-radius: 10px; border: none;
        box-shadow: inset 4px 4px 8px #bebebe, inset -4px -4px 8px #ffffff !important;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; background: linear-gradient(145deg, #f0f0f3, #cacaca);
        box-shadow:  6px 6px 12px #bebebe, -6px -6px 12px #ffffff; color: #0d47a1; font-weight: bold;
    }
    .header-container {
        display: flex; justify-content: space-between; align-items: center;
        background: #e0e5ec; padding: 15px 20px; border-radius: 15px;
        box-shadow: 5px 5px 10px #bebebe, -5px -5px 10px #ffffff; margin-bottom: 25px;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #e0e5ec; color: #555; text-align: center;
        padding: 10px; font-weight: bold; box-shadow: 0px -4px 10px rgba(0,0,0,0.1); z-index: 9999; font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. HEADER & EXPORT ENGINE
# ==========================================
def render_header():
    st.markdown("""
        <div class="header-container">
            <div style="width: 65%; font-family: 'Courier New', monospace; font-weight: bold; color: #2c3e50; font-size: 16px;">
                <marquee direction="left" scrollamount="6">🚀 SISTEM ADMINISTRASI GURU TERPADU - SD MUHAMMADIYAH 8 TULANGAN 🚀</marquee>
            </div>
            <div id="clock" style="font-weight:bold; color:#0d47a1;">Loading...</div>
        </div>
        <script>
            setInterval(function() {
                const now = new Date();
                const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
                document.getElementById('clock').innerHTML = now.toLocaleDateString('id-ID', options) + ' WIB';
            }, 1000);
        </script>
        <div class="footer">Aplikasi by Haris Adz Dzimari &copy; 2025</div>
    """, unsafe_allow_html=True)

def create_simple_docx(title, content, sekolah):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(f"Sekolah: {sekolah}")
    doc.add_paragraph("_"*50)
    doc.add_paragraph(content)
    buf = BytesIO(); doc.save(buf); buf.seek(0)
    return buf

def create_modul_docx(data):
    doc = Document()
    for s in doc.sections: s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Cm(2.54)
    if data['logo']:
        try: doc.add_picture(data['logo'], width=Inches(1.0)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        except: pass
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"MODUL AJAR KURIKULUM MERDEKA\n{data['sekolah']}\n")
    r.bold = True; r.font.size = Pt(14)
    p.add_run(f"{data['alamat']}").font.size = Pt(10)
    doc.add_paragraph("_"*85)

    # Isi Dokumen (Sama seperti sebelumnya, dipersingkat)
    doc.add_heading('I. INFORMASI UMUM', 1)
    table = doc.add_table(rows=0, cols=2); table.style = 'Table Grid'
    info = [("Penyusun", data['guru']), ("Tahun", str(data['tanggal'].year)), ("Kelas", f"{data['kelas']} ({data['fase']})"), ("Mapel", data['mapel']), ("Topik", data['topik'])]
    for k,v in info: r=table.add_row(); r.cells[0].text=k; r.cells[1].text=v
    
    doc.add_heading('II. KOMPONEN INTI', 1)
    doc.add_paragraph(f"Tujuan: {data['tujuan']}")
    doc.add_paragraph(f"Pemantik: {data['pemantik']}")
    
    doc.add_heading('III. KEGIATAN', 1)
    doc.add_paragraph(data['bahan'])
    doc.add_paragraph(data['lkpd'])
    
    doc.add_heading('IV. EVALUASI', 1)
    doc.add_paragraph(data['soal'])
    doc.add_paragraph(data['kunci'])
    
    doc.add_page_break(); doc.add_heading('V. ABSENSI', 1)
    t_absen = doc.add_table(rows=1, cols=5); t_absen.style = 'Table Grid'
    hdr = t_absen.rows[0].cells; hdr[0].text="No"; hdr[1].text="Nama"; hdr[2].text="Hadir"; hdr[3].text="Ket"
    for i, nm in enumerate(data['siswa_list'] if data['siswa_list'] else [""]*25):
        r = t_absen.add_row().cells; r[0].text=str(i+1); r[1].text=nm.strip()

    buf = BytesIO(); doc.save(buf); buf.seek(0)
    return buf

# ==========================================
# 5. HALAMAN FITUR (OFFLINE MODE)
# ==========================================
def menu_modul_ajar(nama_sekolah, alamat_sekolah, kepsek, uploaded_logo):
    st.subheader("📂 Generator Modul Ajar (Mode Cepat)")
    st.info("💡 Mode Template aktif: Menghasilkan format baku secara instan (Edit detail materi di Word nanti).")
    
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(["1️⃣ Identitas", "2️⃣ Inti", "3️⃣ Bahan & LKPD", "4️⃣ Evaluasi", "5️⃣ Asesmen", "6️⃣ Glosarium", "7️⃣ Refleksi"])

    with t1:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: 
            nama_guru = st.text_input("Nama Guru", value=st.session_state.get('nama_guru', ''))
            tanggal = st.date_input("Tanggal")
            mapel = st.text_input("Mapel", value=st.session_state.get('mapel', ''), placeholder="Contoh: IPAS")
        with c2: 
            fase = st.selectbox("Fase", ["Fase A (Kls 1-2)", "Fase B (Kls 3-4)", "Fase C (Kls 5-6)"])
            kelas = st.selectbox("Kelas", ["1","2","3","4","5","6"])
            alokasi = st.text_input("Alokasi Waktu", value="2 JP")
        cp = st.text_area("Capaian Pembelajaran (CP):", height=100)
        st.markdown("</div>", unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        col_inti_1, col_inti_2 = st.columns(2)
        with col_inti_1:
            st.markdown("### 📚 Materi & Tujuan")
            topik = st.text_input("Topik / Bab", value=st.session_state.get('topik', ''))
            model = st.selectbox("Model", ["PBL", "PjBL", "Discovery", "Inquiry"])
            
            if st.button("⚡ Generate Tujuan Otomatis"):
                manage_stats('generate')
                st.session_state['tujuan_ai'] = generate_content_template("tujuan", mapel, topik, fase, kelas, model)
                st.session_state['pemantik_ai'] = generate_content_template("pemantik", mapel, topik, fase, kelas, model)
                st.success("Tujuan berhasil dibuat!")
                
            tujuan = st.text_area("Tujuan Pembelajaran (TP)", value=st.session_state.get('tujuan_ai', ''), height=150)
            pemantik = st.text_input("Pemantik", value=st.session_state.get('pemantik_ai', ''))

        with col_inti_2:
            st.markdown("### 👤 Profil & Diferensiasi")
            profil = st.multiselect("Profil Pelajar", ["Beriman", "Mandiri", "Bernalar Kritis", "Kreatif", "Gotong Royong"], default=["Mandiri"])
            remedial = st.text_area("Remedial:", value="Bimbingan perorangan ulang.", height=80)
            pengayaan = st.text_area("Pengayaan:", value="Tugas proyek tambahan.", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("⚡ Generate Materi & LKPD Otomatis"):
            manage_stats('generate')
            st.session_state['materi_ai'] = generate_content_template("materi", mapel, topik, fase, kelas, model)
            st.session_state['lkpd_ai'] = generate_content_template("lkpd", mapel, topik, fase, kelas, model)
            st.success("Materi & LKPD siap!")
            
        bahan = st.text_area("Materi:", value=st.session_state.get('materi_ai', ''), height=200)
        lkpd = st.text_area("LKPD:", value=st.session_state.get('lkpd_ai', ''), height=200)
        media = st.text_area("Media Ajar:", value="Buku Paket, Video, LCD Proyektor", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    with t4:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        if st.button("⚡ Generate Soal Otomatis"):
            manage_stats('generate')
            st.session_state['soal_ai'] = generate_content_template("soal", mapel, topik, fase, kelas, model)
            st.session_state['kunci_ai'] = generate_content_template("kunci", mapel, topik, fase, kelas, model)
            st.success("Soal siap!")
            
        soal = st.text_area("Soal:", value=st.session_state.get('soal_ai', ''), height=250)
        kunci = st.text_area("Kunci:", value=st.session_state.get('kunci_ai', ''), height=250)
        st.markdown("</div>", unsafe_allow_html=True)

    with t5:
        st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
        teknik_nilai = st.multiselect("Teknik Penilaian", ["Tes Tulis", "Observasi"], default=["Tes Tulis"])
        st.write("Daftar Siswa (Copy-Paste dari Excel):")
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
        ref_guru = st.text_area("Refleksi Guru:", height=100)
        ref_siswa = st.text_area("Refleksi Siswa:", height=100)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DOWNLOAD ---
    st.success("✅ Dokumen Siap Unduh")
    data_export = {
        'logo': uploaded_logo, 'sekolah': nama_sekolah, 'alamat': alamat_sekolah, 'kepsek': kepsek,
        'guru': nama_guru, 'mapel': mapel, 'kelas': kelas, 'fase': fase, 'tanggal': tanggal, 'alokasi': alokasi,
        'cp': cp, 'topik': topik, 'model': model, 'tujuan': tujuan, 'pemantik': pemantik,
        'profil': profil, 'remedial': remedial, 'pengayaan': pengayaan,
        'bahan': bahan, 'lkpd': lkpd, 'media': media, 'soal': soal, 'kunci': kunci,
        'teknik_nilai': teknik_nilai,
        'siswa_list': siswa_list, 'pustaka': pustaka, 'glosarium': glosarium, 
        'ref_guru': ref_guru, 'ref_siswa': ref_siswa
    }
    st.download_button("📄 DOWNLOAD WORD (.DOCX)", create_modul_docx(data_export), f"Modul_{topik}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

def menu_atp(nama_sekolah):
    st.subheader("🗺️ Generator ATP")
    st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
    mapel = st.text_input("Mata Pelajaran")
    topik = st.text_input("Topik Utama")
    kelas = st.selectbox("Kelas ATP", ["1", "2", "3", "4", "5", "6"])
    
    if st.button("⚡ Generate ATP"):
        manage_stats('generate')
        st.session_state['atp_res'] = generate_content_template("atp", mapel, topik, "", kelas, "")
    
    if 'atp_res' in st.session_state:
        st.text_area("Hasil ATP:", value=st.session_state['atp_res'], height=300)
        st.download_button("📥 Simpan ATP (.docx)", create_simple_docx("ALUR TUJUAN PEMBELAJARAN", st.session_state['atp_res'], nama_sekolah), "ATP.docx")
    st.markdown("</div>", unsafe_allow_html=True)

def menu_prota(nama_sekolah):
    st.subheader("📅 Generator Prota")
    st.markdown("<div class='skeuo-card'>", unsafe_allow_html=True)
    mapel = st.text_input("Mapel Prota")
    kelas = st.selectbox("Kelas Prota", ["1", "2", "3", "4", "5", "6"])
    
    if st.button("⚡ Generate Prota"):
        manage_stats('generate')
        st.session_state['prota_res'] = generate_content_template("prota", mapel, "[Topik Umum]", "", kelas, "")
    
    if 'prota_res' in st.session_state:
        st.text_area("Hasil Prota:", value=st.session_state['prota_res'], height=300)
        st.download_button("📥 Simpan Prota (.docx)", create_simple_docx("PROGRAM TAHUNAN", st.session_state['prota_res'], nama_sekolah), "Prota.docx")
    st.markdown("</div>", unsafe_allow_html=True)

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
        
        st.divider()
        st.write("<b>Identitas Sekolah:</b>", unsafe_allow_html=True)
        uploaded_logo = st.file_uploader("Upload Logo", type=['png', 'jpg'])
        nama_sekolah = st.text_input("Sekolah", value="SD MUHAMMADIYAH 8 TULANGAN")
        alamat_sekolah = st.text_area("Alamat", value="Jl. Raya Kenongo RT. 02 RW. 01 Tulangan Sidoarjo")
        kepsek = st.text_input("Kepala Sekolah", value="Muhammad Saifudin Zuhri, M.Pd.")
        
        if st.button("Logout"): 
            st.session_state['logged_in'] = False; st.query_params.clear(); st.rerun()

    if menu == "📂 Modul Ajar": menu_modul_ajar(nama_sekolah, alamat_sekolah, kepsek, uploaded_logo)
    elif menu == "🗺️ Generator ATP": menu_atp(nama_sekolah)
    elif menu == "📅 Generator Prota": menu_prota(nama_sekolah)

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
