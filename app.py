from flask import Flask
from app.my_project.districts.route.district_route import districts_bp
from app.my_project.calls.route.calls_route import calls_bp

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

app.register_blueprint(districts_bp)
app.register_blueprint(calls_bp)

@app.route('/')
def home():
    return "Сервер запущено!"

if __name__ == '__main__':
    app.run(debug=True)