import telebot, requests, time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "BOT_TOKEN" #Put token here
API_KEY   = "crazy" #Dont change key

bot = telebot.TeleBot(BOT_TOKEN)

def tg2num(tg_id, tries=5, delay=1.5):
    for _ in range(tries):
        try:
            r = requests.get(
                "https://aerosend.bond/tgtonum.php",
                params={"key": API_KEY, "num": tg_id},
                timeout=10,
            ).json()
            if r.get("status") == "success":
                return r
        except Exception:
            pass
        time.sleep(delay)

@bot.message_handler(commands=["start"])
def start(m):
    text = (
        "==========================\n"
        "🤖 <b>Welcome to Tg Search Bot</b>\n"
        "==========================\n\n"
        "🔎 <b>How to use</b>\n"
        "Just send me a <b>Telegram ID</b> (numeric)\n"
        "and I'll fetch its linked info.\n\n"
        "⚡ <b>Features</b>\n"
        "• Fast lookup\n"
        "• Country & carrier info\n"
        "• Tap-to-copy results\n\n"
        "🟢 <b>Status:</b> Online\n"
        "🔎 <b>Search:</b> /search or just send an ID\n\n"
        "<i>By Crazy | @PokiePy</i>"
    )
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔎 Search Now", callback_data="search"))
    bot.send_message(m.chat.id, text, parse_mode="HTML", reply_markup=kb)

@bot.message_handler(commands=["search"])
def search_cmd(m):
    bot.reply_to(m, "🔎 Send me a Telegram ID (numeric) to search.")

@bot.message_handler(func=lambda m: True)
def lookup(m):
    tg_id = m.text.strip()
    if not tg_id.isdigit():
        bot.reply_to(m, "❌ ID must be numeric.")
        return

    msg = bot.reply_to(m, "🔎 Searching…")
    data = tg2num(tg_id)

    if not data:
        bot.edit_message_text("❌ No data found.", m.chat.id, msg.message_id)
        return

    text = (
        "==========================\n"
        "📱 <b>Tg Search Result</b>\n"
        "======================\n\n"
        f"<b>TG ID:</b> <code>{data.get('tg_id')}</code>\n"
        f"<b>Mobile:</b> <code>{data.get('mobile')}</code>\n"
        f"<b>Country Code:</b> {data.get('country_code')}\n"
        f"<b>Country:</b> {data.get('country')}\n\n"
        "🟢 <b>Status:</b> Online\n\n"
        "<i>By Crazy | @PokiePy</i>"
    )
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📋 Copy Number", callback_data=f"copy:{data.get('mobile')}"))
    kb.add(InlineKeyboardButton("🔎 Search Again", callback_data="search"))
    bot.edit_message_text(text, m.chat.id, msg.message_id,
                          parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data == "search":
        bot.answer_callback_query(c.id)
        bot.send_message(c.message.chat.id, "🔎 Send me a Telegram ID (numeric).")
    elif c.data.startswith("copy:"):
        num = c.data.split(":", 1)[1]
        bot.answer_callback_query(c.id, f"Copied: {num}", show_alert=True)

bot.infinity_polling()