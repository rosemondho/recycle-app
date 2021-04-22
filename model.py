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
    email = db.Column(db.String, unique=True)
    zip_code = db.Column(db.Integer)
    password = db.Column(db.String)
    pet_num = db.Column(db.Integer)


    def __repr__(self):
        return f'<User user_id={self.user_id} email={self.email}>'

class Recycler(db.Model):
    """A recycler in the recycling directory."""
    __tablename__ = 'recyclers'

    location_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.Text)
    recycling_info = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return f'<Recycler location_id={self.location_id} name={self.name}>'

class FavRecycler(db.Model):
    """A movie rating."""

    __tablename__ = 'fav_recycler'

    recycler_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('recyclers.location_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    comment = db.Column(db.String)

    recycler = db.relationship('Recycler', backref='fav_recycler')
    user = db.relationship('User', backref='fav_recycler')

    def __repr__(self):
        return f'<FavRecycler recycler_id={self.rating_id} comment={self.comment}>'


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
