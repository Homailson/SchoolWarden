from flask import Blueprint
from app.decorators import teacher_required, login_required
from app.utils.common import (
    index,
    occurrence_submission,
    search_students,
    manager_occurrence,
    search_occurrences,
    delete_occurrence,
    update_field,
    configurations,
    password_form_route,
    changing_password,
    email_form_route,
    changing_email,
    profile_info,
    generate_pdf
)

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/')
@login_required
@teacher_required
def index_route():
    return index()


@teacher_bp.route('/register_occurrence', methods=['GET', 'POST'])
@login_required
@teacher_required
def register_occurrence():
    return occurrence_submission('teacher')


@teacher_bp.route('/api/search_students')
@login_required
@teacher_required
def search_students_route():
    return search_students()


@teacher_bp.route('/manager_occurrence')
@login_required
@teacher_required
def manager_occurrence_route():
    return manager_occurrence()


@teacher_bp.route('/manager_occurrence/search')
@login_required
@teacher_required
def search_occurrences_route():
    return search_occurrences()


@teacher_bp.route('/manager_occurrence/delete/<string:id>', methods=['POST'])
@login_required
def delete_occurrence_route(id):
    return delete_occurrence(id)


@teacher_bp.route('/manager_occurrence/update/<string:field>/<string:occurrence_id>', methods=['POST'])
@login_required
def update_occurrence_field_route(field, occurrence_id):
    return update_field(field, occurrence_id)


@teacher_bp.route('/configurations')
@login_required
@teacher_required
def configurations_route():
    return configurations()


@ teacher_bp.route('/profile_info')
@login_required
@ teacher_required
def profile_info_route():
    return profile_info()


@teacher_bp.route('/configurations/password')
@login_required
@teacher_required
def change_password_form():
    return password_form_route()


@teacher_bp.route('/configurations/password/change', methods=['POST'])
@login_required
@teacher_required
def changing_password_route():
    return changing_password()


@teacher_bp.route('/configurations/email')
@login_required
def change_email_form():
    return email_form_route()


@teacher_bp.route('/configurations/email/change', methods=['POST'])
@login_required
@teacher_required
def changing_email_route():
    return changing_email()


@teacher_bp.route('/api/generate_pdf', methods=['POST'])
@login_required
@teacher_required
def generate_pdf_route():
    return generate_pdf()
