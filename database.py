import json
import os
from datetime import datetime

from utils import hapus_foto, hash_pin

FILE_DB = "data_barang.json"

# Status yang boleh dipakai di seluruh aplikasi
STATUS_VALID = ["Hilang", "Ditemukan", "Sudah Kembali ke Pemilik"]


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


# ---------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------
def tambah_barang(
    nama_barang,
    kategori,
    lokasi,
    status,
    kontak_pelapor,
    keterangan="",
    nama_pelapor="",
    foto="",
    pin="",
):
    """Menambahkan laporan barang hilang atau ditemukan ke database.

    status      : 'Hilang' atau 'Ditemukan'
    foto        : path foto dari simpan_foto() di utils.py ("" jika tanpa foto)
    pin         : kode rahasia pelapor, dipakai untuk ubah status / hapus laporan
    Melempar ValueError jika input tidak valid.
    """
    if not nama_barang.strip() or not lokasi.strip() or not kontak_pelapor.strip():
        raise ValueError("Nama barang, lokasi, dan kontak wajib diisi.")
    if status not in ("Hilang", "Ditemukan"):
        raise ValueError("Status awal harus 'Hilang' atau 'Ditemukan'.")
    if len(str(pin)) < 4:
        raise ValueError("PIN minimal 4 karakter.")

    data = muat_data()

    id_baru = 1 if len(data) == 0 else data[-1]["id"] + 1

    barang_baru = {
        "id": id_baru,
        "nama_barang": nama_barang.strip(),
        "kategori": kategori,
        "lokasi": lokasi.strip(),
        "status": status,
        "nama_pelapor": nama_pelapor.strip(),
        "kontak_pelapor": kontak_pelapor.strip(),
        "keterangan": keterangan.strip(),
        "foto": foto,
        "pin": hash_pin(pin),
        "tanggal_lapor": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tanggal_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    data.append(barang_baru)
    simpan_data(data)
    return barang_baru


# ---------------------------------------------------------------
# READ
# ---------------------------------------------------------------
def ambil_barang(id_barang):
    """Mengambil satu barang berdasarkan id. Mengembalikan None jika tidak ada."""
    for item in muat_data():
        if item["id"] == id_barang:
            return item
    return None


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


# ---------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------
def cek_pin(item, pin):
    """True jika PIN yang dimasukkan sama dengan PIN saat melapor."""
    return item.get("pin") == hash_pin(pin)


def ubah_status_barang(id_barang, status_baru, pin):
    """Mengubah status barang, hanya jika PIN benar.

    Contoh: dari 'Hilang' menjadi 'Sudah Kembali ke Pemilik'.
    Mengembalikan True jika berhasil, False jika barang tidak ada atau PIN salah.
    """
    if status_baru not in STATUS_VALID:
        raise ValueError(f"Status harus salah satu dari: {', '.join(STATUS_VALID)}")

    data = muat_data()
    for item in data:
        if item["id"] == id_barang:
            if not cek_pin(item, pin):
                return False
            item["status"] = status_baru
            item["tanggal_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            simpan_data(data)
            return True
    return False


# ---------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------
def hapus_barang(id_barang, pin):
    """Menghapus laporan (misalnya karena salah input), hanya jika PIN benar.
    Foto barang ikut dihapus dari folder uploads.
    Mengembalikan True jika berhasil, False jika barang tidak ada atau PIN salah.
    """
    data = muat_data()
    for item in data:
        if item["id"] == id_barang:
            if not cek_pin(item, pin):
                return False
            data.remove(item)
            simpan_data(data)
            hapus_foto(item.get("foto", ""))
            return True
    return False


if __name__ == "__main__":
    print("Testing database.py...")
    a = tambah_barang(
        "Kunci Motor Honda", "Kunci", "Parkiran Gedung B", "Ditemukan",
        "08123456789", "Gantungan kunci boneka kecil",
        nama_pelapor="Budi", pin="1234",
    )
    b = tambah_barang(
        "Tumbler Corkcicle Hitam", "Botol Minum", "Kantin Utama", "Hilang",
        "08987654321", "Ada stiker kucing",
        nama_pelapor="Ani", pin="5678",
    )
    print("Ubah status, PIN salah :", ubah_status_barang(b["id"], "Sudah Kembali ke Pemilik", "0000"))
    print("Ubah status, PIN benar :", ubah_status_barang(b["id"], "Sudah Kembali ke Pemilik", "5678"))
    print("Hapus, PIN benar       :", hapus_barang(a["id"], "1234"))
    print("Isi database saat ini  :", muat_data())