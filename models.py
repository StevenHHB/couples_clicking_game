from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    significant_other_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    significant_other = db.relationship(
        'User', foreign_keys=[significant_other_id])
    game_results = db.relationship('GameResult', backref='user', lazy=True)


class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    clicks = db.Column(db.Integer, nullable=False)
    won = db.Column(db.Boolean, nullable=False)
    satisfied = db.Column(db.Boolean, default=False)
    prize_selections = db.relationship(
        'PrizeSelection', back_populates='game_result')


class PrizeSelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_result_id = db.Column(db.Integer, db.ForeignKey(
        'game_result.id'), nullable=False)
    prize_id = db.Column(db.Integer, db.ForeignKey('prize.id'), nullable=False)
    satisfied = db.Column(db.Boolean, default=False)
    game_result = db.relationship(
        'GameResult', back_populates='prize_selections')
    prize = db.relationship('Prize', back_populates='prize_selections')


class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    clicks = db.relationship('Click', backref='game_session', lazy=True)


class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_session.id'))
    timestamp = db.Column(db.DateTime, nullable=False)


class Prize(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    prize_selections = db.relationship(
        'PrizeSelection', back_populates='prize')

    def __str__(self):
        return self.name
