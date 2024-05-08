from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm, ModelFormField, ModelFieldList
from wtforms import validators
from wtforms.fields import SelectField
from wtforms.fields import FormField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired
from models import Task,  Priority, Interval, Status, User
from wtforms_alchemy import model_form_factory

# Создание базового класса ModelForm от FlaskForm
BaseModelForm = model_form_factory(FlaskForm)


'''class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session'''


class PriorityForm(ModelForm):
    class Meta:
        model = Priority
        include = ['id', 'name']


class IntervalForm(ModelForm):
    class Meta:
        model = Interval
        include = ['id']


class StatusForm(ModelForm):
    class Meta:
        model = Status
        include = ['id', 'name']


class UserForm(ModelForm):
    class Meta:
        model = User


class SubTaskForm(ModelForm):
    class Meta:
        model = Task
        only = ['id', 'title', 'status_id']


class TaskForm(BaseModelForm):
    class Meta:
        csrf = False  # Отключаем CSRF для этой формы
        model = Task
        # include = ['id', 'title', 'task_type']

    deadline = DateTimeLocalField('Deadline', format='%Y-%m-%dT%H:%M', validators=[validators.Optional()])

    priority = SelectField('Priority', coerce=int, validators=[validators.Optional()])
    # interval = ModelFormField(IntervalForm)
    # worker = ModelFieldList(ModelFormField(UserForm))
    subtasks = ModelFieldList(ModelFormField(SubTaskForm))

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.priority.choices = [(p.id, p.name) for p in Priority.query.all()]
