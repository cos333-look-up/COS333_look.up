import sqlalchemy
from api import req_lib
import json

engine = sqlalchemy.create_engine("postgresql+psycopg2://stwiezab:eN4T8unVzyIE49TzhKCbf1m5lKkGhjWU@peanut.db.elephantsql.com/stwiezab")
metadata = sqlalchemy.MetaData(bind=engine)
sqlalchemy.MetaData.reflect(metadata)

users_table = metadata.tables['users']

with engine.connect() as connection:
  req = req_lib.ReqLib()
  stmt = "SELECT * FROM users WHERE users.display_name IS NULL"
  result = connection.execute(sqlalchemy.text(stmt))

  for row in result:
    netid = row[0]
    result = req.getJSON(req.configs.USERS_FULL, uid=netid)
    if result:
      display_name = result[0]['displayname']
      print(display_name)
      connection.execute(sqlalchemy.update(users_table)
        .where(users_table.c.netid == netid)
        .values(
            is_admin=False,
            is_banned=False,
            display_name=display_name
        ))
  print('All done!')
