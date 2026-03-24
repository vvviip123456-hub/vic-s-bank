import streamlit as st
from supabase import create_client
import pandas as pd

# 1. 已經驗證成功的連線設定 (保留寫死的方式最穩定)
url = "https://tnjmtcldhwzwheylyzwi.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRuam10Y2xkaHd6d2hleWx5endpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyNDY3NzYsImV4cCI6MjA4OTgyMjc3Nn0.6lNYuqH0ymDNQe-GxKkvkRMY9-yIYxawJQKHyqRGAWE"
supabase = create_client(url, key)

st.title("🏦 Lisa & Rody 雲端銀行")

# 2. 側邊欄：切換爸爸管理或小孩查看
role = st.sidebar.radio("切換身分", ["👧👦 小孩查詢", "👨 爸爸管理"])

if role == "👨 爸爸管理":
    st.header("爸比存錢區")
    child = st.selectbox("選擇小孩", ["Lisa", "Rody"])
    amount = st.number_input("存入金額", min_value=1, step=10)
    note = st.text_input("備註", placeholder="例如：幫忙做家事獎勵")
    
    # 這裡請替換成你資料庫裡的真實 UUID
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
        # 寫入資料庫
        supabase.table("transactions").insert(data).execute()
        st.success(f"✅ 已成功幫 {child} 存入 {amount} 元！")

else:
    st.header("目前餘額查詢")
    view_child = st.selectbox("你想看誰的帳戶？", ["Lisa", "Rody"])
    
    child_ids = {
        "Lisa": "填入Lisa的UUID",
        "Rody": "填入Rody的UUID"
    }
    
    # 從資料庫抓取特定小孩的紀錄
    response = supabase.table("transactions").select("*").eq("user_id", child_ids[view_child]).execute()
    df = pd.DataFrame(response.data)
    
    if not df.empty:
        total = df['amount'].sum()
        # 顯示大大的餘額
        st.metric(label=f"{view_child} 的總存款", value=f"${total}")
        st.info(f"💰 預計下個月可以領到的 10% 利息： **${int(total * 0.1)}**")
        
        st.subheader("最近存錢紀錄")
        # 整理表格顯示格式
        display_df = df[['created_at', 'amount', 'description']].sort_values('created_at', ascending=False)
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['時間', '金額', '備註']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("目前還沒有存錢紀錄喔！趕快請爸爸存第一筆錢吧！")
