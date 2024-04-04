from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

# Set Chrome options
chrome_options = webdriver.ChromeOptions()

# Uncomment the line below if you want to run Chrome in headless mode (without opening a visible browser window)
# chrome_options.add_argument("--headless")

# Start a new browser session
driver = webdriver.Chrome(options=chrome_options)

# URL of the webpage you want to automate
url = 'http://127.0.0.1:5000'

# Open the webpage
driver.get(url)

# Wait for the page to load
time.sleep(1)


# Loop from 50 to 70
# Click on the Courses link in the header
courses_link = driver.find_element(By.XPATH, '//a[@href="/classrooms"]')
courses_link.click()

# Wait for the page to load
time.sleep(1)

for subject_number in range(120, 128):

    # Click on the Add Classroom button
    add_classroom_button = driver.find_element(By.XPATH, '//a[@href="/classroom_form"]')
    add_classroom_button.click()

    # Wait for the page to load
    time.sleep(1)

    # Generate classroom name based on the loop iteration
    classroom_name = "Sala Name " + str(subject_number)

    # Generate a random number between 30 and 40 for classroom capacity
    classroom_capacity = random.randint(30, 75)

    # Fill in the classroom name input field
    classroom_name_input = driver.find_element(By.ID, 'classroom_name')
    classroom_name_input.clear()
    classroom_name_input.send_keys(classroom_name)

    # Fill in the classroom capacity input field
    classroom_capacity_input = driver.find_element(By.ID, 'classroom_capacity')
    classroom_capacity_input.clear()
    classroom_capacity_input.send_keys(str(classroom_capacity))

    # Click on the Submit button
    submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
    submit_button.click()

    # Wait for the page to load
    time.sleep(1)

# Close the browser session
driver.quit()

