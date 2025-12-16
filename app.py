import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json  # <--- 補上這行，因為後面有用到 json.loads

# --- 1. 設定 Google Sheets 連線 ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "gcp_json" in st.secrets:
    key_dict = json.loads(st.secrets["gcp_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
# 如果抓不到，就試著讀取本地檔案 -> 這是給你電腦用的
else:
    # (請確認這裡還是您原本的 json 檔名)
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
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d") # 年-月-日
        current_time = now.strftime("%H:%M:%S") # 時:分:秒
        
        # === 修改開始：先檢查是否已經打過卡 ===
        all_records = sheet.get_all_values()
        is_clocked_in = False
        
        for row in all_records:
            # 檢查是否為「今天」且是「這個人」
            if row[0] == current_date and row[1] == user:
                is_clocked_in = True
                break
        
        if is_clocked_in:
            st.warning(f"⚠️ {user}，您今天 ({current_date}) 已經打過上班卡囉！不用重複打卡。")
        else:
            # 沒打過卡，才寫入資料
            sheet.append_row([current_date, user, current_time, "", ""])
            st.success(f"✅ {user} 上班打卡成功！時間：{current_time}")
        # === 修改結束 ===

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
                
                # 檢查是否已經打過下班卡 (防止重複打下班卡覆蓋時間) - 選擇性功能
                # 如果您希望可以重複打下班卡(更新時間)，這段可以不用改
                
                # 1. 填入下班時間 (第 4 欄)
                sheet.update_cell(row_index, 4, current_time)
                
                # 2. 計算工時
                start_time_str = row[2] # 取得上班時間
                if start_time_str: # 確保有上班時間才計算
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
            st.error("❌ 找不到您的上班紀錄！請先打上班卡。")



