import os
import shutil
import re
import uuid
import json
import urllib.parse
import requests
import telebot

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_accurate_images(query, limit):
    unique_id = str(uuid.uuid4())[:8]
    output_dir = f"dataset_{unique_id}"

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # محاكاة متصفح حقيقي بالكامل لتجاوز كشف البوتات على Railway
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    encoded_query = urllib.parse.quote(query.strip())
    search_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch&asearch=arc&async=_id:rg_s,_pms:s,_fmt:pc"

    image_paths = []

    try:
        session = requests.Session()
        res = session.get(search_url, headers=headers, timeout=10)
        
        # استخراج روابط الصور الأصلية باستخدام Regex المباشر
        img_urls = re.findall(r'https?://[^\s"]+\.(?:jpg|jpeg|png)', res.text)
        
        # تصفية الروابط واستبعاد المصغرات الضئيلة
        clean_urls = []
        for url in img_urls:
            if "encrypted-tbn0" not in url and "gstatic" not in url:
                if url not in clean_urls:
                    clean_urls.append(url)

        # لو لم يجد صور كبيرة، نأخذ الصور المتاحة
        if not clean_urls:
            clean_urls = list(set(img_urls))

        count = 0
        for img_url in clean_urls:
            if count >= limit:
                break
            try:
                img_res = session.get(img_url, headers=headers, timeout=5)
                if img_res.status_code == 200 and len(img_res.content) > 5120:
                    file_path = os.path.join(output_dir, f"img_{count}.jpg")
                    with open(file_path, "wb") as f:
                        f.write(img_res.content)
                    image_paths.append(file_path)
                    count += 1
            except Exception:
                continue

        return image_paths, output_dir

    except Exception as e:
        print(f"Error: {e}")
        return [], output_dir

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل اسم الشخصية والعدد:\n`dante dmc5 10`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `dante dmc5 10`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 100:
        bot.reply_to(message, "⚠️ اختر عدداً بين 1 و 100.")
        return

    bot.reply_to(message, f"🔎 جاري جلب {count} صورة لـ «{query}»...")

    image_paths, main_folder = get_accurate_images(query, count)

    if not image_paths:
        bot.reply_to(message, "❌ تعذر العثور على صور مطابقة.")
        if os.path.exists(main_folder):
            shutil.rmtree(main_folder)
        return

    chunk_size = 10
    image_chunks = [image_paths[i:i + chunk_size] for i in range(0, len(image_paths), chunk_size)]

    for chunk in image_chunks:
        files = []
        media = []
        try:
            for path in chunk:
                f = open(path, 'rb')
                files.append(f)
                media.append(telebot.types.InputMediaPhoto(f))
            
            bot.send_media_group(message.chat.id, media)
        except Exception as e:
            print(f"Error sending group: {e}")
        finally:
            for f in files:
                f.close()

    if os.path.exists(main_folder):
        shutil.rmtree(main_folder)

if __name__ == "__main__":
    bot.infinity_polling()
    
