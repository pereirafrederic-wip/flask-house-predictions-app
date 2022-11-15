from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
load_dotenv()

db = SQLAlchemy()
SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{os.getenv("DBUSER")}:{os.getenv("DBPASS")}@{os.getenv("DBHOST")}/{os.getenv("DBNAME")}'
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config["WTF_CSRF_SECRET_KEY"] = os.getenv('WTF_CSRF_SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config.from_object('config')

app.config.update(
SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
from application.database.users import User, init_db
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from application.routes.prediction import prediction
from application.routes.auth import auth
app.register_blueprint(prediction)
app.register_blueprint(auth)
