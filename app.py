from sys import prefix
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_wtf
import os
import auth
import cloudinary
import more_itertools as mit

from api import req_lib

os.environ["APP_SECRET_KEY"] = "asdfadfs"

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
app.secret_key = os.environ["APP_SECRET_KEY"]

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://stwiezab:eN4T8unVzyIE49TzhKCbf1m5lKkGhjWU@peanut.db.elephantsql.com/stwiezab"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

flask_wtf.csrf.CSRFProtect(app)

from models import (
    ClubMembersModel,
    UsersModel,
    ClubsModel,
    JoinRequests,
    InviteRequests,
    CreationRequests,
    UndergraduatesModel,
)

test = True


def checkValidUser():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if not user:
        return flask.abort(flask.redirect("/profile-create"))
    if user.first_time:
        user.first_time = False
        db.session.commit()
        return flask.abort(flask.redirect("/profile-update"))
    if user.is_banned:
        return flask.abort(flask.redirect("/banned"))
    return user


def checkValidAdmin():
    user = checkValidUser()
    if not user.is_admin:
        return flask.abort(flask.redirect("/index"))
    return user


def checkValidClub(clubid):
    club = db.session.get(ClubsModel, clubid)
    if not club:
        return flask.abort(flask.redirect("/index"))
    return club


def checkValidMember(user, club):
    clubmember = db.session.get(
        ClubMembersModel, (user.netid, club.clubid)
    )
    if not clubmember:
        return flask.abort(
            flask.redirect(
                "/group-join-request?clubid=" + str(club.clubid)
            )
        )
    return clubmember


def checkValidModerator(user, club):
    clubmember = checkValidMember(user, club)
    if not clubmember.is_moderator:
        return flask.abort(
            flask.redirect("/group-members?clubid=" + str(club.clubid))
        )
    return clubmember


## Index Route
@app.route("/", methods=["GET"])
def index():
    if auth.loggedin() is not None:
        return flask.redirect("/index")
    html_code = flask.render_template("landing.html")
    response = flask.make_response(html_code)
    return response


# landing page
@app.route("/landing", methods=["GET"])
@app.route("/index", methods=["GET"])
def landing():
    # Setup data model
    user = checkValidUser()
    search_string = flask.request.args.get("search")

    # get the string that user searched and current page number
    page_number = flask.request.args.get("page")
    if not page_number:
        page_number = 0

    if search_string == None:
        html_code = flask.render_template(
            "index.html", user=user, no_search=True
        )
        response = flask.make_response(html_code)
        return response
    else:
        lowercase = search_string.lower()
        users = (
            db.session.query(UsersModel)
            .filter(
                (UsersModel.netid.ilike("%" + lowercase + "%"))
                | (UsersModel.display_name.ilike("%" + lowercase + "%"))
                | (
                    (
                        UsersModel.first_name
                        + " "
                        + UsersModel.last_name
                    ).ilike("%" + lowercase + "%")
                )
            )
            .filter(UsersModel.is_banned == False)
            .order_by(UsersModel.netid)
            .all()
        )
        # split users up into pages of 50. Each page is split into lists of 10.
        # Later on, allow user to select number of results per page.
        users_pages = list(mit.chunked(users, 10))

        results_length = len(users)
        if results_length > 10:
            users = users[:10]

        html_code = flask.render_template(
            "index.html",
            user=user,
            search_string=search_string,
            users=users,
            results_length=results_length,
            users_pages=users_pages,
            max_pages=len(users_pages),
            page_number=int(page_number),
            no_search=False,
        )
        response = flask.make_response(html_code)
        return response


@app.route("/about", methods=["GET"])
def about():
    # Setup data model
    user = checkValidUser()
    html_code = flask.render_template("about.html", user=user)
    response = flask.make_response(html_code)
    return response


@app.route("/logout", methods=["GET"])
def logout():
    auth.logoutapp()


## Profile Creation Route
@app.route("/profile-create", methods=["GET"])
def profilecreation():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if user is not None:
        return flask.redirect("/index")
    # Only needs to render the form
    return flask.render_template("profile-create.html")


## Profile Update Route
@app.route("/profile-update", methods=["GET"])
def profileupdate():
    user = checkValidUser()
    # Only needs to render the update form
    html_code = flask.render_template("profile-update.html", user=user)
    response = flask.make_response(html_code)
    return response


## Profile Posting Route (creation)
@app.route("/profilepost", methods=["POST"])
def profilepost():
    # Get all important pieces of the form and turn them into
    # a data set
    ## ADD MORE AS NEEDED
    netid = auth.authenticate()
    first_name = flask.request.form["first_name"]
    last_name = flask.request.form["last_name"]
    display_name = first_name + " " + last_name
    phone = flask.request.form["phone"]
    instagram = flask.request.form["instagram"]
    snapchat = flask.request.form["snapchat"]
    email = netid + "@princeton.edu"
    try:
        photo = cloudinary.uploader.upload(
            flask.request.files["photo"], public_id=netid
        )["url"]
    except:
        photo = cloudinary.api.resource(
            "/Additional%20Files/default_user_icon"
        )["url"]
    is_admin = False
    is_banned = False
    new_user = UsersModel(
        netid,
        first_name,
        last_name,
        display_name,
        phone,
        instagram,
        snapchat,
        email,
        is_admin,
        is_banned,
        photo,
        False,
    )
    # Input the user into the DB
    db.session.add(new_user)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/index")


## Profile Posting Route (update profile)
@app.route("/profileupdatepost", methods=["POST"])
def profileput():
    # Get all important pieces of the form and change them in the user's info
    ## ADD MORE AS NEEDED
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    user.first_name = flask.request.form["first_name"]
    user.last_name = flask.request.form["last_name"]
    user.display_name = (
        flask.request.form["first_name"]
        + " "
        + flask.request.form["last_name"]
    )
    user.phone = flask.request.form["phone"]
    user.instagram = flask.request.form["instagram"]
    user.snapchat = flask.request.form["snapchat"]
    photo = flask.request.files["photo"]
    if photo:
        user.photo = cloudinary.uploader.upload(photo, public_id=netid)[
            "url"
        ]

    ### DEPRECATED CODE: photo removal ###
    # photo = cloudinary.api.resource(netid)
    # cloudinary.uploader.destroy(photo)

    ### DEPRECATED CODE: replace photo with default ###
    # user.photo = cloudinary.api.resource(
    #     "/Additional%20Files/default_user_icon"
    # )["url"]
    # """
    # if flask.request.files["photo"] == "delete":
    #     user.photo = cloudinary.api.resource(
    #         "/Additional%20Files/default_user_icon"
    #     )["url"]
    # """

    # Input the user into the DB
    db.session.add(user)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/index")


## Group Creation Route
@app.route("/group-create-request", methods=["GET"])
def groupcreation():
    user = checkValidUser()
    # Only needs to render the creation form
    return flask.render_template("group-create-request.html", user=user)


@app.route("/grouprequestpost", methods=["POST"])
def grouprequestpost():
    netid = auth.authenticate()
    name = flask.request.form["name"]
    attributes = ["share_socials", "share_phone"]
    share_phone = flask.request.form.get("share_phone") == "on"
    share_socials = flask.request.form.get("share_socials") == "on"
    public = flask.request.form.get("public") == "on"
    recent_request = (
        db.session.query(CreationRequests)
        .order_by(CreationRequests.reqid.desc())
        .first()
    )
    reqid = 0
    if recent_request is not None:
        reqid = recent_request.reqid + 1
    new_club_request = CreationRequests(
        reqid, name, netid, public, share_phone, share_socials
    )
    db.session.add(new_club_request)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/index")


@app.route("/groups", methods=["GET"])
def groups():
    user = checkValidUser()
    clubs = (
        db.session.query(ClubsModel)
        .filter(ClubMembersModel.netid == user.netid)
        .filter(ClubsModel.clubid == ClubMembersModel.clubid)
        .order_by(ClubsModel.name)
        .all()
    )
    html_code = flask.render_template(
        "groups.html", user=user, clubs=clubs
    )
    response = flask.make_response(html_code)
    return response


@app.route("/group-results", methods=["GET"])
def groupresults():
    user = checkValidUser()
    search = flask.request.args.get("search").lower()
    adminclubs = (
        db.session.query(ClubsModel)
        .filter(ClubMembersModel.netid == user.netid)
        .filter(ClubsModel.clubid == ClubMembersModel.clubid)
        .filter(ClubMembersModel.is_moderator == True)
        .filter(ClubsModel.name.ilike("%" + search + "%"))
        .order_by(ClubsModel.name)
        .all()
    )
    nonadminclubs = (
        db.session.query(ClubsModel)
        .filter(ClubMembersModel.netid == user.netid)
        .filter(ClubsModel.clubid == ClubMembersModel.clubid)
        .filter(ClubMembersModel.is_moderator == False)
        .filter(ClubsModel.name.ilike("%" + search + "%"))
        .order_by(ClubsModel.name)
        .all()
    )
    html_code = flask.render_template(
        "group-results.html",
        user=user,
        adminclubs=adminclubs,
        nonadminclubs=nonadminclubs,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/groups-search", methods=["GET"])
def groupssearch():
    user = checkValidUser()
    html_code = flask.render_template("groups-search.html", user=user)
    response = flask.make_response(html_code)
    return response


@app.route("/group-search-results", methods=["GET"])
def groupsearchresults():
    user = checkValidUser()
    search = flask.request.args.get("search").lower()
    clubs = (
        db.session.query(ClubsModel)
        .filter(ClubsModel.name.ilike("%" + search + "%"))
        .order_by(ClubsModel.name)
        .all()
    )
    html_code = flask.render_template(
        "group-search-results.html", user=user, clubs=clubs
    )
    response = flask.make_response(html_code)
    return response


@app.route("/group-members", methods=["GET"])
def groupmembers():
    user = checkValidUser()
    clubid = flask.request.args.get("clubid")
    club = checkValidClub(clubid)
    clubmember = checkValidMember(user, club)
    adminmembers = (
        db.session.query(UsersModel)
        .filter(ClubMembersModel.clubid == clubid)
        .filter(UsersModel.netid == ClubMembersModel.netid)
        .filter(ClubMembersModel.is_moderator == True)
        .filter(UsersModel.is_banned == False)
        .order_by(UsersModel.first_name)
        .all()
    )
    nonadminmembers = (
        db.session.query(UsersModel)
        .filter(ClubMembersModel.clubid == clubid)
        .filter(UsersModel.netid == ClubMembersModel.netid)
        .filter(ClubMembersModel.is_moderator == False)
        .filter(UsersModel.is_banned == False)
        .order_by(UsersModel.first_name)
        .all()
    )

    html_code = flask.render_template(
        "group-members.html",
        user=user,
        adminmembers=adminmembers,
        nonadminmembers=nonadminmembers,
        clubid=clubid,
        clubmember=clubmember,
        name=club.name,
        is_public=club.public,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/toggle-visibility", methods=["GET", "POST"])
def togglevisibility():
    user = checkValidUser()
    clubid = flask.request.args.get("clubid")
    club = checkValidClub(clubid)
    clubmember = checkValidMember(user, club)
    adminmembers = (
        db.session.query(UsersModel)
        .filter(ClubMembersModel.clubid == clubid)
        .filter(UsersModel.netid == ClubMembersModel.netid)
        .filter(ClubMembersModel.is_moderator == True)
        .filter(UsersModel.is_banned == False)
        .order_by(UsersModel.first_name)
        .all()
    )
    nonadminmembers = (
        db.session.query(UsersModel)
        .filter(ClubMembersModel.clubid == clubid)
        .filter(UsersModel.netid == ClubMembersModel.netid)
        .filter(ClubMembersModel.is_moderator == False)
        .filter(UsersModel.is_banned == False)
        .order_by(UsersModel.first_name)
        .all()
    )

    new_permissions = db.session.get(ClubsModel, clubid)
    new_permissions.public = not club.public

    # Input the user into the DB
    db.session.add(new_permissions)
    db.session.commit()
    html_code = flask.render_template(
        "group-members.html",
        user=user,
        adminmembers=adminmembers,
        nonadminmembers=nonadminmembers,
        clubid=clubid,
        clubmember=clubmember,
        name=club.name,
        is_public=club.public,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/group-requests", methods=["GET"])
def grouprequests():
    user = checkValidUser()
    clubid = flask.request.args.get("clubid")
    club = checkValidClub(clubid)
    clubmember = checkValidModerator(user, club)
    students = (
        db.session.query(UsersModel)
        .filter(JoinRequests.clubid == clubid)
        .filter(UsersModel.netid == JoinRequests.netid)
        .filter(UsersModel.is_banned == False)
        .order_by(UsersModel.first_name)
        .all()
    )
    html_code = flask.render_template(
        "group-requests.html",
        user=user,
        students=students,
        clubid=clubid,
        clubmember=clubmember,
        name=club.name,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/group-join-request", methods=["GET"])
def groupjoinrequest():
    user = checkValidUser()
    clubid = flask.request.args.get("clubid")
    club = checkValidClub(clubid)
    member = db.session.get(ClubMembersModel, (user.netid, clubid))
    if member is not None:
        return flask.redirect("/group-members?clubid=" + clubid)
    html_code = flask.render_template(
        "group-join-request.html", user=user, club=club
    )
    response = flask.make_response(html_code)
    return response


@app.route("/groupjoinpost", methods=["POST"])
def groupjoinpost():
    netid = auth.authenticate()
    clubid = flask.request.args.get("clubid")
    active_request = db.session.get(JoinRequests, (netid, clubid))
    if active_request is not None:
        return flask.redirect("/index")
    request_exists = db.session.get(InviteRequests, (netid, clubid))
    if request_exists is not None:
        return flask.redirect("/my-invites")
    request = JoinRequests(netid, clubid)
    db.session.add(request)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/index")


@app.route("/groupjoinfulfill", methods=["POST"])
def groupjoinfulfill():
    clubid = flask.request.args.get("clubid")
    join_netid = flask.request.args.get("join_netid")
    accept = flask.request.args.get("accept")
    join_request = db.session.get(JoinRequests, (join_netid, clubid))
    db.session.delete(join_request)
    db.session.commit()
    if accept == "1":
        new_club_member = ClubMembersModel(clubid, join_netid, False)
        db.session.add(new_club_member)
        db.session.commit()
    return flask.redirect("/group-requests?clubid=" + clubid)


@app.route("/group-leave", methods=["GET"])
def groupleave():
    user = checkValidUser()
    clubid = flask.request.args.get("clubid")
    club = checkValidClub(clubid)
    member = checkValidMember(user, club)
    html_code = flask.render_template(
        "group-leave.html", user=user, club=club
    )
    response = flask.make_response(html_code)
    return response


@app.route("/groupleavepost", methods=["POST"])
def groupleavepost():
    netid = auth.authenticate()
    clubid = flask.request.args.get("clubid")
    member = db.session.get(ClubMembersModel, (netid, clubid))
    db.session.delete(member)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/groups")


@app.route("/group-remove-member", methods=["GET"])
def groupremovemember():
    user = checkValidUser()
    clubid = flask.request.args.get("clubid")
    club = checkValidClub(clubid)
    member = checkValidModerator(user, club)
    members = (
        db.session.query(ClubMembersModel.is_moderator, UsersModel)
        .filter(ClubMembersModel.clubid == clubid)
        .filter(UsersModel.netid == ClubMembersModel.netid)
        .filter(UsersModel.is_banned == False)
        .order_by(UsersModel.first_name)
        .all()
    )
    html_code = flask.render_template(
        "group-remove-member.html",
        user=user,
        members=members,
        club=club,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/removemember", methods=["POST"])
def removemember():
    clubid = flask.request.args.get("clubid")
    member_netid = flask.request.args.get("netid")
    deleted_member = db.session.get(
        ClubMembersModel, (member_netid, clubid)
    )
    db.session.delete(deleted_member)
    db.session.commit()
    return flask.redirect("/group-remove-member?clubid=" + clubid)


@app.route("/group-moderator-upgrade", methods=["GET"])
def groupmoderatorupgrade():
    user = checkValidUser()
    clubid = flask.request.args.get("clubid")
    club = checkValidClub(clubid)
    member = checkValidModerator(user, club)
    members = (
        db.session.query(ClubMembersModel.is_moderator, UsersModel)
        .filter(ClubMembersModel.clubid == clubid)
        .filter(UsersModel.netid == ClubMembersModel.netid)
        .filter(UsersModel.is_banned == False)
        .order_by(UsersModel.first_name)
        .all()
    )
    html_code = flask.render_template(
        "group-moderator-upgrade.html",
        user=user,
        members=members,
        club=club,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/upgrademember", methods=["POST"])
def upgrademember():
    clubid = flask.request.args.get("clubid")
    member_netid = flask.request.args.get("netid")
    upgraded_member = db.session.get(
        ClubMembersModel, (member_netid, clubid)
    )
    upgraded_member.is_moderator = True
    db.session.add(upgraded_member)
    db.session.commit()
    return flask.redirect("/group-moderator-upgrade?clubid=" + clubid)


@app.route("/group-invite-request", methods=["GET"])
def groupinviterequest():
    user = checkValidUser()
    clubid = flask.request.args.get("clubid")
    club = checkValidClub(clubid)
    member = checkValidModerator(user, club)
    html_code = flask.render_template(
        "group-invite-request.html", user=user, club=club
    )
    response = flask.make_response(html_code)
    return response


@app.route("/groupinvitepost", methods=["POST"])
def groupinvitepost():
    clubid = flask.request.args.get("clubid")
    invited_netid = flask.request.form["netid"]
    invited_user = db.session.get(UsersModel, invited_netid)
    invited_member = db.session.get(
        ClubMembersModel, (invited_netid, clubid)
    )
    join_exists = db.session.get(JoinRequests, (invited_netid, clubid))
    request_exists = db.session.get(
        InviteRequests, (invited_netid, clubid)
    )
    if (
        invited_user is None
        or invited_member is not None
        or join_exists is not None
        or request_exists is not None
    ):
        return flask.redirect(
            flask.url_for("invitenetiderror", clubid=clubid), code=307
        )

    request = InviteRequests(invited_netid, clubid)
    db.session.add(request)
    db.session.commit()
    return flask.redirect("/group-members?clubid=" + clubid)


@app.route("/invite-netid-error", methods=["POST"])
def invitenetiderror():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    clubid = flask.request.args.get("clubid")
    html_code = flask.render_template(
        "invite-netid-error.html", user=user, clubid=clubid
    )
    response = flask.make_response(html_code)
    return response


@app.route("/user-info", methods=["GET"])
def userinfo():
    user = checkValidUser()
    member_netid = flask.request.args.get("netid")
    is_my_profile = member_netid == user.netid

    # if you're looking at your own profile, show all info
    if is_my_profile:
        html_code = flask.render_template(
            "user-info.html",
            requested_user=user,
            user=user,
            share_phone=True,
            share_socials=True,
            is_my_profile=is_my_profile,
        )
        response = flask.make_response(html_code)
        return response

    # find all shared clubs
    member_clubs = db.session.query(ClubMembersModel.clubid).filter(
        ClubMembersModel.netid == member_netid
    )

    user_clubs = db.session.query(ClubMembersModel.clubid).filter(
        ClubMembersModel.netid == user.netid
    )
    shared_clubs = set(member_clubs).intersection(set(user_clubs))
    share_phone = False
    share_socials = False
    for clubid in shared_clubs:
        club = db.session.get(ClubsModel, clubid)
        if club.share_phone:
            share_phone = True
        if club.share_socials:
            share_socials = True
        if share_phone and share_socials:
            break

    requested_user = db.session.get(UsersModel, member_netid)
    if requested_user.is_banned:
        return flask.redirect("/index")
    html_code = flask.render_template(
        "user-info.html",
        requested_user=requested_user,
        user=user,
        share_phone=share_phone,
        share_socials=share_socials,
        is_my_profile=is_my_profile,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/my-invites", methods=["GET"])
def myinvites():
    user = checkValidUser()
    invites = (
        db.session.query(ClubsModel)
        .filter(InviteRequests.netid == user.netid)
        .filter(ClubsModel.clubid == InviteRequests.clubid)
        .all()
    )
    html_code = flask.render_template(
        "my-invites.html", user=user, invites=invites
    )
    response = flask.make_response(html_code)
    return response


@app.route("/invitefulfill", methods=["POST"])
def invitefulfill():
    netid = auth.authenticate()
    clubid = flask.request.args.get("clubid")
    accept = flask.request.args.get("accept")
    invite_request = db.session.get(InviteRequests, (netid, clubid))
    db.session.delete(invite_request)
    db.session.commit()
    if accept == "1":
        new_club_member = ClubMembersModel(clubid, netid, False)
        db.session.add(new_club_member)
        db.session.commit()
    return flask.redirect("/my-invites")


@app.route("/pending-invites", methods=["GET"])
def pendinginvites():
    user = checkValidUser()
    clubid = flask.request.args.get("clubid")
    club = checkValidClub(clubid)
    invites = (
        db.session.query(UsersModel)
        .filter(UsersModel.netid == InviteRequests.netid)
        .filter(InviteRequests.clubid == clubid)
        .filter(UsersModel.is_banned == False)
        .all()
    )
    html_code = flask.render_template(
        "pending-invites.html",
        user=user,
        invites=invites,
        name=club.name,
        clubid=clubid,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/admin-console", methods=["GET"])
def adminconsole():
    user = checkValidAdmin()
    html_code = flask.render_template("admin-console.html", user=user)
    response = flask.make_response(html_code)
    return response


@app.route("/group-creation-requests", methods=["GET"])
def groupcreationrequests():
    user = checkValidAdmin()
    requests = (
        db.session.query(CreationRequests)
        .order_by(CreationRequests.name)
        .all()
    )
    html_code = flask.render_template(
        "group-creation-requests.html", user=user, requests=requests
    )
    response = flask.make_response(html_code)
    return response


@app.route("/groupfulfill", methods=["POST"])
def groupfulfill():
    reqid = flask.request.args.get("reqid")
    creator_netid = flask.request.args.get("netid")
    accept = flask.request.args.get("accept")
    created_club = db.session.get(CreationRequests, reqid)
    if accept == "0":
        db.session.delete(created_club)
        db.session.commit()
        return flask.redirect("/group-creation-requests")
    recent_club = (
        db.session.query(ClubsModel)
        .order_by(ClubsModel.clubid.desc())
        .first()
    )
    clubid = 0
    if recent_club is not None:
        clubid = recent_club.clubid + 1
    name = created_club.name
    share_phone = created_club.share_phone
    share_socials = created_club.share_socials
    public = created_club.public
    new_club = ClubsModel(
        clubid, name, public, share_phone, share_socials
    )
    new_club_member = ClubMembersModel(clubid, creator_netid, True)
    db.session.add(new_club)
    db.session.add(new_club_member)
    db.session.commit()
    db.session.delete(created_club)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect("/group-creation-requests")


@app.route("/group-removal", methods=["GET"])
def groupremoval():
    user = checkValidAdmin()
    groups = (
        db.session.query(ClubsModel.clubid, ClubsModel.name)
        .order_by(ClubsModel.name)
        .all()
    )
    html_code = flask.render_template(
        "group-removal.html", user=user, groups=groups
    )
    response = flask.make_response(html_code)
    return response


@app.route("/removegroup", methods=["POST"])
def removegroup():
    clubid = flask.request.args.get("clubid")
    while True:
        member = (
            db.session.query(ClubMembersModel)
            .filter(ClubMembersModel.clubid == clubid)
            .first()
        )
        joinreq = (
            db.session.query(JoinRequests)
            .filter(JoinRequests.clubid == clubid)
            .first()
        )
        invitereq = (
            db.session.query(InviteRequests)
            .filter(InviteRequests.clubid == clubid)
            .first()
        )
        if member is None and joinreq is None and invitereq is None:
            break
        if member is not None:
            db.session.delete(member)
        if joinreq is not None:
            db.session.delete(joinreq)
        if invitereq is not None:
            db.session.delete(invitereq)
        db.session.commit()
    club = db.session.get(ClubsModel, clubid)
    db.session.delete(club)
    db.session.commit()
    return flask.redirect("/group-removal")


@app.route("/ban-user", methods=["GET"])
def banuser():
    user = checkValidAdmin()
    html_code = flask.render_template("ban-user.html", user=user)
    response = flask.make_response(html_code)
    return response


@app.route("/banuserpost", methods=["POST"])
def banuserpost():
    banned_netid = flask.request.form["netid"]
    user = db.session.get(UsersModel, banned_netid)
    if user is None:
        return flask.redirect(
            flask.url_for("adminnetiderror"), code=307
        )
    if user.is_admin:
        return flask.redirect(
            flask.url_for("adminnetiderror"), code=307
        )
    user.is_banned = True
    db.session.add(user)
    db.session.commit()
    return flask.redirect("/admin-console")


@app.route("/admin-upgrade", methods=["GET"])
def adminupgrade():
    user = checkValidAdmin()
    html_code = flask.render_template("admin-upgrade.html", user=user)
    response = flask.make_response(html_code)
    return response


@app.route("/adminupgradepost", methods=["POST"])
def adminupgradepost():
    upgraded_netid = flask.request.form["netid"]
    user = db.session.get(UsersModel, upgraded_netid)
    if user is None:
        return flask.redirect(
            flask.url_for("adminnetiderror"), code=307
        )
    user.is_admin = True
    db.session.add(user)
    db.session.commit()
    return flask.redirect("/admin-console")


@app.route("/admin-netid-error", methods=["POST"])
def adminnetiderror():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    html_code = flask.render_template(
        "admin-netid-error.html", user=user
    )
    response = flask.make_response(html_code)
    return response


@app.route("/banned", methods=["GET"])
def banned():
    netid = auth.authenticate()
    user = db.session.get(UsersModel, netid)
    if not user.is_banned:
        return flask.redirect("/index")
    html_code = flask.render_template("banned.html")
    response = flask.make_response(html_code)
    return response


@app.route("/banned-users", methods=["GET"])
def bannedusers():
    user = checkValidAdmin()
    banned_users = (
        db.session.query(UsersModel)
        .filter(UsersModel.is_banned == True)
        .order_by(UsersModel.first_name)
        .all()
    )
    html_code = flask.render_template(
        "banned-users.html", user=user, banned_users=banned_users
    )
    response = flask.make_response(html_code)
    return response


@app.route("/unbanuserpost", methods=["POST"])
def unbanuserpost():
    unbanned_netid = flask.request.args.get("netid")
    banned_user = db.session.get(UsersModel, unbanned_netid)
    banned_user.is_banned = False
    db.session.add(banned_user)
    db.session.commit()
    return flask.redirect("/banned-users")


@app.route("/users", methods=["GET"])
def users():
    user = checkValidUser()

    # get the string that user searched and current page number
    search_string = flask.request.args.get("search")
    if not search_string:
        search_string = ""
    page_number = flask.request.args.get("page")
    if not page_number:
        page_number = 0

    # get all users and their information
    users = (
        db.session.query(UsersModel)
        .filter(UsersModel.is_banned == False)
        .order_by(UsersModel.netid)
        .all()
    )

    # if the search string is not empty, find users whose names or netids
    # contain the desired search string
    if search_string:
        lowercase = search_string.lower()
        print(lowercase)
        users = (
            db.session.query(UsersModel)
            .filter(
                (UsersModel.netid.ilike("%" + lowercase + "%"))
                | (UsersModel.display_name.ilike("%" + lowercase + "%"))
                | (
                    (
                        UsersModel.first_name
                        + " "
                        + UsersModel.last_name
                    ).ilike("%" + lowercase + "%")
                )
            )
            .filter(UsersModel.is_banned == False)
            .order_by(UsersModel.netid)
            .all()
        )

    # split users up into pages of 50. Each page is split into lists of 10.
    # Later on, allow user to select number of results per page.
    chunked = list(mit.chunked(users, 50))
    users_pages = []
    for page in chunked:
        users_pages.append(list(mit.chunked(page, 10)))

    html_code = flask.render_template(
        "users.html",
        user=user,
        users_pages=users_pages,
        max_pages=len(users_pages),
        page_number=int(page_number),
        search_string=search_string,
    )
    response = flask.make_response(html_code)
    return response


@app.route("/refresh-database", methods=["POST"])
def refreshdatabase():
    # clear database
    db.session.query(UndergraduatesModel).delete()

    req = req_lib.ReqLib()

    class2023 = req.getJSON(
        req.configs.GROUPS, name="Undergraduate Class of 2023"
    )
    class2024 = req.getJSON(
        req.configs.GROUPS, name="Undergraduate Class of 2024"
    )
    class2025 = req.getJSON(
        req.configs.GROUPS, name="Undergraduate Class of 2025"
    )

    # class of 2026 has no members right now
    # class2026 = req.getJSON(req.configs.GROUPS, name="Undergraduate Class of 2026")

    def get_uid(member):
        return member.split(",")[0][3:]

    for member in class2023[0]["member"]:
        uid = get_uid(member)
        undergraduate = UndergraduatesModel(uid, 2023)
        db.session.add(undergraduate)

    for member in class2024[0]["member"]:
        uid = get_uid(member)
        undergraduate = UndergraduatesModel(uid, 2024)
        db.session.add(undergraduate)

    for member in class2025[0]["member"]:
        uid = get_uid(member)
        undergraduate = UndergraduatesModel(uid, 2025)
        db.session.add(undergraduate)

    # for member in class2026[0]['member']:
    #     uid = get_uid(member)
    #     undergraduate = UndergraduatesModel(uid, 2026)
    #     db.session.add(undergraduate)

    db.session.commit()
    return flask.redirect("/index")


## Profile Update Route
@app.route("/my-contacts", methods=["GET"])
def mycontacts():
    user = checkValidUser()

    clubids = db.session.query(ClubMembersModel.clubid).filter(
        ClubMembersModel.netid == user.netid
    )

    contacts = (
        db.session.query(UsersModel)
        .filter(ClubMembersModel.netid != user.netid)
        .filter(UsersModel.netid == ClubMembersModel.netid)
        .filter(ClubMembersModel.clubid.in_(clubids))
        .filter(UsersModel.is_banned == False)
        .order_by(UsersModel.first_name)
        .all()
    )

    html_code = flask.render_template(
        "my-contacts.html", user=user, contacts=contacts
    )
    response = flask.make_response(html_code)
    return response
