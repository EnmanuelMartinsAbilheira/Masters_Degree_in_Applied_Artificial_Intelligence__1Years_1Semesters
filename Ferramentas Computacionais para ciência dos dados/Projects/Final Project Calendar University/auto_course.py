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
for subject_number in range(111, 121):
    # Click on the Courses link in the header
    courses_link = driver.find_element(By.XPATH, '//a[@href="/classes"]')
    courses_link.click()

    # Wait for the page to load
    time.sleep(2)

    # Click on the Add Course button
    add_course_button = driver.find_element(By.XPATH, '//a[@href="/add_course"]')
    add_course_button.click()

    # Wait for the page to load
    time.sleep(1)

    # Enter course name
    course_name_input = driver.find_element(By.ID, 'course_name')
    course_name_input.clear()
    course_name_input.send_keys("Diciplina " + str(subject_number))

    # Press tab to move to the next input
    course_name_input.send_keys(Keys.TAB)

    # Enter number for the next input
    next_input = driver.switch_to.active_element
            # Generate a random number between 20 and 35 for enrolled students
    diciplinas = random.randint(4, 7)
    next_input.send_keys(diciplinas)

    # Wait for the Save button to be clickable
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="Submit"]'))
    )
    submit_button.click()

    # Wait for the page to load
    time.sleep(1)

    # Find all input elements for subjects
    subject_name_inputs = driver.find_elements(By.XPATH, '//input[starts-with(@id, "subjects-") and contains(@id, "-sub_name")]')
    teacher_inputs = driver.find_elements(By.XPATH, '//input[starts-with(@id, "subjects-") and contains(@id, "-teacher")]')
    enrolled_students_inputs = driver.find_elements(By.XPATH, '//input[starts-with(@id, "subjects-") and contains(@id, "-enrolled_students")]')
    min_days_classes_inputs = driver.find_elements(By.XPATH, '//input[starts-with(@id, "subjects-") and contains(@id, "-min_days_classes")]')
    max_days_classes_inputs = driver.find_elements(By.XPATH, '//input[starts-with(@id, "subjects-") and contains(@id, "-max_days_classes")]')
    min_classes_per_week_inputs = driver.find_elements(By.XPATH, '//input[starts-with(@id, "subjects-") and contains(@id, "-min_classes_per_week")]')
    max_classes_per_week_inputs = driver.find_elements(By.XPATH, '//input[starts-with(@id, "subjects-") and contains(@id, "-max_classes_per_week")]')



    # Input text and numbers for each subject
    for i in range(diciplinas):  # Assuming you need to input for 7 subjects
        subject_name_inputs[i].send_keys("Diciplina " + str(subject_number) + "-! " + str(i+1))
        teacher_inputs[i].send_keys("Teacher Diciplina " + str(subject_number) + "_ " + str(i+1))
        
        # Generate a random number between 20 and 35 for enrolled students
        enrolled_students = random.randint(20, 35)
        enrolled_students_inputs[i].send_keys(str(enrolled_students))
        
        min_days_classes_inputs[i].send_keys(str(1))
        max_days_classes_inputs[i].send_keys(str(2))
        min_classes_per_week_inputs[i].send_keys(str(1))
        max_classes_per_week_inputs[i].send_keys(str(2))


    # Click on the Save button
    save_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
    save_button.click()

    # Wait for the page to load
    time.sleep(1)

    # Fill the input fields with the specified numbers
    min_blocks_per_day_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'min_blocks_per_day'))
    )
    max_blocks_per_day_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'max_blocks_per_day'))
    )
    min_days_of_classes_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'min_days_of_classes'))
    )
    max_days_of_classes_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'max_days_of_classes'))
    )
    max_blocks_per_week_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'max_blocks_per_week'))
    )
    min_blocks_per_period_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'min_blocks_per_period'))
    )

    # Fill the input fields with the specified numbers
    min_blocks_per_day_input.send_keys("1")
    max_blocks_per_day_input.send_keys("4")
    min_days_of_classes_input.send_keys("1")
    max_days_of_classes_input.send_keys("4")
    max_blocks_per_week_input.send_keys("20")
    min_blocks_per_period_input.send_keys("1")

    # Click on the Submit button
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="Submit"]'))
    )
    submit_button.click()

    # Wait for the page to load
    time.sleep(1)

# Close the browser session
driver.quit()



