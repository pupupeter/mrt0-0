from flask import Flask,render_template, request, redirect,jsonify
from routes import register_routes
from history_analysis import history_api  # 新增：引入歷史分析 blueprint
from bb import get_history

app = Flask(__name__)


# 註冊主功能路由
register_routes(app)

# 註冊歷史紀錄分析 API
app.register_blueprint(history_api)
def home():
    return render_template('3.html')

@app.route('/2')
def history():
    return get_history()


if __name__ == '__main__':
    app.run(debug=True)
