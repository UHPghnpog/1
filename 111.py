import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Токен бота
BOT_TOKEN = '8022541734:AAGqQlxVEw_aOWZoQu9GEqF_63D3MPyK8dU'

# Список Telegram ID администраторов
ADMIN_IDS = [5277632677, 7808973197]  # Ваши ID администраторов

bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения состояния пользователя (какую категорию выбрал)
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Предложение по жидкостям", callback_data='liquid'),
               InlineKeyboardButton("Предложение по картриджам", callback_data='cartridge'),
               InlineKeyboardButton("Другое", callback_data='other'))
    
    bot.send_message(message.chat.id, "Привет! Это бот-опросник для вейп-шопа. Выберите категорию для вашего предложения:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    category = ''
    if call.data == 'liquid':
        category = 'жидкостям'
    elif call.data == 'cartridge':
        category = 'картриджам'
    elif call.data == 'other':
        category = 'другому'
    
    user_states[call.from_user.id] = category
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"Напишите ваше предложение по {category}:")

@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_suggestion(message):
    category = user_states.get(message.from_user.id)
    if category:
        user_id = message.from_user.id
        username = message.from_user.username or 'Аноним'
        suggestion = message.text
        
        # Отправляем сообщение каждому администратору
        admin_message = f"Новое предложение от пользователя {username} (ID: {user_id}):\nКатегория: {category}\nТекст: {suggestion}"
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, admin_message)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка отправки сообщения админу {admin_id}: {e}")
        
        bot.send_message(message.chat.id, "Спасибо за ваше предложение! Оно отправлено администраторам.")
        
        # Очищаем состояние
        del user_states[message.from_user.id]
    else:
        bot.send_message(message.chat.id, "Пожалуйста, сначала выберите категорию через /start.")

# Запуск бота
bot.infinity_polling()