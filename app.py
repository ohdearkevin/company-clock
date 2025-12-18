import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, timezone # <--- 修改1：多引入了 timedelta 和 timezone
import json

# --- 1. 設定 Google Sheets 連線 ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "gcp_json" in st.secrets:
    key_dict = json.loads(st.secrets["gcp_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("chiefirm-timeclock-08b635524685.json", scope)   
client = gspread.authorize(creds)

# 打開你的試算表
sheet = client.open("智悅打卡表單").sheet1

# --- 2. 建立 App 介面 ---
st.title("⏰ 智悅科技打卡系統")

# 模擬員工名單
employees = ['蔡禔瑜', '朱欣信', '張淑勤', '羅婉華', '陳玉惠']
user = st.selectbox('請選擇您的名字：', employees)

col1, col2 = st.columns(2)

# 設定台灣時區 (UTC+8)
tw_tz = timezone(timedelta(hours=8)) 

# --- 3. 設定按鈕動作 ---
with col1:
    if st.button('上班打卡'):
        # <--- 修改2：使用 tw_tz 來抓取時間
        now = datetime.now(tw_tz) 
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # 檢查是否已經打過卡
        all_records = sheet.get_all_values()
        is_clocked_in = False
        
        for row in all_records:
            if row[0] == current_date and row[1] == user:
                is_clocked_in = True
                break
        
        if is_clocked_in:
            st.warning(f"⚠️ {user}，您今天 ({current_date}) 已經打過上班卡囉！不用重複打卡。")
        else:
            sheet.append_row([current_date, user, current_time, "", ""])
            st.success(f"✅ {user} 上班打卡成功！時間：{current_time}")

with col2:
    if st.button('下班打卡'):
        # <--- 修改3：使用 tw_tz 來抓取時間
        now = datetime.now(tw_tz)
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        all_records = sheet.get_all_values()
        found = False
        
        for i, row in enumerate(all_records):
            if row[0] == current_date and row[1] == user:
                row_index = i + 1
                
                sheet.update_cell(row_index, 4, current_time)
                
                start_time_str = row[2]
                if start_time_str:
                    FMT = '%H:%M:%S'
                    tdelta = datetime.strptime(current_time, FMT) - datetime.strptime(start_time_str, FMT)
                    
                    sheet.update_cell(row_index, 5, str(tdelta))
                    
                    st.success(f"😴 {user} 下班打卡成功！工時：{tdelta}")
                else:
                    st.warning("⚠️ 雖然打卡了，但系統找不到您的上班時間，無法計算工時。")
                
                found = True
                break
        
        if not found:
            st.error("❌ 找不到您的上班紀錄！請先打上班卡。")





