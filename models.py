from app import db

## Model for users in the database
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


## Models for clubs in the database
class ClubsModel(db.Model):
    __tablename__ = "clubs"

    clubid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    info_shared = db.Column(db.String)
    # info_shared = db.Column(db.LargeBinary)

    def __init__(self, clubid, name, description, info_shared):
        self.clubid = clubid
        self.name = name
        self.description = description
        self.info_shared = info_shared


## Model for club member requests in database
class ClubMembersModel(db.Model):
    __tablename__ = "clubmembers"

    netid = db.Column(db.String, primary_key=True)
    clubid = db.Column(db.Integer, primary_key=True)
    is_moderator = db.Column(db.Boolean)

    def __init__(self, clubid, netid, is_moderator):
        self.clubid = clubid
        self.netid = netid
        self.is_moderator = is_moderator


## Model for club join requests in database
class JoinRequests(db.Model):
    __tablename__ = "joinreqs"

    netid = db.Column(db.String, primary_key=True)
    clubid = db.Column(db.Integer, primary_key=True)

    def __init__(self, netid, clubid):
        self.netid = netid
        self.clubid = clubid


## Model for club invite requests in database
class InviteRequests(db.Model):
    __tablename__ = "invitereqs"

    invitee_netid = db.Column(db.String, primary_key=True)
    clubid = db.Column(db.Integer, primary_key=True)

    def __init__(self, invitee_netid, clubid):
        self.invitee_netid = invitee_netid
        self.clubid = clubid


## Model for club creation requests in database
class CreationRequests(db.Model):
    __tablename__ = "creationreqs"

    netid = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    info_shared = db.Column(db.String)
    # info_shared = db.Column(db.LargeBinary)

    def __init__(self, name, netid, description, info_shared):
        self.name = name
        self.netid = netid
        self.description = description
        # for key, value in info_shared.items():
        #    exec(f'self.{key} = {value}')
        self.info_shared = info_shared
