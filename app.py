import streamlit as st
import gspread
import pandas as pd
import datetime
import json

st.set_page_config(page_title="小野人排班系統", page_icon="🍱", layout="centered")
st.title("🍱 小野人員工排休系統")

# 連線邏輯：改從保險箱 (st.secrets) 讀取
@st.cache_resource 
def init_connection():
    # 這裡會對應到我們等一下在網頁設定的名稱
    creds_info = json.loads(st.secrets["google_credentials"])
    client = gspread.service_account_from_dict(creds_info)
    return client.open("試算表格式與程式碼協作")

try:
    spreadsheet = init_connection()
    sheet_vacation = spreadsheet.worksheet("員工排休表")
    data = sheet_vacation.get_all_records()
    df = pd.DataFrame(data)
    df.columns = [str(col).replace(" ", "") for col in df.columns]

    st.subheader("📝 登記休假")
    employees = ["小菁", "玲玲", "玟玟", "子怡"]
    selected_emp = st.selectbox("1. 請選擇您的名字", employees)
    selected_date = st.date_input("2. 請選擇休假日期", min_value=datetime.date.today())

    if st.button("確認送出休假", type="primary"):
        date_str = selected_date.strftime("%Y/%m/%d")
        if date_str in df['日期(A欄)'].values:
            # 檢查是否已滿 2 人排休
            day_data = df[df['日期(A欄)'] == date_str].iloc[0]
            off_count = sum(1 for emp in employees if str(day_data.get(f"{emp}({chr(66+employees.index(emp))}欄)", "")).strip() == "休")
            
            if off_count >= 2:
                st.error(f"⚠️ 抱歉！{date_str} 已經有 {off_count} 人排休，請選其他日期！")
            else:
                row_idx = df.index[df['日期(A欄)'] == date_str].tolist()[0] + 2
                col_idx = employees.index(selected_emp) + 2 
                sheet_vacation.update_cell(row_idx, col_idx, "休")
                st.success(f"✅ 成功！已寫入雲端！")
                st.balloons()
        else:
            st.warning("找不到該日期，請確認試算表。")

    st.divider()
    st.subheader("📅 當月排休總表預覽")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"連線出錯：{e}")