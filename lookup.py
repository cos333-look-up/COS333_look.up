import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = flask.Flask(__name__, template_folder=".")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
db = SQLAlchemy(app)
migrate = Migrate(app, db)


## Figure out how to store this with CAS or something else
netid = "netid"


## Index Route
@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    ##data = fetch_data(netid)
    data = fetch_data(netid)
    # If no data is associated with the user, they are redirected
    # to create a profile
    if data is None:
        print("Here")
        return flask.redirect(flask.url_for("profilecreation"))
    # Otherwise index is loaded with their clubs
    else:
        html_code = flask.render_template(
            "index.html"  ##, friends=data["friends"], clubs=data["clubs"]
        )
        response = flask.make_response(html_code)
        return response


## Profile Creation Route
@app.route("/profilecreation", methods=["GET"])
def profilecreation():
    # Only needs to render the form
    return flask.render_template("profilecreation.html")


## Profile Posting Route
@app.route("/profilepost", methods=["GET"])
def profilepost():
    # Get all important pieces of the form and turn them into
    # a data set
    ## ADD MORE AS NEEDED
    fname = flask.request.args.get("fname")
    lname = flask.request.args.get("lname")
    phone = flask.request.args.get("phone")
    email = flask.request.args.get("email")
    instagram = flask.request.args.get("instagram")
    snapchat = flask.request.args.get("snapchat")
    data = {
        "netid": netid,
        "is_admin": False,
        "first_name": fname,
        "last_name": lname,
        "phone": phone,
        "email": email,
        "instagram": instagram,
        "snapchat": snapchat,
    }
    # Input the data set attached to the netid into the DB
    input_data(data)
    # Redirect to index for loading the user's new page
    return flask.redirect(flask.url_for("index"))
