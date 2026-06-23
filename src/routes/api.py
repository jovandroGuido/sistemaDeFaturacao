from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from src.database.config.database import db
# pyrefly: ignore [missing-import]
from src.database.models.models import Product
# pyrefly: ignore [missing-import]
from src.lib.login_required import login_required

api = Blueprint('api', __name__)

@api.route('/api/products/search')
@login_required
def api_products_search():
    term = request.args.get('q', '').strip()
    products = []
    if term:
        result = Product.query.filter(db.or_(Product.name.ilike(f'%{term}%'), Product.code.ilike(f'%{term}%'))).limit(10).all()
        products = [{'id': p.id, 'name': p.name, 'code': p.code, 'price': p.price, 'stock': p.stock} for p in result]
    return jsonify(products)