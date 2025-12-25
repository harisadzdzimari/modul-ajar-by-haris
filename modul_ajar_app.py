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
st.set_page_config(page_title="Sultan AI - Modul Ajar", layout="wide", page_icon="🏫")

# --- CSS UNTUK TAMPILAN MODERN ---
st.markdown("""
<style>
    .stTextInput > label {font-weight: bold; color: #333;}
    .stTextArea > label {font-weight: bold; color: #333;}
    .login-box {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI AI GEMINI ---
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

# --- FUNGSI GENERATE WORD (.DOCX) ---
def create_docx(data):
    doc = Document()
    
    # Atur Margin A4
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)

    # KOP SURAT
    if data['logo'] is not None:
        try:
            doc.add_picture(data['logo'], width=Inches(0.8))
        except: pass

    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header.add_run(f"MODUL AJAR KURIKULUM MERDEKA\n{data['sekolah']}\n")
    run.bold = True; run.font.size = Pt(14)
    header.add_run(f"{data['alamat']}").font.size = Pt(10)
    doc.add_paragraph("_"*85)

    # INFORMASI UMUM
    doc.add_heading('I. INFORMASI UMUM', level=1)
    table = doc.add_table(rows=0, cols=2)
    table.style = 'Table Grid'
    
    infos = [
        ("Penyusun", data['guru']), 
        ("Tahun", str(data['tanggal'].year)), 
        ("Jenjang/Kelas", f"SD / {data['kelas']} ({data['fase']})"), 
        ("Mata Pelajaran", data['mapel']), 
        ("Topik", data['topik']), 
        ("Alokasi Waktu", data['alokasi']), 
        ("Model", data['model'])
    ]
    
    for k, v in infos:
        r = table.add_row()
        r.cells[0].text = k
        r.cells[0].paragraphs[0].runs[0].bold = True
        r.cells[1].text = v

    doc.add_paragraph(f"\nCapaian Pembelajaran (CP): {data['cp']}")
    doc.add_paragraph(f"Profil Pelajar: {', '.join(data['dimensi'])}")

    # KOMPONEN INTI
    doc.add_heading('II. KOMPONEN INTI', level=1)
    doc.add_heading('A. Tujuan Pembelajaran', level=2)
    doc.add_paragraph(data['tujuan'])
    doc.add_heading('B. Pemantik', level=2)
    doc.add_paragraph(data['pemantik'])
    
    # LAMPIRAN
    doc.add_page_break()
    doc.add_heading('III. LAMPIRAN', level=1)
    doc.add_heading('1. Bahan Ajar', level=2)
    doc.add_paragraph(data['bahan'])
    doc.add_heading('2. LKPD', level=2)
    doc.add_paragraph(data['lkpd'])
    doc.add_heading('3. Soal Evaluasi', level=2)
    doc.add_paragraph(data['soal'])
    
    # RUBRIK PENILAIAN
    doc.add_heading('4. Rubrik Penilaian Sikap', level=2)
    t_rubrik = doc.add_table(rows=1, cols=5)
    t_rubrik.style = 'Table Grid'
    hdr = t_rubrik.rows[0].cells
    for i, h in enumerate(['Dimensi', 'Sangat Baik (4)', 'Baik (3)', 'Cukup (2)', 'Kurang (1)']):
        hdr[i].text = h
        hdr[i].paragraphs[0].runs[0].bold = True
    
    for dim in data['dimensi']:
        row = t_rubrik.add_row().cells
        row[0].text = dim
        row[1].text = "Membudaya"
        row[2].text = "Berkembang"
        row[3].text = "Mulai Terlihat"
        row[4].text = "Belum Terlihat"

    # TANDA TANGAN
    doc.add_paragraph("\n\n")
    ttd = doc.add_table(rows=1, cols=2)
    ttd.rows[0].cells[0].text = f"Mengetahui,\nKepala Sekolah\n\n\n( {data['kepsek']} )\nNIP. {data['nip']}"
    ttd.rows[0].cells[1].text = f"Sidoarjo, {data['tanggal'].strftime('%d %B %Y')}\nGuru Mata Pelajaran\n\n\n( {data['guru']} )"
    ttd.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- FUNGSI GENERATE PDF (.PDF) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'MODUL AJAR KURIKULUM MERDEKA', 0, 1, 'C')
        self.ln(5)

def create_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Isi Konten Sederhana
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

# --- FUNGSI LOGIN ---
def login_page():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='login-box'>
                <h2 style='color: #0d47a1;'>🏫 SISTEM SEKOLAH PRO</h2>
                <p style='color: #666;'>SD MUHAMMADIYAH 8 TULANGAN</p>
                <hr>
            </div>
            """, unsafe_allow_html=True
        )
        
        username = st.text_input("Username", placeholder="Masukkan ID Guru")
        password = st.text_input("Password", type="password", placeholder="Masukkan Kata Sandi")
        
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

# --- APLIKASI UTAMA ---
def main_app():
    # --- HEADER MEWAH ---
    st.markdown(
        """
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #0d47a1, #1976d2); border-radius: 15px; margin-bottom: 25px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h1 style='margin:0; font-size: 2.5rem;'>🏫 SISTEM PERANGKAT AJAR TERPADU</h1>
            <h3 style='margin-top:10px; font-weight: 300;'>SD MUHAMMADIYAH 8 TULANGAN | KURIKULUM MERDEKA</h3>
        </div>
        """, unsafe_allow_html=True
    )

    # --- SIDEBAR ---
    with st.sidebar:
        st.write(f"👤 Login sebagai: **{st.session_state.get('user_name', 'Guru')}**")
        if st.button("Logout", type="secondary"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.divider()
        st.header("🤖 Konfigurasi AI")
        
        # --- PERBAIKAN: OTOMATIS BACA SECRETS (GITHUB/CLOUD) ---
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ Terhubung otomatis (Secrets Cloud)")
        else:
            api_key = st.text_input("Gemini API Key", type="password", placeholder="Tempel API Key di sini")
            st.info("💡 Isi manual jika dijalankan di komputer lokal.")
        # -------------------------------------------------------

        st.divider()
        st.header("⚙️ Identitas Sekolah")
        uploaded_logo = st.file_uploader("Upload Logo", type=['png', 'jpg'])
        nama_sekolah = st.text_input("Nama Sekolah", value="SD MUHAMMADIYAH 8 TULANGAN")
        alamat_sekolah = st.text_area("Alamat", value="Jl. Raya Kenongo RT. 02 RW. 01 Tulangan Sidoarjo")
        kepsek = st.text_input("Kepala Sekolah", value="MUHAMMAD SAIFUDIN ZUHRI, M.Pd.")
        nip_kepsek = st.text_input("NIP/NBM", value="-")

    # --- TAB MENU ---
    tab_names = ["1️⃣ Identitas & CP", "2️⃣ Komponen Inti (AI)", "3️⃣ Bahan & LKPD (AI)", 
                 "4️⃣ Evaluasi (AI)", "5️⃣ Asesmen", "6️⃣ Glosarium", "7️⃣ Refleksi"]
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(tab_names)

    # --- TAB 1: IDENTITAS ---
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            nama_guru = st.text_input("Nama Guru", placeholder="Nama Lengkap & Gelar")
            tanggal = st.date_input("Tanggal", datetime.date.today())
            mapel = st.text_input("Mapel", placeholder="Contoh: IPAS")
        with c2:
            fase = st.selectbox("Fase", ["Fase A (Kls 1-2)", "Fase B (Kls 3-4)", "Fase C (Kls 5-6)"])
            if "Fase A" in fase: ops_kelas = ["Kelas 1", "Kelas 2"]
            elif "Fase B" in fase: ops_kelas = ["Kelas 3", "Kelas 4"]
            else: ops_kelas = ["Kelas 5", "Kelas 6"]
            kelas = st.selectbox("Kelas", ops_kelas)
            alokasi = st.text_input("Alokasi Waktu", value="2 JP (2 x 35 Menit)")
        
        st.markdown("---")
        cp_text = st.text_area("Capaian Pembelajaran (CP):", height=80, 
                               placeholder="Salin CP dari dokumen resmi...")

    # --- TAB 2: KOMPONEN INTI (DENGAN AI) ---
    with t2:
        col_inti, col_dif = st.columns(2)
        with col_inti:
            st.subheader("Materi & Tujuan")
            topik = st.text_input("Topik / Bab", placeholder="Contoh: Rantai Makanan")
            model = st.selectbox("Model Pembelajaran", ["Deep Learning", "PjBL", "PBL", "Discovery Learning", "Inquiry"])
            
            # --- AI BUTTON UNTUK TUJUAN ---
            c_ai_tp1, c_ai_tp2 = st.columns([1, 3])
            with c_ai_tp1:
                if st.button("✨ Bantu Buat Tujuan", help="Klik untuk membuat Tujuan Pembelajaran otomatis"):
                    if not topik:
                        st.warning("Isi Topik dulu!")
                    elif not api_key:
                        st.error("API Key belum terisi!")
                    else:
                        with st.spinner("AI sedang berpikir..."):
                            prompt = f"Buatkan 3 Tujuan Pembelajaran yang spesifik untuk mapel {mapel} topik {topik} kelas {kelas} SD menggunakan model {model}."
                            st.session_state['tujuan_val'] = tanya_gemini(api_key, prompt)
            
            tujuan = st.text_area("Tujuan Pembelajaran (TP)", height=100, 
                                  value=st.session_state.get('tujuan_val', ''),
                                  placeholder="Klik tombol AI atau ketik manual...")
            
            pemantik = st.text_input("Pertanyaan Pemantik", placeholder="Mengapa kita perlu makan?")
            
        with col_dif:
            st.subheader("Profil & Diferensiasi")
            dimensi = st.multiselect("8 Dimensi Profil:", 
                ["Keimanan", "Kewargaan", "Bernalar Kritis", "Kreativitas", 
                 "Kolaborasi", "Kemandirian", "Kesehatan", "Komunikasi"], default=["Bernalar Kritis", "Kolaborasi"])
            
            st.write("---")
            remedial = st.text_area("Remedial:", value="Pendampingan individu dan penyederhanaan materi.", height=60)
            pengayaan = st.text_area("Pengayaan:", value="Tugas proyek tambahan atau tutor sebaya.", height=60)

    # --- TAB 3: BAHAN AJAR (DENGAN AI) ---
    with t3:
        # --- AI BUTTON UNTUK MATERI ---
        c_ai_mat1, c_ai_mat2 = st.columns([1, 4])
        with c_ai_mat1:
            if st.button("✨ Bantu Buat Materi"):
                if not topik: st.warning("Isi Topik dulu!")
                elif not api_key: st.error("API Key kosong!")
                else:
                    with st.spinner("Menulis materi..."):
                        prompt = f"Buatkan ringkasan materi bahan ajar seru dan mudah dipahami untuk anak {kelas} SD tentang {topik}."
                        st.session_state['materi_val'] = tanya_gemini(api_key, prompt)
        
        st.subheader("📖 Ringkasan Bahan Ajar")
        bahan = st.text_area("Materi Singkat:", height=200, 
                             value=st.session_state.get('materi_val', ''),
                             placeholder="Materi akan muncul di sini...")
        
        st.divider()
        st.subheader("📝 Desain LKPD")
        lkpd_instruksi = st.text_area("Petunjuk LKPD:", value="1. Bentuk kelompok.\n2. Amati video.\n3. Diskusikan dan catat hasil pengamatan.")
        media = st.multiselect("Media Ajar:", ["LCD", "Video", "Laptop", "Alat Peraga"], default=["LCD", "Laptop"])

    # --- TAB 4: EVALUASI (DENGAN AI) ---
    with t4:
        # --- AI BUTTON UNTUK SOAL ---
        if st.button("✨ Bantu Buat Soal & Kunci"):
            if not topik: st.warning("Isi Topik dulu!")
            elif not api_key: st.error("API Key kosong!")
            else:
                with st.spinner("Membuat soal..."):
                    prompt_soal = f"Buatkan 5 soal essay pendek tentang {topik} untuk siswa {kelas} SD."
                    st.session_state['soal_val'] = tanya_gemini(api_key, prompt_soal)
                    
                    prompt_kunci = f"Buatkan kunci jawaban singkat untuk 5 soal essay tentang {topik} tersebut."
                    st.session_state['kunci_val'] = tanya_gemini(api_key, prompt_kunci)

        c_soal, c_kunci = st.columns(2)
        with c_soal:
            st.write("❓ **Soal Latihan**")
            soal = st.text_area("Daftar Soal:", height=200, 
                                value=st.session_state.get('soal_val', "1. ...\n2. ..."),
                                placeholder="Soal akan muncul otomatis...")
        with c_kunci:
            st.write("🔑 **Kunci Jawaban**")
            kunci = st.text_area("Kunci Jawaban:", height=200,
                                 value=st.session_state.get('kunci_val', "1. ...\n2. ..."), 
                                 placeholder="Kunci jawaban muncul otomatis...")

    # --- TAB 5: ASESMEN ---
    with t5:
        st.info("ℹ️ Bagian ini akan menghasilkan tabel Rubrik Penilaian di file akhir.")
        teknik_nilai = st.multiselect("Teknik Penilaian:", ["Tes Tulis", "Observasi", "Unjuk Kerja"], default=["Tes Tulis", "Observasi"])
        
        st.write("**Preview Rubrik Sikap (Otomatis):**")
        df_rubrik = pd.DataFrame({
            "Dimensi": dimensi,
            "Skor 4": ["Membudaya" for _ in dimensi],
            "Skor 3": ["Berkembang" for _ in dimensi],
            "Skor 2": ["Mulai Terlihat" for _ in dimensi],
            "Skor 1": ["Belum Terlihat" for _ in dimensi]
        })
        st.table(df_rubrik)

    # --- TAB 6: GLOSARIUM & PUSTAKA ---
    with t6:
        st.subheader("📚 Daftar Pustaka")
        pustaka = st.text_area("Sumber Belajar:", height=80, value="1. Buku Paket Kemdikbud.\n2. Youtube Video Pembelajaran.")
        
        st.subheader("🔤 Glosarium")
        glosarium = st.text_area("Istilah Sulit:", height=80, value="1. .... : ....")

    # --- TAB 7: REFLEKSI ---
    with t7:
        c_ref1, c_ref2 = st.columns(2)
        with c_ref1:
            st.subheader("🤔 Refleksi Guru")
            ref_guru = st.text_area("Pertanyaan Guru:", value="1. Apakah tujuan tercapai?\n2. Apa kendala hari ini?")
        with c_ref2:
            st.subheader("🙋 Refleksi Siswa")
            ref_siswa = st.text_area("Pertanyaan Siswa:", value="1. Apa yang paling disukai?\n2. Apa yang belum paham?")

    # --- TOMBOL GENERATE ---
    st.markdown("---")
    st.success("✅ Data Siap Diunduh")
    
    # Kumpulkan Data
    data_modul = {
        'logo': uploaded_logo, 'sekolah': nama_sekolah, 'alamat': alamat_sekolah, 'kepsek': kepsek, 'nip': nip_kepsek,
        'guru': nama_guru, 'tanggal': tanggal, 'fase': fase, 'kelas': kelas, 'mapel': mapel, 'alokasi': alokasi,
        'cp': cp_text, 'topik': topik, 'model': model, 'tujuan': tujuan, 'pemantik': pemantik,
        'dimensi': dimensi, 'bahan': bahan, 'lkpd': lkpd_instruksi, 'soal': soal
    }

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("📄 DOWNLOAD WORD (.DOCX)", type="primary", use_container_width=True):
            if not nama_guru or not topik:
                st.error("⚠️ Data belum lengkap! Isi Nama Guru dan Topik.")
            else:
                docx_file = create_docx(data_modul)
                st.download_button(
                    label="⬇️ Klik untuk Simpan Word",
                    data=docx_file,
                    file_name=f"Modul_{topik}_{kelas}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    with col_btn2:
        if st.button("📕 DOWNLOAD PDF", use_container_width=True):
            if not nama_guru or not topik:
                st.error("⚠️ Data belum lengkap! Isi Nama Guru dan Topik.")
            else:
                pdf_file = create_pdf(data_modul)
                st.download_button(
                    label="⬇️ Klik untuk Simpan PDF",
                    data=pdf_file,
                    file_name=f"Modul_{topik}_{kelas}.pdf",
                    mime="application/pdf"
                )

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Inisialisasi Session State
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # Cek Status Login
    if not st.session_state['logged_in']:
        login_page()
    else:
        main_app()
