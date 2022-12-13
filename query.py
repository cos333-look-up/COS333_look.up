import sqlalchemy
from api import req_lib
import json

# USERS TABLE
USERS_NETID = 0
USERS_ISADMIN = 1
USERS_FIRST_NAME = 2
USERS_LAST_NAME = 3
USERS_PHOTO = 4
USERS_PHONE = 5
USERS_INSTAGRAM = 6
USERS_SNAPCHAT = 7
USERS_IS_BANNED = 8
USERS_DISPLAY_NAME = 9
USERS_EMAIL = 10
USERS_FIRST_TIME = 11

def get_names(display_name):
  first_name, last_name = '', ''
  if display_name:
    name_parts = display_name.split(' ')
    first_name = name_parts[0]
    if len(name_parts) == 2:
      last_name = name_parts[1]
    elif len(name_parts) == 3:
      last_name = name_parts[2]
    else:
      if len(name_parts[1]) == 2:
        last_name = " ".join(name_parts[2:])
      else:
        first_name = " ".join(name_parts[:2])
        last_name = name_parts[-1:]
  return first_name, last_name


def main():
  engine = sqlalchemy.create_engine("postgresql+psycopg2://stwiezab:eN4T8unVzyIE49TzhKCbf1m5lKkGhjWU@peanut.db.elephantsql.com/stwiezab")
  metadata = sqlalchemy.MetaData(bind=engine)
  sqlalchemy.MetaData.reflect(metadata)
  users_table = metadata.tables['users']

  with engine.connect() as connection:
    stmt = "SELECT * FROM users WHERE users.first_name IS NULL"
    result = connection.execute(sqlalchemy.text(stmt))

    for row in result:
      netid = row[USERS_NETID]
      display_name = row[USERS_DISPLAY_NAME]
      first_name, last_name = get_names(display_name)

      # UPDATE QUERY: COMMENT AS NEEDED
      connection.execute(sqlalchemy.update(users_table)
        .where(users_table.c.netid == netid)
        .values(
            first_name=first_name,
            last_name=last_name
        ))

      print('Netid: {}'.format(netid))
      print('First name updated to {}'.format(first_name))
      print('Last name updated to {}'.format(last_name))
      print()
      
    print('All done!')

if __name__ == '__main__':
  main()