import random
import os,subprocess,sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try :
    import arabic_reshaper
except ImportError :
    install("arabic_reshaper")

try :
    from bidi.algorithm import get_display
except ImportError:
    install("python-bidi")
    
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    install("pillow") 
try:
    import rubpy
    from rubpy import Client, filters, utils
    from rubpy.types import Updates
except ImportError:
    install('rubpy')
    import rubpy
    from rubpy import Client, filters, utils, exceptions
    from rubpy.types import Updates  


bot = Client(name='LEGO')

# لیست فونت‌های تصادفی (فارسی و انگلیسی)
FONT_PATHS = [
    "fonts/Arial.ttf",         # فونت انگلیسی
    "fonts/Roboto-Regular.ttf", # فونت انگلیسی
    "fonts/Vazir-Regular.ttf",  # فونت فارسی
    "fonts/IranSans.ttf",       # فونت فارسی
]

# تابع برای ایجاد یک رنگ تصادفی
def random_color(brightness=255):
    return tuple(random.randint(0, brightness) for _ in range(3))

# تابع برای محاسبه میزان تضاد رنگی (contrast)
def calculate_brightness(color):
    return (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000

def is_contrasting(color1, color2):
    return abs(calculate_brightness(color1) - calculate_brightness(color2)) > 125

# تابع برای انتخاب یک رنگ تصادفی که با پس‌زمینه تضاد کافی داشته باشد
def random_contrasting_color(background_color):
    text_color = random_color()
    while not is_contrasting(text_color, background_color):
        text_color = random_color()
    return text_color

# تابع برای انتخاب یک فونت تصادفی با اندازه دلخواه
def get_random_font(text, size):
    # انتخاب فونت بر اساس متن (اگر متن فارسی باشد فونت فارسی انتخاب می‌شود)
    if any('\u0600' <= char <= '\u06FF' for char in text):  # بررسی وجود کاراکترهای فارسی
        font_path = random.choice(FONT_PATHS[2:])  # انتخاب فونت فارسی
    else:
        font_path = random.choice(FONT_PATHS[:2])  # انتخاب فونت انگلیسی
    return ImageFont.truetype(font_path, size)

# تابع برای رسم سایه زیر متن
def draw_text_with_shadow(draw, position, text, font, text_color, shadow_color, offset):
    # رسم سایه با استفاده از افست (مثلاً 2 پیکسل به چپ و پایین)
    x, y = position
    draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
    # رسم متن اصلی روی سایه
    draw.text(position, text, font=font, fill=text_color)

# تابع برای ایجاد گرادیانت رنگی به عنوان پس‌زمینه
def create_gradient_background(size, color1, color2):
    base = Image.new('RGB', size, color1)
    top = Image.new('RGB', size, color2)
    mask = Image.new('L', size)
    for y in range(size[1]):
        for x in range(size[0]):
            mask.putpixel((x, y), int(255 * (y / size[1])))
    base.paste(top, (0, 0), mask)
    return base

# تابع برای ایجاد لوگو با افکت‌های پیشرفته
def create_random_logo(text):
    width, height = 800, 400
    # ایجاد گرادیانت رنگی برای پس‌زمینه
    background_color1 = random_color()
    background_color2 = random_color(brightness=200)
    img = create_gradient_background((width, height), background_color1, background_color2)
    draw = ImageDraw.Draw(img)

    # ایجاد چند دایره و مستطیل تصادفی در پس‌زمینه
    for _ in range(5):
        shape_type = random.choice(['circle', 'rectangle'])
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = x1 + random.randint(50, 200), y1 + random.randint(50, 200)
        if shape_type == 'circle':
            draw.ellipse([x1, y1, x2, y2], fill=random_color(), outline=random_color())
        elif shape_type == 'rectangle':
            draw.rectangle([x1, y1, x2, y2], fill=random_color(), outline=random_color())

    # اگر متن فارسی است، از reshaper و bidi استفاده می‌کنیم
    if any('\u0600' <= char <= '\u06FF' for char in text):
        reshaped_text = arabic_reshaper.reshape(text)  # تنظیم متن فارسی
        bidi_text = get_display(reshaped_text)  # نمایش صحیح متن
        text = bidi_text

    # انتخاب یک فونت تصادفی با اندازه مناسب
    font = get_random_font(text, random.randint(50, 100))

    # اندازه متن برای تعیین موقعیت مرکزی
    text_width, text_height = draw.textsize(text, font=font)
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # انتخاب رنگ متنی که با پس‌زمینه تضاد داشته باشد
    text_color = random_contrasting_color(background_color1)
    shadow_color = random_contrasting_color(background_color2)

    # رسم متن با سایه و رنگ تصادفی
    draw_text_with_shadow(draw, (text_x, text_y), text, font, text_color, shadow_color, 4)

    # افکت محو برای جذابیت بیشتر
    img = img.filter(ImageFilter.GaussianBlur(1))

    # ذخیره لوگو
    logo_name = f"{text}_random_logo.png"
    img.save(logo_name)

    return logo_name

# عملکرد ربات: دریافت پیام و تولید لوگو
@bot.on_message_updates(filters.is_private)
async def updates(update: Updates):
    input_text = update.text.strip()
    await update.reply("درحال ساخت لگو")
    # ایجاد لوگو برای متن ورودی
    logo_file = create_random_logo(input_text)

    # ارسال لوگو
    await update.reply_photo(logo_file, caption="لگوی شما اماده شد ")
    

# اجرای ربات
bot.run()

