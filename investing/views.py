from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc
from .models import User, Group, Investment, Invite
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


# Invites page
@views.route("/invites")
@login_required
def invite():
    invites = (
        Invite.query.filter_by(user_id=current_user.id)
        .order_by(desc(Invite.date))
        .all()
    )
    return render_template("invite.html", user=current_user, invites=invites)


@views.route("/invites/<int:invite_id>/<int:accept>", methods=["POST"])
@login_required
def handle_invite(invite_id, accept):
    invite = Invite.query.get_or_404(invite_id)
    if accept:
        group = Group.query.get_or_404(invite.group_id)
        group.users.append(current_user)
        db.session.delete(invite)
        db.session.commit()
        flash(f"Joined {group.name}!", category="success")
    else:
        db.session.delete(invite)
        db.session.commit()
        flash("Invite rejected!", "success")
    redirect_url = "home" if accept else "invite"
    return redirect(url_for(f"views.{redirect_url}"))


@views.route("/leave/<int:group_id>", methods=["POST"])
@login_required
def leave_group(group_id):
    group = Group.query.get_or_404(group_id)
    group.users.remove(current_user)
    db.session.commit()
    flash(f"Leaved {group.name}!", category="success")
    return redirect(url_for(f"views.home"))


@views.route("/group/<int:group_id>", methods=["GET", "POST"])
def group(group_id):
    if request.method == "POST" and "ticker" in request.form:
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
                ticker=ticker.upper(),
                amount=amount,
                shares=shares,
            )
            db.session.add(new_investment)
            db.session.commit()
            flash("Investment added!", category="success")
    elif request.method == "POST" and "email" in request.form:
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        # TODO Need to also check if invite is for user already in the group

        if user:
            if user == current_user:
                flash("Cannot invite yourself.", category="error")
            else:
                if group_id in [group.id for group in user.groups]:  # Already in group
                    flash(
                        f"{user.first_name} is already in this group.", category="error"
                    )
                else:
                    new_invite = Invite(user_id=user.id, group_id=group_id)
                    db.session.add(new_invite)
                    db.session.commit()
                    flash(f"Invited {user.first_name}!", category="success")
        else:
            flash("Email does not exist.", category="error")

    group = Group.query.get_or_404(group_id)
    stats = GroupStats(group)

    def get_user_share(user_id):
        try:
            return stats.user_shares[user_id]
        except Exception:
            return 0

    return render_template(
        "group.html",
        user=current_user,
        group=group,
        stats=stats,
        get_user_share=get_user_share,
    )
