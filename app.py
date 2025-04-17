import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- KONEKSI DATABASE ---
def get_connection():
    return psycopg2.connect(
        host="shuttle.proxy.rlwy.net",
        database="railway",
        user="postgres",
        password="RNCRzYyNwkvCmYnyJtJUOfrxwqWXpzjh",
        port=25419
    )

# --- FUNGSI DB ---
def get_summary_barang():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT b.id, b.nama, b.stok, MAX(w.tanggal) AS tanggal_terakhir
        FROM barang b
        LEFT JOIN barang_waktu w ON b.id = w.barang_id
        GROUP BY b.id, b.nama, b.stok
        ORDER BY b.id
    """, conn)
    conn.close()
    return df

def get_detail_barang(barang_id):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT tanggal, waktu
        FROM barang_waktu
        WHERE barang_id = %s
        ORDER BY tanggal DESC, waktu DESC
    """, conn, params=(barang_id,))
    conn.close()
    return df

def tambah_barang(nama, stok):
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now()
    tanggal = now.date()
    waktu = now.time()

    # Tambah ke tabel barang
    cur.execute("INSERT INTO barang (nama, stok, tanggal) VALUES (%s, %s, %s) RETURNING id", (nama, stok, now))
    barang_id = cur.fetchone()[0]

    # Tambah ke barang_waktu
    cur.execute("INSERT INTO barang_waktu (barang_id, tanggal, waktu) VALUES (%s, %s, %s)", (barang_id, tanggal, waktu))

    conn.commit()
    conn.close()

# --- TAMPILAN UTAMA ---
st.set_page_config(page_title="Inventory Management", layout="wide")
st.title("📦 Inventory Summary")

menu = ["Dashboard", "Tambah Barang"]
selected = st.radio("Menu", menu, horizontal=True)

if selected == "Dashboard":
    st.subheader("📊 Ringkasan Barang")

    df_summary = get_summary_barang()
    st.dataframe(df_summary, use_container_width=True)

    with st.expander("📋 Detail Waktu Input Barang"):
        barang_list = df_summary['nama'].tolist()
        barang_dict = dict(zip(df_summary['nama'], df_summary['id']))
        pilihan = st.selectbox("Pilih Barang", barang_list)

        if pilihan:
            detail_df = get_detail_barang(barang_dict[pilihan])
            st.write(f"🕒 Detail Waktu Input untuk **{pilihan}**")
            st.dataframe(detail_df)

elif selected == "Tambah Barang":
    st.subheader("➕ Tambah Barang Baru")
    nama = st.text_input("Nama Barang")
    stok = st.number_input("Stok Awal", min_value=0)

    if st.button("Simpan"):
        if nama:
            tambah_barang(nama, stok)
            st.success("Barang berhasil ditambahkan.")
        else:
            st.warning("Nama barang tidak boleh kosong.")
