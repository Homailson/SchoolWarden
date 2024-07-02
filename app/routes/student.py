from flask import Blueprint
from app.decorators import student_required
from app.utils.common import index, manager_occurrence, search_occurrences

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
