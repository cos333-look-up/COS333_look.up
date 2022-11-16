import sqlalchemy

engine = sqlalchemy.create_engine("postgresql+psycopg2://stwiezab:eN4T8unVzyIE49TzhKCbf1m5lKkGhjWU@peanut.db.elephantsql.com/stwiezab")

with engine.connect() as connection:
  result = connection.execute(sqlalchemy.text("SELECT * FROM allundergrads"))
  for row in result:
    print(row[0])
