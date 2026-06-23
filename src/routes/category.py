from flask import Blueprint, redirect, render_template, request, url_for, flash
# pyrefly: ignore [missing-import]
from src.lib.login_required import login_required
# pyrefly: ignore [missing-import]
from src.database.models.models import Category
# pyrefly: ignore [missing-import]
from src.database.config.database import db

category = Blueprint('category', __name__)

@category.route('/categories')
@login_required
def categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories.html', categories=categories)

@category.route('/categories/new', methods=['POST'])
@login_required
def categories_new():
    name = request.form['name'].strip()
    if not name:
        flash('Nome da categoria é obrigatório.', 'warning')
        return redirect(url_for('categories'))
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    flash('Categoria adicionada.', 'success')
    return redirect(url_for('categories'))

@category.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def categories_delete(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products:
        flash('Não é possível excluir uma categoria que possui produtos.', 'warning')
        return redirect(url_for('categories'))
    db.session.delete(category)
    db.session.commit()
    flash('Categoria excluída.', 'success')
    return redirect(url_for('categories'))