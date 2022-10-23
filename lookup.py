import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = flask.Flask(__name__, template_folder=".")
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://wglelrtk:p-x6cIocX3JJNBIG0En7UiGVUvUfYFi4@lucky.db.elephantsql.com/wglelrtk"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class UsersModel(db.Model):
    __tablename__ = "users"

    netid = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    phone = db.Column(db.String)
    instagram = db.Column(db.String)
    snapchat = db.Column(db.String)
    is_admin = db.Column(db.Boolean)
    photo = db.Column(db.String)

    def __init__(
        self,
        netid,
        first_name,
        last_name,
        phone,
        instagram,
        snapchat,
        is_admin,
        photo,
    ):
        self.netid = netid
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.instagram = instagram
        self.snapchat = snapchat
        self.is_admin = is_admin
        self.photo = photo

    def __repr__(self):
        return f"<Netid {self.netid}>"


class ClubsModel(db.Model):
    __tablename__ = "clubs"

    club_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    share_photo = db.Column(db.Boolean)
    share_snap = db.Column(db.Boolean)
    share_insta = db.Column(db.Boolean)

    def __init__(
        self,
        club_id,
        name,
        description,
        share_photo,
        share_snap,
        share_insta,
    ):
        self.club_id = club_id
        self.name = name
        self.description = description
        self.share_photo = share_photo
        self.share_snap = share_snap
        self.share_insta = share_insta

    def __repr__(self):
        return f"<Club Name {self.name}>"


##class ClubMembersModel(db.Model):

##class ClubJoinRequests(db.Model)

##class ClubCreationRequests(db.Model)


## Index Route
@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    # Setup data model
    netid = "denisac"
    user = db.session.get(UsersModel, netid)
    # If no data is associated with the user, they are redirected
    # to create a profile
    if user is None:
        return flask.redirect(flask.url_for("profilecreation"))
    # Otherwise index is loaded with their clubs
    else:
        html_code = flask.render_template("index.html")
        response = flask.make_response(html_code)
        return response


## Profile Creation Route
@app.route("/profilecreation", methods=["GET"])
def profilecreation():
    # Only needs to render the form
    return flask.render_template("profilecreation.html")


## Profile Update Route
@app.route("/profileupdate", methods=["GET"])
def profileupdate():
    # Only needs to render the update form
    return flask.render_template("profileupdate.html")


## Profile Posting Route
@app.route("/profilepost", methods=["GET"])
def profilepost():
    # Get all important pieces of the form and turn them into
    # a data set
    ## ADD MORE AS NEEDED
    netid = "denisac"
    first_name = flask.request.args.get("first_name")
    last_name = flask.request.args.get("last_name")
    phone = flask.request.args.get("phone")
    instagram = flask.request.args.get("instagram")
    snapchat = flask.request.args.get("snapchat")
    is_admin = False
    photo = ""
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
    ####db.session.add(new_user)
    ####db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect(flask.url_for("index"))


## Group Creation Route
@app.route("/groupcreation", methods=["GET"])
def groupcreation():
    # Only needs to render the creation form
    return flask.render_template("groupcreation.html")


@app.route("/grouppost", methods=["GET"])
def grouppost():
    name = flask.request.args.get("name")
    description = flask.request.args.get("description")
    share_phone = flask.request.args.get("share_phone")
    share_snap = flask.request.args.get("share_snap")
    share_insta = flask.request.args.get("share_insta")
    new_club = ClubsModel(
        name, description, share_phone, share_snap, share_insta
    )
    # Input the club into the DB
    ####db.session.add(new_club)
    ####db.session.commit()
