from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

pictures = []
netids = ["dh37", "evanwang", "bpjones"]

driver = webdriver.Chrome(ChromeDriverManager().install())

driver.get("https://collface.deptcpanel.princeton.edu/")
print("Sleeping now")
time.sleep(30)
print("Done sleeping")

for netid in netids:
  input = driver.find_element("tag name","input")
  input.clear()
  input.send_keys(netid)
  print("Input complete")
  submit = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/div/div/span/button')
  submit.click()
  time.sleep(2)
  picture = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[3]/div/div/div[2]/ul/li/div[1]/img').get_attribute('src')
  print(picture)
  pictures.append(picture)

print(pictures)
# driver.quit()