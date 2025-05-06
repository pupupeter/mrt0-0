# mrt0-0
mrtlittleproject

if you do not like my introduction you could just click the link 

https://www.deepwiki.com/pupupeter/mrt0-0


-----------------------------------------------------------------------------------------


# 台北捷運資訊整合系統

## 專案說明

本專案旨在提供一個整合台北捷運資訊的平台，讓使用者能夠查詢捷運站點資訊、路線規劃，並分析歷史查詢紀錄。系統利用 Flask 框架開發，結合了多個 Python 模組，實現了以下主要功能：

* **捷運站點資訊查詢：** 提供捷運站點的相關資訊，包含所屬路線及即時擁擠度資訊（若有）。
* **智慧路線規劃：** 根據使用者輸入的起點站和終點站，提供最佳搭乘路徑建議，包括最快路徑和轉乘次數最少路徑。
* **歷史紀錄分析：** 記錄使用者的查詢行為，並提供統計分析，例如熱門站點、常見路徑和查詢時間分布。
* **Gemini 摘要：** 利用 Google 的 Gemini 模型，對歷史查詢紀錄進行摘要分析，提供使用者行為洞察。

## 技術架構

* **Flask:** 作為後端 Web 框架，處理 HTTP 請求，並提供 API 接口。
* **MongoDB:** 用於儲存捷運站點資料和使用者查詢歷史紀錄。
* **Google Gemini API:** 用於生成歷史紀錄的摘要分析。
* **smolagents:** 用於路線規劃功能，提供智慧路徑建議。
* **Pandas & Plotly:** 用於歷史紀錄的資料分析和視覺化。

## 檔案說明

以下為專案中各主要檔案的功能說明：

* `agent_context.py`:  定義了與 smolagents 互動的 Agent，以及處理使用者查詢上下文的邏輯。
* `app.py`:  Flask 應用程式的入口點，負責初始化應用程式、註冊路由和啟動伺服器。
* `bb.py`:  負責從 MongoDB 取得歷史紀錄，並使用 Pandas 和 Plotly 產生統計圖表。
* `cc.py`:  包含了捷運站點資料，以及站點所屬路線和對應的 iframe ID。
* `history_analysis.py`:  實作歷史紀錄分析的相關功能，包括資料統計和 Gemini 摘要產生。
* `history_utils.py`:  提供儲存使用者查詢歷史紀錄到 JSON 檔案和 MongoDB 的工具函式。
* `iframe_config.py`:  定義了嵌入網頁中顯示捷運即時資訊 iframe 的相關設定。
* `routes.py`:  定義了應用程式的路由，包括站點查詢、路線規劃和重置使用者上下文。
* `station_utils.py`:  提供捷運站點的模糊搜尋和路線建議文字解析的工具函式。

## 使用方法

1.  **安裝相依套件：** ```bash
    pip install -r requirements.txt  # (假設你有 requirements.txt)
    ```
2.  **設定環境變數：** * 確保你有 MongoDB 服務正在運行，並更新程式中的連線字串。
    * 設定 Google Gemini API 金鑰。
3.  **啟動應用程式：** ```bash
    python app.py
    ```
4.  **使用 API：** * **查詢站點資訊：** `/search?query=<站點名稱>`
    * **取得路線建議：** `/route?start=<起點站>&end=<終點站>&user_id=<使用者ID>`
    * **取得歷史紀錄統計圖表：** `/2`
    * **取得歷史紀錄分析與摘要：** `/api/history_analysis`
    * **重置使用者上下文：** `/reset_context` (POST 請求，需包含 JSON 格式的 `user_id`)

## 備註

* 部分路線（例如環狀線、萬大線）可能沒有即時資訊。
* 需要適當設定 MongoDB 連線字串和 Gemini API 金鑰才能正常使用完整功能。
