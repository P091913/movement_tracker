from flask_login import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for friendships
friends = db.Table('friends',
                   db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                   db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
                   )

class ComboProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.Column(db.Integer, nullable=False)
    successes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Foreign key referencing the User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='user_combo_progress')

    # Foreign key referencing the Combo table
    combo_id = db.Column(db.Integer, db.ForeignKey('combo.id'), nullable=False)
    combo = db.relationship('Combo', backref='combo_progress_details')

class CustomTrick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trick_name = db.Column(db.String(100), nullable=False)
    # Add more fields as needed

    # Foreign key referencing the User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='custom_tricks')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(15))
    email = db.Column(db.String(35), unique=True)

    user_moves = db.relationship('UserMoves', back_populates='user', cascade="all, delete-orphan")
    posts = db.relationship('Post', backref='author', lazy=True)

    # Friends relationship
    friends = db.relationship('User',
                              secondary=friends,
                              primaryjoin=id == friends.c.user_id,
                              secondaryjoin=id == friends.c.friend_id,
                              backref='friend_users')


class Moves(db.Model):
    move_id = db.Column(db.Integer, primary_key=True)
    move_name = db.Column(db.String(50), unique=True)

    move_users = db.relationship('UserMoves', back_populates='move', cascade="all, delete-orphan")


class UserMoves(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)  # Change 'user' to 'User'
    move_id = db.Column(db.Integer, db.ForeignKey('moves.move_id'), primary_key=True)
    status = db.Column(db.Integer, default=0.0)

    user = db.relationship('User', back_populates='user_moves')  # Fix the back_populates value
    move = db.relationship('Moves', back_populates='move_users')  # Fix the back_populates value


class SessionDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    trick_name = db.Column(db.String(100), nullable=False)
    attempts = db.Column(db.Integer, nullable=False)
    successful_landings = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Foreign key referencing the User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='user_session_details')

    # Foreign key referencing the Moves table
    move_id = db.Column(db.Integer, db.ForeignKey('moves.move_id'), nullable=False)
    move = db.relationship('Moves', backref='move_session_details')



class Combo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key referencing the User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='combos')  # Establishing the relationship

    # Many-to-many relationship with moves
    moves = db.relationship('Moves', secondary='combo_moves', backref='combos')


# Association table for many-to-many relationship between Combo and Moves
combo_moves = db.Table('combo_moves',
                       db.Column('combo_id', db.Integer, db.ForeignKey('combo.id'), primary_key=True),
                       db.Column('move_id', db.Integer, db.ForeignKey('moves.move_id'), primary_key=True)
                       )


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


