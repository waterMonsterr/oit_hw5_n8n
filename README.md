# 🍜 台中 AI 筆記機器人

這是一個結合 **Streamlit (前端)**、**n8n (自動化)** 與 **Notion (資料庫)** 的全端應用。
使用者只需貼上美食部落格或食記的網址，AI 就會自動提取餐廳資訊（店名、價位、評分、交通方式等），並存入 Notion 資料庫中，同時在網頁上即時顯示美食清單。

## 🚀 功能特色
- **AI 智慧分析**：使用 Llama 3 (via Groq) 自動分析網頁內容。
- **一鍵存檔**：自動整理非結構化的文章內容為結構化資料。
- **即時同步**：Streamlit 前端直接讀取 Notion 資料庫。
- **自動分類**：自動標記「食、衣、住、行、育、樂」。

## 🛠️ 技術架構
- **Frontend**: Streamlit (Python)
- **Backend/Workflow**: n8n (Self-hosted via Tunnel)
- **AI Model**: Llama 3 (via Groq API)
- **Database**: Notion

## 📦 安裝與執行

### 1. 安裝依賴套件
```bash
pip install -r requirements.txt