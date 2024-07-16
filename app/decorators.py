from functools import wraps
from flask import redirect, url_for, flash, session


def admin_required(view_func):
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        if 'role' in session and session['role'] == 'admin':
            return view_func(*args, **kwargs)
        else:
            flash('Acesso não autorizado', 'error')
            return redirect(url_for('main.index'))
    return decorated_function


def manager_required(view_func):
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        if 'role' in session and session['role'] == 'manager':
            return view_func(*args, **kwargs)
        else:
            flash('Acesso não autorizado', 'error')
            return redirect(url_for('main.index'))
    return decorated_function


def teacher_required(view_func):
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        if 'role' in session and session['role'] == 'teacher':
            return view_func(*args, **kwargs)
        else:
            flash('Acesso não autorizado', 'error')
            return redirect(url_for('main.index'))
    return decorated_function


def student_required(view_func):
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        if 'role' in session and session['role'] == 'student':
            return view_func(*args, **kwargs)
        else:
            flash('Acesso não autorizado', 'error')
            return redirect(url_for('main.index'))
    return decorated_function
