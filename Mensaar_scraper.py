from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pytz
import json
from pathlib import Path
from collections import defaultdict

def load_existing_counts(count_file):
    """Load existing counts from the JSON file, if it exists."""
    if count_file.exists():
        with open(count_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"meal_counts": {}, "component_counts": {}}

def scrape_mensaar():
    url = "https://mensaar.de/#/menu/sb"
    driver = None
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Set up the Chrome driver using webdriver_manager
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
        
        # Load existing meal and component counts
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        count_file = output_dir / "meal_component_counts.json"
        existing_counts = load_existing_counts(count_file)
        
        # Extract meals by counter titles
        meals = defaultdict(lambda: {"meals": []})
        meal_count = existing_counts["meal_counts"]  # Start from existing counts
        component_count = existing_counts["component_counts"]  # Start from existing counts

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
                    components = {}
                    for component in component_elements:
                        component_text = component.find_element(By.CLASS_NAME, "component-name").text.strip()
                        components[component_text] = True  # Indicate presence
                        component_count[component_text] = component_count.get(component_text, 0) + 1  # Increment count

                    # Count occurrences of each meal
                    meal_count[meal_title] = meal_count.get(meal_title, 0) + 1  # Increment count

                    # Append meal title and components to the corresponding counter
                    meals[counter_title]["meals"].append({
                        "meal": meal_title,
                        "components": components
                    })

        # Create a dictionary to store the results
        result = {
            "date": menu_date,
            "meals": {counter: data["meals"] for counter, data in meals.items()}
        }

        # Save the results to a JSON file
        output_file = output_dir / f"menu_{datetime.now(pytz.timezone('Europe/Berlin')).date()}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"Results saved to {output_file}")

        # Save the updated occurrence counts to the JSON file
        count_result = {
            "meal_counts": dict(meal_count),
            "component_counts": dict(component_count)
        }

        with open(count_file, "w", encoding="utf-8") as f:
            json.dump(count_result, f, ensure_ascii=False, indent=2)

        print(f"Counts saved to {count_file}")

    except Exception as e:
        print(f"Error scraping menu: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_mensaar()
