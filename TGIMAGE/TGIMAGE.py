import os
import logging
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import random
import textwrap

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Токен бота (ЗАМЕНИТЕ НА СВОЙ!)
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Создаем папки для временных файлов
os.makedirs("temp", exist_ok=True)
os.makedirs("fonts", exist_ok=True)

# Состояния пользователей
user_states = {}


# ===== КЛАВИАТУРЫ =====
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('🎨 Эффекты'),
        KeyboardButton('✂️ Инструменты'),
        KeyboardButton('🖼️ Рамки'),
        KeyboardButton('🔠 Текст'),
        KeyboardButton('🌟 Премиум'),
        KeyboardButton('❓ Помощь')
    ]
    markup.add(*buttons)
    return markup


def effects_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('⚫ Ч/Б'),
        KeyboardButton('🟫 Сепия'),
        KeyboardButton('🔍 Резкость'),
        KeyboardButton('🌫️ Размытие'),
        KeyboardButton('📝 Эскиз'),
        KeyboardButton('🎭 Винтаж'),
        KeyboardButton('🌈 Яркость+'),
        KeyboardButton('🌙 Контраст+'),
        KeyboardButton('↩️ Назад')
    ]
    markup.add(*buttons)
    return markup


def tools_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('🔄 Повернуть'),
        KeyboardButton('✂️ Обрезать'),
        KeyboardButton('📏 Размер'),
        KeyboardButton('🎯 Обрезать круг'),
        KeyboardButton('↩️ Назад')
    ]
    markup.add(*buttons)
    return markup


def frames_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('🖼️ Классическая'),
        KeyboardButton('📸 Поляроид'),
        KeyboardButton('⭐ Золотая'),
        KeyboardButton('🎞️ Пленка'),
        KeyboardButton('↩️ Назад')
    ]
    markup.add(*buttons)
    return markup


def text_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('💬 Добавить текст'),
        KeyboardButton('😂 Создать мем'),
        KeyboardButton('🔡 Шрифты'),
        KeyboardButton('🎨 Цвет текста'),
        KeyboardButton('↩️ Назад')
    ]
    markup.add(*buttons)
    return markup


# ===== ОСНОВНЫЕ ОБРАБОТЧИКИ =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_states[user_id] = {'current_menu': 'main'}

    welcome_text = """
    🎉 *Добро пожаловать в PhotoMagicBot!* 🎉

    ✨ *Я могу:* 
    • Применять крутые эффекты к фото
    • Добавлять текст и создавать мемы
    • Обрезать и поворачивать изображения
    • Добавлять красивые рамки
    • И многое другое!

    📸 *Просто отправьте мне фото и выберите действие!*

    🚀 *Начните с отправки фото или выберите опцию из меню ниже*
    """

    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=main_menu()
    )


@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    🤖 *Как использовать бота:*

    1. 📸 *Отправьте фото* - просто пришлите любое изображение
    2. 🎨 *Выберите действие* - используйте кнопки меню
    3. ⚡ *Получите результат* - бот обработает фото

    ✨ *Доступные функции:*
    • 🎨 Эффекты - фильтры и преобразования
    • ✂️ Инструменты - обрезка, поворот, изменение размера
    • 🖼️ Рамки - красивые обрамления для фото
    • 🔠 Текст - добавление надписей и создание мемов

    💡 *Совет:* Для лучшего качества отправляйте фото в высоком разрешении!
    """

    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='Markdown',
        reply_markup=main_menu()
    )


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        user_id = message.chat.id

        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем оригинал
        original_path = f"temp/{user_id}_original.jpg"
        with open(original_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Сохраняем информацию о фото
        if user_id not in user_states:
            user_states[user_id] = {}
        user_states[user_id]['has_photo'] = True

        bot.send_message(
            message.chat.id,
            "✅ *Фото получено!* Выберите действие из меню ниже 🎨",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при загрузке фото")
        logging.error(f"Error handling photo: {e}")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    text = message.text

    # Проверяем есть ли фото
    has_photo = user_states.get(user_id, {}).get('has_photo', False)

    if not has_photo and text not in ['❓ Помощь', '/start', '/help']:
        bot.send_message(
            message.chat.id,
            "📸 *Сначала отправьте мне фото!* Затем выберите действие из меню.",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        return

    # Обработка меню
    if text == '↩️ Назад':
        user_states[user_id]['current_menu'] = 'main'
        bot.send_message(message.chat.id, "📋 Главное меню:", reply_markup=main_menu())

    elif text == '🎨 Эффекты':
        user_states[user_id]['current_menu'] = 'effects'
        bot.send_message(message.chat.id, "🎨 Выберите эффект:", reply_markup=effects_menu())

    elif text == '✂️ Инструменты':
        user_states[user_id]['current_menu'] = 'tools'
        bot.send_message(message.chat.id, "⚒️ Инструменты редактирования:", reply_markup=tools_menu())

    elif text == '🖼️ Рамки':
        user_states[user_id]['current_menu'] = 'frames'
        bot.send_message(message.chat.id, "🖼️ Выберите рамку:", reply_markup=frames_menu())

    elif text == '🔠 Текст':
        user_states[user_id]['current_menu'] = 'text'
        bot.send_message(message.chat.id, "🔠 Работа с текстом:", reply_markup=text_menu())

    elif text == '❓ Помощь':
        send_help(message)

    # Обработка эффектов
    elif text == '⚫ Ч/Б':
        apply_effect(message, 'black_white')
    elif text == '🟫 Сепия':
        apply_effect(message, 'sepia')
    elif text == '🔍 Резкость':
        apply_effect(message, 'sharpen')
    elif text == '🌫️ Размытие':
        apply_effect(message, 'blur')
    elif text == '📝 Эскиз':
        apply_effect(message, 'sketch')
    elif text == '🎭 Винтаж':
        apply_effect(message, 'vintage')
    elif text == '🌈 Яркость+':
        apply_effect(message, 'brightness')
    elif text == '🌙 Контраст+':
        apply_effect(message, 'contrast')

    # Обработка инструментов
    elif text == '🔄 Повернуть':
        rotate_image(message)
    elif text == '✂️ Обрезать':
        bot.send_message(message.chat.id, "✂️ Отправьте мне фото с указанием области для обрезки (покажите в описании)")
    elif text == '📏 Размер':
        resize_image(message)
    elif text == '🎯 Обрезать круг':
        crop_circle(message)

    # Обработка рамок
    elif text in ['🖼️ Классическая', '📸 Поляроид', '⭐ Золотая', '🎞️ Пленка']:
        frame_type = text.split(' ')[1].lower()
        add_frame(message, frame_type)

    # Обработка текста
    elif text == '💬 Добавить текст':
        bot.send_message(message.chat.id, "💬 Введите текст для добавления на фото:")
        user_states[user_id]['waiting_for_text'] = True

    elif text == '😂 Создать мем':
        create_meme(message)

    else:
        if user_states.get(user_id, {}).get('waiting_for_text'):
            add_text_to_image(message, text)
            user_states[user_id]['waiting_for_text'] = False
        else:
            bot.send_message(message.chat.id, "Выберите действие из меню 👇", reply_markup=main_menu())


# ===== ФУНКЦИИ ОБРАБОТКИ ИЗОБРАЖЕНИЙ =====
def apply_effect(message, effect_type):
    try:
        user_id = message.chat.id
        original_path = f"temp/{user_id}_original.jpg"

        if not os.path.exists(original_path):
            bot.send_message(message.chat.id, "❌ Сначала отправьте фото!")
            return

        with Image.open(original_path) as img:
            if effect_type == 'black_white':
                result = img.convert("L")
                caption = "✅ Чёрно-белый эффект применен!"

            elif effect_type == 'sepia':
                result = apply_sepia_filter(img)
                caption = "✅ Эффект сепии применен!"

            elif effect_type == 'sharpen':
                result = img.filter(ImageFilter.SHARPEN)
                caption = "✅ Резкость повышена!"

            elif effect_type == 'blur':
                result = img.filter(ImageFilter.BLUR)
                caption = "✅ Размытие применено!"

            elif effect_type == 'sketch':
                result = img.filter(ImageFilter.CONTOUR)
                caption = "✅ Эскиз создан!"

            elif effect_type == 'vintage':
                result = apply_vintage_filter(img)
                caption = "✅ Винтажный эффект применен!"

            elif effect_type == 'brightness':
                enhancer = ImageEnhance.Brightness(img)
                result = enhancer.enhance(1.5)
                caption = "✅ Яркость увеличена!"

            elif effect_type == 'contrast':
                enhancer = ImageEnhance.Contrast(img)
                result = enhancer.enhance(1.5)
                caption = "✅ Контрастность увеличена!"

            # Сохраняем результат
            result_path = f"temp/{user_id}_result.jpg"
            result.save(result_path, "JPEG", quality=95)

            # Отправляем результат
            with open(result_path, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=caption,
                    reply_markup=main_menu()
                )

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при обработке фото")
        logging.error(f"Error applying effect {effect_type}: {e}")


def apply_sepia_filter(img):
    width, height = img.size
    pixels = img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = img.getpixel((px, py))

            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)

            pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))

    return img


def apply_vintage_filter(img):
    # Добавляем винтажный эффект
    img = img.convert('RGB')
    r, g, b = img.split()

    # Корректируем каналы
    r = r.point(lambda i: i * 1.1)
    g = g.point(lambda i: i * 0.9)
    b = b.point(lambda i: i * 0.8)

    result = Image.merge('RGB', (r, g, b))
    result = result.filter(ImageFilter.SMOOTH)

    return result


def rotate_image(message):
    try:
        user_id = message.chat.id
        original_path = f"temp/{user_id}_original.jpg"

        with Image.open(original_path) as img:
            # Поворачиваем на 90 градусов
            rotated = img.rotate(90, expand=True)

            result_path = f"temp/{user_id}_result.jpg"
            rotated.save(result_path, "JPEG", quality=95)

            with open(result_path, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption="✅ Фото повернуто на 90°!",
                    reply_markup=main_menu()
                )

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при повороте фото")
        logging.error(f"Error rotating image: {e}")


def resize_image(message):
    try:
        user_id = message.chat.id
        original_path = f"temp/{user_id}_original.jpg"

        with Image.open(original_path) as img:
            # Уменьшаем размер в 2 раза
            width, height = img.size
            new_size = (width // 2, height // 2)
            resized = img.resize(new_size, Image.LANCZOS)

            result_path = f"temp/{user_id}_result.jpg"
            resized.save(result_path, "JPEG", quality=95)

            with open(result_path, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=f"✅ Размер изменен: {new_size[0]}x{new_size[1]}",
                    reply_markup=main_menu()
                )

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при изменении размера")
        logging.error(f"Error resizing image: {e}")


def crop_circle(message):
    try:
        user_id = message.chat.id
        original_path = f"temp/{user_id}_original.jpg"

        with Image.open(original_path) as img:
            # Создаем круглую маску
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img.size, fill=255)

            # Применяем маску
            result = Image.new('RGBA', img.size)
            result.paste(img, (0, 0), mask=mask)

            result_path = f"temp/{user_id}_result.png"
            result.save(result_path, "PNG")

            with open(result_path, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption="✅ Круглое фото готово!",
                    reply_markup=main_menu()
                )

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при создании круглого фото")
        logging.error(f"Error cropping circle: {e}")


def add_frame(message, frame_type):
    try:
        user_id = message.chat.id
        original_path = f"temp/{user_id}_original.jpg"

        with Image.open(original_path) as img:
            # Создаем рамку
            if frame_type == 'классическая':
                border_size = 20
                border_color = (255, 255, 255)
            elif frame_type == 'поляроид':
                border_size = (40, 60, 40, 40)  # top, right, bottom, left
                border_color = (255, 255, 255)
            elif frame_type == 'золотая':
                border_size = 15
                border_color = (255, 215, 0)
            else:  # пленка
                border_size = (30, 20, 30, 20)
                border_color = (0, 0, 0)

            if isinstance(border_size, int):
                result = ImageOps.expand(img, border=border_size, fill=border_color)
            else:
                result = ImageOps.expand(img, border=border_size, fill=border_color)

            result_path = f"temp/{user_id}_result.jpg"
            result.save(result_path, "JPEG", quality=95)

            with open(result_path, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=f"✅ Рамка '{frame_type}' добавлена!",
                    reply_markup=main_menu()
                )

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при добавлении рамки")
        logging.error(f"Error adding frame: {e}")


def add_text_to_image(message, text):
    try:
        user_id = message.chat.id
        original_path = f"temp/{user_id}_original.jpg"

        with Image.open(original_path) as img:
            draw = ImageDraw.Draw(img)

            # Простой шрифт (можно заменить на свой)
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()

            # Позиция текста
            text_position = (50, 50)
            text_color = (255, 255, 255)

            # Добавляем обводку
            draw.text((text_position[0] - 2, text_position[1] - 2), text, (0, 0, 0), font=font)
            draw.text((text_position[0] + 2, text_position[1] - 2), text, (0, 0, 0), font=font)
            draw.text((text_position[0] - 2, text_position[1] + 2), text, (0, 0, 0), font=font)
            draw.text((text_position[0] + 2, text_position[1] + 2), text, (0, 0, 0), font=font)

            # Основной текст
            draw.text(text_position, text, text_color, font=font)

            result_path = f"temp/{user_id}_result.jpg"
            img.save(result_path, "JPEG", quality=95)

            with open(result_path, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption="✅ Текст добавлен на фото!",
                    reply_markup=main_menu()
                )

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при добавлении текста")
        logging.error(f"Error adding text: {e}")


def create_meme(message):
    try:
        user_id = message.chat.id
        original_path = f"temp/{user_id}_original.jpg"

        def create_meme(message):
            try:
                user_id = message.chat.id

                # Проверяем, есть ли фото
                original_path = f"temp/{user_id}_original.jpg"
                if not os.path.exists(original_path):
                    bot.send_message(message.chat.id, "❌ Сначала отправьте фото!")
                    return

                # Переходим в режим ввода текста для мема
                user_states[user_id] = {
                    'waiting_for_meme_top': True,
                    'waiting_for_meme_bottom': False
                }

                bot.send_message(
                    message.chat.id,
                    "💬 *Введите текст для ВЕРХНЕЙ части мема:*",
                    parse_mode='Markdown'
                )

            except Exception as e:
                bot.send_message(message.chat.id, "❌ Ошибка при создании мема")
                logging.error(f"Error creating meme: {e}")

        # Обработчик ввода текста для мема
        @bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('waiting_for_meme_top'))
        def handle_meme_top_text(message):
            try:
                user_id = message.chat.id
                top_text = message.text

                # Сохраняем верхний текст
                user_states[user_id]['meme_top_text'] = top_text
                user_states[user_id]['waiting_for_meme_top'] = False
                user_states[user_id]['waiting_for_meme_bottom'] = True

                bot.send_message(
                    message.chat.id,
                    "💬 *Введите текст для НИЖНЕЙ части мема:*",
                    parse_mode='Markdown'
                )

            except Exception as e:
                bot.send_message(message.chat.id, "❌ Ошибка при обработке текста")
                logging.error(f"Error handling meme text: {e}")

        @bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('waiting_for_meme_bottom'))
        def handle_meme_bottom_text(message):
            try:
                user_id = message.chat.id
                bottom_text = message.text

                # Получаем сохраненный верхний текст
                top_text = user_states[user_id].get('meme_top_text', '')

                # Создаем мем
                create_meme_with_text(user_id, top_text, bottom_text)

                # Сбрасываем состояние
                user_states[user_id]['waiting_for_meme_bottom'] = False
                del user_states[user_id]['meme_top_text']

            except Exception as e:
                bot.send_message(message.chat.id, "❌ Ошибка при создании мема")
                logging.error(f"Error creating meme with text: {e}")

        def create_meme_with_text(user_id, top_text, bottom_text):
            try:
                original_path = f"temp/{user_id}_original.jpg"

                with Image.open(original_path) as img:
                    # Конвертируем в RGB если нужно
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    draw = ImageDraw.Draw(img)

                    # Пытаемся использовать красивый шрифт для мемов
                    try:
                        # Пробуем разные шрифты
                        font_sizes = [40, 50, 60]
                        font = None

                        for size in font_sizes:
                            try:
                                font = ImageFont.truetype("arialbd.ttf", size)
                                break
                            except:
                                try:
                                    font = ImageFont.truetype("Arial", size)
                                    break
                                except:
                                    continue

                        if font is None:
                            font = ImageFont.load_default()

                    except Exception as font_error:
                        logging.error(f"Font error: {font_error}")
                        font = ImageFont.load_default()

                    # Функция для добавления текста с обводкой
                    def add_meme_text(text, y_position):
                        # Автоподбор размера шрифта под длину текста
                        text_width = img.width - 40  # Отступы по бокам
                        font_size = 50

                        # Уменьшаем шрифт если текст слишком длинный
                        while font_size > 20:
                            try:
                                test_font = ImageFont.truetype("arialbd.ttf", font_size)
                                text_length = draw.textlength(text, font=test_font)
                                if text_length <= text_width:
                                    break
                            except:
                                pass
                            font_size -= 5

                        try:
                            font = ImageFont.truetype("arialbd.ttf", font_size)
                        except:
                            font = ImageFont.load_default()

                        # Центрируем текст
                        text_length = draw.textlength(text, font=font)
                        x_position = (img.width - text_length) // 2

                        # Добавляем черную обводку
                        for dx in [-2, 0, 2]:
                            for dy in [-2, 0, 2]:
                                if dx != 0 or dy != 0:
                                    draw.text((x_position + dx, y_position + dy), text, (0, 0, 0), font=font)

                        # Белый текст поверх обводки
                        draw.text((x_position, y_position), text, (255, 255, 255), font=font)

                    # Добавляем верхний текст
                    if top_text.strip():
                        add_meme_text(top_text.upper(), 10)

                    # Добавляем нижний текст
                    if bottom_text.strip():
                        text_height = 30  # Примерная высота текста
                        add_meme_text(bottom_text.upper(), img.height - text_height - 20)

                    # Сохраняем результат
                    result_path = f"temp/{user_id}_result.jpg"
                    img.save(result_path, "JPEG", quality=95)

                    # Отправляем результат
                    with open(result_path, 'rb') as photo:
                        bot.send_photo(
                            user_id,
                            photo,
                            caption="😂 *Ваш мем готов!*\nХотите создать еще один?",
                            parse_mode='Markdown',
                            reply_markup=main_menu()
                        )

            except Exception as e:
                bot.send_message(user_id, "❌ Ошибка при создании мема с текстом")
                logging.error(f"Error creating meme with text: {e}")

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при создании мема")
        logging.error(f"Error creating meme: {e}")


# ===== ЗАПУСК БОТА =====
if __name__ == "__main__":
    print("🎨 PhotoMagicBot запущен!")
    print("🤖 Ожидание сообщений...")
    print("💡 Не забудьте заменить BOT_TOKEN на ваш токен!")

    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Bot error: {e}")