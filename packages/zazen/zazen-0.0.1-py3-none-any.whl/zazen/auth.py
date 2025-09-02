from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from .models import User, db

__all__ = [
    "login_manager",
    "login_user",
    "logout_user",
    "current_user",
    "login_required",
    "register_user",
    "authenticate_user",
    "update_user_profile",
    "change_password",
]

login_manager = LoginManager()

login_manager.login_view = "/login"  # Redirect to login page

current_user: User | None


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return User.query.filter_by(username=user_id).one_or_none()


def register_user(
    username, email, password, first_name=None, last_name=None
) -> tuple[bool, str, User | None]:
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return False, "Username already exists", None
    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return False, "Email already exists", None
    # Create new user
    user = User(
        username=username, email=email, first_name=first_name, last_name=last_name
    )
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.commit()
        return True, "User registered successfully", user
    except Exception as e:
        db.session.rollback()
        return False, f"Registration failed: {str(e)}", None


def authenticate_user(username: str, password: str):
    # Try to find user by username or email
    user: User = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    if user and user.check_password(password) and user.is_active:
        return True, "Login successful", user
    return False, "Invalid username/email or password", None


def update_user_profile(user_id: int, **kwargs):
    user = User.query.get(user_id)
    if not user:
        return False, "User not found", None
    # Check for username conflicts
    if "username" in kwargs and kwargs["username"] != user.username:
        if User.query.filter_by(username=kwargs["username"]).first():
            return False, "Username already exists", None
    # Check for email conflicts
    if "email" in kwargs and kwargs["email"] != user.email:
        if User.query.filter_by(email=kwargs["email"]).first():
            return False, "Email already exists", None
    # Update allowed fields
    allowed_fields = ["username", "email", "first_name", "last_name"]
    for field in allowed_fields:
        if field in kwargs:
            setattr(user, field, kwargs[field])
    try:
        db.session.commit()
        return True, "Profile updated successfully", user
    except Exception as e:
        db.session.rollback()
        return False, f"Update failed: {str(e)}", None


def change_password(user_id: int, current_password: str, new_password: str):
    user: User | None = User.query.get(user_id)
    if not user:
        return False, "User not found"
    if not user.check_password(current_password):
        return False, "Current password is incorrect", None
    user.set_password(new_password)
    try:
        db.session.commit()
        return True, "Password changed successfully", user
    except Exception as e:
        db.session.rollback()
        return False, f"Password change failed: {str(e)}", None
