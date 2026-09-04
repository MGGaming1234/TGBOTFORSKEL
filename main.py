import os
import shutil
import uuid
import requests
import telebot
from duckduckgo_search import DDGS

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_accurate_images(query, limit):
    unique_id = str(uuid.uuid4())[:8]
    output_dir = f"dataset_{unique_id}"

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    image_paths = []

    try:
        # البحث باستخدام DuckDuckGo بـ Headers متصفح حقيقي لتفادي الحظر
        results = []
        with DDGS() as ddgs:
            ddgs_gen = ddgs.images(
                keywords=query.strip(),
                region="wt-wt",
                safesearch="off",
                max_results=limit + 10
            )
            for r in ddgs_gen:
                results.append(r)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        }

        count = 0
        for res in results:
            if count >= limit:
                break
            
            img_url = res.get("image")
            if not img_url:
                continue

            try:
                resp = requests.get(img_url, headers=headers, timeout=6)
                if resp.status_code == 200 and len(resp.content) > 10240:
                    file_path = os.path.join(output_dir, f"img_{count}.jpg")
                    with open(file_path, "wb") as f:
                        f.write(resp.content)
                    image_paths.append(file_path)
                    count += 1
            except Exception:
                continue

        return image_paths, output_dir

    except Exception as e:
        print(f"Error fetching images: {e}")
        return [], output_dir

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل اسم الشخصية والعدد:\n`Dante dmc5 10`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `Dante dmc5 10`", parse_mode="Markdown")
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
            
