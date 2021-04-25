"""CRUD operations."""

from model import db, User, Recycler, FavRecycler, connect_to_db


def create_user(name, email, password):
    """Create and return a new user."""

    user = User(name=name, email=email, password=password)

    db.session.add(user)
    db.session.commit()

    return user


def get_user_by_id(user_id):
    """Return a user by primary key."""

    return User.query.filter(User.user_id == user_id).first()


def get_user_by_email(email):
    """Return a user by email."""

    return User.query.filter(User.email == email).first()


def get_recycler_by_id(location_id):
    """Return a recycler by primary key."""

    return Recycler.query.get(location_id)

def user_id_if_match(email, password):
    if User.query.filter(User.password == password).first():
        
        return get_user_by_email(email).user_id

def fav_a_recycler(user, recycler, comments):
    """Return a new favorited recycler."""

    fav_recycler = FavRecycler(user=user, recycler=recycler, comments=comments)

    db.session.add(fav_recycler)
    db.session.commit()

    return fav_recycler


if __name__ == '__main__':
    from server import app
    connect_to_db(app)
