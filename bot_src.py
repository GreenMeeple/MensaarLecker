import re
from rapidfuzz import fuzz
from deep_translator import GoogleTranslator
from datetime import datetime, date
from Mensaar_scraper import scrape_mensaar, UDS_URL, HTW_URL

ABOUT = "🦉 I'm the wisest OWL — your friendly helper for Saarbrücken's cafeteria menus❗ I used my clumsy wings to get what i need from 📜 https://mensaar.de/#/menu/htwcrb and 📜 https://mensaar.de/#/menu/sb. That's modern technology my youngling 😉"

HELP = "🦉 I'm the wisest OWL in Saarbrücken, also the hungriest❗ Of course I know today's menu in UdS and HTW...\nYou can check all menus 🍽️ by clicking the buttons, or @tag me to show me your enthusiasm towards food 🔥🔥🔥"

NOPE = "🦉 Sorry, I only care about the Mensa menu, and my mental health 💪🏾"

QUOTES = [
    "⌛Time is what we want most but what we use worst, so as your wisdom.",
    "🍎An apple a day keeps my life gray. That's not enough to feed a wise OWL❗",
    "🥈Speech is silver, Slient❗ I need food now❗",
    "The best I can do is to give you today's menu, but the best you can do is to talk to an OWL❓ Ha, Pathetic youngling❗",
    "You know I can talk right❓ No need to HOOT❗",
    "Even an OWL sometimes enjoys the vegan menu🥗, I enjoy how it destroys my digestive system🫃",
    "The second worst thing you can do is to talk to a wise OWL, and the first is going to mensa.",
    "If women cannot do anything but cooking, why don't they call it Womensa❓",
    "I learn you mortal's language so that I can flame you like a phoenix🐦‍🔥",
    "Don't Judge a person unless you've walked in their shoes👞. Don't judge a mensa menu unless that's your 30th time walk in your toilet.🚽",
    "🦉Hoot", "🦉Hoot❓", "🦉 Hoot❗" , "🦉 Hoot😡", NOPE
]

MENU_KEYWORDS = [
    "menu", "mensa", "lunch", "essen", "meal", "speiseplan", "cafeteria",
    "food", "mittagessen", "hungry", "htw", "forage", "plan", "cook", "deal"
]

_menu_cache = {"date": None, "UdS": None, "HTW": None}

def get_menu(mensa):
    today = date.today().isoformat()

    if _menu_cache["date"] != today or _menu_cache[mensa] is None:
        print(f"🔄 Refreshing menu cache for {mensa}")
        _menu_cache["date"] = today
        _menu_cache[mensa] = scrape_mensaar(UDS_URL) if mensa == "UdS" else scrape_mensaar(HTW_URL)

    data = _menu_cache[mensa]
    now = datetime.now()
    now_str = now.strftime("%H:%M")
    data_today = [m for m in data if m[0].startswith(today)]

    # Define opening and closing based on cafeteria
    opening, closing = (
        (now.replace(hour=11, minute=30), now.replace(hour=14, minute=30))
        if mensa == "UdS" else
        (now.replace(hour=11, minute=0), now.replace(hour=14, minute=15))
    )

    if now > closing:
        return "⛔ Schade❗ Already closed."
    # Early exit if no menu yet
    if not data_today:
        return f"❌ Current time {now_str}. {'Menu not available yet.' if now < opening else f'No {mensa} menu for today.'}"

    # Determine status
    if now < opening:
        delta = opening - now
        status = f"🕚 Opens in {delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"
    else:
        delta = closing - now
        status = f"🕑 Closes in {delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"

    # Build output
    lines = [
        f"📍 {mensa} Menu:\n🕰️ {now_str} | {status}\n"
    ] + [
        f"• {counter}: {translate_text(meal_mensa)}\n  - {', '.join(translate_text(c) for c in components if c)}"
        for _, counter, meal_mensa, components in data_today
    ]
    return "\n".join(lines)

_translation_cache = {}
def translate_text(text, target='en'):
    if text in _translation_cache:
        return _translation_cache[text]
    try:
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        _translation_cache[text] = translated
        return translated
    except Exception as e:
        print(f"⚠️ Translation failed for '{text}': {e}")
        return text

def is_menu_query(text: str, threshold=80):
    text = re.sub(r'@\w+', '', text)
    text = text.lower()
    return any(fuzz.partial_ratio(text, keyword) >= threshold for keyword in MENU_KEYWORDS)