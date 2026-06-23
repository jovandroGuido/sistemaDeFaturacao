from flask import Blueprint, redirect, render_template, url_for, flash, request
# pyrefly: ignore [missing-import]
from src.lib.login_required import login_required
# pyrefly: ignore [missing-import]
from src.database.models.models import Customer
# pyrefly: ignore [missing-import]
from src.database.config.database import db

customer = Blueprint('customer', __name__)

@customer.route('/customers')
@login_required
def customers():
    query = request.args.get('q', '').strip()
    customers = Customer.query
    if query:
        customers = customers.filter(Customer.name.ilike(f'%{query}%') | Customer.email.ilike(f'%{query}%') | Customer.phone.ilike(f'%{query}%'))
    customers = customers.order_by(Customer.name).all()
    return render_template('customers.html', customers=customers, q=query)

@customer.route('/customers/new', methods=['POST'])
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

@customer.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
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

@customer.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
def customers_delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('Cliente excluído com sucesso.', 'success')
    return redirect(url_for('customers'))