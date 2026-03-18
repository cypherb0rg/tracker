from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Phase(db.Model):
    __tablename__ = 'phases'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    date_range = db.Column(db.String(255))
    goal = db.Column(db.Text)
    target_problems = db.Column(db.Integer)
    estimated_hours = db.Column(db.Integer)

    weeks = db.relationship('Week', backref='phase', lazy='select', cascade='all, delete-orphan')
    mastery_items = db.relationship('PhaseMastery', backref='phase', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Phase {self.number}: {self.title}>'


class Week(db.Model):
    __tablename__ = 'weeks'

    id = db.Column(db.Integer, primary_key=True)
    phase_id = db.Column(db.Integer, db.ForeignKey('phases.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    date_range = db.Column(db.String(255))

    day_blocks = db.relationship('DayBlock', backref='week', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Week {self.number}: {self.title}>'


class DayBlock(db.Model):
    __tablename__ = 'day_blocks'

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    date_range = db.Column(db.String(255))
    estimated_time = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)
    reflection = db.Column(db.Text, default='')

    checklist_items = db.relationship('ChecklistItem', backref='day_block', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<DayBlock {self.title}>'


class ChecklistItem(db.Model):
    __tablename__ = 'checklist_items'

    id = db.Column(db.Integer, primary_key=True)
    day_block_id = db.Column(db.Integer, db.ForeignKey('day_blocks.id'), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # 'learning' | 'leetcode' | 'hackerrank' | 'review'
    label = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(512), default='')
    difficulty = db.Column(db.String(50), default='')  # 'Easy', 'Medium', 'Hard'
    sort_order = db.Column(db.Integer, default=0)
    is_checked = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ChecklistItem {self.label}>'


class PhaseMastery(db.Model):
    __tablename__ = 'phase_mastery'

    id = db.Column(db.Integer, primary_key=True)
    phase_id = db.Column(db.Integer, db.ForeignKey('phases.id'), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    is_checked = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<PhaseMastery {self.label}>'
