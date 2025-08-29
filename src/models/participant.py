from src.models.user import db
from datetime import datetime
import json

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    post = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=25)
    correct_answers = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer, default=0)  # in seconds
    answers = db.Column(db.Text)  # JSON string of answers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Participant {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'department': self.department,
            'post': self.post,
            'email': self.email,
            'mobile': self.mobile,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'time_taken': self.time_taken,
            'answers': json.loads(self.answers) if self.answers else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def set_answers(self, answers_list):
        self.answers = json.dumps(answers_list)
    
    def get_answers(self):
        return json.loads(self.answers) if self.answers else []

