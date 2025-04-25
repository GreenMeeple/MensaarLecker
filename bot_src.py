from rapidfuzz import fuzz
from deep_translator import GoogleTranslator
from datetime import datetime, date

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

def format_menu(data, title):
    now = datetime.now()
    now_str = now.strftime("%H:%M")
    today = date.today().isoformat()
    data_today = [m for m in data if m[0].startswith(today)]

    if not data_today:
        return f"❌ No {title} menu available for today. ({now_str})"
    if title == "UdS":
        opening = now.replace(hour=11, minute=30, second=0, microsecond=0)
        closing = now.replace(hour=14, minute=30, second=0, microsecond=0)
    else:
        opening = now.replace(hour=11, minute=0, second=0, microsecond=0)
        closing = now.replace(hour=14, minute=15, second=0, microsecond=0)

    if now < opening:
        delta = opening - now
        status = f"🕚 Mensa opens in {delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"
    elif now < closing:
        delta = closing - now
        status = f"🕑 Mensa closes in {delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"
    else:
        status = "⛔ Schade❗ Mensa is closed already."

    lines = [f"📍 {title} Menu:\n🕰️ {now_str} | {status}\n"]
    for m in data_today:
        _, counter, meal_title, components = m
        translated_name = translate_text(meal_title)
        translated_components = ", ".join(translate_text(c) for c in components if c)
        lines.append(f"• {counter}: {translated_name}\n  - {translated_components}")
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
    text = text.lower()
    return any(fuzz.partial_ratio(text, keyword) >= threshold for keyword in MENU_KEYWORDS)