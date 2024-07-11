from flask import Flask, render_template, redirect, url_for, flash, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_pymongo import PyMongo
from flask_wtf import CSRFProtect
from config import Config
from app.forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm
import bcrypt
import secrets

mongo = PyMongo()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = secrets.token_urlsafe(32)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'homailson@gmail.com'
    app.config['MAIL_PASSWORD'] = 'arqdgjadbuizeize'

    # Initialize PyMongo with the app
    mongo.init_app(app, app.config['MONGO_URI'])

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
                return redirect(url_for('admin.index_route'))
            elif role == 'teacher':
                return redirect(url_for('teacher.index_route'))
            elif role == 'student':
                return redirect(url_for('student.index_route'))
            elif role == 'manager':
                return redirect(url_for('manager.index_route'))

        form = LoginForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data.encode(
                'utf-8')  # Encode password to bytes

            # Aqui você implementa a lógica para verificar o usuário e senha no MongoDB
            user = mongo.db.users.find_one({'email': email})

            if user and 'email' in user:
                hashed_password = user['password'].encode(
                    'utf-8')  # Encode hashed password to bytes
                if bcrypt.checkpw(password, hashed_password):
                    session['role'] = user['role']
                    session['username'] = user['username']
                    session['email'] = user['email']
                    session['userID'] = str(user['_id'])

                    # Redirecionamento baseado no papel (role)
                    if user['role'] == 'admin':
                        return redirect(url_for('admin.index_route'))
                    elif user['role'] == 'teacher':
                        return redirect(url_for('teacher.index_route'))
                    elif user['role'] == 'student':
                        return redirect(url_for('student.index_route'))
                    elif user['role'] == 'manager':
                        return redirect(url_for('manager.index_route'))
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

    mail = Mail(app)
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    @app.route('/reset_password_request', methods=['GET', 'POST'])
    def reset_password_request():
        form = ResetPasswordRequestForm()
        print("iniciando função")
        if form.validate_on_submit():
            email = form.email.data
            user = mongo.db.users.find_one({"email": email})
            print("validado")
            if user:
                token = s.dumps(email, salt='password-reset-salt')
                reset_url = url_for(
                    'reset_password', token=token, _external=True)
                msg = Message('Redefinir Senha',
                              sender='noreply@example.com', recipients=[email])
                msg.body = f'Para redefinir sua senha, clique no link a seguir: {reset_url}'
                mail.send(msg)
                flash(
                    'Um e-mail com instruções para redefinir sua senha foi enviado.', 'info')
        print("usuario não existe")
        return render_template('common/reset_password_request.html', form=form)

    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        try:
            email = s.loads(token, salt='password-reset-salt', max_age=3600)
        except:
            flash('O link de redefinição de senha é inválido ou expirou.', 'warning')
            return redirect(url_for('reset_password_request'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            mongo = PyMongo(app)
            password = form.password.data
            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt())
            mongo.db.users.update_one(
                {"email": email}, {"$set": {"password": hashed_password.decode('utf-8')}})
            flash('Sua senha foi redefinida com sucesso!', 'success')
            return redirect(url_for('login'))
        return render_template('common/reset_password.html', form=form)

    return app
