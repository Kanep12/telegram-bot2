import os
import html
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

# 👑 Owner
OWNER_ID = 7936569231
admins = {OWNER_ID}

# 🏠 Algne tekst
HOME_CAPTION = (
    "🐶 Tere tulemast DoggieMarketisse!\n\n"
    "Kasuta allolevaid nuppe, et näha infot."
)

# 📦 Stock tekst (TAVALINE TEKST)
stock_text = "📦 Stock\n\nInfo puudub."

# 🔧 HTML blockquote (EI NÄITA >)
def to_blockquote_html(text: str) -> str:
    escaped = html.escape(text)
    lines = escaped.splitlines()
    inner = "<br>".join(lines)
    return f"<blockquote>{inner}</blockquote>"

# 🔘 Menüüd
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Stock", callback_data="stock"),
            InlineKeyboardButton("👤 Operators", callback_data="operators"),
            InlineKeyboardButton("🔗 Links", callback_data="links")
        ]
    ])

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("doggie.png", "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=HOME_CAPTION,
            reply_markup=main_menu_keyboard()
        )

# 🔐 Admin-only /stock (LIHTNE, ILMA >)
async def set_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stock_text

    if update.effective_user.id not in admins:
        await update.message.reply_text("⛔ Sul pole õigust seda käsku kasutada.")
        return

    if not update.message.text or len(update.message.text.split(" ", 1)) < 2:
        await update.message.reply_text(
            "❌ Kasutus:\n"
            "/stock <tekst>\n\n"
            "Ära kasuta > märke – bot vormindab ise."
        )
        return

    stock_text = update.message.text.split(" ", 1)[1]
    await update.message.reply_text("✅ Stock uuendatud!")

# 👑 Owner-only /addadmin
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
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

# 🔘 Nupud
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "stock":
        await query.edit_message_caption(
            caption=to_blockquote_html(stock_text),
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )

    elif query.data == "operators":
        await query.edit_message_caption(
            caption="👤 Operators\n\nAsk from bot",
            reply_markup=back_keyboard()
        )

    elif query.data == "links":
        await query.edit_message_caption(
            caption="🔗 Links\n\n@doggiemarket_bot",
            reply_markup=back_keyboard()
        )

    elif query.data == "back":
        await query.edit_message_caption(
            caption=HOME_CAPTION,
            reply_markup=main_menu_keyboard()
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
