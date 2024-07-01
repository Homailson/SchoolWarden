from flask import Blueprint, render_template, session
from app.decorators import teacher_required
from app.utils.common import (
    occurrence_submission,
    search_students,
    manager_occurrence,
    search_occurrences,
    delete_occurrence,
    update_occurrence_field
)

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


@teacher_bp.route('/manager_occurrence')
@teacher_required
def teacher_occurrence_route():
    return manager_occurrence()


@teacher_bp.route('/manager_occurrence/search')
@teacher_required
def search_occurrences_route():
    return search_occurrences()


@teacher_bp.route('/manager_occurrence/delete/<string:id>', methods=['POST'])
def delete_occurrence_route(id):
    return delete_occurrence(id)


@teacher_bp.route('/manager_occurrence/update/<string:field>/<string:occurrence_id>', methods=['POST'])
def update_occurrence_field_route(field, occurrence_id):
    return update_occurrence_field(field, occurrence_id)
