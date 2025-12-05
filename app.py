import streamlit as st
import requests
import pandas as pd

# ================= 設定區 =================
# 1. Notion 設定
try:
    # 嘗試從 Streamlit Secrets 讀取 (雲端或本地 .streamlit/secrets.toml)
    NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
    DATABASE_ID = st.secrets["DATABASE_ID"]
    N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]
except FileNotFoundError:
    st.error("找不到 secrets.toml 設定檔！請在 .streamlit 資料夾中設定。")
    st.stop()
# =========================================

st.set_page_config(page_title="台中雷達", page_icon="🍜", layout="wide")
st.title("🍜 台中筆記機器人")

# --- Helper: 直接用 Requests 呼叫 Notion API (避開套件問題) ---
def fetch_notion_data():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",  # 指定穩定的 API 版本
        "Content-Type": "application/json"
    }
    
    # 發送 POST 請求來查詢資料庫
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code != 200:
        st.error(f"❌ Notion 連線失敗: {response.status_code}")
        st.json(response.json()) # 顯示錯誤細節
        return []
    
    return response.json().get("results", [])

# --- Helper: 安全讀取欄位內容 ---
def safe_get(props, col_name, data_type):
    try:
        if col_name not in props:
            return "" # 找不到欄位就留白
        
        col_data = props[col_name]
        
        if data_type == "title":
            return col_data["title"][0]["plain_text"] if col_data["title"] else "無標題"
        elif data_type == "rich_text":
            return col_data["rich_text"][0]["plain_text"] if col_data["rich_text"] else ""
        elif data_type == "select":
            return col_data["select"]["name"] if col_data["select"] else ""
        elif data_type == "multi_select":
            return ", ".join([t["name"] for t in col_data["multi_select"]])
        elif data_type == "url":
            return col_data["url"] if col_data["url"] else ""
            
    except Exception:
        return ""
    return ""

# --- 側邊欄：輸入區 ---
with st.sidebar:
    st.header("📝 新增食記")
    url_input = st.text_input("貼上文章網址:")
    if st.button("AI 分析並存檔 🚀", type="primary"):
        if not url_input:
            st.warning("❌ 請先輸入網址！")
        else:
            with st.spinner("🤖 AI 正在閱讀中..."):
                try:
                    response = requests.get(N8N_WEBHOOK_URL, params={"url": url_input})
                    if response.status_code == 200:
                        st.success("✅ 成功！已呼叫 n8n")
                        st.balloons()
                    else:
                        st.error(f"❌ n8n 回傳錯誤: {response.status_code}")
                except Exception as e:
                    st.error(f"連線失敗: {e}")

# --- 主畫面：顯示資料庫 ---
st.subheader("📊 美食口袋名單")

if st.button("🔄 重新整理列表"):
    st.rerun()

# 1. 抓取資料
results = fetch_notion_data()

if results:
    # 2. 整理資料
    rows = []
    for page in results:
        props = page["properties"]
        
        # 這裡對應你的 Notion 欄位名稱
        rows.append({
            "店名": safe_get(props, "店家名稱", "rich_text"),
            "標題": safe_get(props, "Name", "title"),
            "類型": safe_get(props, "類型", "select"),
            "價位": safe_get(props, "價位", "rich_text"),
            "地區": safe_get(props, "所在位置", "rich_text"),
            "交通": safe_get(props, "交通方式", "rich_text"),
            "必點": safe_get(props, "推薦東西", "rich_text")
        })
    
    # 3. 顯示表格
    df = pd.DataFrame(rows)
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "店名": st.column_config.TextColumn("店家名稱", width="medium"),
            "類型": st.column_config.TextColumn("分類", width="small"),
            "地區": st.column_config.TextColumn("地點"),
        }
    )
else:
    st.info("目前沒有資料，或是讀取失敗。")