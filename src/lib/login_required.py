from functools import wraps
from flask import redirect, url_for, session

# Decorator para rotas protegidas
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view