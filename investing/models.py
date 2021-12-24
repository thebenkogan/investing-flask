from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


user_group_identifier = db.Table(
    "user_group_identifier",
    db.Column("group_id", db.Integer, db.ForeignKey("groups.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(150))
    groups = db.relationship("Group", secondary=user_group_identifier)
    investments = db.relationship("Investment", backref="user")


class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    users = db.relationship("User", secondary=user_group_identifier)
    investments = db.relationship("Investment", backref="group")


class Investment(db.Model):
    __tablename__ = "investments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    ticker = db.Column(db.String(5))
    amount = db.Column(db.Float)
    shares = db.Column(db.Float)
