import io
import requests
import telebot

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_images(query, limit):
    image_urls = []
    url = f"https://backend.qwant.com/v3/search/images?q={query}&count={limit}&locale=en_US"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', {}).get('result', {}).get('items', [])
            for item in items[:limit]:
                media_url = item.get('media')
                if media_url:
                    image_urls.append(media_url)
        return image_urls
    except Exception as e:
        print(f"خطأ في البحث: {e}")
        return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل اسم البحث والعدد لجلب الصور ⚡\n\nمثال:\n`one piece 3`\n`jax tadc 5`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `one piece 3`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ اختر عدداً بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري جلب {count} صور لـ «{query}»...")

    images = get_images(query, count)

    if not images:
        bot.reply_to(message, "❌ تعذر العثور على صور، حاول بكلمات أخرى.")
        return

    # تحميل الصورة وإرسالها كملف لتفادي حظر تليجرام للروابط
    sent_any = False
    for img_url in images:
        try:
            res = requests.get(img_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if res.status_code == 200:
                photo_bytes = io.BytesIO(res.content)
                bot.send_photo(message.chat.id, photo_bytes)
                sent_any = True
        except Exception as e:
            print(f"خطأ إرسال صورة: {e}")
            continue

    if not sent_any:
        bot.reply_to(message, "❌ تعذر إرسال الصور إلى المحادثة، جرب كلمة بحث أخرى.")

if __name__ == "__main__":
    print("✅ البوت يعمل وجاهز...")
    bot.infinity_polling()
    
