from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import json

# Google Sheets Setup
SHEET_NAME = "Mensa_Menu"  # Change this to your sheet name
CREDENTIALS_FILE = "credentials.json"  # Ensure you have this file in the same directory

def authenticate_google_sheets():
    """Authenticate and connect to Google Sheets API."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    return client

def scrape_mensaar():
    url = "https://mensaar.de/#/menu/sb"
    driver = None
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Set up the Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(url)
        print("Page loaded. Waiting for content...")

        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "counter"))
        )

        # Extract date
        date_element = driver.find_element(By.CSS_SELECTOR, ".cursor-pointer.active.list-group-item")
        menu_date = date_element.text.strip()
        print(f"Menu date: {menu_date}")

        # Extract meals by counter titles
        meal_data = []

        counters = driver.find_elements(By.CLASS_NAME, "counter")

        for counter in counters:
            counter_title = counter.find_element(By.CLASS_NAME, "counter-title").text.strip()
            
            # Filter for specified counter titles
            if counter_title in ["Menü 1", "Menü 2", "Mensacafé"]:
                meal_elements = counter.find_elements(By.CLASS_NAME, "meal")
                
                for meal in meal_elements:
                    meal_title = meal.find_element(By.CLASS_NAME, "meal-title").text.strip()

                    # Gather components for each meal
                    component_elements = meal.find_elements(By.CLASS_NAME, "component")
                    components = [component.find_element(By.CLASS_NAME, "component-name").text.strip()
                                  for component in component_elements]

                    # Append meal details
                    meal_data.append([menu_date, counter_title, meal_title, ", ".join(components)])

        # Save to Google Sheets
        save_to_google_sheets(meal_data)

    except Exception as e:
        print(f"Error scraping menu: {e}")
    
    finally:
        if driver:
            driver.quit()

def save_to_google_sheets(meal_data):
    """Save meal data to Google Sheets."""
    client = authenticate_google_sheets()
    sheet = client.open(SHEET_NAME).sheet1  # Open first sheet

    # Add column headers if the sheet is empty
    if not sheet.get_all_values():
        sheet.append_row(["Date", "Counter", "Meal", "Components"])

    # Append new data
    for row in meal_data:
        sheet.append_row(row)

    print(f"Data saved to Google Sheets: {SHEET_NAME}")

if __name__ == "__main__":
    scrape_mensaar()