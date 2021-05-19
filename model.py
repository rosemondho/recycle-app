"""Models for recycler app."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """A user."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)


    def __repr__(self):
        return f'<User user_id={self.user_id} name={self.name} email={self.email}>'


class FavRecycler(db.Model):
    """A favorited Recycler."""

    __tablename__ = 'fav_recycler'

    recycler_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    location_id = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    __table_args__ = (db.UniqueConstraint('user_id', 'location_id'), )
    # recycler = db.relationship('Comment', backref='fav_recycler')
    # user = db.relationship('User', backref='fav_recycler')

    def __repr__(self):
        return f'<FavRecycler user_id={self.user_id} location_id={self.location_id}>'


class Comment(db.Model):
    """General comment in the Recycler Details section."""

    __tablename__ = 'comments'

    comment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    location_id = db.Column(db.String)
    #location_id = db.Column(db.Integer, db.ForeignKey('fav_recycler.location_id'))
    name = db.Column(db.String)
    user_id = db.Column(db.Integer)
    comment = db.Column(db.String)

    

    def __repr__(self):
        return f'<Recycler location_id={self.location_id} comment={self.comment}>'


def connect_to_db(flask_app, db_uri='postgresql:///recyclers', echo=True):
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    flask_app.config['SQLALCHEMY_ECHO'] = echo
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = flask_app
    db.init_app(flask_app)

    print('Connected to the db!')


if __name__ == '__main__':
    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app)
