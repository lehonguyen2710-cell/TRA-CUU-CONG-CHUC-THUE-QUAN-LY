
import streamlit as st
import sqlite3
import pandas as pd
from rapidfuzz import process, fuzz
import re

DB_PATH = "doanh_nghiep_pl1_clean.sqlite"
TABLE = "doanh_nghiep"

@st.cache_data
def load_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE}", conn)
    conn.close()
    return df

def format_row_sentence(row):
    parts = []
    dn = str(row.get("doanh_nghiep", "")).strip()
    if dn:
        parts.append(f"Doanh nghiệp: {dn}")
    ht = str(row.get("ho_ten", "")).strip()
    sdt = str(row.get("so_dien_thoai", "")).strip()
    email = str(row.get("email", "")).strip()
    cq = str(row.get("co_quan_thue", "")).strip()
    contact_parts = []
    if ht:
        contact_parts.append(f"Cán bộ phụ trách: {ht}")
    if sdt:
        contact_parts.append(f"số điện thoại {sdt}")
    if email:
        contact_parts.append(f"email {email}")
    if contact_parts:
        parts.append(", ".join(contact_parts))
    if cq:
        parts.append(f"cơ quan thuế: {cq}")
    return ". ".join(parts) + "."

def fuzzy_search(df, query, limit=20, score_cutoff=60):
    choices = df["doanh_nghiep"].fillna("").astype(str).tolist()
    results = process.extract(query, choices, scorer=fuzz.WRatio, limit=limit)
    matched_indices = [r[2] for r in results if r[1] >= score_cutoff]
    return df.iloc[matched_indices]

st.set_page_config(page_title="Tra cứu danh bạ - PL1", layout="wide")
st.title("Tra cứu danh bạ (PL1) — Tìm theo tên doanh nghiệp")

df = load_db()

query = st.text_input("Nhập tên doanh nghiệp hoặc câu tiếng Việt:", "")
limit = st.slider("Số kết quả tối đa hiển thị", min_value=1, max_value=100, value=20)

if st.button("Tra cứu") and query.strip() != "":
    with st.spinner("Đang tìm..."):
        q = query.strip()
        # crude extraction of key phrase
        m = re.search(r'["“„»«](.+?)["”„»«]', q)
        if m:
            q = m.group(1)
        m2 = re.search(r'có chữ\s+([^\?]+)', q, flags=re.I)
        if m2:
            q = m2.group(1).strip()
        df_matched = fuzzy_search(df, q, limit=limit, score_cutoff=40)
        if df_matched.empty:
            st.warning("Không tìm thấy kết quả phù hợp. Thử nhập ít ký tự hơn.")
        else:
            st.success(f"Tìm thấy {len(df_matched)} kết quả (hiển thị tối đa {limit}).")
            st.dataframe(df_matched.reset_index(drop=True))
            st.markdown("### Kết quả dạng câu")
            for idx, row in df_matched.iterrows():
                st.write("-", format_row_sentence(row))
else:
    st.info("Nhập tên doanh nghiệp (vài ký tự) rồi nhấn 'Tra cứu' để bắt đầu.")
