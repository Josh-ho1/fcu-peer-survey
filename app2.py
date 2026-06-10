import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

# --- 1. 學生名單資料庫 ---
groups_data = {
    "組別一": ["洪世瑋", "莊哲霖", "洪鈺恩", "廖宗胤", "林東漳", "林沅佑", "陳威圻", "侯安哲"],
    "組別二": ["顏士綸", "賴秉志", "陳沛妤", "葉南輝", "林柏安", "游宗翰", "林育岑", "柯甫融"],
    "組別三": ["許茂哲", "葉崇豪", "白安凱", "劉易彥", "廖冠瑋", "陳建瀚", "張安圻"],
    "組別四": ["盧宥丞", "賴泓瑋", "蕭義芳", "傅柏誠", "范棋翔", "劉晉成", "劉晉丞"],
    "組別五": ["陳冠邦", "林竑佑", "陳子宇", "王晟祐", "葉子睿", "蕭諺澤", "黃柏穎", "鄭翔勻"],
    "組別六": ["邱湘芸", "謝馨儀", "陳詠晴", "陳樂芯", "彭立喬", "林恒萱", "邱怡瑄", "陳廷瑀"]
}

# --- 2. 安全連線到 Google Sheets (直接用字串解析，不依賴外部檔案與 Secrets) ---
@st.cache_resource
def get_gspread_client():
    try:
        # 將憑證資訊寫成標準 JSON 字串
        key_dict_json = """
        {
          "type": "service_account",
          "project_id": "fcu-survey-2026",
          "private_key_id": "7da5881a29dcf42971be5f51259587bf2a9d8213",
          "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC62fXhYpX8tZ10\\n6fE9D3hD3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ\\n9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xk\\nJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/b\\nB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3Wlkf\\nB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJAgMBAAECggEBAKjX38DlL2f\\n1mD3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xk\\nJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/b\\nB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3Wlkf\\nB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS\\n9D8WkJ9D3xkJhS7/bB3WlkfB/dZlSAoGBAOFm2fXhYpX8tZ106fE9D3hD3xkJhS7/\\nbB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3Wlkf\\nB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS\\n9D8WkJ9D3xkJhSAoGBAMy62fXhYpX8tZ106fE9D3hD3xkJhS7/bB3WlkfB/dZlS\\n9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ\\n9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xk\\nJhSAoGBAK262fXhYpX8tZ106fE9D3hD3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xk\\nJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/b\\nB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3Wlkf\\nBwKBgQDK62fXhYpX8tZ106fE9D3hD3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS\\n7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3W\\nlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhSAoGAZ262fXhY\\npX8tZ106fE9D3hD3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZl\\nS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8WkJ9D3xkJhS7/bB3WlkfB/dZlS9D8Wk\\nJ9D3xkJhS7/bB3WlkfBw==\\n-----END PRIVATE KEY-----\\n",
          "client_email": "fcu-survey-robot@fcu-survey-2026.iam.gserviceaccount.com",
          "client_id": "110394857291048572910",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/fcu-survey-robot%40fcu-survey-2026.iam.gserviceaccount.com",
          "universe_domain": "googleapis.com"
        }
        """
        info = json.loads(key_dict_json)
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"系統初始化失敗，憑證載入錯誤：{e}")
        return None

gc = get_gspread_client()

def get_sheet():
    if gc is None: return None
    try:
        # 老師您的 Google 試算表網址
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/11SqGdBcQ_tgjx2fRzEPqczPzgzBTGnFL4Xe2e04Y0i2w/edit#gid=0"
        return gc.open_by_url(spreadsheet_url).sheet1
    except Exception as e:
        st.error(f"無法開啟指定的 Google 試算表，請確認已將試算表共用給憑證信箱。錯誤：{e}")
        return None

def get_cloud_data():
    sheet = get_sheet()
    if sheet is None: return pd.DataFrame()
    try:
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        if df.empty:
            return pd.DataFrame(columns=["填寫時間", "來源IP", "評分者學號", "評分者姓名", "所屬組別", "被評分者", "給予分數", "保證說明"])
        return df
    except:
        return pd.DataFrame(columns=["填寫時間", "來源IP", "評分者學號", "評分者姓名", "所屬組別", "被評分者", "給予分數", "保證說明"])

# --- 3. 網頁基本設定 ---
st.set_page_config(page_title="課程組內互評系統", layout="centered")
st.title("📊 課程組內互評與統計系統")

if "is_submitted" not in st.session_state:
    st.session_state.is_submitted = False

tab_student, tab_admin = st.tabs(["📝 學生評分介面", "📈 調查成果統計 (教師專用)"])

# ==========================================
# 分頁一：學生評分介面
# ==========================================
with tab_student:
    if st.session_state.is_submitted:
        st.balloons()
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #2e7d32;'>✅ 評分已成功送出！</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>感謝您的填寫，資料已紀錄至系統。</h3>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 返回並讓下一位同學填寫", use_container_width=True):
                st.session_state.is_submitted = False
                st.rerun()
                
    else:
        st.header("填寫互評表單")
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("1. 請輸入您的學號：")
        with col2:
            student_group = st.selectbox("2. 請選擇您的組別：", ["請選擇"] + list(groups_data.keys()))

        if student_group != "請選擇":
            members = groups_data[student_group]
            student_name = st.selectbox("3. 請選擇您的姓名（填表人）：", ["請選擇"] + members)

            if student_name != "請選擇" and student_id:
                st.divider()
                st.subheader(f"👥 請對【{student_group}】的其他組員進行評分")
                st.info("**評分標準：**\n* 0分：都沒出現課堂也沒參與作業\n* 1分：作業參與程度 20% 以下\n* 2分：作業參與程度 20~60%\n* 3分：作業參與程度 60~90%\n* 4分：作業參與程度 90% 以上")

                peers = [m for m in members if m != student_name]
                
                with st.form(key=f"eval_form_{student_group}_{student_name}"):
                    scores = {}
                    for peer in peers:
                        scores[peer] = st.radio(f"請評分【{peer}】的參與度：", options=[0, 1, 2, 3, 4], index=3, horizontal=True, key=f"radio_{student_group}_{student_name}_{peer}")

                    st.divider()
                    st.markdown("**例外情況說明區**")
                    explanation = st.text_area("若您的評分無法滿足「除0、4分外，1、2、3分至少需有一名」的規定，請務必在此填寫「保證說明」：")
                    submit_btn = st.form_submit_button("🚀 送出評分", type="primary")

                if submit_btn:
                    given_scores = list(scores.values())
                    required_scores = {1, 2, 3}
                    missing_scores = required_scores - set(given_scores)

                    if not student_id.strip():
                        st.error("❌ 請確認已填寫最上方的學號！")
                    elif missing_scores and not explanation.strip():
                        st.error(f"⚠️ 送出失敗：您的評分尚未滿足規定（目前缺少給予：{missing_scores}分）。請在上方文字框填寫「保證說明」後再次送出。")
                    else:
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        user_ip = "未知 IP"
                        try:
                            if hasattr(st, "context") and hasattr(st.context, "headers"):
                                user_ip = st.context.headers.get("X-Forwarded-For", st.context.headers.get("Remote-Addr", "雲端環境"))
                        except: pass

                        sheet = get_sheet()
                        if sheet is not None:
                            try:
                                for peer, score in scores.items():
                                    sheet.append_row([
                                        current_time, user_ip, student_id, student_name, student_group, peer, int(score), explanation.strip()
                                    ])
                                st.session_state.is_submitted = True
                                st.rerun()
                            except Exception as e:
                                st.error(f"寫入 Google 試算表失敗。錯誤：{e}")
                        else:
                            st.error("連線錯誤：無法將資料寫入試算表。")

# ==========================================
# 分頁二：調查成果統計 (教師專用)
# ==========================================
with tab_admin:
    st.header("系統管理與統計成果")
    admin_pw = st.text_input("請輸入管理員密碼以檢視成績：", type="password", key="admin_password_input")
    
    if admin_pw == "fcu3069":
        df_results = get_cloud_data()
        submitted_names = set(df_results["評分者姓名"].unique()) if not df_results.empty else set()

        progress_records = []
        for group, names in groups_data.items():
            for name in names:
                if name in submitted_names:
                    sub_time = df_results[df_results["評分者姓名"] == name]["填寫時間"].iloc[0]
                    status = "✅ 已完成"
                    time_val = sub_time
                else:
                    status = "❌ 尚未填寫"
                    time_val = "--"
                progress_records.append({"組別": group, "姓名": name, "填寫狀態": status, "填寫時間": time_val})
        df_progress = pd.DataFrame(progress_records)

        st.divider()
        st.subheader("📋 學生填寫進度與催繳追蹤")
        
        if not df_progress.empty:
            total_students = len(df_progress)
            total_submitted = len(submitted_names)
            total_unsubmitted = total_students - total_submitted
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1: st.metric("應填寫總人數", f"{total_students} 人")
            with col_m2: st.metric("已完成人數", f"{total_submitted} 人")
            with col_m3: st.metric("未完成人數", f"{total_unsubmitted} 人")

            filter_option = st.radio("篩選填報名單：", ["顯示所有人", "只顯示「未填寫」名單"], horizontal=True)
            if filter_option == "只顯示「未填寫」名單":
                df_show = df_progress[df_progress["填寫狀態"] == "❌ 尚未填寫"][["組別", "姓名"]]
                st.dataframe(df_show, use_container_width=True)
            else:
                st.dataframe(df_progress, use_container_width=True)

        st.divider()

        if not df_results.empty:
            st.subheader("1. 學生總結成績表")
            df_results["給予分數"] = pd.to_numeric(df_results["給予分數"])
            stats_df = df_results.groupby(["所屬組別", "被評分者"]).agg(
                獲得總分=("給予分數", "sum"),
                平均得分=("給予分數", "mean"),
                被評分次數=("給予分數", "count")
            ).reset_index()
            stats_df["平均得分"] = stats_df["平均得分"].round(2)
            st.dataframe(stats_df, use_container_width=True)

            st.subheader("2. 原始填答紀錄與保證說明")
            st.dataframe(df_results, use_container_width=True)
        else:
            st.info("雲端試算表中目前尚無 any 學生提交的互評資料。")
