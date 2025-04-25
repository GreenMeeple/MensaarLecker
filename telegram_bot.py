import os
import random
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from Mensaar_scraper import scrape_mensaar, UDS_URL, HTW_URL
from bot_src import *

load_dotenv()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    original_input = update.message.text
    user_input = original_input.lower()
    chat_type = update.message.chat.type
    bot_username = f"@{context.bot.username}".lower()

    print(f"📥 New message from {chat_type}: {original_input}")

    # Check if it's a button press (from keyboard UI)
    is_button_input = user_input in [
        "📜 all menu", "🍽️ uds menu", "🍽️ htw menu",
        "❓ help", "ℹ️ about", "🦉 hoot", "hoot"
    ]

    # Case 1: Private chat — allow all messages
    # Case 2: Group chat — only respond to:
    #   - buttons
    #   - messages that contain bot mention
    if chat_type == "private":
        allow_processing = True
    elif chat_type in ["group", "supergroup"]:
        allow_processing = is_button_input or (bot_username in user_input)
    else:
        allow_processing = False

    if not allow_processing:
        return

    # Now respond based on the message
    match user_input:
        case "📜 all menu":
            uds = scrape_mensaar(UDS_URL)
            htw = scrape_mensaar(HTW_URL)
            msg = format_menu(uds, "UdS") + "\n\n" + format_menu(htw, "HTW")
        case "🍽️ uds menu":
            uds = scrape_mensaar(UDS_URL)
            msg = format_menu(uds, "UdS")
        case "🍽️ htw menu":
            htw = scrape_mensaar(HTW_URL)
            msg = format_menu(htw, "HTW")
        case "❓ help":
            msg = HELP
        case "ℹ️ about":
            msg = ABOUT
        case "🦉 hoot" | "hoot":
            msg = random.choice(QUOTES)
        case _:
            # Only do fuzzy matching if in private chat or tagged in group
            if chat_type == "private" or bot_username in user_input:
                if is_menu_query(user_input):
                    uds = scrape_mensaar(UDS_URL)
                    htw = scrape_mensaar(HTW_URL)
                    msg = format_menu(uds, "UdS") + "\n\n" + format_menu(htw, "HTW")
                else:
                    msg = NOPE
            else:
                return  # Ignore irrelevant messages in group

    await update.message.reply_text(msg)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🍽️ All Menu", "🍽️ UdS Menu", "🍽️ HTW Menu"],
        ["❓ Help", "ℹ️ About", "🦉 Hoot"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🦉 Hoot Hoot❗ Guess we have another mortal here❗\nTell me what you want... wait, why don't you just... click a button below❓",
        reply_markup=reply_markup
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🦉 Bot is running.")
    app.run_polling()