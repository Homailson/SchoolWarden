import os
from flask import Blueprint, render_template, session, jsonify, request, current_app
from app.decorators import teacher_required
from flask_pymongo import PyMongo
from app.utils.common import occurrence_submission, search_students

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/')
@teacher_required
def index():
    username = session.get('username')
    return render_template('teacher/index.html', username=username)


@teacher_bp.route('/register_occurrence', methods=['GET', 'POST'])
@teacher_required
def register_occurrence():
    return occurrence_submission('teacher')


@teacher_bp.route('/api/search_students')
@teacher_required
def search_students_route():
    return search_students()
