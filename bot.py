import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.environ.get("BOT_TOKEN")

# /start käsk
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📦 Stock", callback_data="stock"),
            InlineKeyboardButton("👤 Operators", callback_data="operators"),
            InlineKeyboardButton("🔗 Links", callback_data="links")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("doggie.png", "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption="🐶 *Tere tulemast DoggieMarketisse!*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# Nuppude handler
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "stock":
        await query.edit_message_caption("📦 *Stock* – coming soon", parse_mode="Markdown")

    elif query.data == "operators":
        await query.edit_message_caption("👤 *Operators* – info varsti", parse_mode="Markdown")

    elif query.data == "links":
        await query.edit_message_caption(
            "🔗 *Links*\n\nhttps://t.me/yourchannel",
            parse_mode="Markdown"
        )

# Echo (võid hiljem ära kustutada)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN puudub!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot töötab...")
    app.run_polling()

if __name__ == "__main__":
    main()
