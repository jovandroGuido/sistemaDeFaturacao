from flask import session
# pyrefly: ignore [missing-import]
from src.database.models.models import Product, Sale
# pyrefly: ignore [missing-import]
from src.lib.env import TAX_RATE

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