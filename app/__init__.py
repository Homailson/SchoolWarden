from flask import Flask, render_template, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from flask_wtf import CSRFProtect
from config import Config
from app.forms import LoginForm
import bcrypt

mongo = PyMongo()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize PyMongo with the app
    mongo.init_app(app)
    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Importing blueprints
    from .routes.manager import manager_bp
    from .routes.student import student_bp
    from .routes.teacher import teacher_bp
    from .routes.main import main_bp
    from .routes.admin import admin_bp

    # Register Blueprints
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Login route

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'role' in session:
            role = session['role']
            if role == 'admin':
                return redirect(url_for('admin.index'))
            elif role == 'teacher':
                return redirect(url_for('teacher.index'))
            elif role == 'student':
                return redirect(url_for('student.index'))
            elif role == 'manager':
                return redirect(url_for('manager.index'))

        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data.encode(
                'utf-8')  # Encode password to bytes

            # Aqui você implementa a lógica para verificar o usuário e senha no MongoDB
            user = mongo.db.users.find_one({'username': username})

            if user and 'password' in user:
                hashed_password = user['password'].encode(
                    'utf-8')  # Encode hashed password to bytes
                if bcrypt.checkpw(password, hashed_password):
                    session['role'] = user['role']
                    session['username'] = user['username']
                    session['userID'] = str(user['_id'])

                    # Redirecionamento baseado no papel (role)
                    if user['role'] == 'admin':
                        return redirect(url_for('admin.index'))
                    elif user['role'] == 'teacher':
                        return redirect(url_for('teacher.index'))
                    elif user['role'] == 'student':
                        return redirect(url_for('student.index'))
                    elif user['role'] == 'manager':
                        return redirect(url_for('manager.index'))
                    else:
                        flash('Papel de usuário desconhecido', 'error')
                else:
                    flash('Nome de usuário ou senha inválidos', 'error')
            else:
                flash('Nome de usuário ou senha inválidos', 'error')

        return render_template('login.html', form=form)

    # Logout route
    @app.route('/logout')
    def logout():
        if 'role' in session:
            session.clear()
            flash('Logout realizado com sucesso', 'success')
        else:
            flash('Você já está deslogado', 'info')
        return redirect(url_for('main.index'))

    return app
