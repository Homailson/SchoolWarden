from flask import Blueprint
from app.decorators import student_required, login_required
from app.utils.common import (
    index,
    manager_occurrence,
    search_occurrences,
    configurations,
    username_form_route,
    changing_username,
    password_form_route,
    changing_password,
    email_form_route,
    changing_email,
    profile_info
)

student_bp = Blueprint('student', __name__)


@student_bp.route('/')
@login_required
@student_required
def index_route():
    return index()


@student_bp.route('/manager_occurrence')
@login_required
@student_required
def manager_occurrence_route():
    return manager_occurrence()


@student_bp.route('/manager_occurrence/search')
@login_required
@student_required
def search_occurrences_route():
    return search_occurrences()


@student_bp.route('/student/configurations')
@login_required
@student_required
def configurations_route():
    return configurations()


@ student_bp.route('/profile_info')
@login_required
@ student_required
def profile_info_route():
    return profile_info()

@ student_bp.route('/configurations/username')
@login_required
@ student_required
def change_username_form():
    return username_form_route()


@ student_bp.route('/configurations/username/change', methods=['POST'])
@ student_required
def changing_username_route():
    return changing_username()

@student_bp.route('/configurations/password')
@login_required
@student_required
def change_password_form():
    return password_form_route()


@student_bp.route('/configurations/password/change', methods=['POST'])
@login_required
@student_required
def changing_password_route():
    return changing_password()


@student_bp.route('/configurations/email')
@login_required
@student_required
def change_email_form():
    return email_form_route()


@student_bp.route('/configurations/email/change', methods=['POST'])
@login_required
@student_required
def changing_email_route():
    return changing_email()
