import sqlalchemy

engine = sqlalchemy.create_engine("postgresql+psycopg2://stwiezab:eN4T8unVzyIE49TzhKCbf1m5lKkGhjWU@peanut.db.elephantsql.com/stwiezab")
metadata = sqlalchemy.MetaData(bind=engine)
sqlalchemy.MetaData.reflect(metadata)

users_table = metadata.tables['users']

with engine.connect() as connection:
  result = connection.execute(sqlalchemy.text("SELECT * FROM allundergrads"))


  for row in result:
    stmt = "SELECT users.photo FROM users WHERE users.netid=" + row[0]
    has_photo = connection.execute(sqlalchemy.text(stmt))
    if has_photo == None:
      connection.execute(sqlalchemy.insert(users_table).values(netid=row[0], photo=None))
