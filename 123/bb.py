# bb.py
from flask import render_template, jsonify
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from plotly.io import to_html
import google.generativeai as genai

client = MongoClient("mongodb://localhost:27017/")
db = client["mrt"]
collection = db["mrtdata"]
genai.configure(api_key="AIzaSyBJj-7Am6kkBj-HGjex-d22j78HzNTRLK8")

def get_history():
    # 从 MongoDB 获取历史记录
    history = list(collection.find().sort([("timestamp", -1)]))
    if history:
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['count'] = 1
        
        # 原始的柱状图数据处理
        df_grouped = df.groupby(df['timestamp'].dt.date)['count'].sum().reset_index()
        fig = px.bar(df_grouped, x='timestamp', y='count', title='搜尋紀錄統計', labels={'timestamp': '日期', 'count': '搜尋次數'})
        bar_chart_html = to_html(fig, full_html=False)
        
        # 基于 start 站点的总数绘制饼图
        start_counts = df['start'].value_counts().reset_index(name='count')
        start_counts = start_counts.rename(columns={'index': 'start'})  # 将 'index' 列重命名为 'start'
        start_pie_fig = px.pie(start_counts, names='start', values='count', title='出發站搜尋統計', labels={'start': '出發站', 'count': '搜尋次數'})
        start_pie_chart_html = to_html(start_pie_fig, full_html=False)

        # 基于 end 站点的总数绘制饼图
        end_counts = df['end'].value_counts().reset_index(name='count')
        end_counts = end_counts.rename(columns={'index': 'end'})  # 将 'index' 列重命名为 'end'
        end_pie_fig = px.pie(end_counts, names='end', values='count', title='終點站搜尋統計', labels={'end': '終點站', 'count': '搜尋次數'})
        end_pie_chart_html = to_html(end_pie_fig, full_html=False)

        # 渲染模板并传递柱状图和两个饼图
        return render_template('2.html', graph_html=bar_chart_html, 
                               start_pie_chart_html=start_pie_chart_html, 
                               end_pie_chart_html=end_pie_chart_html)
    else:
        return jsonify({"message": "無搜尋紀錄"})
