from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from app.decorators import manager_required
from app.forms import ClassForm
from app.forms import SubjectForm
from app.forms import StudentForm
from app.forms import TeacherForm
from flask_pymongo import PyMongo
from app.utils.common import (
    index,
    occurrence_submission,
    search_students,
    manager_occurrence,
    search_occurrences,
    delete_occurrence,
    update_field
)
import bcrypt

manager_bp = Blueprint('manager', __name__)


@manager_bp.route('/')
@manager_required
def index_route():
    return index()


@manager_bp.route('/register_class', methods=['GET', 'POST'])
@manager_required
def register_class():
    manager_id = session.get('userID')
    form = ClassForm()
    if form.validate_on_submit():
        classe = form.classe.data
        mongo = PyMongo(current_app)

        # Inserir a nova turma no banco de dados
        mongo.db.classes.insert_one({
            'classe': classe,
            'occurrences': [],
            'manager_id': manager_id
        })
        flash('Turma cadastrada com sucesso!', 'success')
        return redirect(url_for('manager.index_route'))

    return render_template('manager/register_class.html', form=form)


@manager_bp.route('/register_subject', methods=['GET', 'POST'])
@manager_required
def register_subject():
    manager_id = session.get('userID')
    form = SubjectForm()
    if form.validate_on_submit():
        subject = form.subject.data
        mongo = PyMongo(current_app)

        # Inserir a nova turma no banco de dados
        mongo.db.subjects.insert_one({
            'subject': subject,
            'occurrences': [],
            'manager_id': manager_id
        })
        flash('Disciplina cadastrada com sucesso!', 'success')
        return redirect(url_for('manager.index_route'))

    return render_template('manager/register_subject.html', form=form)


@manager_bp.route('/register_student', methods=['GET', 'POST'])
@manager_required
def register_student():
    if 'role' not in session or session['role'] != 'manager':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))
    manager_id = session.get('userID')
    form = StudentForm()
    mongo = PyMongo(current_app)

    # Buscar turmas da coleção classes
    classes = [(str(cls['_id']), cls['classe'])
               for cls in mongo.db.classes.find({"manager_id": manager_id})]

    form.update_classes(classes)

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        classe = form.classe.data

        # Hashing da senha
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password.decode('utf-8'),
            'classe': classe,
            'role': 'student',
            'manager_id': manager_id,
            'occurrences': []
        })
        flash('Estudante cadastrado com sucesso!', 'success')
        return redirect(url_for('manager.index_route'))

    return render_template('manager/register_student.html', form=form)


@manager_bp.route('/register_teacher', methods=['GET', 'POST'])
@manager_required
def register_teacher():
    if 'role' not in session or session['role'] != 'manager':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))

    form = TeacherForm()
    mongo = PyMongo(current_app)
    manager_id = session.get('userID')

    # Buscar turmas da coleção disciplinas
    subjects = [(str(sub['_id']), sub['subject'])
                for sub in mongo.db.subjects.find({"manager_id": manager_id})]
    form.update_subjects(subjects)

    # Buscar turmas da coleção classes
    classes = [(str(cls['_id']), cls['classe'])
               for cls in mongo.db.classes.find({"manager_id": manager_id})]
    form.update_classes(classes)

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        subjects = form.subjects.data
        classes = form.classes.data

        # Hashing da senha
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password.decode('utf-8'),
            'subjects': subjects,
            'classes': classes,
            'role': 'teacher',
            'manager_id': manager_id,
            'occurrences': []
        })
        flash('Professor(a) cadastrado com sucesso!', 'success')
        return redirect(url_for('manager.index_route'))

    return render_template('manager/register_teacher.html', form=form)


@ manager_bp.route('/register_occurrence', methods=['GET', 'POST'])
@ manager_required
def register_occurrence():
    return occurrence_submission('manager')


@ manager_bp.route('/api/search_students')
@ manager_required
def search_students_route():
    return search_students()


@ manager_bp.route('/manager_occurrence')
@ manager_required
def manager_occurrence_route():
    return manager_occurrence()


@ manager_bp.route('/manager_occurrence/search')
@ manager_required
def search_occurrences_route():
    return search_occurrences()


@ manager_bp.route('/manager_occurrence/delete/<string:id>', methods=['POST'])
def delete_occurrence_route(id):
    return delete_occurrence(id)


@ manager_bp.route('/manager_occurrence/update/<string:field>/<string:occurrence_id>', methods=['POST'])
def update_occurrence_field_route(field, occurrence_id):
    return update_field(field, occurrence_id)
