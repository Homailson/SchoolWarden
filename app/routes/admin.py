from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from app.decorators import admin_required
from app.forms import ManagerForm
from flask_pymongo import PyMongo
import bcrypt

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@admin_required
def index():
    username = session.get('username')
    return render_template('admin/index.html', username=username)


@admin_bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register_manager():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))

    form = ManagerForm()
    if form.validate_on_submit():
        name = form.username.data
        password = form.password.data  # Capturar a senha do formulário

        # Hashing da senha
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        mongo = PyMongo(current_app)

        # Inserir o novo gestor no banco de dados
        mongo.db.users.insert_one({
            'username': name,
            # Incluir a senha hashada no documento
            'password': hashed_password.decode('utf-8'),
            'role': 'manager'
        })
        flash('Gestor(a) cadastrado com sucesso!', 'success')
        return redirect(url_for('admin.index'))

    return render_template('admin/register_manager.html', form=form)
