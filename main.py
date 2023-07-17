from data import TELEGRAM_TOKEN, CHATGPT_TOKEN, admin_ids
import telebot
import openai
import sqlite3

# Создание экземпляра бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Установка токена API ChatGPT
openai.api_key = CHATGPT_TOKEN


# Функция для подключения к базе данных SQLite
def connect_database():
    return sqlite3.connect('users.db')


# Создание таблицы пользователей в базе данных (если она еще не создана)
def create_users_table():
    conn = connect_database()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT)''')
    conn.commit()
    conn.close()


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_message = '''Привет! Я Валера, я умнее всяких джипити чатов и готов к диалогу. Отправь мне свои вопросы или сообщения.

    Данный бот бесплатный. Мы его улучшаем и дорабатываем. Он никогда не будет платным.
    Можете поддержать Валеру, если хотите. [Поддержать](https://yoomoney.ru/to/410011769296485)'''

    with open('valera.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=welcome_message, parse_mode='Markdown')


# Обработчик всех остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Получение вопроса от пользователя
    question = message.text

    # Подключение к базе данных
    conn = connect_database()
    c = conn.cursor()

    # Подготовка запроса к ChatGPT
    chat_input = {
        'role': 'system',
        'content': '/start ' + question,
    }

    # Запрос к ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "/start"},
            {"role": "user", "content": question}
        ],
        max_tokens=2000,
        temperature=0.5,
    )

    # Извлечение ответа от ChatGPT
    answer = response.choices[-1].message.content.strip()  # Получение последнего ответа

    # Отправка ответа пользователю
    bot.reply_to(message, answer)

    # Обновление контекста диалога в базе данных
    c.execute("UPDATE users SET context = ? WHERE id=?", (question, message.from_user.id))
    conn.commit()

    # Закрытие соединения с базой данных
    conn.close()


# Запуск бота
create_users_table()  # Создание таблицы пользователей при запуске бота
bot.polling()