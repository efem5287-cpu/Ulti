import os
import subprocess
from flask import Flask, request
import telebot

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL") # Automatically provided by Render

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def index():
    return "[+] Bot is active and running on Render.", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "[+] Render C2 Node Online.")

@bot.message_handler(commands=['shell'])
def handle_shell(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    command = message.text.replace("/shell", "").strip()
    if not command:
        bot.reply_to(message, "[-] No command provided.")
        return

    try:
        output = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        result = output.stdout + output.stderr
        if not result:
            result = "[+] Executed with no output."
    except Exception as e:
        result = f"[-] Error: {str(e)}"

    if len(result) > 4000:
        result = result[:4000] + "\n[Truncated]"

    bot.reply_to(message, f"```\n{result}\n```", parse_mode="Markdown")

if __name__ == "__main__":
    # Remove existing webhook and set new one if URL is available
    if RENDER_EXTERNAL_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{TOKEN}")
        print(f"[+] Webhook set to: {RENDER_EXTERNAL_URL}/{TOKEN}")

    # Render requires binding to 0.0.0.0 and the dynamic PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
  
