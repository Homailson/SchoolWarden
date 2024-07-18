from flask import (
    flash, redirect,
    render_template,
    session, url_for,
    request,
    jsonify,
    make_response
)

from datetime import datetime, timezone
from app.forms import OccurrenceForm, ChangePasswordForm, ChangeEmailForm, ChangeUsernameForm
from app import mongo
from bson.objectid import ObjectId
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Frame, PageTemplate, Image, BaseDocTemplate, Table
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from io import BytesIO
import requests
import bcrypt


def index():
    role = session.get('role')
    username = session.get('username')
    return render_template('common/index.html',
                           username=username,
                           register_endpoint=f'{role}.register_occurrence',
                           manager_endpoint=f'{role}.manager_occurrence_route',
                           role=role
                           )


def sanitize_description(description):
    return description.strip().replace("'", "").replace('"', '')


def occurrence_submission(role):
    if 'role' not in session or session['role'] != role:
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))

    form = OccurrenceForm()
    manager_id = session.get('userID')

    teachers = []
    classes = []
    subjects = []

    if role == 'manager':

        # Buscar dados das coleções
        teachers = list(mongo.db.users.find(
            {'role': 'teacher', 'manager_id': manager_id}))
        manager = mongo.db.users.find_one(
            {'_id': ObjectId(manager_id)}
        )
        teachers.append(manager)
        classes = list(mongo.db.classes.find({'manager_id': manager_id}))
        subjects = list(mongo.db.subjects.find({'manager_id': manager_id}))

    elif role == 'teacher':
        userID = session.get('userID')
        teacher = mongo.db.users.find_one({"_id": ObjectId(userID)})
        teacher_classes = teacher['classes']
        classes = [mongo.db.classes.find_one(
            {"_id": cls_id}) for cls_id in teacher_classes]
        teachers = [teacher]
        teacher_subjects = teacher['subjects']
        subjects = [mongo.db.subjects.find_one(
            {"_id": sub_id}) for sub_id in teacher_subjects]
        manager_id = teacher['manager_id']

    # Atualizar as opções do formulário
    form.update_choices(teachers, classes, subjects)

    # definindo o valor inicial dos campos do formulário atualizado
    form.teacher.choices.insert(0, ("", "selecione um professor(a)"))
    form.classe.choices.insert(0, ("", "selecione uma turma"))
    form.subject.choices.insert(0, ("", "selecione uma disciplina"))

    if form.validate_on_submit():
        teacher_id = form.teacher.data
        students_str = form.student.data
        class_id = form.classe.data
        subject_id = form.subject.data
        classification = form.classification.data
        description = sanitize_description(form.description.data)                

        students_ids = students_str.split(",")

        if students_ids == "None":
            flash('Por favor, selecione um aluno válido.', 'error')
            endpoint = f'{role}.register_occurrence'
            return render_template('common/register_occurrence.html', form=form, endpoint=endpoint)
        
        
        
        students = [mongo.db.users.find_one({"_id":ObjectId(id)}) for id in students_ids]
        stdnts_cls_ids = [stds['classe'] for stds in students]
        teacher = mongo.db.users.find_one({"_id":ObjectId(teacher_id)})
        teacher_cls = teacher['classes']
        teacher_subs = teacher['subjects']
        chosed_cls = mongo.db.classes.find_one({"_id":ObjectId(class_id)})
        chosed_classe = chosed_cls['classe']
        
        if chosed_classe != "Extraturma":
            for id in stdnts_cls_ids:
                print(id, ObjectId(class_id))
                if id != ObjectId(class_id):
                    flash('Ocorrência não cadastrada!\
                        Pelo menos um aluno não pertence à turma escolhida.', 'error')
                    return redirect(url_for(f'{role}.register_occurrence'))

        if ObjectId(class_id) not in teacher_cls:
            flash('Ocorrência não cadastrada!\
                    O professor selecionado não leciona na turma escolhida.', 'error')
            return redirect(url_for(f'{role}.register_occurrence'))        
            
        if ObjectId(subject_id) not in teacher_subs:
            flash('Ocorrência não cadastrada!\
                    O professor selecionado não leciona a disciplina escolhida.', 'error')
            return redirect(url_for(f'{role}.register_occurrence'))    
                
        result = mongo.db.occurrences.insert_one({
            'teacher_id': teacher_id,
            'students_ids': students_ids,
            'class_id': class_id,
            'subject_id': subject_id,
            'manager_id': manager_id,
            'classification': classification,
            'description': description,
            'status': "pendente",
            'solution': "sem solução",
            'date': datetime.now(timezone.utc)
        })

        occurrence_id = result.inserted_id

        for ids in students_ids:
            mongo.db.users.update_one(
                {"_id": ObjectId(ids)},
                {"$push": {"occurrences": occurrence_id}}
            )

        mongo.db.users.update_one(
            {"_id": ObjectId(teacher_id)},
            {"$push": {"occurrences": occurrence_id}}
        )

        mongo.db.users.update_one(
            {"_id": ObjectId(manager_id)},
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

        flash('Ocorrência registrada com sucesso!', 'success')
        return redirect(url_for(f'{role}.index_route'))
    endpoint = f'{role}.register_occurrence'
    return render_template('common/register_occurrence.html', form=form, endpoint=endpoint)


def search_students():
    userID = session.get('userID')
    user = mongo.db.users.find_one({"_id": ObjectId(userID)})
    search_term = request.args.get('q', '')
    if user['role'] == 'manager':
        manager_id = userID
        students = list(mongo.db.users.find(
            {'role': 'student',
             'username': {'$regex': search_term, '$options': 'i'},
             'manager_id': manager_id})
        )
    else:
        teacher_classes = user['classes']
        students = list(mongo.db.users.find(
            {'role': 'student',
             'username': {'$regex': search_term, '$options': 'i'},
             'classe': {"$in": teacher_classes}})
        )

    return jsonify([{'id': str(student['_id']), 'text': student['username']} for student in students])


def get_users_by_id(ids):
    users = []
    for user_id in ids:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user not in users:
            users.append(user)
    return users


def get_classes_by_id(ids):
    classes = []
    for cls_id in ids:
        classe = mongo.db.classes.find_one({"_id": ObjectId(cls_id)})
        classes.append(classe)
    return classes


def get_subjects_by_id(ids):
    subjects = []
    for sub_id in ids:
        subject = mongo.db.subjects.find_one({"_id": ObjectId(sub_id)})
        subjects.append(subject)
    return subjects


def manager_occurrence():
    user_role = session.get('role')
    return render_template(
        'common/manager_occurrence.html',
        user_role=user_role
    )


def search_occurrences():
    # Parâmetros da requisição
    query = request.args.get('query', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 15
    skip = (page - 1) * per_page

    # Informações do usuário da sessão
    userID = session.get('userID')
    userRole = session.get('role')

    # Filtro de busca inicial
    search_filter = {}

    if userRole == 'manager':
        search_filter['manager_id'] = userID

    # Se o usuário for professor (teacher), filtra apenas as ocorrências dele
    if userRole == 'teacher':
        search_filter['teacher_id'] = userID
        teacher = mongo.db.users.find_one({"_id": ObjectId(userID)})
        search_filter['manager_id'] = teacher['manager_id']

    # Se o usuário for estudante (student), filtra apenas as ocorrências dele
    if userRole == 'student':
        search_filter['students_ids'] = userID

    # Condições de busca baseadas na query de pesquisa
    if query:
        # Busca por IDs de usuários com base no username
        users = mongo.db.users.find(
            {'username': {'$regex': query, '$options': 'i'}})
        users_ids = [str(usr['_id']) for usr in users]

        # Condições de busca com operador $or
        search_filter['$or'] = [
            {'description': {'$regex': query, '$options': 'i'}},
            {'classification': {'$regex': query, '$options': 'i'}},
            {'teacher_id': {'$in': users_ids}},
            {'students_ids': {'$in': users_ids}},
            {'manager_id': {'$in': users_ids}}
        ]

    # Adiciona filtro por período (data)
    if start_date and end_date:
        search_filter['date'] = {'$gte': datetime.strptime(start_date, '%Y-%m-%d'),
                                 '$lte': datetime.strptime(end_date, '%Y-%m-%d')}

    # Adiciona filtro por status pendente, se aplicável
    if request.args.get('status') == 'pending':
        search_filter['status'] = 'pendente'

    # Contagem total de ocorrências que correspondem ao filtro
    total_occurrences = mongo.db.occurrences.count_documents(search_filter)

    # Ocorrências paginadas, ordenadas pela data decrescente
    occurrences = list(mongo.db.occurrences.find(
        search_filter).sort("date", -1).skip(skip).limit(per_page))

    # IDs de professores e alunos envolvidos nas ocorrências
    teachers_ids = [occurrence['teacher_id'] for occurrence in occurrences]
    students_ids = [
        student_id for occurrence in occurrences for student_id in occurrence['students_ids']]
    classes_ids = [occurrence['class_id'] for occurrence in occurrences]
    subjects_ids = [occurrence['subject_id'] for occurrence in occurrences]

    # Detalhes dos professores e alunos
    teachers = get_users_by_id(teachers_ids)
    students = get_users_by_id(students_ids)
    classes = get_classes_by_id(classes_ids)
    subjects = get_subjects_by_id(subjects_ids)

    # Formatação dos dados das ocorrências para retorno como JSON
    occurrences_data = []
    for occurrence in occurrences:
        teacher = next((teacher for teacher in teachers if str(
            teacher['_id']) == occurrence['teacher_id']), {})
        occurrence_students = [student for student in students if str(
            student['_id']) in occurrence['students_ids']]
        classe = next((classe for classe in classes if str(
            classe['_id']) == occurrence['class_id']), {})
        subject = next((subject for subject in subjects if str(
            subject['_id']) == occurrence['subject_id']), {})

        occurrences_data.append({
            'id': str(occurrence['_id']),
            'teacher': teacher.get('username', ''),
            'students': [student['username'] for student in occurrence_students],
            'classe': classe.get('classe', ''),
            'subject': subject.get('subject', ''),
            'classification': occurrence['classification'],
            'status': occurrence['status'],
            'description': occurrence['description'],
            'solution': occurrence['solution'],
            'date': occurrence['date'].strftime('%d/%m/%Y')
        })

    # Cálculo do número total de páginas
    total_pages = (total_occurrences + per_page - 1) // per_page

    # Retorno dos dados das ocorrências, página atual e número total de páginas como JSON
    return jsonify({
        'occurrences': occurrences_data,
        'current_page': page,
        'total_pages': total_pages
    })


def delete_occurrence(id):

    # Delete the occurrence from the occurrences collection
    result = mongo.db.occurrences.delete_one({'_id': ObjectId(id)})

    if result.deleted_count == 1:
        # Remove the occurrence ID from the occurrences field in other collections
        mongo.db.subjects.update_one(
            {"occurrences": ObjectId(id)},
            {"$pull": {"occurrences": ObjectId(id)}}
        )

        mongo.db.users.update_many(
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


def update_field(field, occurrence_id):
    data = request.json
    value = sanitize_description(data.get(field))
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


def configurations():
    userID = session.get('userID')
    role = session.get('role')
    user = mongo.db.users.find_one({"_id": ObjectId(userID)})
    username = user['username']
    email = user['email']
    if role != 'admin':
        manager_id = user['_id'] if user['role'] == 'manager' else user['manager_id']
        manager = mongo.db.users.find_one({'_id': ObjectId(manager_id)})
        school = manager['school']
    else:
        school = 'Sem definição'
    return render_template('/common/configbase.html',
                           role=role,
                           username=username,
                           school=school,
                           email=email
                           )


def profile_info():
    userID = session.get('userID')
    role = session.get('role')
    user = mongo.db.users.find_one({"_id": ObjectId(userID)})
    username = user['username']
    email = user['email']
    if role != 'admin':
        manager_id = user['_id'] if user['role'] == 'manager' else user['manager_id']
        manager = mongo.db.users.find_one({'_id': ObjectId(manager_id)})
        school = manager['school']
    else:
        school = 'Sem definição'
    return render_template('/common/profile_info.html',
                           role=role,
                           username=username,
                           school=school,
                           email=email)


def password_form_route():
    form = ChangePasswordForm()
    role = session['role']
    return render_template('/common/change_password.html', form=form, role=role)


def changing_password():
    form = ChangePasswordForm()
    role = session['role']
    if form.validate_on_submit():
        userID = session.get('userID')
        user = mongo.db.users.find_one({"_id": ObjectId(userID)})
        user_password = user['password'].encode('utf-8')
        if user and 'password' in user:
            current_password = form.current_password.data.encode('utf-8')
            if bcrypt.checkpw(current_password, user_password):
                new_password = form.new_password.data.encode('utf-8')
                hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt())
                mongo.db.users.update_one(
                    {"_id": ObjectId(userID)},
                    {"$set": {"password": hashed_password.decode('utf-8')}}
                )
                flash('Sua senha foi alterada com sucesso!', 'success')
                return redirect(url_for(f'{role}.configurations_route'))
            else:
                flash('Senha atual inserida não corresponde', 'error')
    return redirect(url_for(f'{role}.configurations_route'))


def email_form_route():
    form = ChangeEmailForm()
    role = session['role']
    return render_template('/common/change_email.html', form=form, role=role)


def changing_email():
    form = ChangeEmailForm()
    role = session['role']
    if form.validate_on_submit():
        userID = session.get('userID')
        user = mongo.db.users.find_one({"_id": ObjectId(userID)})
        if user and 'email' in user:
            new_email = form.new_email.data
            confirm_email = form.confirm_email.data
            if new_email != confirm_email:
                flash('Os emails não coincidem!', 'error')
            else:
                mongo.db.users.update_one(
                    {"_id": ObjectId(userID)},
                    {"$set": {"email": new_email}}
                )
                flash('Seu e-mail foi alterado com sucesso!', 'success')
                return redirect(url_for(f'{role}.configurations_route'))
        else:
            flash('Este usuário não tem e-mail', 'info')
    else:
        flash('Os emails não coincidem!', 'error')
    return redirect(url_for(f'{role}.configurations_route'))


def username_form_route():
    form = ChangeUsernameForm()
    role = session['role']
    return render_template('/common/change_username.html', form=form, role=role)

def changing_username():
    form = ChangeUsernameForm()
    role = session['role']
    if form.validate_on_submit():
        userID = session.get('userID')
        user = mongo.db.users.find_one({"_id": ObjectId(userID)})
        if user and 'username' in user:
            new_username = form.new_username.data
            confirm_username = form.confirm_username.data
            if new_username != confirm_username:
                flash('Os nomes não coincidem!', 'error')
            else:
                mongo.db.users.update_one(
                    {"_id": ObjectId(userID)},
                    {"$set": {"username": new_username}}
                )
                flash('Seu nome de usuário foi alterado com sucesso!', 'success')
                return redirect(url_for(f'{role}.configurations_route'))
        else:
            flash('Este usuário não tem nome de usuário', 'info')
    else:
        flash('Os nomes de usuário não coincidem!', 'error')
    return redirect(url_for(f'{role}.configurations_route'))


def generate_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        occurrence_id = data.get('occurrence_id')
        if not occurrence_id:
            return jsonify({'error': 'No occurrence_id provided'}), 400

        occurrence_data = mongo.db.occurrences.find_one(
            {"_id": ObjectId(occurrence_id)})

        if not occurrence_data:
            return jsonify({'error': 'Occurrence not found'}), 404

        teacher_info = mongo.db.users.find_one(
            {"_id": ObjectId(occurrence_data['teacher_id'])})
        teacher = teacher_info['username'] if teacher_info else 'Teacher Not Found'

        manager_info = mongo.db.users.find_one(
            {"_id": ObjectId(occurrence_data['manager_id'])})
        manager = manager_info['username'] if manager_info else 'Manager Not Found'

        # Recuperando informações dos estudantes associados
        student_ids = occurrence_data.get('students_ids', [])
        students = []
        for student_id in student_ids:
            student_info = mongo.db.users.find_one(
                {"_id": ObjectId(student_id)})
            if student_info:
                students.append(student_info['username'])

        # Recuperando informações da escola
        school_info = mongo.db.users.find_one(
            {"_id": ObjectId(occurrence_data['manager_id'])})
        school = school_info['school'] if school_info else 'School Not Found'
        school_logo = school_info['logo_url'] if school_info else None

        classe_info = mongo.db.classes.find_one(
            {"_id": ObjectId(occurrence_data['class_id'])})
        classe = classe_info['classe'] if classe_info else 'Class Not Found'

        subject_info = mongo.db.subjects.find_one(
            {"_id": ObjectId(occurrence_data['subject_id'])})
        subject = subject_info['subject'] if subject_info else 'Subject Not Found'

        date = occurrence_data['date']
        description = occurrence_data['description']

        occurrence = {
            "teacher_id": occurrence_data['teacher_id'],
            "teacher": teacher,
            "students": students,
            "manager": manager,
            "school": school,
            "school_logo": school_logo,
            "classe": classe,
            "subject": subject,
            "date": date.strftime("%d/%m/%Y"),
            "description": description
        }

        # Gerar o PDF
        pdf_buffer = BytesIO()
        generate_pdf_file(pdf_buffer, occurrence)
        pdf_buffer.seek(0)

        # Retornar o PDF como resposta
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Disposition'] = 'inline; filename=relatorio.pdf'
        response.headers['Content-Type'] = 'application/pdf'
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_pdf_file(buffer, occurrence):
    # Configuração do tamanho da página e elementos
    doc = BaseDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    normal_style = styles['BodyText']

    normal_style = ParagraphStyle(
        name="NewNormal",
        parent=styles["Normal"],
        fontSize=12,
        spaceAfter=10,
        leading=16,
        textColor=black,
    )

    header_style = ParagraphStyle(
        name='HeaderStyle',
        parent=styles['Normal'],  # Pode ser baseado em outro estilo existente
        fontSize=12,
        leading=16,  # Espaçamento entre linhas
        spaceAfter=10,  # Espaçamento após o parágrafo
        textColor=black,  # Cor do texto
        # Alinhamento centralizado (0=esquerda, 1=centro, 2=direita)
        alignment=1,
        spaceBefore=5,  # Espaçamento antes do parágrafo
        leftIndent=10,  # Recuo à esquerda
        rightIndent=10,  # Recuo à direita
    )

    # Definição de um único frame que cobre toda a página
    frame_width, frame_height = A4
    full_frame = Frame(inch, 0, frame_width - 2*inch, frame_height - 0.30*inch)

    # Definição do template de página com o frame único
    doc.addPageTemplates(PageTemplate(id='full_page', frames=full_frame))

    # Função para baixar a imagem do Google Drive
    def download_image_from_drive(url):
        file_id = url.split('/')[-2]
        download_url = f'https://drive.google.com/uc?id={file_id}'

        response = requests.get(download_url)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            print('Falha ao baixar a imagem')
            return None

    img_url = occurrence['school_logo']

    if img_url:
        img_data = download_image_from_drive(img_url)
        header_image = Image(img_data, width=1*inch,
                             height=0.75*inch, hAlign="RIGHT")
    else:
        print("A imagem não foi carregada!")
        header_image = None

    # Conteúdo para o cabeçalho
    header_paragraph = Paragraph(
        f"<b>Escola:</b> {occurrence['school']}<br/>\
        <b>Gestor(a):</b> {occurrence['manager']}<br/>\
        <b>Data:</b> {occurrence['date']}",
        style=header_style)

    # Header table com header paragraph e header image
    header_table = Table([[header_paragraph, header_image]], colWidths=[
        frame_width*0.50-inch, frame_width*0.50-inch])

    header_table.setStyle([
        ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
    ])

    user = mongo.db.users.find_one({"_id": ObjectId(occurrence['teacher_id'])})
    if user['role'] == 'manager':
        writer = "Gestor(a) "
    else:
        writer = "Professor(a) "

    # Conteúdo do corpo
    body_content = [
        ("Relator(a):", f"{writer}{occurrence['teacher']}"),
        ("Disciplina:", occurrence['subject']),
        # Múltiplos estudantes unidos por vírgula
        ("Estudante(s):", ", ".join(occurrence['students'])),
        ("Turma:", occurrence['classe'])
    ]

    manager_signature = Paragraph("Assinatura do(a) gestor(a)<br/><br/>\
        ______________________________", normal_style)

    tutor_signature = Paragraph("Assinatura do(a) responsável<br/><br/>\
        ______________________________", normal_style)

    footer_table = Table([[manager_signature, tutor_signature]], colWidths=[
        frame_width*0.50-inch, frame_width*0.50-inch])

    # Adicionando elementos ao documento
    elements = []

    elements.append(header_table)
    # Espaçamento entre cabeçalho e linha
    elements.append(Spacer(1, 0.15*inch))

    # Adicionar linha horizontal
    drawing = Drawing(frame_width, 1)
    line = Line(0, 0, frame_width-2*inch, 0)
    drawing.add(line)
    elements.append(drawing)

    # Espaçamento entre cabeçalho e corpo
    elements.append(Spacer(1, 0.5*inch))

    centered_heading_style = ParagraphStyle(
        'CenteredHeading1',
        parent=styles['Heading1'],
        alignment=TA_CENTER
    )

    centered_heading2_style = ParagraphStyle(
        'CenteredHeading1',
        parent=styles['Heading2'],
        alignment=TA_CENTER
    )

    elements.append(
        Paragraph("RELATÓRIO DE OCORRÊNCIA", centered_heading_style))

    elements.append(Spacer(1, 0.75*inch))

    for label, value in body_content:
        elements.append(Paragraph(f"<b>{label}</b> {value}", normal_style))

    elements.append(Spacer(1, 0.5*inch))

    elements.append(Paragraph("DESCRIÇÃO", centered_heading2_style))

    elements.append(Spacer(1, 0.25*inch))

    custom_body_style = ParagraphStyle(
        'CustomBodyText',
        parent=styles['BodyText'],
        fontSize=12,
        alignment=TA_JUSTIFY
    )

    elements.append(
        Paragraph(f"{occurrence['description']}", custom_body_style))

    # Espaçamento entre corpo e rodapé
    elements.append(Spacer(1, 2*inch))
    elements.append(footer_table)

    # Construindo o PDF
    doc.build(elements)
