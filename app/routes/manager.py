from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from app.decorators import manager_required
from app.forms import ClassForm
from app.forms import SubjectForm
from app.forms import StudentForm
from app.forms import TeacherForm
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime
from app.utils.common import occurrence_submission, search_students
import bcrypt

manager_bp = Blueprint('manager', __name__)


@manager_bp.route('/')
@manager_required
def index():
    username = session.get('username')
    return render_template('manager/index.html', username=username)


@manager_bp.route('/register_class', methods=['GET', 'POST'])
@manager_required
def register_class():
    form = ClassForm()
    if form.validate_on_submit():
        classe = form.classe.data
        mongo = PyMongo(current_app)

        # Inserir a nova turma no banco de dados
        mongo.db.classes.insert_one({
            'classe': classe
        })
        flash('Turma cadastrada com sucesso!', 'success')
        return redirect(url_for('manager.index'))

    return render_template('manager/register_class.html', form=form)


@manager_bp.route('/register_subject', methods=['GET', 'POST'])
@manager_required
def register_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        subject = form.subject.data
        mongo = PyMongo(current_app)

        # Inserir a nova turma no banco de dados
        mongo.db.subjects.insert_one({
            'subject': subject
        })
        flash('Disciplina cadastrada com sucesso!', 'success')
        return redirect(url_for('manager.index'))

    return render_template('manager/register_subject.html', form=form)


@manager_bp.route('/register_student', methods=['GET', 'POST'])
@manager_required
def register_student():
    if 'role' not in session or session['role'] != 'manager':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))

    form = StudentForm()
    mongo = PyMongo(current_app)

    # Buscar turmas da coleção classes
    classes = [(str(cls['_id']), cls['classe'])
               for cls in mongo.db.classes.find()]
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
            'role': 'student'
        })
        flash('Estudante cadastrado com sucesso!', 'success')
        return redirect(url_for('manager.index'))

    return render_template('manager/register_student.html', form=form)


@manager_bp.route('/register_teacher', methods=['GET', 'POST'])
@manager_required
def register_teacher():
    if 'role' not in session or session['role'] != 'manager':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))

    form = TeacherForm()
    mongo = PyMongo(current_app)

    # Buscar turmas da coleção disciplinas
    subjects = [(str(sub['_id']), sub['subject'])
                for sub in mongo.db.subjects.find()]
    form.update_subjects(subjects)

    # Buscar turmas da coleção classes
    classes = [(str(cls['_id']), cls['classe'])
               for cls in mongo.db.classes.find()]
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
            'role': 'teacher'
        })
        flash('Professor(a) cadastrado com sucesso!', 'success')
        return redirect(url_for('manager.index'))

    return render_template('manager/register_teacher.html', form=form)


@manager_bp.route('/register_occurrence', methods=['GET', 'POST'])
@manager_required
def register_occurrence():
    return occurrence_submission('manager')


@manager_bp.route('/api/search_students')
@manager_required
def search_students_route():
    return search_students()


def get_users_by_id(ids):
    users = []
    mongo = PyMongo(current_app)
    for user_id in ids:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        users.append(user)
    return users


@manager_bp.route('/manager_occurrence')
def manager_occurrence():
    mongo = PyMongo(current_app)
    occurrences = list(mongo.db.occurrences.find().sort("date", -1).limit(100))
    teachers_ids = [occurrence['teacher_id'] for occurrence in occurrences]
    students_ids = [occurrence['student_id'] for occurrence in occurrences]
    teachers = get_users_by_id(teachers_ids)
    students = get_users_by_id(students_ids)

    occurrences_data = []
    for i, occurrence in enumerate(occurrences):
        occurrence_data = {
            'id': str(occurrence['_id']),
            'teacher': teachers[i]['username'],
            'student': students[i]['username'],
            'description': occurrence['description'],
            'date': occurrence['date'].strftime('%d/%m/%Y')
        }
        occurrences_data.append(occurrence_data)

    return render_template('manager/manager_occurrence.html', occurrences_data=occurrences_data)


@manager_bp.route('/manager_occurrence/search')
def search_occurrences():
    query = request.args.get('query', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    skip = (page - 1) * per_page

    search_filter = {}
    if query:
        mongo = PyMongo(current_app)

        # Busca pelos IDs dos usuários com base no username
        users = list(mongo.db.users.find(
            {'username': {'$regex': query, '$options': 'i'}}))
        users_ids = [str(usr['_id']) for usr in users]

        search_filter = {
            '$or': [
                {'description': {'$regex': query, '$options': 'i'}},
                {'teacher_id': {'$in': users_ids}},
                {'student_id': {'$in': users_ids}}
            ]
        }

    # Adicionando filtro por período (data)
    if start_date and end_date:
        search_filter['date'] = {
            '$gte': datetime.strptime(start_date, '%Y-%m-%d'),
            '$lte': datetime.strptime(end_date, '%Y-%m-%d')
        }

    mongo = PyMongo(current_app)
    total_occurrences = mongo.db.occurrences.count_documents(search_filter)
    occurrences = list(mongo.db.occurrences.find(
        search_filter).sort("date", -1).skip(skip).limit(per_page))

    teachers_ids = [occurrence['teacher_id'] for occurrence in occurrences]
    students_ids = [occurrence['student_id'] for occurrence in occurrences]
    teachers = get_users_by_id(teachers_ids)
    students = get_users_by_id(students_ids)

    occurrences_data = []
    for i, occurrence in enumerate(occurrences):
        occurrence_data = {
            'id': str(occurrence['_id']),
            'teacher': teachers[i]['username'],
            'student': students[i]['username'],
            'description': occurrence['description'],
            'date': occurrence['date'].strftime('%d/%m/%Y')
        }
        occurrences_data.append(occurrence_data)

    total_pages = (total_occurrences + per_page - 1) // per_page

    return jsonify({
        'occurrences': occurrences_data,
        'current_page': page,
        'total_pages': total_pages
    })


@manager_bp.route('/manager_occurrence/delete/<id>', methods=['POST'])
def delete_occurrence(id):
    mongo = PyMongo(current_app)
    result = mongo.db.occurrences.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': result.deleted_count == 1})
