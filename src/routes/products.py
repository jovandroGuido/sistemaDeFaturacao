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
    code = request.form['code'].strip()
    name = request.form['name'].strip()
    category_id = request.form.get('category_id')
    price = request.form.get('price', '0').replace(',', '.')
    stock = request.form.get('stock', '0')
    if not code or not name:
        flash('Código e nome são obrigatórios.', 'warning')
        return redirect(url_for('products'))
    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        flash('Preço ou stock inválido.', 'warning')
        return redirect(url_for('products'))
    product = Product(code=code, name=name, category_id=category_id or None, price=price, stock=stock)
    db.session.add(product)
    db.session.commit()
    flash('Produto cadastrado com sucesso.', 'success')
    return redirect(url_for('products'))

@products_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def products_edit(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        product.code = request.form['code'].strip()
        product.name = request.form['name'].strip()
        product.category_id = request.form.get('category_id') or None
        product.price = float(request.form.get('price', '0').replace(',', '.'))
        product.stock = int(request.form.get('stock', '0'))
        db.session.commit()
        flash('Produto atualizado com sucesso.', 'success')
        return redirect(url_for('products'))
    return render_template('product_edit.html', product=product, categories=categories)

@products_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def products_delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto excluído com sucesso.', 'success')
    return redirect(url_for('products'))