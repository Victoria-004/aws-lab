from flask import Flask, jsonify  
from app.my_project.districts.route.district_route import districts_bp
from app.my_project.calls.route.calls_route import calls_bp
from app.my_project.utils import cache

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

app.register_blueprint(districts_bp)
app.register_blueprint(calls_bp)

@app.route('/')
def home():
    return "Сервер працює"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/cache/stats', methods=['GET'])
def cache_stats():
    return jsonify(cache.get_stats()), 200

@app.route('/cache/stats', methods=['DELETE'])
def reset_cache_stats():
    cache.reset_stats()
    return jsonify({"message": "Статистику кешу скинуто"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)