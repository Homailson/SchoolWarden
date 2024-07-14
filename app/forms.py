from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms.widgets import ListWidget, CheckboxInput


class LoginForm(FlaskForm):
    email = EmailField(
        'E-mail',
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


class SubjectForm(FlaskForm):
    subject = SelectField('Disciplina', choices=[
        ('', 'Selecione uma disciplina'),
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
        ('Ed.Alimentar', 'Ed.Alimentar'),
        ('Higiene&Saúde', 'Higiene&Saúde'),
        ('Ed.Física', 'Ed.Física'),
        ('Ens.Religioso', 'Ens.Religioso')

    ])

    def update_subjects(self, subjects):
        self.subject.choices = [
            (value, label) for value, label in self.subject.choices if label not in subjects
        ]


class ClassForm(FlaskForm):
    classe = SelectField('Turma', choices=[
        ('', 'Selecione uma turma'),
        ('6A', '6A'), ('6B', '6B'), ('6C', '6C'),
        ('7A', '7A'), ('7B', '7B'), ('7C', '7C'),
        ('8A', '8A'), ('8B', '8B'), ('8C', '8C'),
        ('9A', '9A'), ('9B', '9B'), ('9C', '9C')
    ])
    submit = SubmitField('Cadastrar Turma')

    def update_classes(self, classes):
        self.classe.choices = [
            (value, label) for value, label in self.classe.choices if label not in classes
        ]


class ManagerForm(FlaskForm):
    username = StringField(
        'Usuário',
        validators=[
            DataRequired(),
            Length(max=64)
        ]
    )

    email = EmailField(
        'E-mail',
        validators=[
            DataRequired()
        ]
    )

    confirm_email = EmailField(
        'Confirmar e-mail',
        validators=[
            DataRequired(),
            EqualTo("email",
                    message="Os emails precisam ser iguais")
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
        'Confirmar senha',
        validators=[
            DataRequired(),
            EqualTo('password',
                    message='As senhas precisam ser iguais')
        ]
    )

    school = StringField(
        'Escola',
        validators=[
            DataRequired(),
            Length(max=64)
        ]
    )

    logo_url = StringField(
        'Logo da escola'
    )
    submit = SubmitField('Cadastrar')


class TeacherForm(FlaskForm):
    username = StringField(
        'Usuário',
        validators=[
            DataRequired(),
            Length(max=64)
        ]
    )

    email = EmailField(
        'E-mail',
        validators=[
            DataRequired()
        ]
    )

    confirm_email = EmailField(
        'Confirmar e-mail',
        validators=[
            DataRequired(),
            EqualTo("email",
                    message="Os emails precisam ser iguais")
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
    subjects = SelectMultipleField('Disciplina', choices=[],
                                   validators=[DataRequired()])
    classes = SelectMultipleField('Turmas', choices=[],
                                  validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

    def update_subjects(self, subjects):
        self.subjects.choices = subjects

    def update_classes(self, classes):
        self.classes.choices = classes


class StudentForm(FlaskForm):
    username = StringField(
        'Usuário',
        validators=[
            DataRequired(),
            Length(max=64)
        ]
    )

    email = EmailField(
        'E-mail',
        validators=[
            DataRequired()
        ]
    )

    confirm_email = EmailField(
        'Confirmar e-mail',
        validators=[
            DataRequired(),
            EqualTo("email",
                    message="Os emails precisam ser iguais")
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


class OccurrenceForm(FlaskForm):
    teacher = SelectField('Professor', choices=[], validators=[DataRequired()])
    student = StringField('Aluno', validators=[DataRequired()])
    classe = SelectField('Turma', choices=[], validators=[DataRequired()])
    subject = SelectField('Disciplina', choices=[],
                          validators=[DataRequired()])
    classification = SelectField(
        choices=[('', 'Selecione o tipo'),
                 ('Bullying', 'Bullying'),
                 ('CyberBullying', 'CyberBullying'),
                 ('Atraso', 'Atraso'),
                 ('Dormindo em sala', 'Dormindo em sala'),
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

    def update_choices(self, teachers, classes, subjects):
        self.teacher.choices = [
            (teacher['_id'], teacher['username']) for teacher in teachers]
        self.classe.choices = [(classe['_id'], classe['classe'])
                               for classe in classes]
        self.subject.choices = [(subject['_id'], subject['subject'])
                                for subject in subjects]


class ChangeEmailForm(FlaskForm):
    new_email = EmailField(
        'E-mail novo',
        validators=[
            DataRequired()
        ]
    )

    confirm_email = EmailField(
        'Confirmar e-mail',
        validators=[
            DataRequired(),
            EqualTo('new_email',
                    message='Os emails não coincidem!')
        ]
    )
    submit = SubmitField('Alterar')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Senha atual',
        validators=[
            DataRequired()
        ]
    )

    new_password = PasswordField(
        'Senha nova',
        validators=[
            DataRequired()
        ]
    )

    confirm_password = PasswordField(
        'Confirmar senha',
        validators=[
            DataRequired(),
            EqualTo('new_password',
                    message='As senhas precisam ser iguais')
        ]
    )
    submit = SubmitField('Alterar')


class ResetPasswordRequestForm(FlaskForm):
    email = EmailField(
        'E-mail',
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField('Solicitar redefinição de senha')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'Nova senha',
        validators=[
            DataRequired(),
        ]
    )
    confirm_password = PasswordField(
        'Nova senha',
        validators=[
            DataRequired(),
            EqualTo('password')
        ]
    )
    submit = SubmitField('Redefinir senha')
