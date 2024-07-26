from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, jsonify, request
from app.decorators import manager_required, login_required
from app.forms import ClassForm
from app.forms import SubjectForm
from app.forms import StudentForm
from app.forms import TeacherForm
from app import mongo
from datetime import date
from bson.objectid import ObjectId
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
    username_form_route,
    changing_username,
    email_form_route,
    changing_email,
    profile_info,
    generate_pdf,
    dashboard_route,
    dashboard
)
import bcrypt

manager_bp = Blueprint('manager', __name__)


@manager_bp.route('/')
@login_required
@manager_required
def index_route():
    return index()


@manager_bp.route('/register_subject', methods=['GET', 'POST'])
@login_required
@manager_required
def register_subject():
    manager_id = session.get('userID')
    user = mongo.db.users.find_one({"_id": ObjectId(manager_id)})
    subjects_ids = user['subjects']
    subjects_mongo = [mongo.db.subjects.find_one(
        {"_id": id}) for id in subjects_ids]
    subjects = [subj['subject'] for subj in subjects_mongo]
    form = SubjectForm()
    form.update_subjects(subjects)
    year=date.today().year
    if form.validate_on_submit():
        subject = form.subject.data

        # Inserir a nova turma no banco de dados
        result = mongo.db.subjects.insert_one({
            'subject': subject,
            'occurrences': [],
            'manager_id': manager_id,
            'year': year
        })

        subject_id = result.inserted_id

        mongo.db.users.update_one(
            {"_id": ObjectId(manager_id)},
            {"$push": {"subjects": subject_id}}
        )

        flash('Disciplina cadastrada com sucesso!', 'success')
        return redirect(url_for('manager.index_route'))

    return render_template('manager/register_subject.html', form=form, year=year)


@manager_bp.route('/register_class', methods=['GET', 'POST'])
@login_required
@manager_required
def register_class():
    manager_id = session.get('userID')
    user = mongo.db.users.find_one({"_id": ObjectId(manager_id)})
    classes_ids = user['classes']
    classes_mongo = [mongo.db.classes.find_one(
        {"_id": id}) for id in classes_ids]
    classes = [cls['classe'] for cls in classes_mongo]
    form = ClassForm()
    form.update_classes(classes)
    year=date.today().year
    if form.validate_on_submit():
        classe = form.classe.data

        # Inserir a nova turma no banco de dados
        result = mongo.db.classes.insert_one({
            'classe': classe,
            'occurrences': [],
            'manager_id': manager_id,
            'year': year
        })

        classe_id = result.inserted_id

        mongo.db.users.update_one(
            {"_id": ObjectId(manager_id)},
            {"$push": {"classes": classe_id}}
        )

        flash('Turma cadastrada com sucesso!', 'success')
        return redirect(url_for('manager.index_route'))

    return render_template('manager/register_class.html', form=form, year=year)


@ manager_bp.route('/register_teacher', methods=['GET', 'POST'])
@login_required
@ manager_required
def register_teacher():
    if 'role' not in session or session['role'] != 'manager':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))

    form = TeacherForm()
    manager_id = session.get('userID')
    user = mongo.db.users.find_one({"_id": ObjectId(manager_id)})

    # atualizando disciplinas
    subjects_ids = user['subjects']
    subjects_mongo = [mongo.db.subjects.find_one(
        {"_id": id}) for id in subjects_ids]
    subjects = [sub['subject'] for sub in subjects_mongo]
    subjects.remove(
        "Extradisciplina") if "Extradisciplina" in subjects else subjects
    form.update_subjects(subjects)

    # atualizando classes
    classes_ids = user['classes']
    classes_mongo = [mongo.db.classes.find_one(
        {"_id": id}) for id in classes_ids]
    classes = [cls['classe'] for cls in classes_mongo]
    classes.remove("Extraturma") if "Extraturma" in classes else classes
    form.update_classes(classes)

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        confirm_email = form.confirm_email.data
        password = form.password.data
        subjects = form.subjects.data
        classes = form.classes.data

        subjects_ids = [sub['_id']
                        for sub in subjects_mongo if sub['subject'] in subjects]

        classes_ids = [cls['_id']
                       for cls in classes_mongo if cls['classe'] in classes]

        if email != confirm_email:
            flash('Os emails não coincidem!', 'error')
        else:
            # Hashing da senha
            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt())

            mongo.db.users.insert_one({
                'username': username,
                'password': hashed_password.decode('utf-8'),
                'email': email,
                'subjects': subjects_ids,
                'classes': classes_ids,
                'role': 'teacher',
                'manager_id': manager_id,
                'occurrences': []
            })
            flash('Professor(a) cadastrado com sucesso!', 'success')
            return redirect(url_for('manager.index_route'))

    return render_template('manager/register_teacher.html', form=form)


@ manager_bp.route('/register_student', methods=['GET', 'POST'])
@login_required
@ manager_required
def register_student():
    if 'role' not in session or session['role'] != 'manager':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))
    manager_id = session.get('userID')
    user = mongo.db.users.find_one({"_id": ObjectId(manager_id)})

    # atualizando classes
    classes_ids = user['classes']
    classes_mongo = [mongo.db.classes.find_one(
        {"_id": id}) for id in classes_ids]
    classes = [cls['classe'] for cls in classes_mongo]
    classes.remove("Extraturma") if "Extraturma" in classes else classes
    form = StudentForm()
    form.update_classes(classes)

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        confirm_email = form.confirm_email.data
        password = form.password.data
        classe = form.classe.data

        if email != confirm_email:
            flash('Os emails não coincidem!', 'error')
        else:
            # Hashing da senha
            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt())

            classe_id = [cls['_id'] for cls in classes_mongo if cls['classe'] == classe][0]

            mongo.db.users.insert_one({
                'username': username,
                'email': email,
                'password': hashed_password.decode('utf-8'),
                'classe': classe_id,
                'role': 'student',
                'manager_id': manager_id,
                'occurrences': []
            })
            flash('Estudante cadastrado com sucesso!', 'success')
            return redirect(url_for('manager.index_route'))

    return render_template('manager/register_student.html', form=form)


@ manager_bp.route('/register_occurrence', methods=['GET', 'POST'])
@login_required
@ manager_required
def register_occurrence():
    return occurrence_submission('manager')


@ manager_bp.route('/api/search_students')
@login_required
@ manager_required
def search_students_route():
    return search_students()


@ manager_bp.route('/manager_occurrence')
@login_required
@ manager_required
def manager_occurrence_route():
    return manager_occurrence()


@ manager_bp.route('/manager_occurrence/search')
@login_required
@ manager_required
def search_occurrences_route():
    return search_occurrences()


@ manager_bp.route('/manager_occurrence/delete/<string:id>', methods=['POST'])
@login_required
@ manager_required
def delete_occurrence_route(id):
    return delete_occurrence(id)


@ manager_bp.route('/manager_occurrence/update/<string:field>/<string:occurrence_id>', methods=['POST'])
@login_required
@ manager_required
def update_occurrence_field_route(field, occurrence_id):
    return update_field(field, occurrence_id)


@ manager_bp.route('/configurations')
@login_required
@ manager_required
def configurations_route():
    return configurations()


@ manager_bp.route('/profile_info')
@login_required
@ manager_required
def profile_info_route():
    return profile_info()


@ manager_bp.route('/configurations/password')
@login_required
@ manager_required
def change_password_form():
    return password_form_route()


@ manager_bp.route('/configurations/password/change', methods=['POST'])
@login_required
@ manager_required
def changing_password_route():
    return changing_password()


@ manager_bp.route('/configurations/username')
@login_required
@ manager_required
def change_username_form():
    return username_form_route()


@ manager_bp.route('/configurations/username/change', methods=['POST'])
@login_required
@ manager_required
def changing_username_route():
    return changing_username()


@ manager_bp.route('/configurations/email')
@login_required
@ manager_required
def change_email_form():
    return email_form_route()


@ manager_bp.route('/configurations/email/change', methods=['POST'])
@login_required
@ manager_required
def changing_email_route():
    return changing_email()


@manager_bp.route('/api/pending_occurrences_count', methods=['GET'])
@login_required
@manager_required
def pending_occurrences_count():
    role = session.get('role')
    if role == 'manager':
        manager_id = session.get('userID')
        # Encontre as ocorrências pendentes para o gerente específico
        pending_occurrences = list(
            mongo.db.occurrences.find(
                {"manager_id": manager_id,
                 "status": "pendente"}
            )
        )
        # Conte o número de ocorrências pendentes
        pending_counting = len(pending_occurrences)
    else:
        pending_counting = 0

    return jsonify({'pending_count': pending_counting})


@manager_bp.route('manager/students/<string:classe_id>')
def students_manager(classe_id):
    manager_id = session.get('userID')
    classe = mongo.db.classes.find_one({"_id": ObjectId(classe_id)})
    if classe_id:
        students = list(mongo.db.users.find(
            {
                "classe": ObjectId(classe_id),
                "role": "student",
                "manager_id": manager_id
            }
        ))
        return render_template('manager/student_class.html', students=students, classe=classe)
    else:
        return "A Classe não existe"
    
@manager_bp.route('/get-classes')
def get_classes():
    classes = mongo.db.classes.find({"year": date.today().year})
    # Converte os documentos em um formato serializável para JSON
    classes_list = []
    for c in classes:
        # Adiciona o campo _id como uma string
        if c['classe'] != "Extraturma":
            class_item = {
                '_id': str(c['_id']),
                'classe': c['classe'],
                'year': c['year']
            }
            classes_list.append(class_item)
    # Retorna a resposta JSON
    return jsonify({'classes': classes_list})

@manager_bp.route('/update_students', methods=['POST'])
def update_student():
    # Obtendo dados do formulário
    student_id = request.form.get('student-id')
    student_name = request.form.get('student-name')
    student_email = request.form.get('student-email')
    student_class = request.form.get('student-class')

    # Verificando se todos os dados necessários foram fornecidos
    if not student_id or not student_name or not student_email:
        return jsonify({"error": "Dados insuficientes para atualizar o estudante"}), 400

    # Convertendo o ID do estudante para ObjectId
    try:
        student_id = ObjectId(student_id)
    except Exception as e:
        return jsonify({"error": "ID do estudante inválido"}), 400

    # Atualizando o estudante no banco de dados
    result = mongo.db.users.update_one(
        {"_id": student_id, "role": "student"},
        {
            "$set": {
                "username": student_name,
                "email": student_email,
                "classe": ObjectId(student_class)
            }
        }
    )

    if result.matched_count == 0:
        return jsonify({"error": "Estudante não encontrado"}), 404

    # Retornando uma resposta de sucesso
    return jsonify({"success": True, "message": "Estudante atualizado com sucesso"}), 200


@manager_bp.route('manager_students', methods=['GET','POST'])
@login_required
@manager_required
def manager_students():
    manager_id = session.get('userID')
    year=date.today().year
    classes = list(mongo.db.classes.find({"manager_id":manager_id, "year":year}))
    return render_template('manager/manager_students.html', classes=classes)


@manager_bp.route('/api/generate_pdf', methods=['POST'])
@login_required
@manager_required
def generate_pdf_route():
    return generate_pdf()

@manager_bp.route('/dashboard')
@login_required
@manager_required
def dashboard_page():
    return dashboard_route()

@manager_bp.route('/dashboard/dash', methods=['GET','POST'])
@login_required
@manager_required
def dashboard_dash():
    return dashboard()