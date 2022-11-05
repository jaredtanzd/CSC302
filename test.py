from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
options = [
"--headless",
"--disable-gpu",
"--window-size=1920,1200",
"--ignore-certificate-errors",
"--disable-extensions",
"--no-sandbox",
"--disable-dev-shm-usage"
]

for option in options:
    chrome_options.add_argument(option)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("http://0.0.0.0:8050/")
element = WebDriverWait(driver, 2).until(
    EC.presence_of_element_located((By.ID, "voted-input"))
)

#_______________________________________________________ test 1 for correct input _______________________________________________________

votes = driver.find_element(By.ID, "voted-input")
imdb_score = driver.find_element(By.ID, "imdb-input")
critics = driver.find_element(By.ID, "critic-input")
budget = driver.find_element(By.ID, "budget-input")

# fill the elements
votes.send_keys("10")
imdb_score.send_keys("8")
critics.send_keys("100")
budget.send_keys("100000")

#drop down menu
WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Select a genre')]"))).click()
WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Family')]"))).click()


#submit button
select = driver.find_element(By.ID, "submit-button")
select.click()

#idle for 5 seconds
driver.implicitly_wait(5)

labels = driver.find_elements(By.XPATH, "//*[@class='dash-debug-error-count']")
for label in labels:
    assert label.text != "🛑 1" , "Test 1 correct input failed"


driver.refresh()
#_______________________________________________________ test 2 for null input _______________________________________________________

# locate the elements to fill
votes = driver.find_element(By.ID, "voted-input")
imdb_score = driver.find_element(By.ID, "imdb-input")
critics = driver.find_element(By.ID, "critic-input")
budget = driver.find_element(By.ID, "budget-input")

# fill the elements
votes.send_keys("")
imdb_score.send_keys("8")
critics.send_keys("100")
budget.send_keys("100000")

#drop down menu
WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Select a genre')]"))).click()
WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Family')]"))).click()


#submit button
select = driver.find_element(By.ID, "submit-button")
select.click()

#idle for 5 seconds
driver.implicitly_wait(5)

labels = driver.find_elements(By.XPATH, "//*[@class='dash-debug-error-count']")

for label in labels:
    assert label.text == "🛑 1" , "Test 2 null failed"

driver.refresh()
#_______________________________________________________ test 3 for string input _______________________________________________________
# locate the elements to fill

votes = driver.find_element(By.ID, "voted-input")
imdb_score = driver.find_element(By.ID, "imdb-input")
critics = driver.find_element(By.ID, "critic-input")
budget = driver.find_element(By.ID, "budget-input")

# fill the elements
votes.send_keys("asdf")
imdb_score.send_keys("8")
critics.send_keys("100")
budget.send_keys("100000")

#drop down menu
WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Select a genre')]"))).click()
WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Family')]"))).click()


#submit button
select = driver.find_element(By.ID, "submit-button")
select.click()

#idle for 5 seconds
driver.implicitly_wait(5)

labels = driver.find_elements(By.XPATH, "//*[@class='dash-debug-error-count']")

for label in labels:
    assert label.text == "🛑 1" , "Test 3: string input error failed"

print("All tests passed")