import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta

# 1. 連線設定
url = "https://tnjmtcldhwzwheylyzwi.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRuam10Y2xkaHd6d2hleWx5endpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyNDY3NzYsImV4cCI6MjA4OTgyMjc3Nn0.6lNYuqH0ymDNQe-GxKkvkRMY9-yIYxawJQKHyqRGAWE"
supabase = create_client(url, key)

st.title("🏦 Lisa & Rody 雲端銀行")

# 將 ID 統一放在上方
CHILD_IDS = {
    "Lisa": "c8dca726-4350-46e8-a4d9-eaa7add7eb37",
    "Rody": "709b97c8-607b-4a2b-a771-6cce36ebc5f7"
}

# ==========================================
# 🌟 自動配息系統 (每月 10 日自動觸發)
# ==========================================
# 取得台灣時間 (UTC+8)
tw_now = datetime.utcnow() + timedelta(hours=8)

# 只要是 10 號(含)之後，就檢查是否需要發放本月利息
if tw_now.day >= 10:
    interest_desc = f"💰 {tw_now.year}年{tw_now.month}月配息"
    
    for child_name, c_id in CHILD_IDS.items():
        # 抓取該小孩的紀錄來檢查
        res = supabase.table("transactions").select("amount, description").eq("user_id", c_id).execute()
        
        if res.data:
            # 檢查這個月是不是已經發過這筆配息了 (避免重複發放)
            already_paid = any(interest_desc == str(row.get("description", "")) for row in res.data)
            
            if not already_paid:
                # 計算總餘額與利息 (0.797%)
                total_balance = sum(row.get("amount", 0) for row in res.data)
                interest = int(total_balance * 0.00797)
                
                # 如果利息大於 0，就自動存入資料庫
                if interest > 0:
                    supabase.table("transactions").insert({
                        "user_id": c_id,
                        "amount": interest,
                        "description": interest_desc,
                        "type": "income"
                    }).execute()
# ==========================================

# 2. 側邊欄：切換身分
role = st.sidebar.radio("切換身分", ["👧👦 小孩查詢", "👨 爸爸管理"])

if role == "👨 爸爸管理":
    st.header("爸比專屬管理區 🔒")
    password = st.text_input("請輸入爸比專屬密碼", type="password")
    
    if password == "Abc13579@@":
        st.success("解鎖成功！歡迎爸比。")
        
        # 使用 Tabs 把新增和修改功能分開
        tab1, tab2 = st.tabs(["💰 新增存款", "📝 修改/刪除紀錄"])
        
        with tab1:
            child = st.selectbox("選擇小孩", ["Lisa", "Rody"], key="add_child")
            amount = st.number_input("存入金額", min_value=1, step=10, key="add_amount")
            note = st.text_input("備註", placeholder="例如：幫忙做家事獎勵", key="add_note")
            
            if st.button("確認存入"):
                data = {
                    "user_id": CHILD_IDS[child],
                    "amount": amount,
                    "description": note,
                    "type": "income"
                }
                supabase.table("transactions").insert(data).execute()
                st.success(f"✅ 已成功幫 {child} 存入 {amount} 元！")
                st.rerun()
                
        with tab2:
            edit_child = st.selectbox("選擇要修改紀錄的小孩", ["Lisa", "Rody"], key="edit_child")
            res = supabase.table("transactions").select("*").eq("user_id", CHILD_IDS[edit_child]).order("created_at", desc=True).execute()
            edit_df = pd.DataFrame(res.data)
            
            if not edit_df.empty:
                for index, row in edit_df.iterrows():
                    with st.expander(f"紀錄：{row['created_at'][:16]} | {row['description']} | ${row['amount']}"):
                        new_amt = st.number_input("修改金額", value=int(row['amount']), key=f"amt_{row['id']}")
                        new_desc = st.text_input("修改備註", value=str(row['description']), key=f"desc_{row['id']}")
                        
                        col1, col2 = st.columns(2)
                        if col1.button("✅ 更新這筆", key=f"upd_{row['id']}"):
                            supabase.table("transactions").update({"amount": new_amt, "description": new_desc}).eq("id", row['id']).execute()
                            st.success("更新成功！")
                            st.rerun()
                            
                        if col2.button("❌ 刪除這筆", key=f"del_{row['id']}"):
                            supabase.table("transactions").delete().eq("id", row['id']).execute()
                            st.warning("紀錄已刪除！")
                            st.rerun()
            else:
                st.info("目前還沒有紀錄可以修改喔！")
                
    elif password != "":
        st.error("密碼錯誤，請重新確認喔！")

else:
    st.header("目前餘額查詢")
    view_child = st.selectbox("你想看誰的帳戶？", ["Lisa", "Rody"])
    
    response = supabase.table("transactions").select("*").eq("user_id", CHILD_IDS[view_child]).execute()
    df = pd.DataFrame(response.data)
    
    if not df.empty:
        total = df['amount'].sum()
        st.metric(label=f"{view_child} 的總存款", value=f"${total}")
        st.info(f"💡 年息 10%，每月 10 日系統會自動結算並發放配息！")
        
        st.divider()
        
        # --- 小孩新增的支出區塊 ---
        st.subheader("🛍️ 我想花錢 (新增支出)")
        expense_amt = st.number_input("支出金額", min_value=1, step=10, key="exp_amt")
        expense_note = st.text_input("買了什麼？", placeholder="例如：買文具、買零食", key="exp_note")
        
        if st.button("確認支出"):
            if expense_amt > total:
                st.error("🛑 餘額不足！你沒有這麼多錢可以花喔！快去幫忙做家事賺錢吧！")
            else:
                # 支出金額以「負數」存入
                data = {
                    "user_id": CHILD_IDS[view_child],
                    "amount": -expense_amt,
                    "description": f"支出：{expense_note}",
                    "type": "expense"
                }
                supabase.table("transactions").insert(data).execute()
                st.success(f"✅ 已成功紀錄支出 {expense_amt} 元！")
                st.rerun()
                
        st.divider()
        
        st.subheader("最近存提紀錄")
        display_df = df[['created_at', 'amount', 'description']].sort_values('created_at', ascending=False)
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.tz_convert('Asia/Taipei').dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['時間', '金額', '備註']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("目前還沒有存錢紀錄喔！趕快請爸爸存第一筆錢吧！")
