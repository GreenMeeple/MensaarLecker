#!/usr/bin/env python3
import os
import base64
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from bot_src import *

load_dotenv()

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_input = query.data
    print(f"📥 Callback query received: {base64.b64decode(user_input)}")

    match user_input:
        case "8J+TnCBBbGwgTWVudQ==":  # 📜 All Menu
            msg = get_menu("UdS") + "\n\n" + get_menu("HTW")
        case "8J+Nve+4jyBVZFMgbWVudQ==":  # 🍽️ UdS Menu
            msg = get_menu("UdS")
        case "8J+Nve+4jyBIVFcgTWVudQ==":  # 🍽️ HTW Menu
            msg = get_menu("HTW")
        case "4p2TIEhlbHA=":  # ❓ Help
            msg = HELP
        case "4oS577iPIEFib3V0":  # ℹ️ About
            msg = ABOUT
        case "8J+miSBIb290":  # 🦉 Hoot
            msg = random.choice(QUOTES)
        case _:
            msg = "❓ Sorry, I don't understand."

    await query.edit_message_text(text=msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    original_input = update.message.text
    user_input = original_input.lower()
    chat_type = update.message.chat.type
    bot_username = f"@{context.bot.username}".lower()

    print(f"📥 Text message from {chat_type}: {original_input}")

    if chat_type == "private" or (chat_type in ["group", "supergroup"] and bot_username in user_input):
        if is_menu_query(user_input):
            msg = get_menu("UdS") + "\n\n" + get_menu("HTW")
        else:
            msg = NOPE
        await update.message.reply_text(msg)

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # clean keyboard just in case
    # await update.message.reply_text("Remove unwanted reply keyboard hoot hoot...", reply_markup=ReplyKeyboardRemove())  # zero-width space

    keyboard = [
        [InlineKeyboardButton("📜 All Menu", callback_data="8J+TnCBBbGwgTWVudQ==")],
        [InlineKeyboardButton("🍽️ UdS Menu", callback_data="8J+Nve+4jyBVZFMgbWVudQ==")],
        [InlineKeyboardButton("🍽️ HTW Menu", callback_data="8J+Nve+4jyBIVFcgTWVudQ==")],
        [InlineKeyboardButton("❓ Help", callback_data="4p2TIEhlbHA=")],
        [InlineKeyboardButton("ℹ️ About", callback_data="4oS577iPIEFib3V0")],
        [InlineKeyboardButton("🦉 Hoot", callback_data="8J+miSBIb290")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🦉 Hoot Hoot❗ Guess we have another mortal here❗\nTell me what you want... wait, why don't you just... click a button below❓",
        reply_markup=reply_markup
    )

def main():
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    app.add_handler(CommandHandler("owl", panel))
    app.add_handler(CallbackQueryHandler(handle_callback))  # Now handling inline button clicks
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🦉 Bot is running.")
    app.run_polling()

if __name__ == "__main__":
    main()