import sqlalchemy
from api import req_lib

engine = sqlalchemy.create_engine("postgresql+psycopg2://stwiezab:eN4T8unVzyIE49TzhKCbf1m5lKkGhjWU@peanut.db.elephantsql.com/stwiezab")
metadata = sqlalchemy.MetaData(bind=engine)
sqlalchemy.MetaData.reflect(metadata)

users_table = metadata.tables['users']

with engine.connect() as connection:
  connection.execute("GRANT ALL PRIVILEGES ON TABLE users to stwiezab;")
  result = connection.execute(sqlalchemy.text("SELECT netid FROM users"))
  req = req_lib.ReqLib()

  for row in result:
    netid = row[0]
    def get_first_last(names):
      if len(names) == 2:
        return names[0], names[1]
      else:
        return names[0], names[2]

    names = req.getJSON(
    req.configs.USERS_BASIC,
    uid=netid,
    )
    if names:
      email = names[0]['mail'].lower()
      print(email)
      connection.execute(sqlalchemy.update(users_table)
        .values(email=email)
        .where(users_table.c.netid == netid))

  print('All emails updated!')
