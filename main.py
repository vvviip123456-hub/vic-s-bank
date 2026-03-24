import streamlit as st
from supabase import create_client
import pandas as pd

# 加上這行測試標記，用來確認雲端真的有更新！
st.write("系統版本：v1.0 (強制更新測試)")

# 1. 強制宣告變數 (請確認等號左邊是全小寫的 url 和 key)
url = "https://tnjmtcldhwzwheylyzwi.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRuam10Y2xkaHd6d2hleWx5endpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyNDY3NzYsImV4cCI6MjA4OTgyMjc3Nn0.6lNYuqH0ymDNQe-GxKkvkRMY9-yIYxawJQKHyqRGAWE"

# 2. 建立資料庫連線
supabase = create_client(url, key)

st.title("🏦 Lisa & Rody 雲端銀行")
st.success("資料庫連線設定成功！")
