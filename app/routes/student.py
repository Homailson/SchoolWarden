from flask import Blueprint
from app.decorators import student_required
from app.utils.common import (
    index,
    manager_occurrence,
    search_occurrences,
    configurations,
    password_form_route,
    changing_password,
    email_form_route
)

student_bp = Blueprint('student', __name__)


@student_bp.route('/')
@student_required
def index_route():
    return index()


@student_bp.route('/manager_occurrence')
@student_required
def manager_occurrence_route():
    return manager_occurrence()


@student_bp.route('/manager_occurrence/search')
@student_required
def search_occurrences_route():
    return search_occurrences()


@student_bp.route('/student/configurations')
@student_required
def manager_configurations():
    return configurations()


@student_bp.route('/student/configurations/change_password')
@student_required
def change_password_form():
    return password_form_route()


@student_bp.route('/student/configurations/change_password', methods=['POST'])
@student_required
def changing_password_route():
    return changing_password()


@student_bp.route('/student/configurations/change_email')
@student_required
def change_email_form():
    return email_form_route()
