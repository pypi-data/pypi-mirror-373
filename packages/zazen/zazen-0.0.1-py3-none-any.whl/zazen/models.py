from datetime import datetime, timezone
from typing import Optional

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Boolean, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Initialize SQLAlchemy with new style base
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(80), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __init__(
        self,
        username: str,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self) -> str:
        # Note: Flask-Login expects the user ID to be a string
        # Do not use this method manually
        return self.username

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username

    def update_last_login(self) -> None:
        self.last_login = datetime.utcnow()
        db.session.commit()

    def deactivate(self) -> None:
        self.is_active = False
        db.session.commit()

    def activate(self) -> None:
        self.is_active = True
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.get_full_name(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class AppletState(db.Model):
    __tablename__ = "applet_state"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    applet_name: Mapped[str] = mapped_column(String(80), nullable=False)
    state_data: Mapped[Optional[JSON]] = mapped_column(
        JSON, nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )

    def __init__(
        self, id: str, user_id: int, applet_name: str, state_data: Optional[dict] = None
    ):
        self.id = id
        self.user_id = user_id
        self.applet_name = applet_name
        self.state_data = state_data

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "applet_name": self.applet_name,
            "state_data": self.state_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<AppletState {self.applet_name} for User {self.user_id}>"
