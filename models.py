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
    # Possible to make info_shared a collection of boolean columns?
    # Would help for modularity and readability
    # Could keep it as a string - would need to encode/decode
    # Could have a boolean var for each attribute also
    # More generally, store information everywhere as a list or as separate vars?
    info_shared = db.Column(db.String)

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

    joinid = db.Column(db.Integer, primary_key=True)
    clubid = db.Column(db.Integer)
    netid = db.Column(db.Integer)

    def __init__(self, joinid, clubid, netid):
        self.joinid = joinid
        self.clubid = clubid
        self.netid = netid

## Model for club creation requests in database
class CreationRequests(db.Model):
    __tablename__ = "creationreqs"

    createid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    netid = db.Column(db.Integer)
    description = db.Column(db.String)
    info_shared = db.Column(db.String)

    def __init__(self, createid, name, netid, description, info_shared):
        self.createid = createid
        self.name = name
        self.netid = netid
        self.description = description
        self.info_shared = info_shared
