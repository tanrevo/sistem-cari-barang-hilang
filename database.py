import json
import os
from datetime import datetime


FILE_DB = "data_barang.json"


def muat_data():
    """Membaca semua data barang dari file JSON.
    Jika file belum ada, otomatis membuat file baru berisi list kosong [].
    """
    if not os.path.exists(FILE_DB):
        simpan_data([])
        return []

    try:
        with open(FILE_DB, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
      
        return []


def simpan_data(data):
    """Menyimpan list data ke dalam file JSON."""
    with open(FILE_DB, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def tambah_barang(
    nama_barang, kategori, lokasi, status, kontak_pelapor, keterangan=""
):
    """Menambahkan laporan barang hilang atau ditemukan ke database.
    Parameter 'status' bisa diisi: 'Hilang' atau 'Ditemukan'
    """
    data = muat_data()

   
    id_baru = 1 if len(data) == 0 else data[-1]["id"] + 1

    barang_baru = {
        "id": id_baru,
        "nama_barang": nama_barang,
        "kategori": kategori,
        "lokasi": lokasi,
        "status": status, 
        "kontak_pelapor": kontak_pelapor,
        "keterangan": keterangan,
        "tanggal_lapor": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    data.append(barang_baru)
    simpan_data(data)
    return barang_baru


def cari_barang(keyword="", filter_status="Semua"):
    """Mencari barang berdasarkan kata kunci (nama/lokasi/kategori) dan filter status."""
    data = muat_data()
    hasil = []
    keyword = keyword.lower().strip()

    for item in data:
        cocok_status = (
            filter_status == "Semua"
            or item["status"].lower() == filter_status.lower()
        )
        cocok_keyword = (
            keyword in item["nama_barang"].lower()
            or keyword in item["lokasi"].lower()
            or keyword in item["kategori"].lower()
            or keyword in item["keterangan"].lower()
        )

        if cocok_status and cocok_keyword:
            hasil.append(item)

    return hasil


def ubah_status_barang(id_barang, status_baru):
    """Mengubah status barang (misal dari 'Hilang' menjadi 'Sudah Dikembalikan')."""
    data = muat_data()
    for item in data:
        if item["id"] == id_barang:
            item["status"] = status_baru
            simpan_data(data)
            return True
    return False


def hapus_barang(id_barang):
    """Menghapus data barang berdasarkan ID-nya."""
    data = muat_data()
    data_baru = [item for item in data if item["id"] != id_barang]

    if len(data_baru) < len(data):
        simpan_data(data_baru)
        return True
    return False



if __name__ == "__main__":
    print("Testing database.py...")
    tambah_barang(
        "Kunci Motor Honda \n",
        "Kunci\n",
        "Parkiran Gedung B\n",
        "Ditemukan\n",
        "08123456789\n",
        "Gantungan kunci boneka kecil\n",
    )
    tambah_barang(
        "Tumbler Corkcicle Hitam\n",
        "Botol Minum\n",
        "Kantin Utama\n",
        "Hilang\n",
        "08987654321\n",
        "Ada stiker kucing\n",
    )
    print("Isi database saat ini:", muat_data())