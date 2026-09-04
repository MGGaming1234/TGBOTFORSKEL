import os
import shutil
import re
import uuid
import telebot
from icrawler.builtin import YandexImageCrawler

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_accurate_images(query, limit):
    unique_id = str(uuid.uuid4())[:8]
    output_dir = f"dataset_{unique_id}"

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    try:
        clean_query = query.strip()

        # Yandex هو الأفضل للألعاب والأنمي وما بيبلكش سيرفرات Railway
        crawler = YandexImageCrawler(
            downloader_threads=4,
            storage={'root_dir': output_dir},
            log_level=50
        )
        
        crawler.crawl(
            keyword=clean_query, 
            max_num=limit + 3,
            min_size=(200, 200)
        )
        
        image_paths = []
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            files.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
            
            for file in files:
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path) and os.path.getsize(file_path) > 5120:
                    image_paths.append(file_path)
                    
        return image_paths[:limit], output_dir
    except Exception as e:
        print(f"Error: {e}")
        return [], output_dir

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل اسم الشخصية والعدد:\n`dmc5 dante 10`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `dmc5 dante 10`", parse_mode="Markdown")
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
    
