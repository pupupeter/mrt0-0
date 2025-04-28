from flask import Flask, Blueprint, jsonify, request
import google.generativeai as genai
from pymongo import MongoClient
import pandas as pd

# 初始化 Flask 應用
app = Flask(__name__)

# Blueprint 設定
history_api = Blueprint('history_api', __name__)

# MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")  # 確保 MongoDB 正常運行
db = client["mrt"]
collection = db["mrtdata"]

# 設定 Gemini API Key
genai.configure(api_key="GEMINI_API_KEY")  # ← 改成你的金鑰
model = genai.GenerativeModel('gemini-2.0-flash')

# Gemini 摘要產生函式
def generate_summary_with_gemini(data: dict) -> str:
    prompt = f"""
你是一位捷運資料分析師，請根據以下查詢歷史的統計數據，提供一段摘要與見解，包括熱門站點、使用時間趨勢與任何你觀察到的趨勢。

統計資料如下：
- 查詢總次數：{data['total_queries']}
- 熱門起點站：{data['top_start_stations']}
- 熱門終點站：{data['top_end_stations']}
- 常見路徑：{data['most_frequent_routes']}
- 查詢時間分布（以小時為單位）：{data['query_hour_distribution']}

請用繁體中文撰寫，並條列出 2~3 個使用者行為的觀察與建議。
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini 摘要失敗：{str(e)}"

# API 路由：歷史紀錄分析
@history_api.route('/history_analysis', methods=['GET'])
def analyze_history():
    try:
        # 讀取資料
        records = list(collection.find({}, {"_id": 0}))
        if not records:
            return jsonify({'error': '沒有歷史紀錄'}), 404

        # pandas 分析
        df = pd.DataFrame(records)
        total_queries = len(df)

        # 檢查資料欄位名稱是否正確，並計算熱門站點與路徑
        if 'start' not in df.columns or 'end' not in df.columns or 'timestamp' not in df.columns:
            return jsonify({'error': '資料格式錯誤，缺少必要欄位'}), 400

        top_start = df['start'].value_counts().head(5).to_dict()
        top_end = df['end'].value_counts().head(5).to_dict()

        df['route'] = df['start'] + " -> " + df['end']
        top_routes = df['route'].value_counts().head(5).to_dict()

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        hour_distribution = df['hour'].value_counts().sort_index().to_dict()

        # 整理資料
        stats = {
            'total_queries': total_queries,
            'top_start_stations': top_start,
            'top_end_stations': top_end,
            'most_frequent_routes': top_routes,
            'query_hour_distribution': hour_distribution
        }

        # 產出 Gemini 摘要
        summary = generate_summary_with_gemini(stats)

        # 回傳 JSON
        return jsonify({
            **stats,
            'summary': summary
        })

    except Exception as e:
        return jsonify({'error': f'分析失敗: {str(e)}'}), 500

# API 路由：自定義摘要功能
@history_api.route('/generate_summary', methods=['POST'])
def generate_summary():
    try:
        # 從請求中取得資料
        data = request.get_json()

        # 確保資料有提供必要的欄位
        required_fields = ['total_queries', 'top_start_stations', 'top_end_stations', 'most_frequent_routes', 'query_hour_distribution']
        if not all(field in data for field in required_fields):
            return jsonify({'error': '缺少必要資料欄位'}), 400

        # 產生摘要
        summary = generate_summary_with_gemini(data)

        # 回傳摘要結果
        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': f'摘要生成失敗: {str(e)}'}), 500


# 設定路由
app.register_blueprint(history_api, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)



"""
#把摘要的刪掉，看能不能融在
import json
import os
from pymongo import MongoClient
from datetime import datetime

HISTORY_FILE = 'search_history.json'

# MongoDB 連線設定
client = MongoClient("mongodb://localhost:27017/")
db = client["mrt_db"]
collection = db["search_history"]

def save_search_history(record):
    # 只保留需要的欄位
    simplified_record = {
        "user_id": record.get("user_id", "anonymous"),
        "start": record["start"],
        "end": record["end"],
        "fastest_route": record["fastest_route"],
        "fewest_transfers_route": record["fewest_transfers_route"],
        "timestamp": record.get("timestamp", datetime.now().isoformat())
    }

    # 存入 JSON 檔案
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            pass
    history.append(simplified_record)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    # 存入 MongoDB
    collection.insert_one(simplified_record)
    print("資料已成功儲存到 JSON 與 MongoDB！")
"""


"""
然後把
unction generateSummaryFromStats() {
            const summaryContainer = document.getElementById('summary-container');
            const summaryResult = document.getElementById('summary-result');

            summaryContainer.innerHTML = '生成摘要中...';

            fetch('/api/history_analysis')
                .then(response => response.json())
                .then(data => {
                    return fetch('/api/generate_summary', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            total_queries: data.total_queries,
                            top_start_stations: data.top_start_stations,
                            top_end_stations: data.top_end_stations,
                            most_frequent_routes: data.most_frequent_routes,
                            query_hour_distribution: data.query_hour_distribution
                        })
                    });
                })
                .then(response => response.json())
                .then(data => {
                    summaryResult.textContent = data.summary || '無法生成摘要';
                    summaryContainer.innerHTML = '';
                })
                .catch(error => {
                    console.error('摘要生成錯誤:', error);
                    summaryResult.textContent = '摘要生成失敗';
                    summaryContainer.innerHTML = '';
                });
        }
    </script>

刪掉就好
"""