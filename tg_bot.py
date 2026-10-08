import telebot
import requests
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# =========================
# CONFIGURATION
# =========================

BOT_TOKEN = "8078339956:AAG-OH0m-BpcrmIfOIyaGjVxcFJba5aRi5E"  # Put your bot token here
API_KEY = "crazy"  # Keep unchanged

# Force Join Configuration
# Use @channelusername OR numeric channel ID.
# Set to None to disable that channel.
FORCE_JOIN_CHANNEL_1 = "@SpicyxNetwork"
FORCE_JOIN_CHANNEL_2 = "@SpicyxNetwork"

# Public usernames used for the Join buttons.
# These should normally match the channels above when using @username.
FORCE_JOIN_LINK_1 = "https://t.me/Attracted2Her"
FORCE_JOIN_LINK_2 = "https://t.me/Attracted2Her"

# =========================
# BOT
# =========================

bot = telebot.TeleBot(BOT_TOKEN)


# =========================
# TELEGRAM MEMBERSHIP CHECK
# =========================

def is_user_joined(user_id, channel):
    """
    Check whether a Telegram user is a member of the specified channel.

    The bot must have sufficient permissions in the channel to reliably
    retrieve membership information.
    """

    if not channel:
        return True

    try:
        member = bot.get_chat_member(channel, user_id)

        return member.status in (
            "creator",
            "administrator",
            "member",
        )

    except Exception:
        return False


def check_force_join(user_id):
    """
    Returns:
        True  -> user has joined all configured channels
        False -> user has not joined one or more channels
    """

    channels = [
        FORCE_JOIN_CHANNEL_1,
        FORCE_JOIN_CHANNEL_2,
    ]

    for channel in channels:
        if channel and not is_user_joined(user_id, channel):
            return False

    return True


# =========================
# FORCE JOIN KEYBOARD
# =========================

def force_join_keyboard():
    kb = InlineKeyboardMarkup()

    if FORCE_JOIN_CHANNEL_1:
        kb.add(
            InlineKeyboardButton(
                "📢 Join Channel 1",
                url=FORCE_JOIN_LINK_1
            )
        )

    if FORCE_JOIN_CHANNEL_2:
        kb.add(
            InlineKeyboardButton(
                "📢 Join Channel 2",
                url=FORCE_JOIN_LINK_2
            )
        )

    kb.add(
        InlineKeyboardButton(
            "✅ I Joined — Check Again",
            callback_data="check_join"
        )
    )

    return kb


def send_force_join_message(chat_id):
    text = (
        "🔒 <b>Join Required</b>\n\n"
        "To use this bot, you must join the required channel"
        " before continuing.\n\n"
        "After joining, press <b>✅ I Joined — Check Again</b>.\n\n"
        "🤖 <b>Provided by @SpicyxNetwork</b>"
    )

    bot.send_message(
        chat_id,
        text,
        parse_mode="HTML",
        reply_markup=force_join_keyboard()
    )


# =========================
# TELEGRAM ID LOOKUP
# =========================

def tg2num(tg_id, tries=5, delay=1.5):
    for _ in range(tries):
        try:
            r = requests.get(
                "https://aerosend.bond/tgtonum.php",
                params={
                    "key": API_KEY,
                    "num": tg_id
                },
                timeout=10,
            )

            data = r.json()

            if data.get("status") == "success":
                return data

        except Exception:
            pass

        time.sleep(delay)

    return None


# =========================
# /START
# =========================

@bot.message_handler(commands=["start"])
def start(m):

    # Force join check
    if not check_force_join(m.from_user.id):
        send_force_join_message(m.chat.id)
        return

    text = (
        "==========================\n"
        "🤖 <b>Welcome to Tg Search Bot</b>\n"
        "==========================\n\n"
        "🔎 <b>How to use</b>\n"
        "Send me a <b>Telegram ID</b> (numeric)\n"
        "and I'll process your request.\n\n"
        "⚡ <b>Features</b>\n"
        "• Fast lookup\n"
        "• Country & carrier information\n"
        "• Tap-to-copy results\n\n"
        "🟢 <b>Status:</b> Online\n"
        "🔎 <b>Search:</b> /search or just send an ID\n\n"
        "<i>Provided by @SpicyxNetwork</i>"
    )

    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton(
            "🔎 Search Now",
            callback_data="search"
        )
    )

    bot.send_message(
        m.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=kb
    )


# =========================
# /SEARCH
# =========================

@bot.message_handler(commands=["search"])
def search_cmd(m):

    if not check_force_join(m.from_user.id):
        send_force_join_message(m.chat.id)
        return

    bot.reply_to(
        m,
        "🔎 Send me a Telegram ID (numeric) to search."
    )


# =========================
# LOOKUP
# =========================

@bot.message_handler(func=lambda m: True)
def lookup(m):

    # Check force join before processing messages
    if not check_force_join(m.from_user.id):
        send_force_join_message(m.chat.id)
        return

    if not m.text:
        return

    tg_id = m.text.strip()

    if not tg_id.isdigit():
        bot.reply_to(
            m,
            "❌ ID must be numeric."
        )
        return

    msg = bot.reply_to(
        m,
        "🔎 Searching…"
    )

    data = tg2num(tg_id)

    if not data:
        bot.edit_message_text(
            "❌ No data found.",
            m.chat.id,
            msg.message_id
        )
        return

    text = (
        "==========================\n"
        "📱 <b>Tg Search Result</b>\n"
        "==========================\n\n"
        f"<b>TG ID:</b> <code>{data.get('tg_id')}</code>\n"
        f"<b>Mobile:</b> <code>{data.get('mobile')}</code>\n"
        f"<b>Country Code:</b> {data.get('country_code')}\n"
        f"<b>Country:</b> {data.get('country')}\n\n"
        "🟢 <b>Status:</b> Online\n\n"
        "<i>Provided by @SpicyxNetwork</i>"
    )

    kb = InlineKeyboardMarkup()

    mobile = data.get("mobile")

    if mobile:
        kb.add(
            InlineKeyboardButton(
                "📋 Copy Number",
                callback_data=f"copy:{mobile}"
            )
        )

    kb.add(
        InlineKeyboardButton(
            "🔎 Search Again",
            callback_data="search"
        )
    )

    bot.edit_message_text(
        text,
        m.chat.id,
        msg.message_id,
        parse_mode="HTML",
        reply_markup=kb
    )


# =========================
# CALLBACKS
# =========================

@bot.callback_query_handler(func=lambda c: True)
def cb(c):

    # -------------------------
    # Force Join Check
    # -------------------------

    if c.data == "check_join":

        if check_force_join(c.from_user.id):

            bot.answer_callback_query(
                c.id,
                "✅ Membership confirmed!"
            )

            text = (
                "==========================\n"
                "🤖 <b>Welcome to Tg Search Bot</b>\n"
                "==========================\n\n"
                "🔎 <b>How to use</b>\n"
                "Send me a <b>Telegram ID</b> (numeric)\n"
                "and I'll process your request.\n\n"
                "⚡ <b>Features</b>\n"
                "• Fast lookup\n"
                "• Country & carrier information\n"
                "• Tap-to-copy results\n\n"
                "🟢 <b>Status:</b> Online\n\n"
                "<i>Provided by @SpicyxNetwork</i>"
            )

            kb = InlineKeyboardMarkup()

            kb.add(
                InlineKeyboardButton(
                    "🔎 Search Now",
                    callback_data="search"
                )
            )

            try:
                bot.edit_message_text(
                    text,
                    c.message.chat.id,
                    c.message.message_id,
                    parse_mode="HTML",
                    reply_markup=kb
                )
            except Exception:
                bot.send_message(
                    c.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=kb
                )

        else:

            bot.answer_callback_query(
                c.id,
                "❌ You haven't joined all required channels yet.",
                show_alert=True
            )

        return

    # -------------------------
    # Search
    # -------------------------

    if c.data == "search":

        if not check_force_join(c.from_user.id):
            bot.answer_callback_query(
                c.id,
                "❌ Please join the required channel(s) first.",
                show_alert=True
            )

            send_force_join_message(
                c.message.chat.id
            )

            return

        bot.answer_callback_query(c.id)

        bot.send_message(
            c.message.chat.id,
            "🔎 Send me a Telegram ID (numeric)."
        )

        return

    # -------------------------
    # Copy Number
    # -------------------------

    if c.data.startswith("copy:"):

        # Membership check before displaying the callback result
        if not check_force_join(c.from_user.id):
            bot.answer_callback_query(
                c.id,
                "❌ Please join the required channel(s) first.",
                show_alert=True
            )
            return

        num = c.data.split(":", 1)[1]

        bot.answer_callback_query(
            c.id,
            f"Copied: {num}",
            show_alert=True
        )


# =========================
# START BOT
# =========================

print("🤖 Bot started...")
print("📢 Force Join system enabled.")
print("🌐 Provided by @SpicyxNetwork")

bot.infinity_polling()
