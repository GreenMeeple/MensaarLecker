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

    user_input = update.message.text
    chat_type = update.message.chat.type
    bot_username = f"@{context.bot.username}"
    should_reply = (
        chat_type == "private" or
        (chat_type in ["group", "supergroup"] and bot_username in user_input)
    )
    if not should_reply:
        return
    
    print(f"📥 New message from {chat_type}: {user_input}")
    match user_input.lower():
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
            if is_menu_query(user_input):
                uds = scrape_mensaar(UDS_URL)
                htw = scrape_mensaar(HTW_URL)
                msg = format_menu(uds, "UdS") + "\n\n" + format_menu(htw, "HTW")
            else:
                msg = NOPE
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