from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    total_experience = db.Column(db.Integer, default=0)
    last_practice_date = db.Column(db.Date, nullable=True)
    total_practices = db.Column(db.Integer, default=0)
    
    practices = db.relationship('Practice', backref='user', lazy=True)
    
    def get_exp_for_level(self, level):
        import math
        base = 100
        return int(base * (1 + math.log(max(level, 2)) / math.log(2)))
    
    def get_level_exp_threshold(self, level):
        if level <= 1:
            return 0
        total = 0
        for i in range(1, level + 1):
            total += self.get_exp_for_level(i)
        return total
    
    def to_dict(self):
        current_threshold = self.get_level_exp_threshold(self.current_level)
        next_threshold = self.get_level_exp_threshold(self.current_level + 1)
        exp_in_level = max(0, self.total_experience - current_threshold)
        exp_needed = max(1, next_threshold - current_threshold)
        
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'current_level': self.current_level,
            'experience': self.experience,
            'total_experience': self.total_experience,
            'exp_in_level': exp_in_level,
            'exp_needed': exp_needed,
            'level_progress': min(1, max(0, exp_in_level / exp_needed)),
            'total_practices': self.total_practices,
            'last_practice_date': self.last_practice_date.isoformat() if self.last_practice_date else None
        }


class Practice(db.Model):
    __tablename__ = 'practices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    practice_date = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    chords_practiced = db.Column(db.Text, nullable=False)
    deepseek_summary = db.Column(db.Text, nullable=True)
    deepseek_next_plan = db.Column(db.Text, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'practice_date': self.practice_date.isoformat(),
            'level': self.level,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'chords_practiced': self.chords_practiced,
            'deepseek_summary': self.deepseek_summary,
            'deepseek_next_plan': self.deepseek_next_plan,
            'duration_seconds': self.duration_seconds
        }


class Chord(db.Model):
    __tablename__ = 'chords'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    guitar_positions = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'notes': self.notes,
            'level': self.level,
            'guitar_positions': self.guitar_positions
        }
