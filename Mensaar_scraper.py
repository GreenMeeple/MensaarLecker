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
import time
import json
from datetime import date

# Google Sheets Setup
SHEET_NAME = "MensaarLecker"  # Change to match your actual sheet name

# German month mapping
GERMAN_MONTHS = {
    "Januar": "01", "Februar": "02", "März": "03", "April": "04",
    "Mai": "05", "Juni": "06", "Juli": "07", "August": "08",
    "September": "09", "Oktober": "10", "November": "11", "Dezember": "12"
}

UDS_URL = "https://mensaar.de/#/menu/sb"
HTW_URL = "https://mensaar.de/#/menu/htwcrb"

# Override json.loads to help debug malformed JSON issues
original_json_loads = json.loads

def safe_json_loads(value, *args, **kwargs):
    try:
        return original_json_loads(value, *args, **kwargs)
    except json.JSONDecodeError as e:
        print("❌ JSONDecodeError:", e)
        print("🧪 Offending string:", value[:200])
        return {}

json.loads = safe_json_loads

def format_date(german_date):
    match = re.search(r"(\d{1,2})\. (\w+) (\d{4})", german_date)
    if match:
        day, month, year = match.groups()
        month_number = GERMAN_MONTHS.get(month, "00")
        return f"{year}-{month_number}-{int(day):02d}"
    return "0000-00-00"

def scrape_mensaar(url, sheet_name):
    driver = None
    try:
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
        print("✅ Page loaded. Waiting for content...")

        time.sleep(5)  # give JS time to load

        # Wait for menu to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "counter"))
            )
            print("✅ Menu loaded!")
        except:
            print("❌ Menu failed to load (no .counter found)")

        # Try to get the date
        try:
            date_element = driver.find_element(By.CSS_SELECTOR, ".cursor-pointer.active.list-group-item")
            menu_date_raw = date_element.text.strip()
            menu_date = format_date(menu_date_raw) if menu_date_raw else "0000-00-00"
            # Ensure the scraped menu_date is for today
        except Exception as e:
            print(f"❌ Failed to extract date: {e}")
            menu_date = "0000-00-00"

        if menu_date != date.today().isoformat():
            print(f"⚠️ Skipping menu for {menu_date} — not today's date.")
            return  # Stop the function early
        else: print(f"📅 Today is {menu_date}")

        meal_data = []
        counters = driver.find_elements(By.CLASS_NAME, "counter")

        for counter in counters:
            counter_title = counter.find_element(By.CLASS_NAME, "counter-title").text.strip()
            if url == UDS_URL: 
                title_list = ["Menü 1", "Menü 2", "Mensacafé"]
            else:
                title_list = ["Menü 1", "Menü 2", "Wahlessen"]
                
            if counter_title in title_list:
                meal_elements = counter.find_elements(By.CLASS_NAME, "meal")

                for meal in meal_elements:
                    meal_title = meal.find_element(By.CLASS_NAME, "meal-title").text.strip()

                    component_elements = meal.find_elements(By.CLASS_NAME, "component-name")
                    components = [c.text.strip() for c in component_elements]

                    meal_data.append([menu_date, counter_title, meal_title, components])

        if meal_data:
            save_to_google_sheets(meal_data, sheet_name)
        else:
            print("⚠️ No meals found.")

    except Exception as e:
        print(f"❌ Error scraping menu: {e}")
    finally:
        if driver:
            driver.quit()
        print("✅ Scraper completed.")

def save_to_google_sheets(meal_data, sheet_name):
    import os

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    try:
        # Read and validate credentials.json before using it
        if not os.path.exists("credentials.json"):
            print("❌ credentials.json not found!")
            return
        with open("credentials.json", "r", encoding="utf-8") as f:
            raw_creds = f.read()
            print("🧪 First 100 chars of credentials.json:", raw_creds[:100])
            creds_data = json.loads(raw_creds)

        # Save to a temp file just in case gspread needs it as a file
        temp_path = "parsed_credentials.json"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(creds_data, f)

        creds = ServiceAccountCredentials.from_json_keyfile_name(temp_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).worksheet(sheet_name)
        print("✅ Google Sheets Auth OK")

    except json.JSONDecodeError as e:
        print("❌ JSON parsing error in credentials.json:", e)
        return
    except Exception as e:
        print(f"❌ Google Sheets Auth Failed: {e}")
        return

    max_components = max(len(row[3]) for row in meal_data)
    headers = ["Date", "Counter", "Meal"] + [f"Component {i+1}" for i in range(max_components)]

    if not sheet.get_all_values():
        sheet.append_row(headers)

    for row in meal_data:
        components = row[3] + [""] * (max_components - len(row[3]))
        sheet.append_row(row[:3] + components)

    print("✅ Data saved to Google Sheets.")


if __name__ == "__main__":
    scrape_mensaar(UDS_URL, sheet_name="Menu_uds")
    scrape_mensaar(HTW_URL, sheet_name="Menu_htw")
