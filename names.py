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
      full_name = names[0]['displayname'].split(' ')
      first_name, last_name = get_first_last(full_name)
      print(first_name, last_name)
      connection.execute(sqlalchemy.update(users_table)
        .values(first_name=first_name, last_name=last_name)
        .where(users_table.c.netid == netid))

  print('All names updated!')
