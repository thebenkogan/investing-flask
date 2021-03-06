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
    groups = db.relationship("Group", secondary=user_group_identifier, backref="users")
    investments = db.relationship("Investment", backref="user")
    invites = db.relationship("Invite", backref="user")


class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    investments = db.relationship("Investment", backref="group")
    invites = db.relationship("Invite", backref="group")


class Investment(db.Model):
    __tablename__ = "investments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    ticker = db.Column(db.String(5))
    amount = db.Column(db.Numeric(20, 2))
    shares = db.Column(db.Numeric(20, 2))


class Invite(db.Model):
    __tablename__ = "invites"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
