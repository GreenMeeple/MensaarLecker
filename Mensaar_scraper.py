from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import datetime

# Google Sheets Setup
SHEET_NAME = "MensaarLecker"  # Change this to your sheet name

# German month mapping
GERMAN_MONTHS = {
    "Januar": "01", "Februar": "02", "März": "03", "April": "04",
    "Mai": "05", "Juni": "06", "Juli": "07", "August": "08",
    "September": "09", "Oktober": "10", "November": "11", "Dezember": "12"
}

def format_date(german_date):
    """
    Converts a German date format like 'Mittwoch, 25. September 2024'
    to 'YYYY-MM-DD' format.
    """
    match = re.search(r"(\d{1,2})\. (\w+) (\d{4})", german_date)
    if match:
        day, month, year = match.groups()
        month_number = GERMAN_MONTHS.get(month, "00")  # Get month number, default to "00" if not found
        return f"{year}-{month_number}-{int(day):02d}"  # Format as YYYY-MM-DD
    return "0000-00-00"  # Fallback in case of an issue


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
        print("✅ Page loaded. Waiting for content...")

        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "counter"))
        )

        # Extract date
        date_element = driver.find_element(By.CSS_SELECTOR, ".cursor-pointer.active.list-group-item")
        menu_date = format_date(date_element.text.strip())  # Convert to YYYY-MM-DD format
        print(f"📅 Menu date: {menu_date}")

        # Extract meals by counter titles
        meal_data = []

        counters = driver.find_elements(By.CLASS_NAME, "counter")

        for counter in counters:
            counter_title = counter.find_element(By.CLASS_NAME, "counter-title").text.strip()
            
            if counter_title in ["Menü 1", "Menü 2", "Mensacafé"]:
                meal_elements = counter.find_elements(By.CLASS_NAME, "meal")
                
                for meal in meal_elements:
                    meal_title = meal.find_element(By.CLASS_NAME, "meal-title").text.strip()

                    # Gather components separately
                    component_elements = meal.find_elements(By.CLASS_NAME, "component-name")
                    components = [c.text.strip() for c in component_elements]

                    # Append structured data
                    meal_data.append([menu_date, counter_title, meal_title, components])

        # Save to Google Sheets
        save_to_google_sheets(meal_data)

    except Exception as e:
        print(f"❌ Error scraping menu: {e}")
    
    finally:
        if driver:
            driver.quit()

def save_to_google_sheets(meal_data):
    """Save meal data to Google Sheets with separate component columns."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    try:
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        print("✅ Google Sheets Authentication Successful!")
    except Exception as e:
        print(f"❌ Google Sheets Authentication Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Determine the max number of components in any meal
    max_components = max(len(row[3]) for row in meal_data)

    # Generate column headers dynamically
    headers = ["Date", "Counter", "Meal"] + [f"Component {i+1}" for i in range(max_components)]

    # If the sheet is empty, add headers
    if not sheet.get_all_values():
        sheet.append_row(headers)

    # Append new data with empty cells for missing components
    for row in meal_data:
        # Ensure all rows have the same number of columns
        components = row[3] + [""] * (max_components - len(row[3]))  # Pad missing components
        sheet.append_row(row[:3] + components)  # Combine date, counter, meal, and components

    print(f"✅ Data saved to Google Sheets: {SHEET_NAME}")


if __name__ == "__main__":
    scrape_mensaar()