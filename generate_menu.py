import requests
import datetime
from collections import Counter

# Google Apps Script URL
SCRIPT_URL = "https://script.googleusercontent.com/macros/echo?user_content_key=AehSKLi1GfO-Gv8mOZT2yAZiuObuFah4SfO3yL-8v5ttyczhLNjc54QwEXxrUUA-tG3Hm9OD71kja_nmNqmmnqTuFQhR_JsVFTeOVlQ_i_Go_JT20OFIj9JNSUwOZKeqHNwAXEA6aB6UqmrSNaqpqUtdizlU8memnIBISS8Fs3rtzBIuioM6JYUJfiha44O5SX0u0UCXR_HMzXJVR9_DjTFy-cn_XOhxK8_J1jJ2N1pfvnIOvUeSFtXeyCpCQDVQYMb0jABlV8YJQPc1hYF3fcYGoUCBNWKu8g&lib=MjLlBRtX5qgaM2u21xtweVb8p07uDipDZ";

# Fetch JSON data
def fetch_menu():
    try:
        response = requests.get(SCRIPT_URL)
        response.raise_for_status()  # Raise error if bad response
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching menu: {e}")
        return []

# Generate today's menu (index.html)
def generate_index_html(menu_data):
    today = datetime.date.today().isoformat()
    weekday = datetime.datetime.today().strftime("%A")
    is_weekend = weekday in ["Saturday", "Sunday"]

    # Calculate meal frequencies across all days
    meal_names = [meal["Meal"] for meal in menu_data]
    meal_frequencies = Counter(meal_names)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mensaar Today</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; text-align: center; background-image: url('src/uds_spirit.jpg'); }}
        h1 {{
            background: rgba(255, 255, 255, 0.8); 
            color: #003C71;
            padding: 10px 20px;
            display: inline-block; 
            border-radius: 10px; 
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2); 
        }}
        .container {{ width: 80%; margin: auto; }}
        .closed-message {{ font-size: 26px; color: red; font-weight: bold; padding: 20px; background: #fff3f3; border-radius: 10px; }}
        .menu-card {{ background: white; padding: 15px; margin: 10px 0; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); text-align: left; }}
        .meal-title {{ font-size: 20px; font-weight: bold; }}
        .meal-components {{ font-size: 16px; color: #666; }}
        .meal-frequency {{ font-size: 14px; color: #888; font-style: italic; }}
        .button {{ padding: 12px 20px; background: #007bff; color: white; border-radius: 5px; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>Mensaar Menu for {today}</h1></br>
    <a href="menu.html" class="button">📜 View Full Menu</a>
    <div class="container">
    """

    if is_weekend:
        html += '<p class="closed-message">🚫 Mensa is closed on weekends! 🍽️</p>'
    else:
        today_menu = [m for m in menu_data if m["Date"].startswith(today)]
        if not today_menu:
            html += '<p class="closed-message">❌ No menu available for today!</p>'
        else:
            for meal in today_menu:
                meal_name = meal["Meal"]
                freq = meal_frequencies.get(meal_name, 1)
                frequency_text = f"📊 Seen {freq} time{'s' if freq > 1 else ''} since 2025.03.20"

                components = "<br>".join(
                    f"✅ {meal[f'Component {i}']}" for i in range(1, 6) if meal.get(f'Component {i}')
                )
                html += f"""
                <div class="menu-card">
                    <p class="meal-title">🍽️ {meal_name}</p>
                    <p class="meal-frequency">{frequency_text}</p>
                    <p class="meal-components">{components}</p>
                </div>
                """

    html += """
    </div>
</body>
</html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html updated.")

# Generate full menu (menu.html)
def generate_menu_html(menu_data):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Full Mensaar Menu</title>
    
    <!-- DataTables CSS & JS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>

    <style>
        body { font-family: Arial, sans-serif; padding: 20px; text-align: center; background-image: url('src/uds_spirit.jpg'); }
        h1 {
            background: rgba(255, 255, 255, 0.8); 
            color: color: #003C71;
            padding: 10px 20px;
            display: inline-block; 
            border-radius: 10px; 
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2); 
        }
        table { width: 90%; margin: 20px auto; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; }
        th { background-color: #003C71; color: white; }
        .button { padding: 10px 15px; background: #007bff; color: white; border-radius: 5px; text-decoration: none; }
        .button:hover { background: #0056b3; }
        /* Fix visibility of DataTables UI */


        /* Change dropdown & search box background */
        .dataTables_length, 
        .dataTables_filter, 
        .dataTables_info, 
        .dataTables_paginate {
            background: rgba(255, 255, 255, 0.8); /* Light background */
            padding: 10px;
            border-radius: 5px;
        }

        /* Style dropdown and search input */
        .dataTables_length select,
        .dataTables_filter input {
            background: white;
            color: black;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        /* Improve button visibility */
        .dataTables_paginate .paginate_button {
            color: white !important;
            border-radius: 5px;
            padding: 5px 10px;
        }

        .dataTables_paginate .paginate_button:hover {
            background: #0056b3 !important; /* Darker blue on hover */
        }
    </style>
</head>
<body>
    <h1>Full Mensaar Menu</h1></br>
    <a href="index.html" class="button">🏠 Back to Home</a>
    
    <table id="menuTable" class="display">
        <thead>
            <tr>
                <th>Date</th>
                <th>Counter</th>
                <th>Meal</th>
                <th>Component 1</th>
                <th>Component 2</th>
                <th>Component 3</th>
                <th>Component 4</th>
                <th>Component 5</th>
            </tr>
        </thead>
        <tbody>
    """

    for meal in menu_data:
        html += f"""
        <tr>
            <td>{meal['Date'].split('T')[0]}</td>
            <td>{meal['Counter']}</td>
            <td>{meal['Meal']}</td>
            <td>{meal['Component 1']}</td>
            <td>{meal['Component 2']}</td>
            <td>{meal['Component 3']}</td>
            <td>{meal['Component 4']}</td>
            <td>{meal['Component 5']}</td>
        </tr>
        """

    html += """
        </tbody>
    </table>

    <script>
        $(document).ready(function() {
            $('#menuTable').DataTable({
                "paging": true,
                "searching": true,
                "ordering": true,
                "info": true,
                "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
                "order": [[0, "desc"]],
            });
        });
    </script>
</body>
</html>
    """

    with open("menu.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ menu.html updated.")

# Main execution
if __name__ == "__main__":
    menu_data = fetch_menu()
    if menu_data:
        generate_index_html(menu_data)
        generate_menu_html(menu_data)
    else:
        print("❌ No data received.")
