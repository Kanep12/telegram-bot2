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

# 🧑‍💼 Operatorite andmed
operators = {}  
# user_id: {username, loc, online, delivery}

# 🏠 Home
HOME_CAPTION = (
    "🐶 Tere tulemast DoggieMarketisse!\n\n"
    "Kasuta allolevaid nuppe."
)

# 🔧 Blockquote HTML
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

# 👑 add admin
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    new_admin = int(context.args[0])
    admins.add(new_admin)

    if new_admin not in operators:
        operators[new_admin] = {
            "username": "Not set",
            "loc": "Not set",
            "online": False,
            "delivery": False
        }

    await update.message.reply_text("✅ Admin lisatud")

# 🔐 check admin
def is_admin(user_id):
    return user_id in admins

# 👤 /operator @name
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

# 📍 /loc
async def set_loc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return

    operators[uid]["loc"] = " ".join(context.args)
    await update.message.reply_text("📍 Location uuendatud")

# 🟢 /online
async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return

    operators[uid]["online"] = True
    await update.message.reply_text("🟢 Status: ONLINE")

# 🔴 /offline
async def offline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return

    operators[uid]["online"] = False
    await update.message.reply_text("🔴 Status: OFFLINE")

# 🚚 /delivery yes/no
async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return

    operators[uid]["delivery"] = context.args[0].lower() == "yes"
    await update.message.reply_text("🚚 Delivery uuendatud")

# 👤 Operators view
async def show_operators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not operators:
        text = "Operators info puudub."
    else:
        lines = []
        for op in operators.values():
            lines.append(
                f"{op['username']}\n"
                f"📍 {op['loc']}\n"
                f"{'🟢 Online' if op['online'] else '🔴 Offline'}\n"
                f"🚚 Delivery: {'Yes' if op['delivery'] else 'No'}\n"
            )
        text = "\n".join(lines)

    await update.callback_query.edit_message_caption(
        caption=box(text),
        parse_mode="HTML",
        reply_markup=back()
    )

# 🔘 Buttons
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "operators":
        await show_operators(update, context)

    elif q.data == "back":
        await q.edit_message_caption(
            caption=HOME_CAPTION,
            reply_markup=main_menu()
        )

# main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("operator", set_operator))
    app.add_handler(CommandHandler("loc", set_loc))
    app.add_handler(CommandHandler("online", online))
    app.add_handler(CommandHandler("offline", offline))
    app.add_handler(CommandHandler("delivery", delivery))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot töötab...")
    app.run_polling()

if __name__ == "__main__":
    main()
