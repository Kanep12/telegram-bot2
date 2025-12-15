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

# 📦 STOCK (töötab jälle)
stock_text = "📦 Stock\n\nInfo puudub."

# 👤 OPERATORS
operators = {}
# user_id: {username, loc, online, delivery}

# 🏠 Home tekst
HOME_CAPTION = (
    "🐶 Tere tulemast DoggieMarketisse!\n\n"
    "Kasuta allolevaid nuppe, et näha infot."
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

# 🔐 ADMIN CHECK
def is_admin(user_id: int) -> bool:
    return user_id in admins

# =====================
# 📦 STOCK KÄSUD
# =====================

# /stock <tekst>
async def set_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stock_text

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Sul pole õigust seda käsku kasutada.")
        return

    if len(update.message.text.split(" ", 1)) < 2:
        await update.message.reply_text("/stock <tekst>")
        return

    stock_text = update.message.text.split(" ", 1)[1]
    await update.message.reply_text("✅ Stock uuendatud!")

# =====================
# 👤 OPERATORS KÄSUD
# =====================

# /operator @username
async def set_operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return

    operators.setdefault(uid, {
        "username": "",
        "loc": "Not set",
        "online": False,
        "delivery": False
    })

    operators[uid]["username"] = context.args[0]
    await update.message.reply_text("✅ Operator nimi uuendatud")

# /loc <asukoht>
async def set_loc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return

    operators.setdefault(uid, {
        "username": "Not set",
        "loc": "Not set",
        "online": False,
        "delivery": False
    })

    operators[uid]["loc"] = " ".join(context.args)
    await update.message.reply_text("📍 Location uuendatud")

# /online
async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return

    operators.setdefault(uid, {
        "username": "Not set",
        "loc": "Not set",
        "online": False,
        "delivery": False
    })

    operators[uid]["online"] = True
    await update.message.reply_text("🟢 Status: ONLINE")

# /offline
async def offline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return

    operators.setdefault(uid, {
        "username": "Not set",
        "loc": "Not set",
        "online": False,
        "delivery": False
    })

    operators[uid]["online"] = False
    await update.message.reply_text("🔴 Status: OFFLINE")

# /delivery yes|no
async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return

    operators.setdefault(uid, {
        "username": "Not set",
        "loc": "Not set",
        "online": False,
        "delivery": False
    })

    operators[uid]["delivery"] = context.args[0].lower() == "yes"
    await update.message.reply_text("🚚 Delivery uuendatud")

# =====================
# 🔘 NUPUD
# =====================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # 📦 STOCK VIEW
    if q.data == "stock":
        await q.edit_message_caption(
            caption=box(stock_text),
            parse_mode="HTML",
            reply_markup=back()
        )

    # 👤 OPERATORS VIEW
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

    # 🔗 LINKS
    elif q.data == "links":
        await q.edit_message_caption(
            caption="🔗 Links\n\n@doggiemarket_bot",
            reply_markup=back()
        )

    # 🔙 BACK
    elif q.data == "back":
        await q.edit_message_caption(
            caption=HOME_CAPTION,
            reply_markup=main_menu()
        )

# =====================
# 👑 ADD ADMIN
# =====================

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    admins.add(int(context.args[0]))
    await update.message.reply_text("✅ Admin lisatud")

# =====================
# MAIN
# =====================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", set_stock))

    app.add_handler(CommandHandler("operator", set_operator))
    app.add_handler(CommandHandler("loc", set_loc))
    app.add_handler(CommandHandler("online", online))
    app.add_handler(CommandHandler("offline", offline))
    app.add_handler(CommandHandler("delivery", delivery))

    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot töötab...")
    app.run_polling()

if __name__ == "__main__":
    main()
