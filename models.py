from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey


db = SQLAlchemy()


# Модель для таблицы Users
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.Text)
    avatar_src = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.user_id,
            'user_name': self.user_name,
            'avatar_src': self.avatar_src
        }


# Модель для таблицы ChatHistory
class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    message_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date = db.Column(db.Date)
    time = db.Column(db.Text)
    text = db.Column(db.Text)
    files = db.Column(db.Text)
    position = db.Column(db.Text)
    user = db.relationship('User', backref=db.backref('messages', lazy=True))


# Модель для таблицы Quotes
class Quote(db.Model):
    __tablename__ = 'quotes'
    QuoteID = db.Column(db.Integer, primary_key=True)
    Quote = db.Column(db.String(255))


# Модель для таблицы Videos
class Video(db.Model):
    __tablename__ = 'videos'
    VideoID = db.Column(db.Integer, primary_key=True)
    VideoPath = db.Column(db.String(255))
    ListIDs = db.Column(db.String(255))  # Это поле предполагает, что IDs хранятся в виде строки
    GroupIDs = db.Column(db.String(255))  # Аналогично для GroupIDs


# Модель для таблицы trading_journal
class TradingJournal(db.Model):
    __tablename__ = 'trading_journal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    trading_day = db.Column(db.Text)
    time = db.Column(db.Text)
    bias = db.Column(db.Text)
    news = db.Column(db.Text)
    session = db.Column(db.Text)
    model = db.Column(db.Text)
    reason = db.Column(db.Text)
    result = db.Column(db.Text, default="0")
    comment = db.Column(db.Text)
    files = db.Column(db.Text)


# Модель для таблицы diary
class Diary(db.Model):
    __tablename__ = 'diary'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    time = db.Column(db.Text)
    bias = db.Column(db.Text)
    reason = db.Column(db.Text)
    lessons = db.Column(db.Text)
    score = db.Column(db.Text)
    comment = db.Column(db.Text)
    files = db.Column(db.Text)


# Модель для таблицы project_journal
class ProjectJournal(db.Model):
    __tablename__ = 'project_journal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    time = db.Column(db.Text)
    project_name = db.Column(db.Text)
    step = db.Column(db.Text)
    comment = db.Column(db.Text)
    files = db.Column(db.Text)


# Модель для таблицы backtest_journal
class BacktestJournal(db.Model):
    __tablename__ = 'backtest_journal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    trading_day = db.Column(db.Text)
    time = db.Column(db.Text)
    bias = db.Column(db.Text)
    news = db.Column(db.Text)
    session = db.Column(db.Text)
    model = db.Column(db.Text)
    reason = db.Column(db.Text)
    result = db.Column(db.Text, default="0")
    comment = db.Column(db.Text)
    files = db.Column(db.Text)


# ToDoBase

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column('ProjectID', db.Integer, primary_key=True)
    name = db.Column('ProjectName', db.String(255))


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column('TaskID', db.Integer, primary_key=True)
    title = db.Column('Title', db.String(255))
    description = db.Column('Description', db.Text)
    due_date = db.Column('DueDate', db.Date)
    status_id = db.Column('StatusID', db.Integer, db.ForeignKey('statuses.StatusID'))
    priority_id = db.Column('PriorityID', db.Integer, db.ForeignKey('priorities.PriorityID'))
    interval_id = db.Column('IntervalID', db.Integer, db.ForeignKey('intervals.IntervalID'))


class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column('ListID', db.Integer, primary_key=True)
    name = db.Column('ListName', db.String(255))


class Status(db.Model):
    __tablename__ = 'statuses'
    id = db.Column('StatusID', db.Integer, primary_key=True)
    name = db.Column('StatusName', db.String(255))


class Priority(db.Model):
    __tablename__ = 'priorities'
    id = db.Column('PriorityID', db.Integer, primary_key=True)
    name = db.Column('PriorityName', db.String(255))


class Interval(db.Model):
    __tablename__ = 'intervals'
    id = db.Column('IntervalID', db.Integer, primary_key=True)
    minutes = db.Column('IntervalMinutes', db.Integer)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column('GroupID', db.Integer, primary_key=True)
    name = db.Column('GroupName', db.String(255))


# Вспомогательная таблица для связи между задачами и проектами
task_project_relations = Table('task_project_relations', db.Model.metadata,
    Column('TaskID', Integer, ForeignKey('tasks.TaskID'), primary_key=True),
    Column('ProjectID', Integer, ForeignKey('projects.ProjectID'), primary_key=True)
)

# Вспомогательная таблица для связи между списками и проектами
list_project_relations = Table('list_project_relations', db.Model.metadata,
    Column('ListID', Integer, ForeignKey('lists.ListID'), primary_key=True),
    Column('ProjectID', Integer, ForeignKey('projects.ProjectID'), primary_key=True)
)

# Вспомогательная таблица для связи между задачами и списками
task_list_relations = Table('task_list_relations', db.Model.metadata,
    Column('TaskID', Integer, ForeignKey('tasks.TaskID'), primary_key=True),
    Column('ListID', Integer, ForeignKey('lists.ListID'), primary_key=True)
)

# Вспомогательная таблица для связи между списками и группами
list_group_relations = Table('list_group_relations', db.Model.metadata,
    Column('ListID', Integer, ForeignKey('lists.ListID'), primary_key=True),
    Column('GroupID', Integer, ForeignKey('groups.GroupID'), primary_key=True)
)

# Установка связей многие-ко-многим
Project.tasks = db.relationship('Task', secondary='task_project_relations', back_populates='projects')
Project.lists = db.relationship('List', secondary='list_project_relations', back_populates='projects')
Task.projects = db.relationship('Project', secondary='task_project_relations', back_populates='tasks')
Task.lists = db.relationship('List', secondary='task_list_relations', back_populates='tasks')
List.tasks = db.relationship('Task', secondary='task_list_relations', back_populates='lists')
List.projects = db.relationship('Project', secondary='list_project_relations', back_populates='lists')
List.groups = db.relationship('Group', secondary='list_group_relations', back_populates='lists')
Group.lists = db.relationship('List', secondary='list_group_relations', back_populates='groups')

# Установка связей один-ко-многим
Status.tasks = db.relationship('Task', backref='status')
Priority.tasks = db.relationship('Task', backref='priority')
Interval.tasks = db.relationship('Task', backref='interval')
