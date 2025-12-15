import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.environ.get("BOT_TOKEN")

# 👑 Sina (owner)
OWNER_ID = 7936569231

# 👤 Adminide hulk
admins = {OWNER_ID}

# 📦 Muudetav stock tekst
stock_text = "📦 Stock on hetkel tühi."

# /start
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
            caption="🐶 Tere tulemast DoggieMarketisse!",
            reply_markup=reply_markup
        )

# 🔐 Admin-only /stock
async def set_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stock_text

    user_id = update.effective_user.id

    if user_id not in admins:
        await update.message.reply_text("⛔ Sul pole õigust seda käsku kasutada.")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Kasutus:\n/stock siia kirjuta uus stock tekst"
        )
        return

    stock_text = " ".join(context.args)
    await update.message.reply_text("✅ Stock tekst uuendatud!")

# 👑 Owner-only /addadmin
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ Ainult owner saab admini lisada.")
        return

    if not context.args:
        await update.message.reply_text("❌ Kasutus: /addadmin <user_id>")
        return

    try:
        new_admin = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ User ID peab olema number.")
        return

    admins.add(new_admin)
    await update.message.reply_text(f"✅ Admin lisatud: {new_admin}")

# Nupud
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "stock":
        await query.edit_message_caption(
            f"📦 Stock\n\n{stock_text}"
        )

    elif query.data == "operators":
        await query.edit_message_caption(
            "👤 Operators\n\nComing soon"
        )

    elif query.data == "links":
        await query.edit_message_caption(
            "🔗 Links\n\nhttps://t.me/doggiemarket_bot"
        )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN puudub!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", set_stock))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot töötab...")
    app.run_polling()

if __name__ == "__main__":
    main()
