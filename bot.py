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

# 👤 Operators
# user_id: {username, loc, online, delivery}
operators = {}

# 📦 Stock
stock_text = "📦 Stock\n\nInfo puudub."

# 🏠 Home
HOME_CAPTION = (
    "🐶 Tere tulemast DoggieMarketisse!\n\n"
    "Kasuta allolevaid nuppe."
)

# 🔧 HTML blockquote
def box(text: str) -> str:
    return f"<blockquote>{html.escape(text)}</blockquote>"

# 🔘 Keyboards
def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Stock", callback_data="stock"),
            InlineKeyboardButton("👤 Operators", callback_data="operators"),
            InlineKeyboardButton("🔗 Links", callback_data="links")
        ]
    ])

def back():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("doggie.png", "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=HOME_CAPTION,
            reply_markup=main_menu()
        )

# =====================
# 📦 STOCK
# =====================
async def set_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Ainult owner saab stocki muuta.")
        return

    if len(update.message.text.split(" ", 1)) < 2:
        await update.message.reply_text("/stock <tekst>")
        return

    global stock_text
    stock_text = update.message.text.split(" ", 1)[1]
    await update.message.reply_text("✅ Stock uuendatud!")

# =====================
# 👑 ADD OPERATOR
# =====================
async def add_operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text("/addoperator @username")
        return

    username = context.args[0]

    operators[username] = {
        "user_id": None,
        "username": username,
        "loc": "Not set",
        "online": False,
        "delivery": False
    }

    await update.message.reply_text(f"✅ Operator lisatud: {username}")

# =====================
# 👤 OPERATOR INIT
# =====================
def get_operator(user):
    for op in operators.values():
        if op["user_id"] == user.id:
            return op

    if user.username:
        key = f"@{user.username}"
        if key in operators:
            operators[key]["user_id"] = user.id
            return operators[key]

    return None

# =====================
# 👤 OPERATOR KÄSUD
# =====================
async def set_loc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return

    op["loc"] = " ".join(context.args)
    await update.message.reply_text("📍 Location uuendatud")

async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return

    op["online"] = True
    await update.message.reply_text("🟢 Status: ONLINE")

async def offline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return

    op["online"] = False
    await update.message.reply_text("🔴 Status: OFFLINE")

async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return

    op["delivery"] = context.args[0].lower() == "yes"
    await update.message.reply_text("🚚 Delivery uuendatud")

# =====================
# 🔘 BUTTONS
# =====================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "stock":
        await q.edit_message_caption(
            caption=box(stock_text),
            parse_mode="HTML",
            reply_markup=back()
        )

    elif q.data == "operators":
        if not operators:
            text = "👤 Operators\n\nInfo puudub."
        else:
            parts = []
            for op in operators.values():
                parts.append(
                    f"{op['username']}\n"
                    f"📍 {op['loc']}\n"
                    f"{'🟢 Online' if op['online'] else '🔴 Offline'}\n"
                    f"🚚 Delivery: {'Yes' if op['delivery'] else 'No'}"
                )
            text = "\n\n".join(parts)

        await q.edit_message_caption(
            caption=box(text),
            parse_mode="HTML",
            reply_markup=back()
        )

    elif q.data == "links":
        await q.edit_message_caption(
            caption="🔗 Links\n\n@doggiemarket_bot",
            reply_markup=back()
        )

    elif q.data == "back":
        await q.edit_message_caption(
            caption=HOME_CAPTION,
            reply_markup=main_menu()
        )

# =====================
# MAIN
# =====================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", set_stock))

    app.add_handler(CommandHandler("addoperator", add_operator))
    app.add_handler(CommandHandler("loc", set_loc))
    app.add_handler(CommandHandler("online", online))
    app.add_handler(CommandHandler("offline", offline))
    app.add_handler(CommandHandler("delivery", delivery))

    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot töötab...")
    app.run_polling()

if __name__ == "__main__":
    main()
