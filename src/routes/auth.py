from flask import Blueprint, flash, redirect, render_template, request, session, url_for
# pyrefly: ignore [missing-import]
from src.database.models.models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.name
            session.permanent = True
            flash('Login efetuado com sucesso.', 'success')
            return redirect(url_for('dashboard'))
        flash('Credenciais inválidas. Tente novamente.', 'danger')
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('login'))