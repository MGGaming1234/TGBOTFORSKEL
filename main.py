import requests
import telebot

# التوكين الجديد
TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

# دالة البحث في بينترست
def search_pinterest(query, limit):
    url = "https://www.pinterest.com/resource/BaseSearchResource/get/"
    params = {
        "source_param": f'{{"data":{{"query":"{query}"}},"options":{{"page_size":{limit}}}}}'
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        results = data['resource_response']['data']['results']
        
        image_urls = []
        for result in results:
            if 'images' in result and 'orig' in result['images']:
                image_urls.append(result['images']['orig']['url'])
                if len(image_urls) == limit:
                    break
        return image_urls
    except Exception as e:
        print(f"حدث خطأ أثناء جلب الصور: {e}")
        return []

# أمر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل لي اسم الشيء وعدد الصور.\nمثال:\n`سيارات 3`\n`انمي 5`", 
        parse_mode="Markdown"
    )

# استقبال الرسائل
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل الكلمة متبوعة بالعدد.\nمثال: `قطط 3`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ الرجاء اختيار عدد بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري البحث عن {count} صور لـ «{query}»...")

    images = search_pinterest(query, count)

    if not images:
        bot.reply_to(message, "❌ لم يتم العثور على صور.")
        return

    for img_url in images:
        try:
            bot.send_photo(message.chat.id, img_url)
        except Exception:
            continue

# تشغيل البوت
if __name__ == "__main__":
    print("✅ البوت يعمل الآن بنجاح...")
    bot.infinity_polling()
    
