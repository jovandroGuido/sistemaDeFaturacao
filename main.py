import os
from flask import Flask, session
# pyrefly: ignore [missing-import]
from src.database.config.database import init_database
# pyrefly: ignore [missing-import]
from src.lib.env import TAX_RATE, SECRET_KEY
# pyrefly: ignore [missing-import]
from src.routes import auth, dashboard, products, category, customer, sales, reports, api

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
    app.config['SECRET_KEY'] = SECRET_KEY
    init_database(app)

    # Lista de rotas (blueprints)
    blueprints = [
        (auth),
        (dashboard),
        (products),
        (customer),
        (category),
        (sales),
        (reports),
        (api)
    ]
    
    # Loop para registrar todos automaticamente
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
        
    return app

@app.context_processor
def inject_globals():
    return {'tax_rate': TAX_RATE, 'current_user': session.get('user_name')}

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
