import hashlib
import os
from datetime import datetime

FOLDER_FOTO = os.path.join("uploads", "barang")
EKSTENSI_FOTO = (".jpg", ".jpeg", ".png")


def simpan_foto(file_foto):
    """Menyimpan foto yang diupload ke folder uploads/barang.

    file_foto adalah objek dari st.file_uploader (punya .name dan .getvalue()).
    Mengembalikan path foto yang tersimpan, atau "" jika tidak ada foto.
    """
    if file_foto is None:
        return ""

    ekstensi = os.path.splitext(file_foto.name)[1].lower()
    if ekstensi not in EKSTENSI_FOTO:
        raise ValueError("Format foto harus JPG atau PNG.")

    os.makedirs(FOLDER_FOTO, exist_ok=True)

    # Nama file dibuat unik dari waktu upload supaya foto tidak saling menimpa
    nama_file = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ekstensi
    path_foto = os.path.join(FOLDER_FOTO, nama_file)

    with open(path_foto, "wb") as file:
        file.write(file_foto.getvalue())

    return path_foto


def hapus_foto(path_foto):
    """Menghapus file foto dari folder uploads jika ada."""
    if path_foto and os.path.exists(path_foto):
        os.remove(path_foto)


def hash_pin(pin):
    """Mengubah PIN menjadi kode acak (hash) supaya PIN asli tidak tersimpan di file JSON."""
    return hashlib.sha256(str(pin).encode("utf-8")).hexdigest()