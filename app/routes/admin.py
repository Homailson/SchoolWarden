from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from app.decorators import admin_required
from app.forms import ManagerForm
from app.utils.common import (
    index,
    configurations,
    password_form_route,
    changing_password,
    email_form_route,
    changing_email,
    profile_info
)
from app import mongo
import bcrypt

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@admin_required
def index_route():
    return index()


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
        school = form.school.data
        email = form.email.data
        confirm_email = form.confirm_email.data
        logo_url = form.logo_url.data
        if email != confirm_email:
            flash('As senhas não coincidem!')
            return redirect(url_for('admin.register_manager'))
        else:
            # Hashing da senha
            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt())

            # Inserir o novo gestor no banco de dados
            mongo.db.users.insert_one({
                'username': name,
                'email': email,
                'password': hashed_password.decode('utf-8'),
                'school': school,
                'logo_url': logo_url,
                'occurrences': [],
                'subjects': [],
                'classes': [],
                'role': 'manager'
            })
            flash('Gestor(a) cadastrado com sucesso!', 'success')
            return redirect(url_for('admin.index_route'))

    return render_template('admin/register_manager.html', form=form)


@admin_bp.route('/configurations')
@admin_required
def configurations_route():
    return configurations()


@admin_bp.route('/configurations/password')
@admin_required
def change_password_form():
    return password_form_route()


@admin_bp.route('/profile_info')
@admin_required
def profile_info_route():
    return profile_info()


@admin_bp.route('/configurations/password/change', methods=['POST'])
@admin_required
def changing_password_route():
    return changing_password()


@admin_bp.route('/configurations/email')
def change_email_form():
    return email_form_route()


@admin_bp.route('/configurations/email/change', methods=['POST'])
@admin_required
def changing_email_route():
    return changing_email()
