from flask import Blueprint
from app.decorators import monitor_required, login_required
from app.utils.common import (
    index,
    occurrence_submission,
    search_students,
    manager_occurrence,
    search_occurrences,
    delete_occurrence,
    update_field,
    configurations,
    username_form_route,
    changing_username,
    password_form_route,
    changing_password,
    email_form_route,
    changing_email,
    profile_info,
    generate_pdf
)

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/')
@login_required
@monitor_required
def index_route():
    return index()

@monitor_bp.route('/register_occurrence', methods=['GET', 'POST'])
@login_required
@monitor_required
def register_occurrence():
    return occurrence_submission('monitor')


@monitor_bp.route('/api/search_students')
@login_required
@monitor_required
def search_students_route():
    return search_students()


@monitor_bp.route('/manager_occurrence')
@login_required
@monitor_required
def manager_occurrence_route():
    return manager_occurrence()


@monitor_bp.route('/manager_occurrence/search')
@login_required
@monitor_required
def search_occurrences_route():
    return search_occurrences()


@monitor_bp.route('/manager_occurrence/delete/<string:id>', methods=['POST'])
@login_required
def delete_occurrence_route(id):
    return delete_occurrence(id)


@monitor_bp.route('/manager_occurrence/update/<string:field>/<string:occurrence_id>', methods=['POST'])
@login_required
def update_occurrence_field_route(field, occurrence_id):
    return update_field(field, occurrence_id)


@monitor_bp.route('/configurations')
@login_required
@monitor_required
def configurations_route():
    return configurations()


@ monitor_bp.route('/profile_info')
@login_required
@ monitor_required
def profile_info_route():
    return profile_info()

@ monitor_bp.route('/configurations/username')
@login_required
@ monitor_required
def change_username_form():
    return username_form_route()


@ monitor_bp.route('/configurations/username/change', methods=['POST'])
@ monitor_required
def changing_username_route():
    return changing_username()

@monitor_bp.route('/configurations/password')
@login_required
@monitor_required
def change_password_form():
    return password_form_route()


@monitor_bp.route('/configurations/password/change', methods=['POST'])
@login_required
@monitor_required
def changing_password_route():
    return changing_password()


@monitor_bp.route('/configurations/email')
@login_required
def change_email_form():
    return email_form_route()


@monitor_bp.route('/configurations/email/change', methods=['POST'])
@login_required
@monitor_required
def changing_email_route():
    return changing_email()


@monitor_bp.route('/api/generate_pdf', methods=['POST'])
@login_required
@monitor_required
def generate_pdf_route():
    return generate_pdf()

