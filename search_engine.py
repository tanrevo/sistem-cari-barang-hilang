import database as db


def proses_pencarian(
    keyword="",
    filter_status="Semua",
    filter_jenis="Semua",
    urutan="Terbaru",
):
    semua_data = db.muat_data()
    hasil = []
    kata_kunci = keyword.lower().strip()

    for item in semua_data:
        cocok_status = (
            filter_status == "Semua" or item.get("status") == filter_status
        )
        cocok_jenis = (
            filter_jenis == "Semua" or item.get("jenis_laporan") == filter_jenis
        )

        if kata_kunci == "":
            cocok_keyword = True
        else:
            nama = item.get("nama_barang", "").lower()
            lokasi = item.get("detail_lokasi", "").lower()
            ciri = item.get("detail_barang", "").lower()
            cocok_keyword = (
                kata_kunci in nama or kata_kunci in lokasi or kata_kunci in ciri
            )

        if cocok_status and cocok_jenis and cocok_keyword:
            hasil.append(item)

    if urutan == "Terbaru":
        hasil.sort(key=lambda x: x["id"], reverse=True)
    else:
        hasil.sort(key=lambda x: x["id"], reverse=False)

    return hasil


def hitung_statistik():
    semua_data = db.muat_data()
    total = len(semua_data)
    belum_ketemu = sum(
        1 for item in semua_data if item.get("status") == "Belum Ditemukan"
    )
    sudah_ketemu = sum(
        1 for item in semua_data if item.get("status") == "Sudah Ditemukan"
    )

    return {
        "total": total,
        "belum": belum_ketemu,
        "sudah": sudah_ketemu,
    }