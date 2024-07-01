from flask import current_app, flash, redirect, render_template, session, url_for, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime, timezone
from app.forms import OccurrenceForm
from bson.objectid import ObjectId


def occurrence_submission(role):
    if 'role' not in session or session['role'] != role:
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))

    form = OccurrenceForm()
    mongo = PyMongo(current_app)

    teachers = []
    classes = []
    subjects = []

    if role == 'manager':

        # Buscar dados das coleções
        teachers = list(mongo.db.users.find({'role': 'teacher'}))
        classes = list(mongo.db.classes.find())
        subjects = list(mongo.db.subjects.find())

    elif role == 'teacher':
        userID = session.get('userID')
        teacher = mongo.db.users.find_one({"_id": ObjectId(userID)})
        teacher_classes = teacher['classes']
        classes = [mongo.db.classes.find_one(
            {"_id": ObjectId(cls_id)}) for cls_id in teacher_classes]
        teachers = [teacher]
        teacher_subjects = teacher['subjects']
        subjects = [mongo.db.subjects.find_one(
            {"_id": ObjectId(sub_id)}) for sub_id in teacher_subjects]

    # Atualizar as opções do formulário
    form.update_choices(teachers, classes, subjects)

    if form.validate_on_submit():
        teacher_id = form.teacher.data
        student_id = form.student.data
        class_id = form.classe.data
        subject_id = form.subject.data
        classification = form.classification.data
        description = form.description.data

        print("ID do estudante: ", student_id)

        if student_id == "None":
            flash('Por favor, selecione um aluno válido.', 'error')
            return render_template(f'{role}/register_occurrence.html', form=form)

        result = mongo.db.occurrences.insert_one({
            'teacher_id': teacher_id,
            'student_id': student_id,
            'class_id': class_id,
            'subject_id': subject_id,
            'classification': classification,
            'description': description,
            'status': "pendente",
            'solution': "sem solução",
            'date': datetime.now(timezone.utc)
        })

        occurrence_id = result.inserted_id

        mongo.db.users.update_one(
            {"_id": ObjectId(student_id)},
            {"$push": {"occurrences": occurrence_id}}
        )

        mongo.db.users.update_one(
            {"_id": ObjectId(teacher_id)},
            {"$push": {"occurrences": occurrence_id}}
        )

        mongo.db.classes.update_one(
            {"_id": ObjectId(class_id)},
            {"$push": {"occurrences": occurrence_id}}
        )

        mongo.db.subjects.update_one(
            {"_id": ObjectId(subject_id)},
            {"$push": {"occurrences": occurrence_id}}
        )

        flash('Ocorrência cadastrada com sucesso!', 'success')
        return redirect(url_for(f'{role}.index'))

    return render_template(f'{role}/register_occurrence.html', form=form)


def search_students():
    search_term = request.args.get('q', '')
    mongo = PyMongo(current_app)
    students = list(mongo.db.users.find(
        {'role': 'student', 'username': {'$regex': search_term, '$options': 'i'}}))
    return jsonify([{'id': str(student['_id']), 'text': student['username']} for student in students])


def get_users_by_id(ids):
    users = []
    mongo = PyMongo(current_app)
    for user_id in ids:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        users.append(user)
    return users


def manager_occurrence():
    user_role = session.get('role')
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

    return render_template(
        'manager/manager_occurrence.html',
        occurrences_data=occurrences_data,
        user_role=user_role
    )


def search_occurrences():
    query = request.args.get('query', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 15
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
                {'classification': {'$regex': query, '$options': 'i'}},
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

    # Adicionando filtro por status pendente (se aplicável)
    status = request.args.get('status')  # Obtém o parâmetro de status
    if status == 'pending':
        search_filter['status'] = 'pendente'

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
            'classification': occurrence['classification'],
            'status': occurrence['status'],
            'description': occurrence['description'],
            'solution': occurrence['solution'],
            'date': occurrence['date'].strftime('%d/%m/%Y')
        }
        occurrences_data.append(occurrence_data)

    total_pages = (total_occurrences + per_page - 1) // per_page

    return jsonify({
        'occurrences': occurrences_data,
        'current_page': page,
        'total_pages': total_pages
    })


def delete_occurrence(id):
    mongo = PyMongo(current_app)

    # Delete the occurrence from the occurrences collection
    result = mongo.db.occurrences.delete_one({'_id': ObjectId(id)})

    if result.deleted_count == 1:
        # Remove the occurrence ID from the occurrences field in other collections
        mongo.db.subjects.update_one(
            {"occurrences": ObjectId(id)},
            {"$pull": {"occurrences": ObjectId(id)}}
        )

        mongo.db.users.update_one(
            {"occurrences": ObjectId(id)},
            {"$pull": {"occurrences": ObjectId(id)}}
        )

        mongo.db.classes.update_one(
            {"occurrences": ObjectId(id)},
            {"$pull": {"occurrences": ObjectId(id)}}
        )

        return jsonify({'success': True, 'message': 'Occurrence deleted successfully.'})
    else:
        return jsonify({'success': False, 'message': 'Occurrence not found.'}), 404


def update_occurrence_field(field, occurrence_id):
    mongo = PyMongo(current_app)
    data = request.json
    value = data.get(field)
    if not value:
        return jsonify(success=False, message=f"{field} not provided")

    occurrence = mongo.db.occurrences.find_one(
        {'_id': ObjectId(occurrence_id)})
    if occurrence:
        if field == "solution":
            if value == "sem solução":
                mongo.db.occurrences.update_one(
                    {'_id': ObjectId(occurrence_id)},
                    {'$set': {'status': "pendente"}}
                )
                mongo.db.occurrences.update_one(
                    {'_id': ObjectId(occurrence_id)},
                    {'$set': {field: value}}
                )
            else:
                mongo.db.occurrences.update_one(
                    {'_id': ObjectId(occurrence_id)},
                    {'$set': {"status": "resolvido"}}
                )
                mongo.db.occurrences.update_one(
                    {'_id': ObjectId(occurrence_id)},
                    {'$set': {field: value}}
                )
        else:
            mongo.db.occurrences.update_one(
                {'_id': ObjectId(occurrence_id)},
                {'$set': {field: value}}
            )
        return jsonify(success=True)
    return jsonify(success=False)
