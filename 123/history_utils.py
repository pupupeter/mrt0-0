import json
import os
from pymongo import MongoClient

HISTORY_FILE = 'search_history.json'

# 設定 MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")  # 替換成你的連線字串
db = client["mrt"]
collection = db["mrtdata"]

def save_search_history(record):
    history = []

    # 讀取現有 JSON 檔案
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []

    # 加入新紀錄
    history.append(record)

    # 寫回 JSON 檔案
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    # 寫入 MongoDB（單筆插入）
    collection.insert_one(record)
    print("已儲存到 JSON 及 MongoDB")
