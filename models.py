from app import db

## Model for users in the database
class UsersModel(db.Model):
    __tablename__ = "users"

    netid = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    display_name = db.Column(db.String)
    phone = db.Column(db.String)
    instagram = db.Column(db.String)
    snapchat = db.Column(db.String)
    email = db.Column(db.String)
    is_admin = db.Column(db.Boolean)
    is_banned = db.Column(db.Boolean)
    photo = db.Column(db.String)
    first_time = db.Column(db.Boolean)

    def __init__(
        self,
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
        first_time,
    ):
        self.netid = netid
        self.first_name = first_name
        self.last_name = last_name
        self.display_name = display_name
        self.phone = phone
        self.instagram = instagram
        self.snapchat = snapchat
        self.email = email
        self.is_admin = is_admin
        self.is_banned = is_banned
        self.photo = photo
        self.first_time = first_time


## Models for clubs in the database
class ClubsModel(db.Model):
    __tablename__ = "clubs"

    clubid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    public = db.Column(db.Boolean)
    share_phone = db.Column(db.Boolean)
    share_socials = db.Column(db.Boolean)

    def __init__(
        self, clubid, name, public, share_phone, share_socials
    ):
        self.clubid = clubid
        self.name = name
        self.public = public
        self.share_phone = share_phone
        self.share_socials = share_socials


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

    netid = db.Column(db.String, primary_key=True)
    clubid = db.Column(db.Integer, primary_key=True)

    def __init__(self, netid, clubid):
        self.netid = netid
        self.clubid = clubid


## Model for club creation requests in database
class CreationRequests(db.Model):
    __tablename__ = "creationreqs"

    reqid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    netid = db.Column(db.String)
    public = db.Column(db.Boolean)
    share_phone = db.Column(db.Boolean)
    share_socials = db.Column(db.Boolean)

    def __init__(
        self, reqid, name, netid, public, share_phone, share_socials
    ):
        self.reqid = reqid
        self.name = name
        self.netid = netid
        self.public = public
        self.share_phone = share_phone
        self.share_socials = share_socials


## Model for undergrads
class UndergraduatesModel(db.Model):
    __tablename__ = "allundergrads"

    netid = db.Column(db.String, primary_key=True)
    classyear = db.Column(db.Integer, primary_key=True)

    def __init__(self, netid, classyear):
        self.netid = netid
        self.classyear = classyear
