from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm, ModelFormField, ModelFieldList
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
        include = ['id']


class IntervalForm(ModelForm):
    class Meta:
        model = Interval
        include = ['id']


class StatusForm(ModelForm):
    class Meta:
        model = Status
        include = ['id']


class UserForm(ModelForm):
    class Meta:
        model = User


class SubTaskForm(ModelForm):
    class Meta:
        model = Task
        only = ['id', 'title', 'status_id']


class TaskForm(ModelForm):
    class Meta:
        model = Task

    deadline = DateTimeLocalField('Deadline', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])

    priority = ModelFormField(PriorityForm)
    interval = ModelFormField(IntervalForm)
    worker = ModelFieldList(FormField(UserForm))
    subtasks = ModelFieldList(FormField(SubTaskForm))
