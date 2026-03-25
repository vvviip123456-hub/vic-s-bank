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

# 取得台灣時間 (UTC+8)
tw_now = datetime.utcnow() + timedelta(hours=8)
tw_today = tw_now.date()

# ==========================================
# 🌟 系統自動化處理區 (進站自動執行)
# ==========================================
# 【自動化 A：每月 10 日自動配息】
if tw_today.day >= 10:
    interest_desc = f"💰 {tw_today.year}年{tw_today.month}月配息"
    for child_name, c_id in CHILD_IDS.items():
        res = supabase.table("transactions").select("amount, description").eq("user_id", c_id).execute()
        if res.data:
            already_paid = any(interest_desc == str(row.get("description", "")) for row in res.data)
            if not already_paid:
                total_balance = sum(row.get("amount", 0) for row in res.data)
                interest = int(total_balance * 0.00797)
                if interest > 0:
                    supabase.table("transactions").insert({
                        "user_id": c_id, "amount": interest, "description": interest_desc, "type": "income"
                    }).execute()

# 【自動化 B：每週一下午 2 點結算時鐘獎勵】
curr_week_monday = tw_today - timedelta(days=tw_today.weekday())
settlement_threshold = datetime(curr_week_monday.year, curr_week_monday.month, curr_week_monday.day, 14, 0, 0)

if tw_now >= settlement_threshold:
    settle_week_start = curr_week_monday - timedelta(days=7) # 結算上週
else:
    settle_week_start = curr_week_monday - timedelta(days=14) # 結算上上週

settle_week_end = settle_week_start + timedelta(days=6)
settlement_desc = f"🎁 {settle_week_start.strftime('%m/%d')}至{settle_week_end.strftime('%m/%d')} 準時任務獎勵"
reward_mapping = {1:10, 2:20, 3:30, 4:50, 5:60, 6:80, 7:100}

for child_name, c_id in CHILD_IDS.items():
    res_settle = supabase.table("transactions").select("description").eq("user_id", c_id).eq("description", settlement_desc).execute()
    if not res_settle.data:
        clock_res = supabase.table("transactions").select("description").eq("user_id", c_id).eq("amount", 0).execute()
        count = 0
        for i in range(7):
            d_str = f"🕒 任務打卡 ({(settle_week_start + timedelta(days=i)).strftime('%Y-%m-%d')})"
            if any(r.get('description') == d_str for r in clock_res.data):
                count += 1
                
        reward_amount = reward_mapping.get(count, 0)
        # ⚠️ 這裡已經將原本導致報錯的 "reward" 改回安全的 "income"
        supabase.table("transactions").insert({
            "user_id": c_id, "amount": reward_amount, "description": settlement_desc, "type": "income"
        }).execute()
# ==========================================

# 2. 側邊欄：切換身分
role = st.sidebar.radio("切換身分", ["👧👦 小孩查詢", "👨 爸爸管理"])

if role == "👨 爸爸管理":
    st.header("爸比專屬管理區 🔒")
    password = st.text_input("請輸入爸比專屬密碼", type="password")
    
    if password == "Abc13579@@":
        st.success("解鎖成功！")
        tab1, tab2 = st.tabs(["💰 新增存款", "📝 修改/刪除紀錄"])
        
        with tab1:
            child = st.selectbox("選擇小孩", ["Lisa", "Rody"], key="add_child")
            amount = st.number_input("存入金額", min_value=1, step=10, key="add_amount")
            note = st.text_input("備註", placeholder="例如：幫忙做家事獎勵", key="add_note")
            
            if st.button("確認存入"):
                supabase.table("transactions").insert({
                    "user_id": CHILD_IDS[child], "amount": amount, "description": note, "type": "income"
                }).execute()
                st.success(f"✅ 已成功存入 {amount} 元！")
                st.rerun()
                
        with tab2:
            edit_child = st.selectbox("選擇小孩", ["Lisa", "Rody"], key="edit_child")
            res = supabase.table("transactions").select("*").eq("user_id", CHILD_IDS[edit_child]).order("created_at", desc=True).execute()
            edit_df = pd.DataFrame(res.data)
            
            if not edit_df.empty:
                real_records = edit_df[edit_df['amount'] != 0]
                for index, row in real_records.iterrows():
                    with st.expander(f"{row.get('created_at', '')[:10]} | {row.get('description', '')} | ${row.get('amount', 0)}"):
                        new_amt = st.number_input("修改金額", value=int(row.get('amount', 0)), key=f"amt_{row.get('id')}")
                        new_desc = st.text_input("修改備註", value=str(row.get('description', '')), key=f"desc_{row.get('id')}")
                        
                        col1, col2 = st.columns(2)
                        if col1.button("✅ 更新", key=f"upd_{row.get('id')}"):
                            supabase.table("transactions").update({"amount": new_amt, "description": new_desc}).eq("id", row.get('id')).execute()
                            st.rerun()
                        if col2.button("❌ 刪除", key=f"del_{row.get('id')}"):
                            supabase.table("transactions").delete().eq("id", row.get('id')).execute()
                            st.rerun()
            else:
                st.info("目前還沒有可修改的紀錄喔！")
    elif password != "":
        st.error("密碼錯誤喔！")

else:
    st.header("首頁與存款查詢")
    view_child = st.selectbox("你是誰？", ["Lisa", "Rody"])
    
    response = supabase.table("transactions").select("*").eq("user_id", CHILD_IDS[view_child]).execute()
    df = pd.DataFrame(response.data)
    
    if not df.empty:
        total = df['amount'].sum()
        st.metric(label=f"{view_child} 的總存款", value=f"${total}")
        st.info(f"💡 年息 10% 自動配息。週一 14:00 自動發放上週打卡獎金！")
        
        st.divider()
        
        # --- ⏰ 每日準時任務打卡區 ---
        st.subheader("🎯 本週準時任務打卡")
        st.write("每天準時完成任務可以點亮一個時鐘！")
        
        week_start = tw_today - timedelta(days=tw_today.weekday())
        weekdays_name = ["一", "二", "三", "四", "五", "六", "日"]
        
        cols = st.columns(7)
        for i in range(7):
            current_day = week_start + timedelta(days=i)
            day_str = current_day.strftime('%Y-%m-%d')
            target_desc = f"🕒 任務打卡 ({day_str})"
            
            is_completed = any(row.get('description') == target_desc for row in response.data)
            
            with cols[i]:
                st.caption(f"週{weekdays_name[i]}")
                if is_completed:
                    st.markdown("### ⏰")
                else:
                    if current_day == tw_today:
                        if st.button("⚪", key=f"btn_{day_str}", help="點擊打卡今天任務！"):
                            # ⚠️ 這裡也已經將 "reward" 改回 "income"
                            supabase.table("transactions").insert({
                                "user_id": CHILD_IDS[view_child], "amount": 0, "description": target_desc, "type": "income"
                            }).execute()
                            st.rerun()
                    else:
                        st.markdown("### ⚪")
                        
        st.divider()
        
        # --- 🛍️ 新增支出區塊 ---
        st.subheader("🛍️ 我想花錢 (新增支出)")
        expense_amt = st.number_input("支出金額", min_value=1, step=10, key="exp_amt")
        expense_note = st.text_input("買了什麼？", placeholder="例如：買文具、買零食", key="exp_note")
        
        if st.button("確認支出"):
            if expense_amt > total:
                st.error("🛑 餘額不足喔！快去達成任務賺錢吧！")
            else:
                supabase.table("transactions").insert({
                    "user_id": CHILD_IDS[view_child], "amount": -expense_amt, "description": f"支出：{expense_note}", "type": "expense"
                }).execute()
                st.success(f"✅ 已成功紀錄支出 {expense_amt} 元！")
                st.rerun()
                
        st.divider()
        
        st.subheader("最近存提紀錄")
        real_transactions = df[df['amount'] != 0]
        if not real_transactions.empty:
            display_df = real_transactions[['created_at', 'amount', 'description']].sort_values('created_at', ascending=False)
            display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.tz_convert('Asia/Taipei').dt.strftime('%Y-%m-%d')
            display_df.columns = ['日期', '金額', '備註']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.write("目前還沒有金錢紀錄喔！")
    else:
        st.info("目前還沒有任何紀錄喔！趕快請爸爸存第一筆錢吧！")
