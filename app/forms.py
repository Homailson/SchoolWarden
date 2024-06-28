from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput


class LoginForm(FlaskForm):
    username = StringField(
        'Usuário',
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        'Senha',
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField('Entrar')


class ManagerForm(FlaskForm):
    username = StringField(
        'Usuário',
        validators=[
            DataRequired(),
            Length(max=64)
        ]
    )
    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )
    confirm_password = PasswordField(
        'Confirmar Senha',
        validators=[
            DataRequired(),
            EqualTo('password',
                    message='As senhas precisam ser iguais')
        ]
    )
    submit = SubmitField('Cadastrar')


class ClassForm(FlaskForm):
    classe = SelectField('Selecione a Turma', choices=[
        ('6A', '6A'), ('6B', '6B'), ('6C', '6C'),
        ('7A', '7A'), ('7B', '7B'), ('7C', '7C'),
        ('8A', '8A'), ('8B', '8B'), ('8C', '8C'),
        ('9A', '9A'), ('9B', '9B'), ('9C', '9C')
    ])
    submit = SubmitField('Cadastrar Turma')


class SubjectForm(FlaskForm):
    subject = SelectField('Selecione uma Disciplina', choices=[
        ('Matemática', 'Matemática'),
        ('L.Portuguesa', 'L.Portuguesa'),
        ('Geografia', 'Geografia'),
        ('L.Inglesa', 'L.Inglesa'),
        ('História', 'História'),
        ('Ciências', 'Ciências'),
        ('Vida&Prevenção', 'Vida&Prevenção'),
        ('Artes', 'Artes'),
        ('Exp.Matemática', 'Exp.Matemática'),
        ('Prod.Textual', 'Prod.Textual'),
        ('Ciências&Tecnologia', 'Ciências&Tecnologia'),
        ('EducaçãoAlimentar', 'EducaçãoAlimentar'),
        ('Higiene&Saúde', 'Higiene&Saude'),
        ('Ed.Física', 'Ed.Fisica')

    ])
    submit = SubmitField('Cadastrar Disciplina')


class StudentForm(FlaskForm):
    username = StringField(
        'Usuário',
        validators=[
            DataRequired(),
            Length(max=64)
        ]
    )
    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )
    confirm_password = PasswordField(
        'Confirmar Senha',
        validators=[
            DataRequired(),
            EqualTo('password',
                    message='As senhas precisam ser iguais')
        ]
    )
    classe = SelectField('Turma', choices=[], validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

    def update_classes(self, classes):
        self.classe.choices = classes


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


def at_least_one_selected(form, field):
    if not field.data:
        raise ValidationError(
            'Você deve selecionar pelo menos uma disciplina.')


class TeacherForm(FlaskForm):
    username = StringField(
        'Usuário',
        validators=[
            DataRequired(),
            Length(max=64)
        ]
    )
    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )
    confirm_password = PasswordField(
        'Confirmar Senha',
        validators=[
            DataRequired(),
            EqualTo('password',
                    message='As senhas precisam ser iguais')
        ]
    )
    subjects = MultiCheckboxField('Disciplina', choices=[],
                                  validators=[at_least_one_selected])
    classes = MultiCheckboxField(
        'Turmas', choices=[], validators=[at_least_one_selected])
    submit = SubmitField('Cadastrar')

    def update_subjects(self, subjects):
        self.subjects.choices = subjects

    def update_classes(self, classes):
        self.classes.choices = classes


class OccurrenceForm(FlaskForm):
    teacher = SelectField('Professor', choices=[], validators=[DataRequired()])
    student = StringField('Aluno', validators=[DataRequired()])
    classe = SelectField('Turma', choices=[], validators=[DataRequired()])
    subject = SelectField('Disciplina', choices=[],
                          validators=[DataRequired()])
    classification = SelectField(
        'Tipo',
        choices=[('Bullying', 'Bullying'),
                 ('CyberBullying', 'CyberBullying'),
                 ('Agressão física', 'Agressão física'),
                 ('Agressão verbal', 'Agressão verbal'),
                 ('Uso não autorizado de celular',
                  'Uso não autorizado de celular'),
                 ('Desrrespeito a funcionário', 'Desrrespeito a funcionário'),
                 ('Trapaça em prova', 'Trapaça em prova'),
                 ('Vandalismo', 'Vandalismo'),
                 ('Fuga da escola', 'Fuga da escola'),
                 ('Furto', 'Furto'),
                 ('Uso de substância ilícita', 'Uso de substância ilícita'),
                 ('Porte de arma', 'Porte de arma'),
                 ('Assédio', 'Assédio'),
                 ('Automutilacão', 'Automutilacão')
                 ],
        validators=[DataRequired()]
    )
    description = TextAreaField('Descrição', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

    def update_choices(self, teachers, classes, subjects):
        self.teacher.choices = [
            (teacher['_id'], teacher['username']) for teacher in teachers]
        self.classe.choices = [(classe['_id'], classe['classe'])
                               for classe in classes]
        self.subject.choices = [(subject['_id'], subject['subject'])
                                for subject in subjects]
