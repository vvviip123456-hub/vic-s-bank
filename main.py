import streamlit as st
from supabase import create_client
import pandas as pd

# 1. 連線到 Supabase (這裡會使用 GitHub 的 Secrets 設定)
SUPABASE_URL = "https://tnjmtcldhwzwheylyzwi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRuam10Y2xkaHd6d2hleWx5endpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyNDY3NzYsImV4cCI6MjA4OTgyMjc3Nn0.6lNYuqH0ymDNQe-GxKkvkRMY9-yIYxawJQKHyqRGAWE"
SUPABASE = create_client(URL, KEY)

st.title("🏦 Lisa & Rody 雲端銀行")

# 側邊欄切換身分
role = st.sidebar.radio("切換身分", ["小孩查詢", "爸爸管理"])

if role == "爸爸管理":
    st.header("爸比存錢區")
    child = st.selectbox("選擇小孩", ["Lisa", "Rody"])
    amount = st.number_input("存入金額", min_value=1)
    note = st.text_input("備註", placeholder="例如：考試獎勵")
    
    # 對應你之前在 Supabase 建立的 UUID
    child_ids = {
        "Lisa": "c8dca726-4350-46e8-a4d9-eaa7add7eb37",
        "Rody": "709b97c8-607b-4a2b-a771-6cce36ebc5f7"
    }

    if st.button("確認存入"):
        data = {
            "user_id": child_ids[child],
            "amount": amount,
            "description": note,
            "type": "income"
        }
        supabase.table("transactions").insert(data).execute()
        st.success(f"已成功幫 {child} 存入 {amount} 元！")

else:
    st.header("餘額查詢")
    # 這裡會從資料庫抓取最新的資料並計算利息
    response = supabase.table("transactions").select("*").execute()
    df = pd.DataFrame(response.data)
    
    if not df.empty:
        total = df['amount'].sum()
        st.metric("目前總餘額", f"${total}")
        st.write(f"💰 預計下月利息: ${int(total * 0.1)}")
        st.subheader("最近紀錄")
        st.table(df[['created_at', 'amount', 'description']].sort_values('created_at', ascending=False))
