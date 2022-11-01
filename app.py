from sys import prefix
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import auth
import cloudinary

cloudinary.config(
    cloud_name="dqv7e2cyi",
    api_key="244334546783172",
    api_secret="P-0gM5gXEWHk7UCcQr1xIav3pQg",
)
import cloudinary.uploader
import cloudinary.api

app = flask.Flask(
    __name__, template_folder="src", static_folder="static_files"
)
with open("secret_key") as f:
    env_vars = dict(line.strip().split("=", 1) for line in f)
app.secret_key = env_vars["APP_SECRET_KEY"]
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://stwiezab:eN4T8unVzyIE49TzhKCbf1m5lKkGhjWU@peanut.db.elephantsql.com/stwiezab"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import (
    ClubMembersModel,
    UsersModel,
    ClubsModel,
    JoinRequests,
)


## Index Route
@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    # Setup data model
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    # If no data is associated with the user, they are redirected
    # to create a profile
    if user is None:
        return flask.redirect(flask.url_for("profilecreation"))
    # Otherwise index is loaded with their clubs
    else:
        html_code = flask.render_template("index.html", user=user)
        response = flask.make_response(html_code)
        return response


## Profile Creation Route
@app.route("/profile-create", methods=["GET"])
def profilecreation():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is not None:
        return flask.redirect("/")
    # Only needs to render the form
    return flask.render_template("profile-create.html")


## Profile Update Route
@app.route("/profile-update", methods=["GET"])
def profileupdate():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    # Only needs to render the update form
    else:
        html_code = flask.render_template(
            "profile-update.html", user=user
        )
        response = flask.make_response(html_code)
        return response


## Profile Posting Route
@app.route("/profilepost", methods=["POST"])
def profilepost():
    # Get all important pieces of the form and turn them into
    # a data set
    ## ADD MORE AS NEEDED
    netid = auth.authenticate()
    first_name = flask.request.form["first_name"]
    last_name = flask.request.form["last_name"]
    phone = flask.request.form["phone"]
    instagram = flask.request.form["instagram"]
    snapchat = flask.request.form["snapchat"]
    try:
        photo = cloudinary.uploader.upload(
            flask.request.files["photo"], public_id=netid
        )["url"]
    except:
        photo = cloudinary.api.resource(
            prefix="/Additional Files/", public_id="default_user_icon"
        )
    is_admin = False
    new_user = UsersModel(
        netid,
        first_name,
        last_name,
        phone,
        instagram,
        snapchat,
        is_admin,
        photo,
    )
    # Input the user into the DB
    db.session.add(new_user)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/")


## Profile Posting Route
@app.route("/profileupdatepost", methods=["POST"])
def profileput():
    # Get all important pieces of the form and change them in the user's info
    ## ADD MORE AS NEEDED
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    user.first_name = flask.request.form["first_name"]
    user.last_name = flask.request.form["last_name"]
    user.phone = flask.request.form["phone"]
    user.instagram = flask.request.form["instagram"]
    user.snapchat = flask.request.form["snapchat"]
    try:
        photo = cloudinary.api.resource(netid)
        cloudinary.uploader.destroy(photo)
    except:
        pass
    try:
        user.photo = cloudinary.uploader.upload(
            flask.request.files["photo"], public_id=netid
        )["url"]
    except:
        user.photo = cloudinary.api.resource(
            "/Additional%20Files/default_user_icon"
        )["url"]
    # Input the user into the DB
    db.session.add(user)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/")


## Group Creation Route
@app.route("/group-create", methods=["GET"])
def groupcreation():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    # Only needs to render the creation form
    return flask.render_template("group-create.html")


@app.route("/grouppost", methods=["POST"])
def grouppost():
    netid = auth.authenticate()
    recent_club = (
        db.session.query(ClubsModel)
        .order_by(ClubsModel.clubid.desc())
        .first()
    )
    clubid = recent_club.clubid + 1
    name = flask.request.form["name"]
    description = flask.request.form["description"]
    attributes = ["share_socials", "share_phone"]
    info_shared = ""
    for attribute in attributes:
        if flask.request.form.get(attribute) is None:
            info_shared += "0"
        else:
            info_shared += "1"
    new_club = ClubsModel(clubid, name, description, info_shared)
    new_club_member = ClubMembersModel(clubid, netid, True)
    db.session.add(new_club)
    db.session.add(new_club_member)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/")


@app.route("/groups", methods=["GET"])
def groups():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    group_member = (
        db.session.query(ClubMembersModel.clubid, ClubsModel.name)
        .filter(ClubMembersModel.netid == netid)
        .filter(ClubsModel.clubid == ClubMembersModel.clubid)
        .order_by(ClubsModel.name)
        .all()
    )
    clubs = []
    for club in group_member:
        clubs.append(db.session.get(ClubsModel, club.clubid))
    html_code = flask.render_template(
        "groups.html", user=user, clubs=clubs
    )
    response = flask.make_response(html_code)
    return response


@app.route("/groups-search", methods=["GET"])
def groupssearch():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    group_member = (
        db.session.query(ClubsModel.clubid, ClubsModel.name)
        .order_by(ClubsModel.name)
        .all()
    )
    clubs = []
    for club in group_member:
        clubs.append(db.session.get(ClubsModel, club.clubid))
    html_code = flask.render_template(
        "groups-search.html", user=user, clubs=clubs
    )
    response = flask.make_response(html_code)
    return response


@app.route("/group-members", methods=["GET"])
def groupmembers():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    clubid = flask.request.args.get("clubid")
    member = db.session.get(ClubMembersModel, (netid, clubid))
    if member is None:
        return flask.redirect(
            "/group-join-request?clubid=" + str(clubid)
        )
    group_member = (
        db.session.query(ClubMembersModel.netid, UsersModel.netid)
        .filter(ClubMembersModel.clubid == clubid)
        .filter(UsersModel.netid == ClubMembersModel.netid)
        .order_by(UsersModel.first_name)
        .all()
    )
    print(group_member)
    members = []
    for member in group_member:
        members.append(db.session.get(UsersModel, member.netid))
    html_code = flask.render_template(
        "group-members.html",
        user=user,
        members=members,
        clubid=clubid,
        clubmember=member,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/group-join-request", methods=["GET"])
def groupjoinrequest():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    clubid = flask.request.args.get("clubid")
    club = db.session.get(ClubsModel, clubid)
    if club is None:
        return flask.redirect("/")
    html_code = flask.render_template(
        "group-join-request.html", user=user, club=club
    )
    response = flask.make_response(html_code)
    return response


@app.route("/groupjoinpost", methods=["POST"])
def groupjoinpost():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    clubid = flask.request.args.get("clubid")
    active_request = db.session.get(JoinRequests, (netid, clubid))
    if active_request is not None:
        return flask.redirect("/")
    request = JoinRequests(netid, clubid)
    db.session.add(request)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/")


@app.route("/group-invite-request", methods=["GET"])
def groupinviterequest():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    clubid = flask.request.args.get("clubid")
    member = db.session.get(ClubMembersModel, (netid, clubid))
    if member.is_moderator is False:
        return flask.redirect("groups")
    non_group_members = (
        db.session.query(ClubMembersModel.netid, UsersModel.netid)
        .filter(ClubMembersModel.clubid != clubid)
        .filter(UsersModel.netid == ClubMembersModel.netid)
        .order_by(UsersModel.first_name)
        .all()
    )
    if non_group_members is None:
        return flask.redirect("/group-members")
    club = db.session.get(ClubsModel, clubid)
    if club is None:
        return flask.redirect("/")
    html_code = flask.render_template(
        "group-invite-request.html", user=user, club=club
    )
    response = flask.make_response(html_code)
    return response


@app.route("/groupinvitepost", methods=["GET", "POST"])
def groupinvitepost():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    clubid = flask.request.args.get("clubid")
    netid = flask.request.form["netid"]
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect("/")
    request = JoinRequests(netid, clubid)
    db.session.add(request)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/")


@app.route("/member-info", methods=["GET"])
def memberinfo():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is None:
        return flask.redirect(flask.url_for("profile-create"))
    member_netid = flask.request.args.get("netid")
    clubid = flask.request.args.get("clubid")
    member = db.session.get(ClubMembersModel, (netid, clubid))
    if member is None:
        return flask.redirect("/")
    member = db.session.get(ClubMembersModel, (member_netid, clubid))
    if member is None:
        return flask.redirect("/")
    member_user = db.session.get(UsersModel, member_netid)
    html_code = flask.render_template(
        "member-info.html", member_user=member_user, user=user
    )
    response = flask.make_response(html_code)
    return response
