import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

MAX_UPLOAD_SIZE_MB = 1
BASEDIR = os.path.abspath(os.path.dirname(__file__))
SERVER_PATH = os.path.join(BASEDIR, 'db.sqlite')
UPLOAD_FOLDER = r'C:/englishtips/englishtips_web_api/version/'
ALLOWED_EXTENSIONS = {'txt', 'zip'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + SERVER_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ba86103dafb9ec379d26c7bd92206424'

db = SQLAlchemy(app)
Migrate(app, db)

from project.admin.views import confused_word_blueprints
app.register_blueprint(confused_word_blueprints, url_prefix='/admin')
