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
        description = form.description.data

        print("ID do estudante: ", student_id)

        if student_id == "None":
            flash('Por favor, selecione um aluno válido.', 'error')
            return render_template(f'{role}/register_occurrence.html', form=form)

        mongo.db.occurrences.insert_one({
            'teacher_id': teacher_id,
            'student_id': student_id,
            'class_id': class_id,
            'subject_id': subject_id,
            'description': description,
            'date': datetime.now(timezone.utc)
        })
        flash('Ocorrência cadastrada com sucesso!', 'success')
        return redirect(url_for(f'{role}.index'))

    return render_template(f'{role}/register_occurrence.html', form=form)


def search_students():
    search_term = request.args.get('q', '')
    mongo = PyMongo(current_app)
    students = list(mongo.db.users.find(
        {'role': 'student', 'username': {'$regex': search_term, '$options': 'i'}}))
    return jsonify([{'id': str(student['_id']), 'text': student['username']} for student in students])
