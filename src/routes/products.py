from flask import Blueprint, flash, redirect, render_template, url_for, request

# pyrefly: ignore [missing-import]
from src.database.models.models import Product, Category
# pyrefly: ignore [missing-import]
from src.lib.login_required import login_required
# pyrefly: ignore [missing-import]
from src.database.config.database import db

products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
@login_required
def products():
    query = request.args.get('q', '').strip()
    products = Product.query.join(Category, isouter=True)
    if query:
        products = products.filter(db.or_(Product.name.ilike(f'%{query}%'), Product.code.ilike(f'%{query}%'), Category.name.ilike(f'%{query}%')))
    products = products.order_by(Product.name).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('products.html', products=products, categories=categories, q=query)

@products_bp.route('/products/new', methods=['POST'])
@login_required
def products_new():
    code = request.form.get('code', '').strip()
    name = request.form.get('name', '').strip()
    category_id = request.form.get('category_id')
    price_raw = request.form.get('price', '').strip().replace(',', '.')
    stock_raw = request.form.get('stock', '').strip()
    
    # 1. Validação de Campos Vazios
    if not code or not name or not price_raw or not stock_raw:
        flash('Código, nome, preço e estoque são campos obrigatórios.', 'warning')
        return redirect(url_for('products.products'))
        
    # 2. Validação de Erros de Conversão
    try:
        price = float(price_raw)
        stock = int(stock_raw)
    except ValueError:
        flash('Preço ou estoque com formato numérico inválido.', 'warning')
        return redirect(url_for('products.products'))
        
    if price < 0 or stock < 0:
        flash('Preço e estoque não podem ser negativos.', 'warning')
        return redirect(url_for('products.products'))
        
    # 3. Validação de Dados Duplicados
    existing = Product.query.filter_by(code=code).first()
    if existing:
        flash('Já existe um produto cadastrado com este código.', 'warning')
        return redirect(url_for('products.products'))
        
    # 4. Tratamento de Erros de Base de Dados
    try:
        product = Product(code=code, name=name, category_id=category_id or None, price=price, stock=stock)
        db.session.add(product)
        db.session.commit()
        flash('Produto cadastrado com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
        log_error(f"Erro de base de dados ao cadastrar produto (código: {code})", e)
        flash('Erro no banco de dados ao salvar o produto.', 'danger')
        
    return redirect(url_for('products.products'))

@products_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def products_edit(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id')
        price_raw = request.form.get('price', '').strip().replace(',', '.')
        stock_raw = request.form.get('stock', '').strip()
        
        # 1. Validação de Campos Vazios
        if not code or not name or not price_raw or not stock_raw:
            flash('Código, nome, preço e estoque são campos obrigatórios.', 'warning')
            return redirect(url_for('products.products_edit', product_id=product_id))
            
        # 2. Validação de Erros de Conversão
        try:
            price = float(price_raw)
            stock = int(stock_raw)
        except ValueError:
            flash('Preço ou estoque com formato numérico inválido.', 'warning')
            return redirect(url_for('products.products_edit', product_id=product_id))
            
        if price < 0 or stock < 0:
            flash('Preço e estoque não podem ser negativos.', 'warning')
            return redirect(url_for('products.products_edit', product_id=product_id))
            
        # 3. Validação de Dados Duplicados
        existing = Product.query.filter(Product.code == code, Product.id != product_id).first()
        if existing:
            flash('Já existe outro produto cadastrado com este código.', 'warning')
            return redirect(url_for('products.products_edit', product_id=product_id))
            
        # 4. Tratamento de Erros de Base de Dados
        try:
            product.code = code
            product.name = name
            product.category_id = category_id or None
            product.price = price
            product.stock = stock
            db.session.commit()
            flash('Produto atualizado com sucesso.', 'success')
            return redirect(url_for('products.products'))
        except Exception as e:
            db.session.rollback()
            from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
            log_error(f"Erro de base de dados ao editar produto {product_id}", e)
            flash('Erro no banco de dados ao atualizar o produto.', 'danger')
            
    return render_template('product_edit.html', product=product, categories=categories)

@products_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def products_delete(product_id):
    product = Product.query.get_or_404(product_id)
    # 4. Tratamento de Erros de Base de Dados (ex: FK constraint)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Produto excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
        log_error(f"Erro ao excluir produto {product_id} (possivelmente vinculado a vendas)", e)
        flash('Erro de banco de dados: Não é possível excluir um produto que já está associado a vendas ou movimentações.', 'danger')
        
    return redirect(url_for('products.products'))