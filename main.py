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
        
    @app.errorhandler(Exception)
    def handle_exception(e):
        from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
        from flask import request, jsonify, render_template
        from werkzeug.exceptions import HTTPException
        
        # Determina o código de status HTTP apropriado
        code = 500
        if isinstance(e, HTTPException):
            code = e.code
            
        error_msg = str(e)
        
        # Loga a exceção usando o logger centralizado
        log_error(f"Exceção capturada pelo manipulador global: {error_msg}", e)
        
        # Se for requisição de API, retorna resposta JSON
        if request.path.startswith('/api/'):
            return jsonify({"error": "Erro interno do servidor.", "details": error_msg}), code
            
        # Renderiza a página de erro amigável
        return render_template('error.html', error_msg=error_msg), code
        
    @app.context_processor
    def inject_globals():
        return {'tax_rate': TAX_RATE, 'current_user': session.get('user_name')}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
