import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = flask.Flask(__name__, template_folder=".")
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://stwiezab:eN4T8unVzyIE49TzhKCbf1m5lKkGhjWU@peanut.db.elephantsql.com/stwiezab"
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

    clubid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    info_shared = db.Column(db.String)

    def __init__(self, clubid, name, description, info_shared):
        self.clubid = clubid
        self.name = name
        self.description = description
        self.info_shared = info_shared

    def __repr__(self):
        return f"<Club Name {self.name}>"


##class ClubMembersModel(db.Model):

##class JoinRequests(db.Model)

##class CreationRequests(db.Model)


## Figure out how to store this with CAS or something else


## Index Route
@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    # Setup data model
    netid = "bobdondero"
    user = db.session.get(UsersModel, netid)
    # If no data is associated with the user, they are redirected
    # to create a profile
    if user is None:
        return flask.redirect(flask.url_for("profilecreation"))
    # Otherwise index is loaded with their clubs
    else:
        print(user.first_name)
        print(user.last_name)
        print(user.instagram)
        print(user.phone)
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
@app.route("/profilepost", methods=["POST"])
def profilepost():
    # Get all important pieces of the form and turn them into
    # a data set
    ## ADD MORE AS NEEDED
    netid = flask.request.form["netid"]
    first_name = flask.request.form["first_name"]
    last_name = flask.request.form["last_name"]
    phone = flask.request.form["phone"]
    instagram = flask.request.form["instagram"]
    snapchat = flask.request.form["snapchat"]
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
    db.session.add(new_user)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect(flask.url_for("index"))


## Group Creation Route
@app.route("/groupcreation", methods=["GET"])
def groupcreation():
    # Only needs to render the creation form
    return flask.render_template("groupcreation.html")


@app.route("/grouppost", methods=["POST"])
def grouppost():
    clubid = db.session.query(ClubsModel).count() + 1
    name = flask.request.form["name"]
    description = flask.request.form["description"]
    info_shared = ""
    try:
        share_socials = flask.request.form["share_socials"]
        info_shared = "1"
    except:
        info_shared = "0"
    try:
        share_phone = flask.request.form["share_phone"]
        info_shared = info_shared + "1"
    except:
        info_shared = info_shared + "0"
    new_club = ClubsModel(clubid, name, description, info_shared)
    db.session.add(new_club)
    db.session.commit()
    # Redirect to index for loading the user's new page
    return flask.redirect(flask.url_for("index"))
