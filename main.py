import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ---------------- CONFIG ----------------
TOKEN = "8081107634:AAFZM3FkxoMLcBmOcwwjEgR3BpWBItDHJRE"
ADMIN_ID = 7305414716

NAGAD_NUMBER = "01868991990"
BKASH_NUMBER = "01774610224"

bot = telebot.TeleBot(TOKEN)

# ---------------- BACK KEYBOARD ----------------
def back_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Back"))
    return kb

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💰 Deposit", callback_data="deposit"))
    bot.send_message(
        message.chat.id,
        "Welcome MoneyGo Bot!\n\nDeposit করতে নিচের বাটনে চাপুন।",
        reply_markup=markup
    )

# ---------------- BACK ----------------
@bot.message_handler(func=lambda message: message.text and message.text.lower() == "back")
def go_back(message):
    start(message)

# ---------------- CALLBACK HANDLER ----------------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id

    if call.data == "deposit":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📌 Nagad", callback_data="nagad"))
        markup.add(InlineKeyboardButton("📌 bKash", callback_data="bkash"))
        bot.send_message(call.message.chat.id, "পেমেন্ট মেথড সিলেক্ট করুন:", reply_markup=markup)

    elif call.data in ["nagad", "bkash"]:
        method = "Nagad" if call.data == "nagad" else "bKash"
        number = NAGAD_NUMBER if method == "Nagad" else BKASH_NUMBER
        bot.send_message(
            call.message.chat.id,
            f"✅ {method} Send Money (Personal)\n\n📌 Number: {number}\n\n"
            "টাকা পাঠানোর পর শুধু Transaction ID লিখুন\n❌ স্ক্রিনশট লাগবে না",
            reply_markup=back_keyboard()
        )
        bot.register_next_step_handler(call.message, process_transaction_id, method)

    elif call.data.startswith("approve_") or call.data.startswith("reject_"):
        data = call.data.split("_")
        action = data[0]
        user_id = int(data[1])
        item_type = data[2]

        if action == "approve":
            if item_type == "deposit":
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("💳 BDT Wallet", callback_data=f"wallet_{user_id}"))
                markup.add(InlineKeyboardButton("🎮 Player ID", callback_data=f"player_{user_id}"))
                bot.send_message(
                    user_id,
                    "✅ আপনার পেমেন্ট কমপ্লিট হয়েছে!\n\n"
                    "এখন অপশন নির্বাচন করুন:",
                    reply_markup=markup
                )
            elif item_type in ["wallet", "player"]:
                bot.send_message(
                    user_id,
                    "প্লিজ চেক করুন আপনার ডিপোজিট কমপ্লিট হয়েছে\n\n"
                    "অসংখ্য ধন্যবাদ 😘\n\n"
                    "আবার ডিপোজিট করতে Back বাটনের টাপ করুন",
                    reply_markup=back_keyboard()
                )
            bot.answer_callback_query(call.id, "Approved ✅")
        else:
            bot.send_message(
                user_id,
                "আপনার ভুল ডিটেলস দেওয়ার কারণে পেমেন্ট রিজেক্ট করা হলো\n"
                "এটি দ্বিতীয় বার করলে আপনাকে ব্লক করা হবে",
                reply_markup=back_keyboard()
            )
            bot.answer_callback_query(call.id, "Rejected ❌")

    elif call.data.startswith("wallet_") or call.data.startswith("player_"):
        data = call.data.split("_")
        action = data[0]
        user_id = int(data[1])

        if action == "wallet":
            bot.send_message(user_id, "আপনার MG Wallet নাম্বার দিন:", reply_markup=back_keyboard())
            bot.register_next_step_handler(call.message, receive_wallet, user_id)
        else:
            bot.send_message(user_id, "আপনার Player ID এবং Password দিন (এক লাইনে):", reply_markup=back_keyboard())
            bot.register_next_step_handler(call.message, receive_player, user_id)

# ---------------- TRANSACTION ID ----------------
def process_transaction_id(message, method):
    if message.text.lower() == "back":
        start(message)
        return
    txn_id = message.text.strip()
    user_id = message.from_user.id
    bot.send_message(
        user_id,
        "⏳ আপনার পেমেন্ট চেক করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...",
        reply_markup=back_keyboard()
    )

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}_deposit"))
    markup.add(InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}_deposit"))

    bot.send_message(
        ADMIN_ID,
        f"🆕 New Deposit Request\n\n👤 User ID: {user_id}\n💳 Method: {method}\n🧾 Transaction ID: {txn_id}",
        reply_markup=markup
    )

# ---------------- WALLET ----------------
def receive_wallet(message, user_id):
    if message.text.lower() == "back":
        start(message)
        return
    wallet = message.text.strip()
    bot.send_message(user_id, "⏳ Pending...", reply_markup=back_keyboard())
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}_wallet"))
    markup.add(InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}_wallet"))
    bot.send_message(
        ADMIN_ID,
        f"📌 Wallet Request\n\nUser: {user_id}\nMG Wallet: {wallet}",
        reply_markup=markup
    )

# ---------------- PLAYER ----------------
def receive_player(message, user_id):
    if message.text.lower() == "back":
        start(message)
        return
    player_info = message.text.strip()
    bot.send_message(user_id, "⏳ Pending...", reply_markup=back_keyboard())
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}_player"))
    markup.add(InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}_player"))
    bot.send_message(
        ADMIN_ID,
        f"🎮 Player Request\n\nUser: {user_id}\nPlayer Info: {player_info}",
        reply_markup=markup
    )

# ---------------- RUN BOT ----------------
print("Bot is starting...")
bot.infinity_polling()
