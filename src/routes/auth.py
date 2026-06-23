from flask import Blueprint, flash, redirect, render_template, request, session, url_for
# pyrefly: ignore [missing-import]
from src.database.models.models import User
# pyrefly: ignore [missing-import]
from src.lib.logger import log_error

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # 1. Validação de Campos Vazios
        if not email or not password:
            flash('E-mail e senha são campos obrigatórios.', 'warning')
            return render_template('login.html')
            
        # 2. Validação de Formato (E-mail)
        if '@' not in email:
            flash('O formato do e-mail inserido é inválido.', 'warning')
            return render_template('login.html')
            
        # 3. Tratamento de Erros de Base de Dados
        try:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session.clear()
                session['user_id'] = user.id
                session['user_name'] = user.name
                session.permanent = True
                flash('Login efetuado com sucesso.', 'success')
                return redirect(url_for('dashboard.home'))
            flash('Credenciais inválidas. Tente novamente.', 'danger')
        except Exception as e:
            log_error(f"Erro de base de dados ao tentar autenticar utilizador '{email}'", e)
            flash('Erro interno ao processar o login. Por favor, tente novamente.', 'danger')
            
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('auth.login'))