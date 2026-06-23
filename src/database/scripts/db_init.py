import os
from flask import Flask
from database import init_database, db
from models import User, Category, Product, Customer, PaymentMethod

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
init_database(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@faturapro.ao').first():
        admin = User(name='Administrador', email='admin@faturapro.ao', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
    if not PaymentMethod.query.first():
        methods = ['Dinheiro', 'Cartão', 'Transferência Bancária', 'Multicaixa']
        db.session.add_all([PaymentMethod(name=m) for m in methods])
    if not Category.query.first():
        papelaria = Category(name='Papelaria')
        eletronicos = Category(name='Eletrônicos')
        acessorios = Category(name='Acessórios')
        db.session.add_all([papelaria, eletronicos, acessorios])
    else:
        papelaria = Category.query.filter_by(name='Papelaria').first()
        eletronicos = Category.query.filter_by(name='Eletrônicos').first()
        acessorios = Category.query.filter_by(name='Acessórios').first()
    if not Product.query.first():
        db.session.add_all([
            Product(code='P001', name='Caneta Azul', category=papelaria, price=0.50, stock=120),
            Product(code='P002', name='Caderno A4', category=papelaria, price=2.80, stock=60),
            Product(code='P003', name='Mouse Óptico', category=eletronicos, price=15.00, stock=25),
        ])
    if not Customer.query.first():
        db.session.add_all([
            Customer(name='João Silva', phone='+244 923 000 000', email='joao@cliente.ao', address='Rua da Liberdade, Luanda'),
            Customer(name='Maria Pereira', phone='+244 924 000 000', email='maria@cliente.ao', address='Avenida de Portugal, Talatona'),
        ])
    db.session.commit()
    print('Banco inicializado com dados de exemplo.')
