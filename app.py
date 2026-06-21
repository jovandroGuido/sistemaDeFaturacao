import os
from functools import wraps
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import init_database, db
from models import User, Category, Product, Customer, PaymentMethod, Sale, SaleItem, StockMovement

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
init_database(app)

# Taxa de IVA padrão
TAX_RATE = 0.23

# Decorator para rotas protegidas
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# Utilitários de carrinho
def get_cart():
    return session.get('cart', {})

def save_cart(cart):
    session['cart'] = cart

# Calcula valores do carrinho
def calculate_cart(cart):
    items = []
    subtotal = 0.0
    for pid, quantity in cart.items():
        product = Product.query.get(int(pid))
        if not product:
            continue
        total_price = round(product.price * quantity, 2)
        items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price,
        })
        subtotal += total_price
    subtotal = round(subtotal, 2)
    discount = 0.0
    tax = round((subtotal - discount) * TAX_RATE, 2)
    total = round(subtotal - discount + tax, 2)
    return items, subtotal, discount, tax, total

# Gera número de venda sequencial
def generate_sale_number():
    last_sale = Sale.query.order_by(Sale.id.desc()).first()
    next_index = 1 if not last_sale else last_sale.id + 1
    return f'INV-{next_index:05d}'

@app.context_processor
def inject_globals():
    return {'tax_rate': TAX_RATE, 'current_user': session.get('user_name')}

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_sales = Sale.query.count()
    total_products = Product.query.count()
    total_customers = Customer.query.count()
    today = date.today()
    daily_sales = db.session.query(db.func.sum(Sale.total)).filter(db.func.date(Sale.date) == today).scalar() or 0.0
    latest_sales = Sale.query.order_by(Sale.date.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.stock <= 5).order_by(Product.stock.asc()).limit(5).all()
    return render_template('dashboard.html', total_sales=total_sales, total_products=total_products,
                           total_customers=total_customers, daily_sales=round(daily_sales, 2),
                           latest_sales=latest_sales, low_stock=low_stock)

@app.route('/products')
@login_required
def products():
    query = request.args.get('q', '').strip()
    products = Product.query.join(Category, isouter=True)
    if query:
        products = products.filter(db.or_(Product.name.ilike(f'%{query}%'), Product.code.ilike(f'%{query}%'), Category.name.ilike(f'%{query}%')))
    products = products.order_by(Product.name).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('products.html', products=products, categories=categories, q=query)

@app.route('/products/new', methods=['POST'])
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

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
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

@app.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def products_delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto excluído com sucesso.', 'success')
    return redirect(url_for('products'))

@app.route('/customers')
@login_required
def customers():
    query = request.args.get('q', '').strip()
    customers = Customer.query
    if query:
        customers = customers.filter(Customer.name.ilike(f'%{query}%') | Customer.email.ilike(f'%{query}%') | Customer.phone.ilike(f'%{query}%'))
    customers = customers.order_by(Customer.name).all()
    return render_template('customers.html', customers=customers, q=query)

@app.route('/customers/new', methods=['POST'])
@login_required
def customers_new():
    name = request.form['name'].strip()
    phone = request.form['phone'].strip()
    email = request.form['email'].strip().lower()
    address = request.form['address'].strip()
    if not name:
        flash('Nome do cliente é obrigatório.', 'warning')
        return redirect(url_for('customers'))
    customer = Customer(name=name, phone=phone, email=email, address=address)
    db.session.add(customer)
    db.session.commit()
    flash('Cliente cadastrado com sucesso.', 'success')
    return redirect(url_for('customers'))

@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def customers_edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        customer.name = request.form['name'].strip()
        customer.phone = request.form['phone'].strip()
        customer.email = request.form['email'].strip().lower()
        customer.address = request.form['address'].strip()
        db.session.commit()
        flash('Cliente atualizado com sucesso.', 'success')
        return redirect(url_for('customers'))
    return render_template('customer_edit.html', customer=customer)

@app.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
def customers_delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('Cliente excluído com sucesso.', 'success')
    return redirect(url_for('customers'))

@app.route('/categories')
@login_required
def categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/new', methods=['POST'])
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

@app.route('/categories/<int:category_id>/delete', methods=['POST'])
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

@app.route('/sales/new')
@login_required
def sales_new():
    products = Product.query.order_by(Product.name).all()
    customers = Customer.query.order_by(Customer.name).all()
    payment_methods = PaymentMethod.query.order_by(PaymentMethod.name).all()
    cart = get_cart()
    items, subtotal, discount, tax, total = calculate_cart(cart)
    return render_template('sales_new.html', products=products, customers=customers,
                           payment_methods=payment_methods, cart_items=items,
                           subtotal=subtotal, discount=discount, tax=tax, total=total)

@app.route('/sales/cart/add', methods=['POST'])
@login_required
def cart_add():
    product_id = request.form['product_id']
    quantity = int(request.form.get('quantity', 1))
    cart = get_cart()
    cart[product_id] = cart.get(product_id, 0) + max(1, quantity)
    save_cart(cart)
    flash('Produto adicionado ao carrinho.', 'success')
    return redirect(url_for('sales_new'))

@app.route('/sales/cart/update', methods=['POST'])
@login_required
def cart_update():
    cart = get_cart()
    for product_id, quantity in request.form.items():
        if product_id.startswith('qty_'):
            pid = product_id.replace('qty_', '')
            try:
                qty = int(quantity)
                if qty > 0:
                    cart[pid] = qty
                else:
                    cart.pop(pid, None)
            except ValueError:
                continue
    save_cart(cart)
    flash('Carrinho atualizado.', 'info')
    return redirect(url_for('sales_new'))

@app.route('/sales/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def cart_remove(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    flash('Item removido do carrinho.', 'info')
    return redirect(url_for('sales_new'))

@app.route('/sales/cart/clear')
@login_required
def cart_clear():
    session.pop('cart', None)
    flash('Carrinho limpo.', 'info')
    return redirect(url_for('sales_new'))

@app.route('/sales/checkout', methods=['POST'])
@login_required
def sales_checkout():
    customer_id = request.form.get('customer_id')
    payment_method_id = request.form.get('payment_method_id')
    discount = request.form.get('discount', '0').replace(',', '.')
    cart = get_cart()
    if not cart:
        flash('Carrinho vazio. Adicione produtos antes de finalizar.', 'warning')
        return redirect(url_for('sales_new'))
    try:
        discount = float(discount)
    except ValueError:
        discount = 0.0
    items, subtotal, _, tax, total = calculate_cart(cart)
    discount = min(max(discount, 0.0), subtotal)
    tax = round((subtotal - discount) * TAX_RATE, 2)
    total = round(subtotal - discount + tax, 2)
    sale = Sale(number=generate_sale_number(), customer_id=customer_id or None,
                user_id=session['user_id'], payment_method_id=payment_method_id,
                subtotal=subtotal, tax=tax, discount=discount, total=total)
    db.session.add(sale)
    for item in items:
        product = item['product']
        quantity = item['quantity']
        total_price = item['total_price']
        sale_item = SaleItem(sale=sale, product=product, quantity=quantity,
                             unit_price=product.price, total_price=total_price)
        db.session.add(sale_item)
        product.stock = max(0, product.stock - quantity)
        movement = StockMovement(product=product, quantity=-quantity,
                                 reason=f'Venda {sale.number}')
        db.session.add(movement)
    db.session.commit()
    session.pop('cart', None)
    flash('Venda finalizada com sucesso.', 'success')
    return redirect(url_for('sale_invoice', sale_id=sale.id))

@app.route('/sales/history')
@login_required
def sales_history():
    query = request.args.get('q', '').strip()
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    sales = Sale.query.join(Customer, isouter=True)
    if query:
        sales = sales.filter(db.or_(Sale.number.ilike(f'%{query}%'), Customer.name.ilike(f'%{query}%')))
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            sales = sales.filter(Sale.date >= date_from_obj)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            sales = sales.filter(Sale.date <= date_to_obj)
        except ValueError:
            pass
    sales = sales.order_by(Sale.date.desc()).all()
    return render_template('sales_history.html', sales=sales, q=query, date_from=date_from, date_to=date_to)

@app.route('/sales/<int:sale_id>')
@login_required
def sale_invoice(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    return render_template('invoice.html', sale=sale)

@app.route('/reports')
@login_required
def reports():
    today = date.today()
    month_start = today.replace(day=1)
    daily_total = db.session.query(db.func.sum(Sale.total)).filter(db.func.date(Sale.date) == today).scalar() or 0.0
    monthly_total = db.session.query(db.func.sum(Sale.total)).filter(Sale.date >= month_start).scalar() or 0.0
    top_products = db.session.query(Product.name, db.func.sum(SaleItem.quantity).label('sold'))\
        .join(SaleItem).group_by(Product.id).order_by(db.desc('sold')).limit(5).all()
    top_customers = db.session.query(Customer.name, db.func.sum(Sale.total).label('spent'))\
        .join(Sale).group_by(Customer.id).order_by(db.desc('spent')).limit(5).all()
    low_stock = Product.query.filter(Product.stock <= 5).order_by(Product.stock.asc()).all()
    return render_template('reports.html', daily_total=round(daily_total, 2),
                           monthly_total=round(monthly_total, 2), top_products=top_products,
                           top_customers=top_customers, low_stock=low_stock)

@app.route('/api/products/search')
@login_required
def api_products_search():
    term = request.args.get('q', '').strip()
    products = []
    if term:
        result = Product.query.filter(db.or_(Product.name.ilike(f'%{term}%'), Product.code.ilike(f'%{term}%'))).limit(10).all()
        products = [{'id': p.id, 'name': p.name, 'code': p.code, 'price': p.price, 'stock': p.stock} for p in result]
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)
