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
    name = request.form.get('name', '').strip()
    
    # 1. Validação de Campo Vazio
    if not name:
        flash('Nome da categoria é obrigatório.', 'warning')
        return redirect(url_for('category.categories'))
        
    # 2. Validação de Dados Duplicados
    existing = Category.query.filter_by(name=name).first()
    if existing:
        flash('Já existe uma categoria cadastrada com este nome.', 'warning')
        return redirect(url_for('category.categories'))
        
    # 3. Tratamento de Erros de Base de Dados
    try:
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash('Categoria adicionada com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
        log_error(f"Erro de base de dados ao cadastrar categoria '{name}'", e)
        flash('Erro no banco de dados ao salvar a categoria.', 'danger')
        
    return redirect(url_for('category.categories'))

@category.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def categories_delete(category_id):
    category_to_delete = Category.query.get_or_404(category_id)
    
    if category_to_delete.products:
        flash('Não é possível excluir uma categoria que possui produtos.', 'warning')
        return redirect(url_for('category.categories'))
        
    # 3. Tratamento de Erros de Base de Dados
    try:
        db.session.delete(category_to_delete)
        db.session.commit()
        flash('Categoria excluída com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
        log_error(f"Erro ao excluir categoria {category_id}", e)
        flash('Erro no banco de dados ao excluir a categoria.', 'danger')
        
    return redirect(url_for('category.categories'))