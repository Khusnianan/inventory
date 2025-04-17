import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
from io import BytesIO

# --- KONFIGURASI DATABASE ---
def get_connection():
    return psycopg2.connect(
        host="shuttle.proxy.rlwy.net",
        database="railway",
        user="postgres",
        password="RNCRzYyNwkvCmYnyJtJUOfrxwqWXpzjh",
        port=25419
    )

# --- FUNGSI DATABASE ---
def get_barang():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM barang ORDER BY id", conn)
    conn.close()
    return df

def tambah_barang(nama, stok):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO barang (nama, stok, tanggal) VALUES (%s, %s, %s)", (nama, stok, datetime.now()))
    conn.commit()
    conn.close()

def tambah_transaksi(tipe, barang_id, jumlah):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO transaksi (tipe, barang_id, jumlah, tanggal) VALUES (%s, %s, %s, %s)", (tipe, barang_id, jumlah, datetime.now()))
    if tipe == 'in':
        cur.execute("UPDATE barang SET stok = stok + %s WHERE id = %s", (jumlah, barang_id))
    else:
        cur.execute("UPDATE barang SET stok = stok - %s WHERE id = %s", (jumlah, barang_id))
    conn.commit()
    conn.close()

# --- TAMPILAN DASHBOARD ---
st.set_page_config(page_title="Inventory Management", layout="wide")
st.title("📦 Inventory Management System")

menu = ["Dashboard", "Tambah Barang", "Transaksi Masuk", "Transaksi Keluar"]
selected = st.radio("Pilih Menu", menu, horizontal=True)

menu_style = """
    <style>
    .stRadio > div {
        flex-direction: row;
        gap: 1rem;
    }
    .stRadio > div label {
        padding: 8px 20px;
        border-radius: 10px;
        background-color: #e0e0e0;
        font-weight: 500;
        cursor: pointer;
    }
    .stRadio > div label[data-baseweb="radio"]:has(input:checked) {
        background-color: #4CAF50;
        color: white;
    }
    </style>
"""
st.markdown(menu_style, unsafe_allow_html=True)

if selected == "Dashboard":
    df = get_barang()
    st.subheader("📊 Data Stok Barang")
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='StokBarang')
        excel_data = output.getvalue()
        st.download_button(
            label="📥 Export ke Excel (XLSX)",
            data=excel_data,
            file_name='data_stok_barang.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    with col2:
        st.markdown("### 🖨️ Cetak Data Tabel")
        html_string = f"""
            <html>
            <head>
                <script>
                    function printDiv() {{
                        var divContents = document.getElementById("print-area").innerHTML;
                        var a = window.open('', '', 'height=600, width=800');
                        a.document.write('<html><head><title>Print</title></head><body>');
                        a.document.write(divContents);
                        a.document.write('</body></html>');
                        a.document.close();
                        a.print();
                    }}
                </script>
            </head>
            <body>
                <div id="print-area">
                    {df.to_html(index=False)}
                </div>
                <br/>
                <button onclick="printDiv()" style="padding:10px 20px; font-size:16px; background-color:#4CAF50; color:white; border:none; border-radius:5px;">🖨️ Cetak Tabel</button>
            </body>
            </html>
        """
        components.html(html_string, height=600, scrolling=True)

elif selected == "Tambah Barang":
    st.subheader("➕ Tambah Barang Baru")
    nama = st.text_input("Nama Barang")
    stok = st.number_input("Stok Awal", min_value=0)
    if st.button("Simpan"):
        tambah_barang(nama, stok)
        st.success("Barang berhasil ditambahkan.")

elif selected == "Transaksi Masuk":
    st.subheader("📥 Transaksi Masuk")
    df = get_barang()
    barang_dict = dict(zip(df['nama'], df['id']))
    barang = st.selectbox("Pilih Barang", options=list(barang_dict.keys()))
    jumlah = st.number_input("Jumlah Masuk", min_value=1)
    if st.button("Tambah Transaksi Masuk"):
        tambah_transaksi("in", barang_dict[barang], jumlah)
        st.success("Transaksi masuk berhasil ditambahkan.")

elif selected == "Transaksi Keluar":
    st.subheader("📤 Transaksi Keluar")
    df = get_barang()
    barang_dict = dict(zip(df['nama'], df['id']))
    barang = st.selectbox("Pilih Barang", options=list(barang_dict.keys()))
    jumlah = st.number_input("Jumlah Keluar", min_value=1)
    if st.button("Tambah Transaksi Keluar"):
        tambah_transaksi("out", barang_dict[barang], jumlah)
        st.success("Transaksi keluar berhasil ditambahkan.")
