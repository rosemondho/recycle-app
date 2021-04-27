"""CRUD operations."""

from model import db, User, Comment, FavRecycler, connect_to_db
import materials

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


def get_favorited_recyclers(user_id):
    """Return all favorited recyclers and comments."""

    return FavRecycler.query.filter(
        FavRecycler.user_id == user_id).all()


def is_recycler_favorited(location_id, user_id):
    """Checks if recycler has been favorited or not."""

    if FavRecycler.query.filter(
        FavRecycler.location_id == location_id,
        FavRecycler.user_id == user_id).first():
        return True
    
    return False


def get_favorited_location_ids_list(user_id):
    """Returns location IDs of favorited recyclers."""
    
    location_ids = FavRecycler.query.filter(FavRecycler.user_id == user_id).all()

    return [location.location_id for location in location_ids]


def user_id_if_match(email, password):
    """Returns user_id of user if the login is successful."""
    
    if get_user_by_email(email) and get_user_by_email(email).password == password:
        return get_user_by_email(email).user_id


def create_comment(user_id, name, location_id, comment):
    """Create and return a new comment."""

    comment = Comment(user_id=user_id, name=name, location_id=location_id, comment=comment)

    db.session.add(comment)
    db.session.commit()

    return comment


def get_recycler_comments(location_id):
    """Return all comments of a recycler."""

    return Comment.query.filter(Comment.location_id==location_id).all()


# def get_names_in_comments(location_id):
#     all_comments = Comment.query.filter(Comment.location_id==location_id).all()
#     all_user_ids = [comment.user_id for comment in all_comments]
    
#     return [User.query.get(user_id).name for user_id in all_user_ids]


def fav_a_recycler(user_id, location_id):
    """Return a new favorited recycler."""

    fav_recycler = FavRecycler(user_id=user_id, location_id=location_id)

    db.session.add(fav_recycler)
    db.session.commit()

    return fav_recycler


if __name__ == '__main__':
    from server import app
    connect_to_db(app)
