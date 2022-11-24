from re import A
from scipy.fftpack import idctn
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import sqlalchemy

engine = sqlalchemy.create_engine("postgresql+psycopg2://stwiezab:eN4T8unVzyIE49TzhKCbf1m5lKkGhjWU@peanut.db.elephantsql.com/stwiezab")
metadata = sqlalchemy.MetaData(bind=engine)
sqlalchemy.MetaData.reflect(metadata)
users_table = metadata.tables['users']

netids = []
with engine.connect() as connection:
  result = connection.execute(sqlalchemy.text("SELECT * FROM allundergrads"))
  for row in result:
    netids.append(row[0])
    
  driver = webdriver.Chrome(ChromeDriverManager().install())

  driver.get("https://collface.deptcpanel.princeton.edu/")
  print("Sleeping now")
  time.sleep(25)
  print("Done sleeping")

  for netid in netids:
    # check if an existing user has a photo already
    # print("netid: " + netid)
    stmt = "SELECT users.photo FROM users WHERE users.netid='" + netid + "'"
    # connection.execute(sqlalchemy.insert(users_table).values(netid="dh37", photo=None))
    queryResult = connection.execute(sqlalchemy.text(stmt))
    print(queryResult)
    

    user_photo = queryResult.first()
    # print("user photo", user_photo)
    if not user_photo:
      input = driver.find_element("tag name","input")
      input.clear()
      input.send_keys(netid)
      # print("Input complete")
      submit = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/div/div/span/button')
      submit.click()
      time.sleep(1)
      try:
        picture = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[3]/div/div/div[2]/ul/li/div[1]/img').get_attribute('src')
        print(picture)

        connection.execute(sqlalchemy.insert(users_table).values(netid=netid, photo=picture))
      except:
        continue
  
  print("All done, congratulations!")
    # driver.quit()