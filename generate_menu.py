import requests
import datetime
from collections import Counter

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwZf63mZm9RS44JtwKX_ZgjJSpmKlo5cZlF_wAIhXUnXeajhTF2ralMCoYK7yhbp7k/exec"

def fetch_menu():
    try:
        response = requests.get(SCRIPT_URL)
        response.raise_for_status()
        data = response.json()
        return data.get("Menu_uds", []), data.get("Menu_htw", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching menu: {e}")
        return [], []

def generate_index_html(uds_data, htw_data):
    today = datetime.date.today().isoformat()
    meal_freqs = Counter([m["Meal"] for m in uds_data + htw_data])

    def meal_cards(menu):
        cards = ""
        todays_menu = [m for m in menu if m["Date"].startswith(today)]
        if not todays_menu:
            return '<p class="closed-message">❌ No menu available for today!</p>'
        for m in todays_menu:
            name = m["Meal"]
            freq = meal_freqs[name]
            freq_txt = f"📊 Seen {freq} time{'s' if freq > 1 else ''} since 2025.03.20"
            components = "<br>".join(
                f"✅ {m.get(f'Component {i}', '')}" for i in range(1, 6) if m.get(f'Component {i}')
            )
            cards += f"""<div class="menu-card">
                <p class="meal-title">🍽️ {name}</p>
                <p class="meal-frequency">{freq_txt}</p>
                <p class="meal-components">{components}</p>
            </div>"""
        return f'<div class="menu-grid">{cards}</div>'

    def table_rows(menu):
        rows = ""
        for m in menu:
            comps = "".join(f"<td>{m.get(f'Component {i}', '')}</td>" for i in range(1, 6))
            rows += f"<tr><td>{m['Date'].split('T')[0]}</td><td>{m['Counter']}</td><td>{m['Meal']}</td>{comps}</tr>"
        return rows

    html = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <title>Mensaar Full Menu</title>
            <link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css">
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; background-image: url('src/uds_spirit.jpg'); padding: 20px; }}
                h1 {{ background: rgba(255, 255, 255, 0.8); color: #003C71; padding: 10px 20px; display: inline-block; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2); }}
                .buttons {{ text-align: center; margin-bottom: 20px; }}
                .button {{ padding: 10px 15px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                .section {{ display: none; padding: 10px; background: rgba(255,255,255,0.9); border-radius: 10px; }}
                .active {{ display: block; }}
                .menu-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin-top: 10px; }}
                .menu-card {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 1px 1px 6px rgba(0,0,0,0.1); text-align: left; }}
                .meal-title {{ font-size: 18px; font-weight: bold; }}
                .meal-frequency {{ font-size: 14px; color: #888; }}
                .closed-message {{ font-size: 26px; color: red; font-weight: bold; padding: 20px; background: #fff3f3; border-radius: 10px; }}
                table {{ width: 100%; margin-top: 20px; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; }}
                th {{ background-color: #003C71; color: white; }}
                h2 {{ margin-top: 10px; color: #003C71; }}

            </style>
            </head>
            <body>
            <h1>Mensaar Menu - {today}</h1>
            <div class="buttons">
                <button class="button" onclick="show('today-uds')">📅 UDS Today</button>
                <button class="button" onclick="show('today-htw')">📅 HTW Today</button>
                <button class="button" onclick="show('full-uds')">📋 Full UDS</button>
                <button class="button" onclick="show('full-htw')">📋 Full HTW</button>
            </div>

            <div id="today-uds" class="section active">
            <h2>UDS – Today's Menu</h2>
            {meal_cards(uds_data)}
            </div>

            <div id="today-htw" class="section">
            <h2>HTW – Today's Menu</h2>
            {meal_cards(htw_data)}
            </div>

            <div id="full-uds" class="section">
            <h2>📋 Full UDS Menu</h2>
            <table id="uds-table">
                <thead><tr><th>Date</th><th>Counter</th><th>Meal</th><th>Component 1</th><th>Component 2</th><th>Component 3</th><th>Component 4</th><th>Component 5</th></tr></thead>
                <tbody>{table_rows(uds_data)}</tbody>
            </table>
            </div>

            <div id="full-htw" class="section">
            <h2>📋 Full HTW Menu</h2>
            <table id="htw-table">
                <thead><tr><th>Date</th><th>Counter</th><th>Meal</th><th>Component 1</th><th>Component 2</th><th>Component 3</th><th>Component 4</th><th>Component 5</th></tr></thead>
                <tbody>{table_rows(htw_data)}</tbody>
            </table>
            </div>

            <script>
                function show(id) {{
                document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
                document.getElementById(id).classList.add('active');
                }}
                $(document).ready(function() {{
                $('#uds-table').DataTable();
                $('#htw-table').DataTable();
                }});
            </script>
            </body>
            </html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html (all-in-one) generated.")

if __name__ == "__main__":
    uds_data, htw_data = fetch_menu()
    print(f"🔎 UDS entries: {len(uds_data)}")
    print(f"🔎 HTW entries: {len(htw_data)}")

    if uds_data or htw_data:
        generate_index_html(uds_data, htw_data)
    else:
        print("❌ No data received.")
