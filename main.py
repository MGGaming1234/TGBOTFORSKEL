import os
import shutil
import uuid
import requests
import urllib.parse
from bs4 import BeautifulSoup
import telebot

TOKEN = "8988279223:AAF3Y5ZKTkWP15P7zNXUJD9gFP7v7odYCP0"

bot = telebot.TeleBot(TOKEN)

def get_accurate_images(query, limit):
    unique_id = str(uuid.uuid4())[:8]
    output_dir = f"dataset_{unique_id}"

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # استخدام Pinterest للوصول لأدق صور الألعاب والشخصيات بدون حظر
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://www.pinterest.com/search/pins/?q={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    image_paths = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # استخراج روابط الصور الحقيقية بدقة عالية
        img_tags = soup.find_all("img")
        urls = []
        
        for img in img_tags:
            src = img.get("src")
            if src and "i.pinimg.com" in src:
                # تحويل الصورة إلى أعلى دقة عالية (originals/736x)
                high_res_url = re.sub(r'/(236x|474x)/', '/736x/', src)
                if high_res_url not in urls:
                    urls.append(high_res_url)

        count = 0
        for img_url in urls:
            if count >= limit:
                break
            try:
                img_data = requests.get(img_url, headers=headers, timeout=5).content
                if len(img_data) > 8192:  # استبعاد الأيقونات والصور التالفة
                    file_path = os.path.join(output_dir, f"img_{count}.jpg")
                    with open(file_path, "wb") as f:
                        f.write(img_data)
                    image_paths.append(file_path)
                    count += 1
            except Exception:
                continue

        return image_paths, output_dir

    except Exception as e:
        print(f"Error fetching from Pinterest: {e}")
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
                
