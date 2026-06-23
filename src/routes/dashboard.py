from flask import Blueprint, redirect, render_template, url_for
# pyrefly: ignore [missing-import]
from src.database.models.models import Product, Customer, Sale
# pyrefly: ignore [missing-import]
from src.lib.login_required import login_required
# pyrefly: ignore [missing-import]
from src.database.config.database import db
# pyrefly: ignore [missing-import]
from datetime import date

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def home():
    return redirect(url_for('dashboard'))

@dashboard.route('/dashboard')
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