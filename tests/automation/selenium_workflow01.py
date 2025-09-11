# Example Selenium automation for your Flask app

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()  # Or use webdriver.Firefox()

loginUser = "lomithadj"
loginPassword = "12345678"
invitee1 = "pasi"
invitee2 = "nuwan"

# 1. Go to login page
driver.get("http://localhost:5000/login")

# 2. Login
driver.find_element(By.NAME, "username").send_keys(loginUser)
driver.find_element(By.NAME, "password").send_keys(loginPassword) 
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
time.sleep(2)

# 3. Create a new project
driver.find_element(By.NAME, "name").send_keys("Selenium Project")
driver.find_element(By.CSS_SELECTOR, "form[action='/project/create'] button[type='submit']").click()
time.sleep(2)

# 4. Go to the newly created project detail page
# Find the project link by name
project_links = driver.find_elements(By.LINK_TEXT, "Selenium Project")
project_links[0].click()
time.sleep(2)

# 5. Invite two users
for username in [invitee1, invitee2]:  # Replace with actual usernames
    invite_input = driver.find_element(By.NAME, "username")
    invite_input.clear()
    invite_input.send_keys(username)
    driver.find_element(By.CSS_SELECTOR, "form[action*='/invite'] button[type='submit']").click()
    time.sleep(10)

driver.quit()