from flask import Flask
from flask_cors import CORS
from config import Config

from routes.auth_routes import auth
from routes.planner_routes import planner
from routes.progress_routes import progress
from routes.mentor_routes import mentor
from routes.impact_routes import impact

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(planner)
app.register_blueprint(progress)
app.register_blueprint(mentor, url_prefix='/mentor')
app.register_blueprint(impact, url_prefix='/impact')

if __name__ == "__main__":
    app.run(debug=True)
