from flask import Blueprint, render_template
# pyrefly: ignore [missing-import]
from src.database.config.database import db
# pyrefly: ignore [missing-import]
from src.database.models.models import Product, Customer, Sale, SaleItem
# pyrefly: ignore [missing-import]
from src.lib.login_required import login_required
from datetime import date

reports = Blueprint('reports', __name__)

@reports.route('/reports')
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