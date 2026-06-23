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
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip().lower()
    address = request.form.get('address', '').strip()
    
    # 1. Validação de Campo Vazio
    if not name:
        flash('Nome do cliente é obrigatório.', 'warning')
        return redirect(url_for('customer.customers'))
        
    # 2. Validação de Formato (Erro de Conversão/Formato)
    if email and '@' not in email:
        flash('O formato do e-mail inserido é inválido.', 'warning')
        return redirect(url_for('customer.customers'))
        
    # 3. Tratamento de Erros de Base de Dados
    try:
        new_customer = Customer(name=name, phone=phone, email=email, address=address)
        db.session.add(new_customer)
        db.session.commit()
        flash('Cliente cadastrado com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
        log_error(f"Erro de base de dados ao cadastrar cliente '{name}'", e)
        flash('Erro no banco de dados ao salvar o cliente.', 'danger')
        
    return redirect(url_for('customer.customers'))

@customer.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def customers_edit(customer_id):
    customer_to_edit = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip().lower()
        address = request.form.get('address', '').strip()
        
        # 1. Validação de Campo Vazio
        if not name:
            flash('Nome do cliente é obrigatório.', 'warning')
            return redirect(url_for('customer.customers_edit', customer_id=customer_id))
            
        # 2. Validação de Formato (Erro de Conversão/Formato)
        if email and '@' not in email:
            flash('O formato do e-mail inserido é inválido.', 'warning')
            return redirect(url_for('customer.customers_edit', customer_id=customer_id))
            
        # 3. Tratamento de Erros de Base de Dados
        try:
            customer_to_edit.name = name
            customer_to_edit.phone = phone
            customer_to_edit.email = email
            customer_to_edit.address = address
            db.session.commit()
            flash('Cliente atualizado com sucesso.', 'success')
            return redirect(url_for('customer.customers'))
        except Exception as e:
            db.session.rollback()
            from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
            log_error(f"Erro de base de dados ao editar cliente {customer_id}", e)
            flash('Erro no banco de dados ao atualizar o cliente.', 'danger')
            
    return render_template('customer_edit.html', customer=customer_to_edit)

@customer.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
def customers_delete(customer_id):
    customer_to_delete = Customer.query.get_or_404(customer_id)
    
    # 3. Tratamento de Erros de Base de Dados (ex: FK constraint)
    try:
        db.session.delete(customer_to_delete)
        db.session.commit()
        flash('Cliente excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        from src.lib.logger import log_error  # pyrefly: ignore [missing-import]
        log_error(f"Erro ao excluir cliente {customer_id} (possivelmente vinculado a vendas)", e)
        flash('Erro de banco de dados: Não é possível excluir um cliente que já possui vendas associadas.', 'danger')
        
    return redirect(url_for('customer.customers'))