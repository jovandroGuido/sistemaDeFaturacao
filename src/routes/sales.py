from flask import Blueprint, redirect, request, render_template, flash, session, url_for
# pyrefly: ignore [missing-import]
from src.database.config.database import db
# pyrefly: ignore [missing-import]
from src.database.models.models import Product, Customer, PaymentMethod, Sale, SaleItem, StockMovement
# pyrefly: ignore [missing-import]
from src.lib.login_required import login_required
# pyrefly: ignore [missing-import]
from src.services.cart.cart import get_cart, calculate_cart, save_cart, generate_sale_number
# pyrefly: ignore [missing-import]
from src.lib.env import TAX_RATE
from datetime import datetime

sales = Blueprint('sales', __name__)

@sales.route('/sales/new')
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

@sales.route('/sales/cart/add', methods=['POST'])
@login_required
def cart_add():
    product_id = request.form.get('product_id')
    quantity_raw = request.form.get('quantity', '1').strip()
    
    # 1. Validação de Campo Vazio
    if not product_id:
        flash('ID do produto inválido.', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    # 2. Validação de Conversão (Quantidade de itens)
    try:
        quantity = int(quantity_raw)
    except ValueError:
        flash('A quantidade inserida deve ser um número inteiro válido.', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    if quantity <= 0:
        flash('A quantidade inserida deve ser maior que zero.', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    # Busca produto para verificar existência e estoque
    product = Product.query.get(product_id)
    if not product:
        flash('Produto não encontrado.', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    cart = get_cart()
    current_qty = cart.get(str(product_id), 0)
    requested_total = current_qty + quantity
    
    if requested_total > product.stock:
        flash(f'Quantidade solicitada excede o estoque disponível ({product.stock}).', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    cart[str(product_id)] = requested_total
    save_cart(cart)
    flash('Produto adicionado ao carrinho.', 'success')
    return redirect(url_for('sales.sales_new'))

@sales.route('/sales/cart/update', methods=['POST'])
@login_required
def cart_update():
    cart = get_cart()
    has_error = False
    for field_name, quantity in request.form.items():
        if field_name.startswith('qty_'):
            pid = field_name.replace('qty_', '')
            product = Product.query.get(pid)
            if not product:
                cart.pop(pid, None)
                continue
            try:
                qty = int(quantity)
                if qty <= 0:
                    cart.pop(pid, None)
                elif qty > product.stock:
                    cart[pid] = product.stock
                    flash(f'Quantidade de "{product.name}" ajustada para o estoque máximo disponível ({product.stock}).', 'warning')
                    has_error = True
                else:
                    cart[pid] = qty
            except ValueError:
                flash(f'Quantidade inválida para o produto "{product.name}".', 'warning')
                has_error = True
    save_cart(cart)
    if not has_error:
        flash('Carrinho atualizado.', 'info')
    return redirect(url_for('sales.sales_new'))

@sales.route('/sales/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def cart_remove(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    flash('Item removido do carrinho.', 'info')
    return redirect(url_for('sales.sales_new'))

@sales.route('/sales/cart/clear')
@login_required
def cart_clear():
    session.pop('cart', None)
    flash('Carrinho limpo.', 'info')
    return redirect(url_for('sales.sales_new'))

@sales.route('/sales/checkout', methods=['POST'])
@login_required
def sales_checkout():
    customer_id = request.form.get('customer_id')
    payment_method_id = request.form.get('payment_method_id')
    discount_raw = request.form.get('discount', '0').strip().replace(',', '.')
    
    # 1. Validação de Campos Vazios
    if not payment_method_id:
        flash('A forma de pagamento é obrigatória.', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    cart = get_cart()
    if not cart:
        flash('Carrinho vazio. Adicione produtos antes de finalizar.', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    # 2. Validação de Conversão (Desconto)
    try:
        discount = float(discount_raw)
    except ValueError:
        flash('Desconto com formato numérico inválido.', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    if discount < 0:
        flash('O desconto não pode ser negativo.', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    items, subtotal, _, tax, total = calculate_cart(cart)
    
    if discount > subtotal:
        flash('O desconto não pode ser maior que o subtotal da venda.', 'warning')
        return redirect(url_for('sales.sales_new'))
        
    tax = round((subtotal - discount) * TAX_RATE, 2)
    total = round(subtotal - discount + tax, 2)
    
    # 3. Tratamento de Erros de Base de Dados e Validação de Estoque Final
    try:
        sale = Sale(number=generate_sale_number(), customer_id=customer_id or None,
                    user_id=session['user_id'], payment_method_id=payment_method_id,
                    subtotal=subtotal, tax=tax, discount=discount, total=total)
        db.session.add(sale)
        
        # Validar estoque de cada produto novamente no checkout para evitar inconsistências
        for item in items:
            product = item['product']
            quantity = item['quantity']
            
            if product.stock < quantity:
                raise ValueError(f"Estoque insuficiente para o produto '{product.name}' (Disponível: {product.stock}, Solicitado: {quantity}).")
                
            total_price = item['total_price']
            sale_item = SaleItem(sale=sale, product=product, quantity=quantity,
                                 unit_price=product.price, total_price=total_price)
            db.session.add(sale_item)
            product.stock -= quantity
            
            movement = StockMovement(product=product, quantity=-quantity,
                                     reason=f'Venda {sale.number}')
            db.session.add(movement)
            
        db.session.commit()
        session.pop('cart', None)
        flash('Venda finalizada com sucesso.', 'success')
        return redirect(url_for('sales.sale_invoice', sale_id=sale.id))
        
    except ValueError as ve:
        db.session.rollback()
        flash(str(ve), 'warning')
        return redirect(url_for('sales.sales_new'))
    except Exception as e:
        db.session.rollback()
        from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
        log_error("Erro de base de dados ao finalizar venda (checkout)", e)
        flash('Erro de banco de dados: Não foi possível finalizar a venda.', 'danger')
        return redirect(url_for('sales.sales_new'))

@sales.route('/sales/history')
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

@sales.route('/sales/<int:sale_id>')
@login_required
def sale_invoice(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    return render_template('invoice.html', sale=sale)