import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- 1. 設定 Google Sheets 連線 ---
#這三行是固定的咒語，用來告訴 Google 我們是誰
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if "gcp_json" in st.secrets:
    key_dict = json.loads(st.secrets["gcp_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("chiefirm-timeclock-08b635524685.json", scope)
client = gspread.authorize(creds)

# 打開你的試算表 (請確認這裡的名稱跟你的檔案名稱完全一樣)
sheet = client.open("智悅打卡表單").sheet1

# --- 2. 建立 App 介面 ---
st.title("⏰ 公司打卡系統")

# 模擬員工名單
employees = ['蔡禔瑜', '朱欣信', '張淑勤', '羅婉華', '陳玉惠']
user = st.selectbox('請選擇您的名字：', employees)

col1, col2 = st.columns(2)

# --- 3. 設定按鈕動作 ---
with col1:
      if st.button('上班打卡'):
          # 抓取現在時間
          now = datetime.now()
          current_date = now.strftime("%Y-%m-%d") # 年-月-日
          current_time = now.strftime("%H:%M:%S") # 時:分:秒
                    
          # 把資料寫進 Google Sheet
          # 順序對應我們設好的標題：[日期, 姓名, 上班時間, 下班時間(先留空), 總工時(先留空)]
          sheet.append_row([current_date, user, current_time, "", ""])
                    
          st.success(f"✅ {user} 上班打卡成功！時間：{current_time}")

with col2:
    if st.button('下班打卡'):
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        all_records = sheet.get_all_values()
        found = False
        
        for i, row in enumerate(all_records):
            # 檢查是否為「今天」且是「這個人」
            if row[0] == current_date and row[1] == user:
                row_index = i + 1
                
                # 1. 填入下班時間 (第 4 欄)
                sheet.update_cell(row_index, 4, current_time)
                
                # 2. 計算工時
                start_time_str = row[2] # 取得上班時間
                if start_time_str: # 確保有上班時間才計算
                    # 把文字轉成時間物件才能相減
                    FMT = '%H:%M:%S'
                    tdelta = datetime.strptime(current_time, FMT) - datetime.strptime(start_time_str, FMT)
                    
                    # 填入總工時 (第 5 欄)
                    sheet.update_cell(row_index, 5, str(tdelta))
                    
                    st.success(f"😴 {user} 下班打卡成功！工時：{tdelta}")
                else:
                    st.warning("⚠️ 雖然打卡了，但系統找不到您的上班時間，無法計算工時。")
                
                found = True
                break
        
        if not found:
            st.error("❌ 找不到您的上班紀錄！請確認今天是否有打「上班卡」。")

