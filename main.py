import os
import telebot
from flask import Flask
from threading import Thread

TOKEN = os.environ.get("TOKEN")

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route("/")
def home():
    return "MoneyGo Bot is Running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_web).start()

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "✅ MoneyGo Bot Online!\nডিপোজিট করতে শুরু করুন।")

print("Bot Started Successfully...")
bot.infinity_polling()
