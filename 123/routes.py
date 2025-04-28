from flask import request, jsonify, render_template
from iframe_config import iframe_data
from cc import station_data
from station_utils import fuzzy_search_station, parse_route_response
from agent_context import (
    fastest_agent, fewest_transfers_agent,
    run_with_user_context, reset_user_context
)
from history_utils import save_search_history
import datetime
def register_routes(app):
    @app.route('/')
    def index():
        return render_template('3.html')

    @app.route('/search', methods=['GET'])
    def search():
        query = request.args.get('query', '').lower()
        results = []

        if query in station_data:
            station_info = station_data[query]
            if 'line' in station_info and station_info['line'] in iframe_data:
                results.append(iframe_data[station_info['line']])
            elif 'lines' in station_info:
                for line in station_info['lines']:
                    if line in iframe_data:
                        results.append(iframe_data[line])
            return jsonify(results) if results else jsonify({'error': f'找不到 {query} 的擁擠度資訊'}), 404
        else:
            matches = fuzzy_search_station(query)
            if matches:
                for match in matches:
                    station_info = station_data.get(match, {})
                    if 'lines' in station_info:
                        for line in station_info['lines']:
                            if line in iframe_data:
                                results.append(iframe_data[line])
                    elif 'line' in station_info and station_info['line'] in iframe_data:
                        results.append(iframe_data[station_info['line']])
                if results:
                    return jsonify(results)
            return jsonify({'error': f'找不到「{query}」相關的捷運資訊，請確認站名是否正確。'}), 404

    @app.route('/route', methods=['GET'])
    def get_route():
        start_station = request.args.get('start', '').lower()
        end_station = request.args.get('end', '').lower()
        user_id = request.args.get('user_id', 'anonymous')

        def resolve_station(name):
            if name in station_data:
                return name
            matches = fuzzy_search_station(name)
            return matches[0] if matches else None

        resolved_start = resolve_station(start_station)
        resolved_end = resolve_station(end_station)

        if not resolved_start or not resolved_end:
            return jsonify({'error': '找不到起點或終點站，請確認輸入是否正確'}), 400

        question = f"從 {resolved_start} 到 {resolved_end} 的最佳台北捷運搭乘路徑是？"

        try:
            fastest = run_with_user_context(fastest_agent, question, user_id, 'fastest')
            fewest = run_with_user_context(fewest_transfers_agent, question, user_id, 'fewest')

            # 新增：儲存搜尋紀錄
            save_search_history({
                'user_id': user_id,
                'start': resolved_start,
                'end': resolved_end,
                'fastest_route': parse_route_response(fastest),
                'fewest_transfers_route': parse_route_response(fewest),
                'timestamp': datetime.datetime.now().isoformat()
            })

            return jsonify({
                'start': resolved_start,
                'end': resolved_end,
                'fastest_route': parse_route_response(fastest),
                'fewest_transfers_route': parse_route_response(fewest)
            })
        except Exception as e:
            return jsonify({'error': f'無法取得路線建議：{str(e)}'}), 500

    @app.route('/reset_context', methods=['POST'])
    def reset_context():
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({'error': '缺少 user_id'}), 400
        reset_user_context(user_id)
        return jsonify({'message': f'{user_id} 的上下文已清除'})
    
