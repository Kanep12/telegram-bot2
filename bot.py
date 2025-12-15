import os
import json
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
DATA_FILE = "data.json"

# =====================
# 🧠 ANDMED (vaikimisi)
# =====================
stock_text = "📦 Stock\n\nInfo puudub."

operators = {}
# @username: {user_id, loc, online, delivery}

links = []
# [{name, url}]

# =====================
# 💾 LOAD / SAVE
# =====================
def load_data():
    global stock_text, operators, links
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            stock_text = data.get("stock_text", stock_text)
            operators = data.get("operators", {})
            links = data.get("links", [])

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "stock_text": stock_text,
                "operators": operators,
                "links": links
            },
            f,
            ensure_ascii=False,
            indent=2
        )

# =====================
# 🏠 HOME
# =====================
HOME_CAPTION = (
    "🐶 Tere tulemast DoggieMarketisse!\n\n"
    "Kasuta allolevaid nuppe."
)

# =====================
# 🎨 UI
# =====================
def box(text: str) -> str:
    return f"<blockquote>{html.escape(text)}</blockquote>"

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

# =====================
# /start
# =====================
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
    save_data()
    await update.message.reply_text("✅ Stock salvestatud!")

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
        "loc": "Not set",
        "online": False,
        "delivery": False
    }

    save_data()
    await update.message.reply_text(f"✅ Operator lisatud: {username}")

def get_operator(user):
    if not user.username:
        return None

    key = f"@{user.username}"
    if key in operators:
        operators[key]["user_id"] = user.id
        save_data()
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
    save_data()
    await update.message.reply_text("📍 Location salvestatud")

async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return
    op["online"] = True
    save_data()
    await update.message.reply_text("🟢 ONLINE")

async def offline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return
    op["online"] = False
    save_data()
    await update.message.reply_text("🔴 OFFLINE")

async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return
    op["delivery"] = context.args[0].lower() == "yes"
    save_data()
    await update.message.reply_text("🚚 Delivery salvestatud")

# =====================
# 🔗 LINKS
# =====================
async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("/link <nimi> <url>")
        return

    name = context.args[0]
    url = context.args[1]

    links.append({
        "name": name,
        "url": url
    })

    save_data()
    await update.message.reply_text("✅ Link lisatud!")

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
            text = "👤 Operators | Info puudub."
        else:
            rows = []
            for username, op in operators.items():
                rows.append(
                    f"{username} | "
                    f"📍 {op['loc']} | "
                    f"{'🟢 Online' if op['online'] else '🔴 Offline'} | "
                    f"🚚 {'Yes' if op['delivery'] else 'No'}"
                )
            text = "\n".join(rows)

        await q.edit_message_caption(
            caption=box(text),
            parse_mode="HTML",
            reply_markup=back()
        )

    elif q.data == "links":
        if not links:
            text = "🔗 Links\n\nInfo puudub."
        else:
            rows = []
            for l in links:
                rows.append(f"{l['name']} → {l['url']}")
            text = "\n".join(rows)

        await q.edit_message_caption(
            caption=box(text),
            parse_mode="HTML",
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
    load_data()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", set_stock))
    app.add_handler(CommandHandler("addoperator", add_operator))

    app.add_handler(CommandHandler("loc", set_loc))
    app.add_handler(CommandHandler("online", online))
    app.add_handler(CommandHandler("offline", offline))
    app.add_handler(CommandHandler("delivery", delivery))

    app.add_handler(CommandHandler("link", add_link))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot töötab...")
    app.run_polling()

if __name__ == "__main__":
    main()
