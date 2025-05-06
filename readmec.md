# 台北捷運資訊整合系統

## 專案說明

本專案旨在建立一個功能完善的平台，方便使用者查詢台北捷運的相關資訊。它不僅提供基本的站點資訊和路線規劃，還進一步分析使用者的查詢歷史，並利用大型語言模型（LLM）生成有價值的摘要。

**主要功能：**

* **即時站點資訊查詢：** 使用者可以查詢特定捷運站的資訊，系統會顯示該站所屬的路線，並整合外部資源（iframe）顯示即時的擁擠度資訊。對於轉乘站，系統會列出所有相關路線的資訊。
* **智慧路線規劃：** 系統能根據使用者提供的起點站和終點站，計算並推薦最佳的搭乘路徑。它會同時提供兩種建議：
    * **最快路徑：** 以旅行時間為主要考量。
    * **最少轉乘路徑：** 減少轉乘次數，提升搭乘舒適度。
* **使用者查詢歷史紀錄：** 系統會記錄使用者的查詢行為，包括起點站、終點站、查詢時間和推薦路徑。這些資料用於後續的分析。
* **歷史紀錄分析與摘要：** 透過分析歷史紀錄，系統可以產生各種統計資訊，例如：
    * 熱門起點站和終點站。
    * 常見的搭乘路線。
    * 使用者查詢的時間分布。
    * 利用 Google Gemini 模型，系統會根據這些統計資料生成摘要，提供對使用者行為的深入洞察和建議。

## 技術架構

本專案採用分層架構，主要包含以下幾個部分：

* **後端 (Backend):**
    * **Flask:** 一個輕量級的 Python Web 框架，用於處理 HTTP 請求、管理路由和提供 API 接口。
    * **MongoDB:** 一個 NoSQL 資料庫，用於儲存捷運站點資料和使用者查詢歷史紀錄。其靈活的 schema 設計非常適合儲存半結構化的歷史資料。
    * **smolagents:** 一個用於構建智慧代理程式的函式庫。在本專案中，它被用來計算捷運路線建議。
    * **Google Gemini API:** Google 的大型語言模型 API，用於生成歷史紀錄的摘要分析。
    * **Pandas:** 一個強大的 Python 資料分析函式庫，用於處理和分析歷史查詢紀錄。
    * **Plotly:** 一個互動式繪圖函式庫，用於將歷史紀錄分析結果視覺化，例如產生長條圖和圓餅圖。
* **資料來源:**
    * **靜態站點資料:** 儲存在 Python 字典中，包含每個捷運站的名稱、所屬路線和用於顯示即時資訊的外部 iframe ID。
    * **外部即時資訊:** 透過嵌入外部網站提供的 iframe 來顯示捷運擁擠度等即時資訊。

## 檔案說明

以下詳細說明專案中各主要檔案的功能和設計：

* **`agent_context.py`:**
    * 定義了與 `smolagents` 互動的 `CodeAgent`，用於路線規劃。
    * 使用 `LiteLLMModel` 封裝了 Gemini 模型。
    * 實作了使用者查詢上下文管理。對於每個使用者，系統會維護其最近的查詢歷史，這有助於改善路線建議的準確性。
    * `run_with_user_context` 函式負責執行 Agent 並更新使用者上下文。
    * `reset_user_context` 函式用於清除特定使用者的查詢歷史。
* **`app.py`:**
    * Flask 應用程式的入口點。
    * 初始化 Flask 應用程式實例。
    * 使用 `register_routes` 函式註冊主功能路由。
    * 使用 `register_blueprint` 方法註冊 `history_analysis` blueprint，將歷史紀錄分析相關的 API 整合到應用程式中。
    * 定義了 `/` 路由，用於顯示主頁 (`3.html`)。
    * 定義了 `/2` 路由，用於顯示歷史紀錄統計圖表。
    * 啟動 Flask 開發伺服器。
* **`bb.py`:**
    * 負責處理歷史紀錄的視覺化。
    * `get_history` 函式從 MongoDB 讀取查詢歷史。
    * 使用 Pandas 將歷史資料轉換為 DataFrame，方便進行分析。
    * 使用 Plotly 產生各種統計圖表：
        * **長條圖：** 顯示每日的查詢次數。
        * **圓餅圖：** 顯示熱門的起點站和終點站。
    * 使用 `to_html` 函式將 Plotly 圖表轉換為 HTML 片段，並將其嵌入到網頁模板 (`2.html`) 中。
* **`cc.py`:**
    * 包含了捷運站點的靜態資料。
    * `station_data` 字典儲存了每個站點的資訊，包括：
        * `line`: 所屬路線。
        * `iframe_id`: 用於顯示該路線即時資訊的外部 iframe 的 ID。
        * `lines` 和 `iframe_ids`: 對於轉乘站，儲存多條路線和對應的 iframe ID。
* **`history_analysis.py`:**
    * 實作歷史紀錄分析的核心功能。
    * 定義了 `history_api` Blueprint，用於組織相關的 API 路由。
    * `analyze_history` 函式：
        * 從 MongoDB 讀取歷史紀錄。
        * 使用 Pandas 進行資料清理和分析。
        * 計算各種統計指標，例如總查詢次數、熱門站點、常見路線和查詢時間分布。
        * 呼叫 `generate_summary_with_gemini` 函式生成摘要。
        * 以 JSON 格式回傳分析結果和摘要。
    * `generate_summary` 函式：
        * 允許使用者提供自訂的統計資料，並生成相應的摘要。
    * `generate_summary_with_gemini` 函式：
        * 使用 Gemini 模型生成歷史紀錄的摘要。
        * 構建一個包含統計資料的 prompt，並將其傳遞給 Gemini 模型。
        * 處理 Gemini API 的回應和可能的錯誤。
* **`history_utils.py`:**
    * 提供儲存使用者查詢歷史紀錄的工具函式。
    * `save_search_history` 函式：
        * 將查詢紀錄儲存到 JSON 檔案 (`search_history.json`)。
        * 將查詢紀錄插入到 MongoDB 的 `mrtdata` collection 中。
* **`iframe_config.py`:**
    * 定義了用於顯示捷運即時資訊的外部 iframe 的相關設定。
    * `iframe_data` 字典儲存了每個 iframe 的 ID 和標題。
* **`routes.py`:**
    * 定義了應用程式的主要路由。
    * `register_routes` 函式：
        * 定義了 `/` 路由，用於顯示主頁。
        * 定義了 `/search` 路由，用於查詢站點資訊。
            * 接收 `query` 參數，並在 `station_data` 中查找匹配的站點。
            * 如果找到站點，則回傳相關的 iframe 資訊。
            * 如果找不到完全匹配的站點，則使用 `fuzzy_search_station` 函式進行模糊搜尋。
        * 定義了 `/route` 路由，用於取得路線建議。
            * 接收 `start` 和 `end` 參數，並使用 `fuzzy_search_station` 函式解析站點名稱。
            * 呼叫 `run_with_user_context` 函式，使用 `fastest_agent` 和 `fewest_transfers_agent` 計算路線建議。
            * 使用 `parse_route_response` 函式解析 Agent 的回應。
            * 使用 `save_search_history` 函式儲存查詢紀錄。
        * 定義了 `/reset_context` 路由，用於重置使用者上下文。
            * 接收 `user_id` 參數，並清除該使用者的查詢歷史。
* **`station_utils.py`:**
    * 提供捷運站點相關的工具函式。
    * `fuzzy_search_station` 函式：
        * 使用 `difflib.get_close_matches` 函式進行模糊搜尋，找到與使用者輸入最接近的站點名稱。
    * `parse_route_response` 函式：
        * 解析 Agent 回傳的路線建議文字，並將其轉換為結構化的清單。

## 使用方法

1.  **環境設定:**
    * **安裝 Python:** 確保你的系統已安裝 Python 3.x。
    * **安裝 MongoDB:** 下載並安裝 MongoDB Community Server。啟動 MongoDB 服務。
    * **設定環境變數:**
        * 安裝 `python-dotenv`: `pip install python-dotenv`
        * 建立 `.env` 檔案，並在其中設定 MongoDB 連線字串和 Google Gemini API 金鑰：

        ```
        MONGODB_URI="mongodb://localhost:27017/"  # 根據你的 MongoDB 設定修改
        GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
        ```

2.  **安裝相依套件:**

    ```bash
  
    pip install Flask pymongo pandas plotly-express python-dotenv smolagents google-generativeai difflib
    ```

3.  **啟動應用程式:**

    ```bash
    python app.py
    ```

    應用程式將會在本地端啟動開發伺服器。

4.  **使用 API:**

    你可以使用 HTTP 請求與應用程式互動，以下是一些範例：

    * **查詢站點資訊:**

        ```
        GET /search?query=<站點名稱>
        ```

        * 範例: `/search?query=台北車站`
        * 回應: JSON 格式的站點資訊，包含相關路線的 iframe 設定。

    * **取得路線建議:**

        ```
        GET /route?start=<起點站>&end=<終點站>&user_id=<使用者ID>
        ```

        * 範例: `/route?start=台北車站&end=西門&user_id=user123`
        * 回應: JSON 格式的路線建議，包含最快路徑和最少轉乘路徑。

    * **取得歷史紀錄統計圖表:**

        ```
        GET /2
        ```

        * 回應: 包含統計圖表的 HTML 頁面。

    * **取得歷史紀錄分析與摘要:**

        ```
        GET /api/history_analysis
        ```

        * 回應: JSON 格式的分析結果，包含統計資料和 Gemini 生成的摘要。

    * **重置使用者上下文:**

        ```
        POST /reset_context
        Content-Type: application/json
        Body: {"user_id": "<使用者ID>"}
        ```

        * 範例:
            ```
            POST /reset_context
            Content-Type: application/json
            Body: {"user_id": "user123"}
            ```
        * 回應: JSON 格式的回應，確認上下文已清除。

## 注意事項

* **資料準確性：** 系統提供的即時資訊依賴於外部資源，其準確性無法保證。
* **錯誤處理：** 程式中已包含基本的錯誤處理，但仍可能存在未預期的錯誤。
* **效能：** 對於高流量的應用，可能需要考慮效能優化，例如使用快取。
* **安全性：** 本專案未包含完整的安全性措施，例如身份驗證和授權，在實際部署時需要額外加強。
