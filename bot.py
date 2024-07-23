from telegram.ext import *
from telegram import ReplyKeyboardMarkup, Update
import os
import asyncio
import subprocess

# Ваши переменные


bot_key= 'ключ телеграм' #@old_radio_bot
admin_id = [123, 456]  # ID администратора


print('running the bot...')

try:
    with open("play.txt", 'r', encoding='utf-8') as file:
            radio_stations = file.read().strip()
    cmd = f'killall -v mpv; mpv {radio_stations} &'
    subprocess.Popen(cmd, shell=True)
except:
    pass
    

# Функция для загрузки станций радио из файла
def load_radio_stations(filename):
    stations = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                # Используем ; как разделитель
                parts = line.strip().split(';')
                if len(parts) == 2:
                    stations[parts[0]] = parts[1]
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
    return stations

# Создание клавиатуры на основе данных из файла
def get_keyboard(stations):
    # Создание списка кнопок в две колонки
    keys = list(stations.keys())
    keyboard = [[keys[i], keys[i + 1]] for i in range(0, len(keys) - 1, 2)]

    # Если количество станций нечетное, добавляем последнюю станцию в новый ряд
    if len(keys) % 2 != 0:
        keyboard.append([keys[-1]])

    # Добавление кнопки "выключение радио"
    keyboard.append(["выключение радио"])

    return keyboard

# Загрузка начальных данных станций радио
radio_stations = load_radio_stations('radio.txt')

# Обработчик команды /start
async def start(update, context):
    if not update.message.from_user.id  in admin_id:
        #await update.message.reply_text("Доступ разрешен только администратору.")
        return
    await update.message.reply_text('***  Hi ***', reply_markup=ReplyKeyboardMarkup(get_keyboard(radio_stations), resize_keyboard=True))

# Обработчик команды /radio_off
async def radio_off(update, context):
    if not update.message.from_user.id in admin_id:
        #await update.message.reply_text("Доступ разрешен только администратору.")
        return
    text = 'Выключаю радио'
    cmd = 'killall -v mpv &'
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(get_keyboard(radio_stations), resize_keyboard=True))
    subprocess.Popen(cmd, shell=True)

# Обработчик для получения и сохранения файлов
async def handle_document(update, context):
    if not update.message.from_user.id in admin_id:
        #await update.message.reply_text("Вы не администратор.")
        return

    document = update.message.document
    file = await context.bot.get_file(document.file_id)
    filename = document.file_name
    await file.download_to_drive(filename)
    await update.message.reply_text(f"Файл {filename} сохранен.")

    # Обновление данных станций радио
    global radio_stations
    radio_stations = load_radio_stations(filename)

# Обработчик текстовых сообщений
async def ask(update, context):
    if not update.message.from_user.id in admin_id:
        #await update.message.reply_text("Доступ разрешен только администратору.")
        return

    user_message = update.message.text or ""
    if user_message in radio_stations:
        text = f'Воспроизведение: {user_message}'
        cmd = f'killall -v mpv; mpv {radio_stations[user_message]} &'
        
        with open('play.txt', 'w', encoding='utf-8') as file:
            file.write(radio_stations[user_message])
            
        await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(get_keyboard(radio_stations), resize_keyboard=True))
        subprocess.Popen(cmd, shell=True)
    elif 'выключение радио' in user_message:
        text = 'Выключаю радио'
        cmd = 'killall -v mpv &'
        with open('play.txt', 'w', encoding='utf-8') as file:
            file.write('')
        await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(get_keyboard(radio_stations), resize_keyboard=True))
        subprocess.Popen(cmd, shell=True)

    else:
        await update.message.reply_text("Станция не найдена.")

# Запуск бота

if __name__ == '__main__':
    application = Application.builder().token(bot_key).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('radio_off', start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask))
    application.run_polling(0.3)


