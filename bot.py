import os
import json
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
OWNER_ID = 7936569231

STOCK_FILE = "stock.txt"
OPERATORS_FILE = "operators.json"
LINKS_FILE = "links.txt"

# =====================
# LOAD / SAVE
# =====================

def load_stock():
    if os.path.exists(STOCK_FILE):
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "📦 Stock\n\nInfo puudub."

def save_stock(text):
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write(text)

def load_operators():
    if os.path.exists(OPERATORS_FILE):
        with open(OPERATORS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_operators(data):
    with open(OPERATORS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_links():
    links = []
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    name, url = line.strip().split("|", 1)
                    links.append({"name": name, "url": url})
    return links

def save_links(links):
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        for l in links:
            f.write(f"{l['name']}|{l['url']}\n")

# =====================
# DATA
# =====================

stock_text = load_stock()
operators = load_operators()
links = load_links()

# =====================
# UI
# =====================

HOME_CAPTION = (
    "🐶 Tere tulemast DoggieMarketisse!\n\n"
    "Kasuta allolevaid nuppe."
)

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
# STOCK
# =====================

async def set_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stock_text
    if update.effective_user.id != OWNER_ID:
        return

    stock_text = update.message.text.split(" ", 1)[1]
    save_stock(stock_text)
    await update.message.reply_text("✅ Stock salvestatud")

# =====================
# OPERATORS
# =====================

async def add_operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    username = context.args[0]
    operators[username] = {
        "user_id": None,
        "loc": "Not set",
        "online": False,
        "delivery": False
    }
    save_operators(operators)
    await update.message.reply_text(f"✅ Operator lisatud: {username}")

def get_operator(user):
    if not user.username:
        return None
    key = f"@{user.username}"
    if key in operators:
        operators[key]["user_id"] = user.id
        save_operators(operators)
        return operators[key]
    return None

async def set_loc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return
    op["loc"] = " ".join(context.args)
    save_operators(operators)
    await update.message.reply_text("📍 Location salvestatud")

async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return
    op["online"] = True
    save_operators(operators)
    await update.message.reply_text("🟢 ONLINE")

async def offline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return
    op["online"] = False
    save_operators(operators)
    await update.message.reply_text("🔴 OFFLINE")

async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = get_operator(update.effective_user)
    if not op:
        return
    op["delivery"] = context.args[0].lower() == "yes"
    save_operators(operators)
    await update.message.reply_text("🚚 Delivery salvestatud")

# =====================
# LINKS (nimi võib sisaldada VAHESID)
# =====================

async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    url = context.args[-1]
    name = " ".join(context.args[:-1])

    links.append({"name": name, "url": url})
    save_links(links)
    await update.message.reply_text("✅ Link lisatud")

# =====================
# BUTTONS
# =====================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "stock":
        await q.edit_message_caption(
            caption=stock_text,
            reply_markup=back()
        )

    elif q.data == "operators":
        if not operators:
            text = "👤 OPERATORS\n\nInfo puudub."
        else:
            rows = ["👤 OPERATORS\n"]
            for username, op in operators.items():
                rows.append(
                    f"{username} | 📍 {op['loc']} | "
                    f"{'🟢 Online' if op['online'] else '🔴 Offline'} | "
                    f"🚚 {'Yes' if op['delivery'] else 'No'}"
                )
            text = "\n".join(rows)

        await q.edit_message_caption(
            caption=text,
            reply_markup=back()
        )

    elif q.data == "links":
        if not links:
            text = "🔗 LINKS\n\nInfo puudub."
        else:
            rows = ["🔗 LINKS\n"]
            for l in links:
                rows.append(f"📢 {l['name']}\n🔗 {l['url']}\n")
            text = "\n".join(rows)

        await q.edit_message_caption(
            caption=text,
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
    app.add_handler(CommandHandler("link", add_link))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot töötab...")
    app.run_polling()

if __name__ == "__main__":
    main()
