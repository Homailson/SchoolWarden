from flask import Blueprint, render_template, session
from app.decorators import student_required

student_bp = Blueprint('student', __name__)


@student_bp.route('/')
@student_required
def index():
    username = session.get('username')
    return render_template('student/index.html', username=username)
