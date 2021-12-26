from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from requests.api import get
from sqlalchemy.sql.functions import user
from .models import Group, Investment
from .price import get_price, GroupStats
from . import db

views = Blueprint("views", __name__)

# Home page
@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        group = request.form.get("group")

        if len(group) < 3:
            flash("Group name is too short!", category="error")
        else:
            new_group = Group(name=group)
            new_group.users.append(current_user)
            db.session.add(new_group)
            db.session.commit()
            flash("Group added!", category="success")

    return render_template("home.html", user=current_user)


@views.route("/group/<int:group_id>", methods=["GET", "POST"])
def group(group_id):
    if request.method == "POST":
        ticker = request.form.get("ticker")
        amount = request.form.get("amount")
        shares = request.form.get("shares")

        ticker_price = get_price(ticker)

        if ticker_price == None:
            flash("Symbol does not exist!", category="error")
        elif len(ticker) > 5:
            flash("Symbol name is too long!", category="error")
        else:
            new_investment = Investment(
                user_id=current_user.id,
                group_id=group_id,
                ticker=ticker,
                amount=amount,
                shares=shares,
            )
            db.session.add(new_investment)
            db.session.commit()
            flash("Investment added!", category="success")

    group = Group.query.get_or_404(group_id)
    stats = GroupStats(group)
    return render_template("group.html", user=current_user, group=group)
