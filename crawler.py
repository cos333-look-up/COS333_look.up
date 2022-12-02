from re import A
from scipy.fftpack import idctn
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import sqlalchemy
import cloudinary
import requests
import os

cloudinary.config(
    cloud_name="dqv7e2cyi",
    api_key="244334546783172",
    api_secret="P-0gM5gXEWHk7UCcQr1xIav3pQg",
)
import cloudinary.uploader
import cloudinary.api

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
    queryResult = connection.execute(sqlalchemy.text(stmt))

    input = driver.find_element("tag name","input")
    input.clear()
    input.send_keys(netid)
    # print("Input complete")
    submit = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/div/div/span/button')
    submit.click()
    time.sleep(2)
    try:
      picture = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[3]/div/div/div[2]/ul/li/div[1]/img').get_attribute('src')
      print(picture)

      # download picture and then upload to cloudinary
      open('test.txt', 'wb').close()
      img_data = requests.get(picture).content
      with open('temp.jpg', 'wb') as handler:
          handler.write(img_data)

      cloudinary_photo = cloudinary.uploader.upload(
        'temp.jpg', public_id=netid
      )["url"]

      print(cloudinary_photo)
      update = sqlalchemy.update(users_table).where(users_table.c.netid == netid).values({"photo": cloudinary_photo})
      connection.execute(update)
      # print("Made it here!")
    except Exception as ex:
      print(ex)
      continue

  print("All done, congratulations!")