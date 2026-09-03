import os
import shutil
import re
import telebot
from bing_image_downloader import downloader

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_top_character_images(query, limit):
    output_dir = "dataset"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # إضافة تركيز دقيق للحصول على النتائج الأولى للشخصية فقط
    strict_query = f"{query.strip()} character"

    try:
        downloader.download(
            strict_query, 
            limit=limit, 
            output_dir=output_dir, 
            adult_filter_off=False, 
            force_replace=False, 
            timeout=10,
            verbose=False
        )
        
        image_paths = []
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                # ترتيب الصور برقم نتيجة البحث المباشرة (Image_1, Image_2, ...)
                files.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.getsize(file_path) > 5120:
                        image_paths.append(file_path)
                    
        return image_paths, output_dir
    except Exception as e:
        print(f"خطأ أثناء الجلب: {e}")
        return [], output_dir

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! أرسل اسم الشخصية والعدد لجلب أصل وأعلى نتائج البحث فوراً 🎯\n\nمثال:\n`dmc5 dante 3`", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().split()

    if len(text) < 2 or not text[-1].isdigit():
        bot.reply_to(message, "⚠️ **خطأ!** أرسل كلمة البحث متبوعة بالعدد.\nمثال: `dmc5 dante 3`", parse_mode="Markdown")
        return

    count = int(text[-1])
    query = " ".join(text[:-1])

    if count < 1 or count > 10:
        bot.reply_to(message, "⚠️ اختر عدداً بين 1 و 10.")
        return

    bot.reply_to(message, f"🔎 جاري جلب أعالي نتائج البحث لـ «{query}»...")

    image_paths, main_folder = get_top_character_images(query, count)

    if not image_paths:
        bot.reply_to(message, "❌ لم يتم العثور على صور مطابقة.")
        return

    # إرسال ألبوم يحتوي على أعلى النتائج المتطابقة بالترتيب
    try:
        media = []
        files = []
        for path in image_paths[:count]:
            f = open(path, 'rb')
            files.append(f)
            media.append(telebot.types.InputMediaPhoto(f))
        
        bot.send_media_group(message.chat.id, media)

        for f in files:
            f.close()
    except Exception as e:
        print(f"فشل إرسال الألبوم، جاري الإرسال الفردي: {e}")
        for path in image_paths[:count]:
            try:
                with open(path, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo)
            except Exception:
                continue

    if os.path.exists(main_folder):
        shutil.rmtree(main_folder)

if __name__ == "__main__":
    print("✅ البوت يعمل لجلب أصل نتائج الشخصيات...")
    bot.infinity_polling()
                    
    
