import flask
import db_edit

app = flask.Flask(__name__, template_folder=".")

## Figure out how to store this with CAS or something else
netid = "netid"

## Fetching data from DB (probably a function in a separate file)
def fetch_data(netid):
    # Do something with DB to fetch profile or return None if
    # no profile exists yet
    pass


## Inputs data into the DB (probably a function in a separate file)
def input_data(netid, data):
    # Add a new profile to the db with the associated data
    # and netid
    pass


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
