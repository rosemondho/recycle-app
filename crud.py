"""CRUD operations."""

from model import db, User, Recycler, FavRecycler, connect_to_db


def create_user(email, password):
    """Create and return a new user."""

    user = User(email=email, password=password)

    db.session.add(user)
    db.session.commit()

    return user


def get_users():
    """Return all users."""

    return User.query.all()


def get_user_by_id(user_id):
    """Return a user by primary key."""

    return User.query.get(user_id)


def get_user_by_email(email):
    """Return a user by email."""

    return User.query.filter(User.email == email).first()


# def create_movie(title, overview, release_date, poster_path):
#     """Create and return a new movie."""

#     movie = Movie(title=title,
#                   overview=overview,
#                   release_date=release_date,
#                   poster_path=poster_path)

#     db.session.add(movie)
#     db.session.commit()

#     return movie


# def get_recyclers():
#     """Return all recyclers."""

#     return Recycler.query.all()


def get_recycler_by_id(location_id):
    """Return a movie by primary key."""

    return Recycler.query.get(location_id)


def fav_a_recycler(user, recycler, comments):
    """Create and return a new rating."""

    fav_recycler = FavRecycler(user=user, recycler=recycler, comments=comments)

    db.session.add(fav_recycler)
    db.session.commit()

    return fav_recycler


if __name__ == '__main__':
    from server import app
    connect_to_db(app)
