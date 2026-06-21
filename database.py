import os
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_FILE = os.path.join(DB_DIR, 'app.db')

os.makedirs(DB_DIR, exist_ok=True)

# Instância de banco de dados que será inicializada no app.py
db = SQLAlchemy()

def get_database_uri():
    return f'sqlite:///{DB_FILE}'

def init_database(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
