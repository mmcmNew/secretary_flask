from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Status(db.Model):
    __tablename__ = 'statuses'
    StatusID = db.Column(db.Integer, primary_key=True)
    StatusName = db.Column(db.String(255))


# Модель для таблицы Intervals
class Interval(db.Model):
    __tablename__ = 'intervals'
    IntervalID = db.Column(db.Integer, primary_key=True)
    IntervalCount = db.Column(db.Integer)


# Модель для таблицы Priority
class Priority(db.Model):
    __tablename__ = 'priority'
    PriorityID = db.Column(db.Integer, primary_key=True)
    PriorityName = db.Column(db.String(255))


# Модель для таблицы Lists
class List(db.Model):
    __tablename__ = 'lists'
    ListID = db.Column(db.Integer, primary_key=True)
    ListName = db.Column(db.String(255))
    PriorityID = db.Column(db.Integer, db.ForeignKey('Priority.PriorityID'))
    StatusID = db.Column(db.Integer, db.ForeignKey('Statuses.StatusID'))
    isProject = db.Column(db.Boolean)
    DueDate = db.Column(db.Date)


# Модель для таблицы Groups
class Group(db.Model):
    __tablename__ = 'groups'
    GroupID = db.Column(db.Integer, primary_key=True)
    GroupName = db.Column(db.String(255))
    ListID = db.Column(db.Integer, db.ForeignKey('Lists.ListID'))
    StatusID = db.Column(db.Integer, db.ForeignKey('Statuses.StatusID'))
    PriorityID = db.Column(db.Integer, db.ForeignKey('Priority.PriorityID'))


# Модель для таблицы Tasks
class Task(db.Model):
    __tablename__ = 'tasks'
    TaskID = db.Column(db.Integer, primary_key=True)
    Level = db.Column(db.Integer)
    Title = db.Column(db.String(255))
    Descriptions = db.Column(db.Text)
    DueDate = db.Column(db.Date)
    DueTime = db.Column(db.Time)
    Attachments = db.Column(db.LargeBinary)
    Notes = db.Column(db.Text)
    PriorityID = db.Column(db.Integer, db.ForeignKey('Priority.PriorityID'))
    StatusID = db.Column(db.Integer, db.ForeignKey('Statuses.StatusID'))
    ListID = db.Column(db.Integer, db.ForeignKey('Lists.ListID'))
    GroupID = db.Column(db.Integer, db.ForeignKey('Groups.GroupID'))
    IntervalID = db.Column(db.Integer, db.ForeignKey('Intervals.IntervalID'))


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
    image = db.Column(db.Text)
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


# Модель для таблицы Plan
class Plan(db.Model):
    __tablename__ = 'plan'
    PlanID = db.Column(db.Integer, primary_key=True)
    PlanDate = db.Column(db.Date)
    TasksIDs = db.Column(db.String(255))  # Предполагается, что это строка с ID задач
    SubTaskIDs = db.Column(db.String(255))  # Аналогично для SubTaskIDs
    CompletedTasksIDs = db.Column(db.String(255))  # ID завершенных задач
    CompletedSubTasksIDs = db.Column(db.String(255))  # ID завершенных подзадач


# Модель для таблицы ChatHistory уже определена, поэтому перейдем к следующим

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
    screenshots = db.Column(db.Text)  # Путь к скриншотам или URL


# Модель для таблицы diary
class Diary(db.Model):
    __tablename__ = 'diary'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    time = db.Column(db.Text)
    bias = db.Column(db.Text)
    reason = db.Column(db.Text)
    lessons = db.Column(db.Text)
    result = db.Column(db.Text)
    comment = db.Column(db.Text)


# Модель для таблицы project_journal
class ProjectJournal(db.Model):
    __tablename__ = 'project_journal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    time = db.Column(db.Text)
    project_name = db.Column(db.Text)
    step = db.Column(db.Text)
    comment = db.Column(db.Text)


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
