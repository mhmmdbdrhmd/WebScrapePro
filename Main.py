import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import time

# Function to handle the Selenium interactions
def process_data_row(data_row):
    # Setup Chrome in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    try:
        # Navigate to the page
        driver.get('https://servicios.sbs.gob.pe/ReporteSituacionPrevisional/Afil_Consulta.aspx')
        
        # Fill the form with data from CSV

        driver.find_element(By.NAME, 'ctl00$ContentPlaceHolder1$txtNumeroDoc').send_keys(data_row['Document'])
        driver.find_element(By.NAME, 'ctl00$ContentPlaceHolder1$txtAp_pat').send_keys(data_row['Lastname1'])
        driver.find_element(By.NAME, 'ctl00$ContentPlaceHolder1$txtAp_mat').send_keys(data_row['Lastname2'])
        driver.find_element(By.NAME, 'ctl00$ContentPlaceHolder1$txtPri_nom').send_keys(data_row['Name1'])
        # Assume second name is optional and can be left blank
        
        # Click the search button and wait for results
        driver.find_element(By.NAME, 'ctl00$ContentPlaceHolder1$btnBuscar').click()
        wait = WebDriverWait(driver, 5)

        #Finding if there is no result
        result_element = wait.until(EC.visibility_of_element_located(
            (By.ID, 'ctl00_ContentPlaceHolder1_lblErrorTxt')))
        result_text = result_element.text
        print(data_row['Document'] + "\t" + data_row['Lastname1'] + "\t" + data_row['Lastname2'] + "\t" + data_row['Name1'] +' : '+ result_text)
        
    except Exception as e:
        try: #Finding if there is a section called Active (or so in french)

            result_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/form/div[3]/div/div[1]/table[2]/tbody/tr[6]/td/div/table/tbody/tr[3]/td/div'))
            )
            result_text = "Active"
            print(data_row['Document'] + "\t" + data_row['Lastname1'] + "\t" + data_row['Lastname2'] + "\t" + data_row['Name1'] +' : '+ result_text)
        except TimeoutException: # Other errors, most likely timing out.

            print(f"{data_row['Document']}\t{data_row['Lastname1']}\t{data_row['Lastname2']}\t{data_row['Name1']} : Error")
            # Log the failed row and the error message
            failed_rows.append(data_row)

    finally: #Exiting the drive
        driver.quit()
#Read data from CSV
data_to_process = []

with open('data.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data_to_process.append(row)

#will be used to log errors
failed_rows = []

# Use ThreadPoolExecutor to run Selenium in parallel threads
with ThreadPoolExecutor(max_workers=20) as executor:  # Adjust the number of workers as needed
    executor.map(process_data_row, data_to_process)

print(len(failed_rows))