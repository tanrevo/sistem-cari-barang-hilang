import os
import database as db
import search_engine as se
import streamlit as st

st.set_page_config(page_title="Cari Barang Hilang", page_icon="🔍", layout="wide")

st.title("🔍 Sistem Informasi Cari & Temukan Barang Hilang")
st.caption("Laporkan barang yang hilang atau barang temuan di sekitar kampus.")

tab_daftar, tab_tambah = st.tabs(
    ["📋 Daftar & Cari Barang", "➕ Buat Laporan Baru"]
)

# ==========================================
# TAB 1: DAFTAR, PENCARIAN & UPDATE STATUS
# ==========================================
with tab_daftar:
    # 1. Ringkasan Statistik di bagian atas
    stat = se.hitung_statistik()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Laporan", f"{stat['total']} Barang")
    m2.metric("Belum Ditemukan", f"{stat['belum']} Barang")
    m3.metric("Sudah Ditemukan", f"{stat['sudah']} Barang")

    st.divider()

    # 2. Baris Kontrol Pencarian & Filter (4 Kolom)
    col_cari, col_jenis, col_status, col_urut = st.columns([2.2, 1.2, 1.2, 1])
    with col_cari:
        keyword = st.text_input(
            "🔍 Cari Barang",
            placeholder="Ketik nama barang, ciri-ciri, atau lokasi...",
        )
    with col_jenis:
        filter_jenis = st.selectbox(
            "Jenis Laporan",
            ["Semua", "Kehilangan Barang", "Menemukan Barang"],
        )
    with col_status:
        filter_status = st.selectbox(
            "Status Barang", ["Semua", "Belum Ditemukan", "Sudah Ditemukan"]
        )
    with col_urut:
        urutan = st.selectbox("Urutkan", ["Terbaru", "Terlama"])

    # 3. Panggil mesin pencari dari search_engine.py
    daftar_barang = se.proses_pencarian(
        keyword=keyword,
        filter_status=filter_status,
        filter_jenis=filter_jenis,
        urutan=urutan,
    )

    st.caption(f"Menampilkan **{len(daftar_barang)}** hasil pencarian.")
    st.divider()

    # 4. Menampilkan daftar kartu barang hasil pencarian
    if not daftar_barang:
        st.info("Belum ada data barang yang sesuai dengan pencarian.")
    else:
        for item in daftar_barang:
            with st.container(border=True):
                col_foto, col_info, col_aksi = st.columns([1.2, 2.5, 1.3])

                # Kolom Foto
                with col_foto:
                    if item["path_foto"] and os.path.exists(item["path_foto"]):
                        st.image(item["path_foto"], use_container_width=True)
                    else:
                        st.markdown(
                            "<div style='height:150px; background:#262730; display:flex; align-items:center; justify-content:center; border-radius:8px; color:#888;'>Tidak ada foto</div>",
                            unsafe_allow_html=True,
                        )

                # Kolom Detail Barang
                with col_info:
                    badge_warna = (
                        "🟢" if item["status"] == "Sudah Ditemukan" else "🔴"
                    )
                    st.subheader(f"{item['nama_barang']}")
                    st.markdown(
                        f"**{badge_warna} Status:** `{item['status']}` | **Kategori:** `{item['jenis_laporan']}`"
                    )
                    st.write(f"📍 **Detail Lokasi:** {item['detail_lokasi']}")
                    st.write(f"📝 **Detail Barang:** {item['detail_barang']}")
                    st.write(
                        f"📞 **Kontak Pelapor/Penemu:** `{item['kontak']}`"
                    )
                    st.caption(f"Dilaporkan pada: {item['waktu']}")

                # Kolom Ubah Status oleh Pelapor
                with col_aksi:
                    st.write("**Update Status:**")
                    status_sekarang = item["status"]
                    pilihan_status = ["Belum Ditemukan", "Sudah Ditemukan"]
                    index_default = pilihan_status.index(status_sekarang)

                    status_baru = st.selectbox(
                        "Ubah status",
                        pilihan_status,
                        index=index_default,
                        key=f"select_{item['id']}",
                        label_visibility="collapsed",
                    )

                    if st.button("Simpan Status", key=f"btn_{item['id']}"):
                        db.ubah_status(item["id"], status_baru)
                        st.success("Status diperbarui!")
                        st.rerun()

# ==========================================
# TAB 2: FORM TAMBAH BARANG HILANG / TEMUAN
# ==========================================
with tab_tambah:
    st.subheader("Form Laporan Barang")
    with st.form("form_laporan", clear_on_submit=True):
        nama_barang = st.text_input(
            "Nama Barang *", placeholder="Contoh: Dompet Kulit Coklat"
        )

        col1, col2 = st.columns(2)
        with col1:
            jenis_laporan = st.selectbox(
                "Jenis Laporan *", ["Kehilangan Barang", "Menemukan Barang"]
            )
        with col2:
            status_awal = st.selectbox(
                "Status Saat Ini *", ["Belum Ditemukan", "Sudah Ditemukan"]
            )

        detail_lokasi = st.text_input(
            "Detail Lokasi *",
            placeholder="Contoh: Meja paling pojok Kantin Gedung A",
        )
        detail_barang = st.text_area(
            "Detail / Ciri-ciri Barang *",
            placeholder="Contoh: Warna hitam, ada gantungan kunci huruf R, isi KTM",
        )
        kontak = st.text_input(
            "Kontak Penemu / Pelapor (WA / IG / ID Line) *",
            placeholder="Contoh: WA 08123456789",
        )
        foto = st.file_uploader(
            "Upload Foto Barang (Opsional)", type=["jpg", "jpeg", "png"]
        )

        submit = st.form_submit_button("Kirim Laporan", type="primary")

        if submit:
            if (
                not nama_barang
                or not detail_lokasi
                or not detail_barang
                or not kontak
            ):
                st.error("Semua kolom bertanda bintang (*) wajib diisi!")
            else:
                path_foto = db.simpan_foto(foto)
                db.tambah_barang(
                    nama_barang=nama_barang,
                    jenis_laporan=jenis_laporan,
                    status=status_awal,
                    detail_lokasi=detail_lokasi,
                    detail_barang=detail_barang,
                    kontak=kontak,
                    path_foto=path_foto,
                )
                st.success(
                    "Laporan berhasil ditambahkan! Cek di tab 'Daftar & Cari Barang'."
                )