import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "doanh_nghiep_pl1_clean.sqlite"

st.set_page_config(page_title="Tra cứu công chức thuế", layout="wide")

st.title("🔍 Tra cứu công chức thuế quản lý")

query = st.text_input("Nhập mã số thuế hoặc tên doanh nghiệp:")

if st.button("Tra cứu"):
    if query.strip() == "":
        st.warning("Vui lòng nhập thông tin cần tra cứu.")
    else:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            f"SELECT * FROM doanh_nghiep WHERE mst LIKE '%{query}%' OR ten_doanh_nghiep LIKE '%{query}%'", 
            conn
        )
        conn.close()

        if df.empty:
            st.error("❌ Không tìm thấy kết quả.")
        else:
            st.success(f"✅ Tìm thấy {len(df)} kết quả.")
            st.dataframe(df)
