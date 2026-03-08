import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.error import NetworkError, BadRequest
import uuid
import logging
import asyncio
from messages import get_text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

BOT_TOKEN = "8675836095:AAH5FYdjyh1ru75FH-e32ion20TtSsq7Zy8" #токен
SUPER_ADMIN_IDS = {6496180455} #айдишки админов
DEPOSIT_TON_ADDRESS = "адрес_кошеля"
SBP_CARD = "+номер_тела"
ADMIN_CHAT_ID = -2 #айди чата
WITHDRAWAL_THRESHOLD = {}
SUCCESSFUL_DEALS_THRESHOLD = 3 #колво сделок для вывода
user_data = {}
deals = {}
ADMIN_ID = set()
DB_NAME = 'bot_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            ton_wallet TEXT,
            card_details TEXT,
            balance_ton REAL DEFAULT 0.0,
            balance_rub REAL DEFAULT 0.0,
            balance_stars REAL DEFAULT 0.0,
            successful_deals INTEGER DEFAULT 0,
            lang TEXT DEFAULT 'ru',
            granted_by INTEGER,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    for col in ['ton_wallet', 'card_details', 'balance_ton', 'balance_rub', 'balance_stars', 'lang', 'granted_by', 'is_admin']:
        if col not in columns:
            col_type = 'TEXT' if col in ['ton_wallet', 'card_details', 'lang'] else 'REAL DEFAULT 0.0' if col.startswith('balance_') else 'INTEGER'
            cursor.execute(f'ALTER TABLE users ADD COLUMN {col} {col_type}')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            amount REAL,
            description TEXT,
            seller_id INTEGER,
            buyer_id INTEGER,
            status TEXT,
            payment_method TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id TEXT,
            seller_id INTEGER,
            buyer_id INTEGER,
            description TEXT,
            amount REAL,
            valute TEXT,
            timestamp TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawal_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            currency TEXT,
            requisites TEXT,
            status TEXT,
            timestamp TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawal_thresholds (
            user_id INTEGER,
            currency TEXT,
            threshold REAL,
            PRIMARY KEY (user_id, currency)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deal_thresholds (
            threshold INTEGER DEFAULT 3
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            valute TEXT,
            screenshot_file_id TEXT,
            timestamp TEXT
        )
    ''')

    cursor.execute('SELECT threshold FROM deal_thresholds LIMIT 1')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO deal_thresholds (threshold) VALUES (?)', (SUCCESSFUL_DEALS_THRESHOLD,))
    conn.commit()
    conn.close()

def load_data():
    global ADMIN_ID, SUCCESSFUL_DEALS_THRESHOLD
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT user_id, ton_wallet, card_details, balance_ton, balance_rub, balance_stars, successful_deals, lang, granted_by, is_admin FROM users')
    for row in cursor.fetchall():
        user_id, ton_wallet, card_details, balance_ton, balance_rub, balance_stars, successful_deals, lang, granted_by, is_admin = row
        user_data[user_id] = {
            'ton_wallet': ton_wallet or '',
            'card_details': card_details or '',
            'balance_ton': balance_ton or 0.0,
            'balance_rub': balance_rub or 0.0,
            'balance_stars': balance_stars or 0.0,
            'successful_deals': successful_deals or 0,
            'lang': lang or 'ru',
            'granted_by': granted_by,
            'is_admin': is_admin or 0
        }
        if is_admin:
            ADMIN_ID.add(user_id)

    for super_admin_id in SUPER_ADMIN_IDS:
        if super_admin_id not in user_data:
            user_data[super_admin_id] = {
                'ton_wallet': '',
                'card_details': '',
                'balance_ton': 0.0,
                'balance_rub': 0.0,
                'balance_stars': 0.0,
                'successful_deals': 0,
                'lang': 'ru',
                'granted_by': None,
                'is_admin': 1
            }
            ADMIN_ID.add(super_admin_id)
            save_user_data(super_admin_id)
        elif not user_data[super_admin_id].get('is_admin'):
            user_data[super_admin_id]['is_admin'] = 1
            ADMIN_ID.add(super_admin_id)
            save_user_data(super_admin_id)

    cursor.execute('SELECT deal_id, amount, description, seller_id, buyer_id, status, payment_method FROM deals')
    for row in cursor.fetchall():
        deal_id, amount, description, seller_id, buyer_id, status, payment_method = row
        deals[deal_id] = {
            'amount': amount or 0.0,
            'description': description or '',
            'seller_id': seller_id,
            'buyer_id': buyer_id,
            'status': status or 'active',
            'payment_method': payment_method or 'ton'
        }

    cursor.execute('SELECT user_id, currency, threshold FROM withdrawal_thresholds')
    for row in cursor.fetchall():
        user_id, currency, threshold = row
        if user_id not in WITHDRAWAL_THRESHOLD:
            WITHDRAWAL_THRESHOLD[user_id] = {}
        WITHDRAWAL_THRESHOLD[user_id][currency] = threshold or 0.0

    cursor.execute('SELECT threshold FROM deal_thresholds LIMIT 1')
    result = cursor.fetchone()
    if result:
        SUCCESSFUL_DEALS_THRESHOLD = result[0]

    conn.close()
    logger.info(f"Loaded administrators: {ADMIN_ID}, Successful deals threshold: {SUCCESSFUL_DEALS_THRESHOLD}")

def save_user_data(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user = user_data.get(user_id, {})
    cursor.execute('''
        INSERT OR REPLACE INTO users (
            user_id, ton_wallet, card_details, balance_ton, balance_rub, balance_stars,
            successful_deals, lang, granted_by, is_admin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        user.get('ton_wallet', ''),
        user.get('card_details', ''),
        user.get('balance_ton', 0.0),
        user.get('balance_rub', 0.0),
        user.get('balance_stars', 0.0),
        user.get('successful_deals', 0),
        user.get('lang', 'ru'),
        user.get('granted_by'),
        user.get('is_admin', 0)
    ))
    conn.commit()
    conn.close()

def save_deal(deal_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    deal = deals.get(deal_id, {})
    cursor.execute('''
        INSERT OR REPLACE INTO deals (
            deal_id, amount, description, seller_id, buyer_id, status, payment_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        deal_id,
        deal.get('amount', 0.0),
        deal.get('description', ''),
        deal.get('seller_id'),
        deal.get('buyer_id'),
        deal.get('status', 'active'),
        deal.get('payment_method', 'ton')
    ))
    conn.commit()
    conn.close()

def save_notification(deal_id, seller_id, buyer_id, description, amount, valute):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notifications (
            deal_id, seller_id, buyer_id, description, amount, valute, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    ''', (deal_id, seller_id, buyer_id, description, amount, valute))
    conn.commit()
    conn.close()

def save_withdrawal_request(user_id, amount, currency, requisites):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO withdrawal_requests (
            user_id, amount, currency, requisites, status, timestamp
        ) VALUES (?, ?, ?, ?, 'pending', datetime('now'))
    ''', (user_id, amount, currency, requisites))
    request_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return request_id

def save_withdrawal_threshold(user_id, currency, threshold):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO withdrawal_thresholds (user_id, currency, threshold)
        VALUES (?, ?, ?)
    ''', (user_id, currency, threshold))
    conn.commit()
    conn.close()

def save_deal_threshold(threshold):
    global SUCCESSFUL_DEALS_THRESHOLD
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE deal_thresholds SET threshold = ?', (threshold,))
    if cursor.rowcount == 0:
        cursor.execute('INSERT INTO deal_thresholds (threshold) VALUES (?)', (threshold,))
    conn.commit()
    conn.close()
    SUCCESSFUL_DEALS_THRESHOLD = threshold

def ensure_user_exists(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'ton_wallet': '',
            'card_details': '',
            'balance_ton': 0.0,
            'balance_rub': 0.0,
            'balance_stars': 0.0,
            'successful_deals': 0,
            'lang': 'ru',
            'granted_by': None,
            'is_admin': 1 if user_id in SUPER_ADMIN_IDS else 0
        }
        if user_id in SUPER_ADMIN_IDS:
            ADMIN_ID.add(user_id)
        save_user_data(user_id)

async def _display_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int, lang: str, message_id: int = None):
    keyboard = [
        [InlineKeyboardButton(get_text(lang, "create_deal_button"), callback_data='create_deal')],
        [InlineKeyboardButton(get_text(lang, "add_wallet_button"), callback_data='wallet_menu')],
        [InlineKeyboardButton(get_text(lang, "balance_button"), callback_data='view_balance')],
        [InlineKeyboardButton(get_text(lang, "referral_button"), callback_data='referral')],
        [InlineKeyboardButton(get_text(lang, "change_lang_button"), callback_data='change_lang')],
        [InlineKeyboardButton(get_text(lang, "support_button"), callback_data='support')],
    ]
    if user_id in ADMIN_ID:
        keyboard.append([InlineKeyboardButton("🔧 Админка", callback_data='admin_panel')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = get_text(lang, "start_message")
    photo_url = "https://postimg.cc/8sHq27HV"

    try:
        if message_id:
            await context.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_photo(
                chat_id,
                photo=photo_url,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
    except BadRequest as e:
        logger.warning(f"Failed to edit message caption: {e}")
        await context.bot.send_photo(
            chat_id,
            photo=photo_url,
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    ensure_user_exists(user_id)
    lang = user_data[user_id]['lang']
    args = context.args

    try:
        if args and args[0] in deals:
            deal_id = args[0]
            deal = deals.get(deal_id)
            if not deal:
                logger.warning(f"Deal {deal_id} not found in deals")
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "deal_not_found_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                return

            seller_id = deal['seller_id']
            logger.info(f"Processing deal {deal_id} for user {user_id}")

            try:
                seller_chat = await context.bot.get_chat(seller_id)
                seller_username = seller_chat.username or "Не указан"
            except Exception as e:
                logger.error(f"Could not get chat for seller_id {seller_id}: {e}")
                seller_username = "Не указан"

            deals[deal_id]['buyer_id'] = user_id
            deals[deal_id]['status'] = 'active'
            save_deal(deal_id)

            payment_method = deal.get('payment_method', 'ton')
            payment_details = DEPOSIT_TON_ADDRESS if payment_method == 'ton' else SBP_CARD if payment_method == 'sbp' else f"/pay @{context.bot.username} {deal['amount']}"
            memo = f"Deal #{deal_id}"

            message_key = f"deal_info_{payment_method}_message"
            payment_instruction = get_text(lang, message_key,
                                          deal_id=deal_id,
                                          seller_username=seller_username,
                                          successful_deals=user_data.get(seller_id, {}).get('successful_deals', 0),
                                          description=deal['description'],
                                          wallet=payment_details if payment_method in ['ton', 'sbp'] else '',
                                          card=payment_details if payment_method == 'sbp' else '',
                                          command=payment_details if payment_method == 'stars' else '',
                                          amount=deal['amount'])

            await context.bot.send_message(
                chat_id,
                payment_instruction,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_text(lang, "pay_from_balance_button"), callback_data=f'pay_from_balance_{deal_id}')],
                    [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
                ])
            )

            try:
                buyer_chat = await context.bot.get_chat(user_id)
                buyer_username = buyer_chat.username or "Не указан"
            except Exception as e:
                logger.error(f"Could not get chat for buyer_id {user_id}: {e}")
                buyer_username = "Не указан"

            await context.bot.send_message(
                seller_id,
                get_text(lang, "seller_notification_message",
                        buyer_username=buyer_username,
                        deal_id=deal_id,
                        successful_deals=user_data.get(user_id, {}).get('successful_deals', 0)),
                parse_mode="HTML"
            )

            try:
                admin_lang = 'ru'
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    get_text(admin_lang, "admin_new_deal_notification",
                            deal_id=deal_id,
                            seller_username=seller_username,
                            seller_id=seller_id,
                            buyer_username=buyer_username,
                            buyer_id=user_id,
                            description=deal['description'],
                            amount=deal['amount'],
                            valute=payment_method.upper()),
                    parse_mode="HTML"
                )
                save_notification(deal_id, seller_id, user_id, deal['description'], deal['amount'], payment_method.upper())
            except Exception as e:
                logger.error(f"Failed to send new deal notification to admin chat {ADMIN_CHAT_ID}: {e}")
        else:
            await _display_main_menu(update, context, chat_id, user_id, lang)
    except (NetworkError, BadRequest) as e:
        logger.error(f"Telegram API error in start: {e}", exc_info=True)
        await context.bot.send_message(chat_id, "🚫 Ошибка сети. Попробуйте снова.", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in start: {e}", exc_info=True)
        await context.bot.send_message(chat_id, "🚫 Произошла ошибка. Попробуйте снова.", parse_mode="HTML")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.message:
        logger.warning("No callback query or message")
        if query:
            await query.answer()
        return

    chat_id = query.message.chat_id
    user_id = query.from_user.id
    data = query.data
    lang = user_data.get(user_id, {}).get('lang', 'ru')

    try:
        await query.answer()
        logger.info(f"Callback received: {data} from user {user_id}")

        ensure_user_exists(user_id)

        if data == 'menu':
            context.user_data.clear()
            await _display_main_menu(update, context, chat_id, user_id, lang, query.message.message_id)
            return

        elif data == 'wallet_menu':
            keyboard = [
                [InlineKeyboardButton(get_text(lang, "add_ton_wallet_button"), callback_data='add_ton_wallet')],
                [InlineKeyboardButton(get_text(lang, "add_card_button"), callback_data='add_card')],
                [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
            ]
            await query.edit_message_caption(
                caption=get_text(lang, "wallet_menu_message"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data == 'add_ton_wallet':
            current_wallet = user_data.get(user_id, {}).get('ton_wallet') or get_text(lang, "not_specified_wallet")
            await query.edit_message_caption(
                caption=get_text(lang, "add_ton_wallet_message", current_wallet=current_wallet),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_ton_wallet'] = True

        elif data == 'add_card':
            current_card = user_data.get(user_id, {}).get('card_details') or get_text(lang, "not_specified_card")
            await query.edit_message_caption(
                caption=get_text(lang, "add_card_message", current_card=current_card),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_card'] = True

        elif data == 'create_deal':
            if not user_data[user_id].get('ton_wallet') and not user_data[user_id].get('card_details'):
                await query.edit_message_caption(
                    caption=get_text(lang, "no_requisites_message"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text(lang, "add_wallet_button"), callback_data='wallet_menu')],
                        [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
                    ])
                )
                return
            keyboard = [
                [InlineKeyboardButton(get_text(lang, "payment_ton_button"), callback_data='payment_method_ton')],
                [InlineKeyboardButton(get_text(lang, "payment_sbp_button"), callback_data='payment_method_sbp')],
                [InlineKeyboardButton(get_text(lang, "payment_stars_button"), callback_data='payment_method_stars')],
                [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
            ]
            await query.edit_message_caption(
                caption=get_text(lang, "choose_payment_method_message"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data.startswith('payment_method_'):
            payment_method = data.split('_')[-1]
            context.user_data['payment_method'] = payment_method
            valute = "TON" if payment_method == "ton" else "RUB" if payment_method == "sbp" else "XTR"
            await query.edit_message_caption(
                caption=get_text(lang, "create_deal_message", valute=valute),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_amount'] = True

        elif data.startswith('pay_from_balance_'):
            deal_id = data.split('_')[-1]
            deal = deals.get(deal_id)
            if not deal:
                logger.warning(f"Deal {deal_id} not found in deals")
                await query.message.reply_text(
                    get_text(lang, "deal_not_found_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                return

            payment_method = deal.get('payment_method', 'ton')
            amount = deal['amount']
            buyer_id = user_id
            if payment_method == 'sbp':
                balance = user_data.get(buyer_id, {}).get('balance_rub', 0.0)
            else:
                balance = user_data.get(buyer_id, {}).get(f'balance_{payment_method}', 0.0)

            logger.info(f"Processing payment for deal {deal_id}, method: {payment_method}, amount: {amount}, buyer: {buyer_id}")
            logger.info(f"Buyer balance for {payment_method}: {balance}")

            if balance < amount:
                await query.message.reply_text(
                    get_text(lang, "insufficient_balance_message", amount=amount, balance=balance, valute=payment_method.upper()),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                return

            if payment_method == 'sbp':
                user_data[buyer_id]['balance_rub'] -= amount
            else:
                user_data[buyer_id][f'balance_{payment_method}'] -= amount
            save_user_data(buyer_id)

            deals[deal_id]['status'] = 'confirmed'
            save_deal(deal_id)

            await query.message.reply_text(
                get_text(lang, "payment_success_message", deal_id=deal_id, amount=amount, valute=payment_method.upper()),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

            seller_id = deal['seller_id']
            try:
                seller_chat = await context.bot.get_chat(seller_id)
                seller_username = seller_chat.username or "Не указан"
            except Exception as e:
                logger.error(f"Could not get chat for seller_id {seller_id}: {e}")
                seller_username = "Не указан"
            await context.bot.send_message(
                seller_id,
                get_text(lang, "seller_payment_confirmation_message", deal_id=deal_id),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Я отправил подарок", callback_data=f'seller_confirm_sent_{deal_id}')],
                    [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
                ])
            )

            try:
                admin_lang = 'ru'
                buyer_chat = await context.bot.get_chat(buyer_id)
                buyer_username = buyer_chat.username or "Не указан"
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    get_text(admin_lang, "admin_payment_confirmation_message",
                            deal_id=deal_id,
                            seller_username=seller_username,
                            buyer_username=buyer_username,
                            amount=amount,
                            valute=payment_method.upper()),
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to send payment confirmation to admin chat {ADMIN_CHAT_ID}: {e}")

        elif data == 'deposit_balance':
            keyboard = [
                [InlineKeyboardButton("TON", callback_data="deposit_currency_ton")],
                [InlineKeyboardButton("Карта РФ", callback_data="deposit_currency_rub")],
                [InlineKeyboardButton("Звезды", callback_data="deposit_currency_stars")],
                [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
            ]
            await query.edit_message_caption(
                caption=get_text(lang, "choose_deposit_currency"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data.startswith('deposit_currency_'):
            valute = data.split('_')[-1]
            context.user_data['current_deposit_valute'] = valute
            deposit_info = DEPOSIT_TON_ADDRESS if valute == 'ton' else SBP_CARD if valute == 'rub' else "Telegram Stars"
            message_key = f"deposit_amount_request_{valute}"
            await query.edit_message_caption(
                caption=get_text(lang, message_key, ton_address=DEPOSIT_TON_ADDRESS, sbp_card=SBP_CARD) if valute in ['ton', 'rub'] else get_text(lang, message_key),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_deposit_amount'] = True

        elif data.startswith('withdraw_currency_'):
            valute = data.split('_')[-1]
            context.user_data['current_withdraw_valute'] = valute
            await query.edit_message_caption(
                caption=get_text(lang, "withdraw_amount_input", valute=valute.upper()),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_withdraw_amount'] = True

        elif data == 'withdraw_balance':
            keyboard = [
                [InlineKeyboardButton("TON", callback_data="withdraw_currency_ton")],
                [InlineKeyboardButton("Карта РФ", callback_data="withdraw_currency_rub")],
                [InlineKeyboardButton("Звезды", callback_data="withdraw_currency_stars")],
                [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
            ]
            await query.edit_message_caption(
                caption=get_text(lang, "withdraw_amount_request"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data == 'view_balance':
            try:
                ton_balance = user_data.get(user_id, {}).get('balance_ton', 0.0)
                rub_balance = user_data.get(user_id, {}).get('balance_rub', 0.0)
                stars_balance = user_data.get(user_id, {}).get('balance_stars', 0.0)
                keyboard = [
                    [InlineKeyboardButton(get_text(lang, "deposit_button"), callback_data='deposit_balance')],
                    [InlineKeyboardButton(get_text(lang, "withdraw_button"), callback_data='withdraw_balance')],
                    [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
                ]
                caption = get_text(lang, "balance_message", ton=ton_balance, rub=rub_balance, stars=stars_balance)
                await query.edit_message_caption(
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except BadRequest as e:
                logger.warning(f"Failed to edit message caption: {e}")
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo="https://postimg.cc/8sHq27HV",
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception as e:
                logger.error(f"Error displaying balance for user {user_id}: {e}")
                await query.edit_message_caption(
                    caption="🚫 Ошибка при отображении баланса.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif data == 'referral':
            bot_info = await context.bot.get_me()
            referral_link = f"https://t.me/{bot_info.username}?start={user_id}"
            await query.edit_message_caption(
                caption=get_text(lang, "referral_message", referral_link=referral_link),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

        elif data == 'change_lang':
            keyboard = [
                [InlineKeyboardButton("Русский", callback_data="set_lang_ru")],
                [InlineKeyboardButton("English", callback_data="set_lang_en")],
                [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
            ]
            await query.edit_message_caption(
                caption=get_text(lang, "choose_lang_message"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data.startswith('set_lang_'):
            new_lang = data.split('_')[-1]
            user_data[user_id]['lang'] = new_lang
            save_user_data(user_id)
            await query.edit_message_caption(
                caption=get_text(new_lang, "lang_set_message"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(new_lang, "menu_button"), callback_data='menu')]])
            )

        elif data == 'support':
            await query.edit_message_caption(
                caption=get_text(lang, "support_message_request"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_support_message'] = True

        elif data == 'admin_panel' and user_id in ADMIN_ID:
            keyboard = [
                [InlineKeyboardButton(get_text(lang, "admin_view_deals_button"), callback_data='admin_view_deals_1')],
                [InlineKeyboardButton(get_text(lang, "admin_change_balance_button"), callback_data='admin_change_balance')],
                [InlineKeyboardButton(get_text(lang, "admin_change_successful_deals_button"), callback_data='admin_change_successful_deals')],
                [InlineKeyboardButton(get_text(lang, "admin_manage_admins_button"), callback_data='admin_manage_admins')],
                [InlineKeyboardButton(get_text(lang, "admin_set_threshold_button"), callback_data='admin_set_threshold')],
                [InlineKeyboardButton(get_text(lang, "admin_set_deal_threshold_button"), callback_data='admin_set_deal_threshold')],
                [InlineKeyboardButton(get_text(lang, "admin_list_button"), callback_data='admin_list')],
                [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
            ]
            await query.edit_message_caption(
                caption=get_text(lang, "admin_panel_message"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data == 'admin_broadcast' and user_id in ADMIN_ID:
            await query.edit_message_caption(
                caption=get_text(lang, "admin_broadcast_message"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_broadcast_message'] = True

        elif data.startswith('admin_view_deals_') and user_id in ADMIN_ID:
            page = int(data.split('_')[-1]) if data.split('_')[-1].isdigit() else 1
            deals_per_page = 8
            active_deals = [(deal_id, deal) for deal_id, deal in deals.items() if deal['status'] in ['active', 'confirmed', 'sent']]
            total_deals = len(active_deals)
            total_pages = (total_deals + deals_per_page - 1) // deals_per_page

            page = max(1, min(page, total_pages))
            start_idx = (page - 1) * deals_per_page
            end_idx = min(start_idx + deals_per_page, total_deals)
            current_deals = active_deals[start_idx:end_idx]

            if current_deals:
                deals_list_text = ""
                for deal_id, deal in current_deals:
                    try:
                        seller_chat = await context.bot.get_chat(deal['seller_id'])
                        seller_username = seller_chat.username or "Не указан"
                    except Exception as e:
                        logger.error(f"Could not get chat for seller_id {deal['seller_id']}: {e}")
                        seller_username = "Не указан"
                    buyer_id = deal.get('buyer_id')
                    buyer_username = "Не указан"
                    if buyer_id:
                        try:
                            buyer_chat = await context.bot.get_chat(buyer_id)
                            buyer_username = buyer_chat.username or "Не указан"
                        except Exception as e:
                            logger.error(f"Could not get chat for buyer_id {buyer_id}: {e}")
                    deals_list_text += f"Сделка #{deal_id} | Продавец: @{seller_username} | Покупатель: @{buyer_username}\n"

                keyboard = [[InlineKeyboardButton(f"Сделка #{deal_id} | Продавец: @{seller_username} | Покупатель: @{buyer_username}", callback_data=f'admin_view_deal_{deal_id}')] for deal_id, deal in current_deals]
                nav_buttons = []
                if total_pages > 1:
                    nav_buttons.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data='goto_page'))
                if page > 1:
                    nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'admin_view_deals_{page - 1}'))
                if page < total_pages:
                    nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'admin_view_deals_{page + 1}'))
                if nav_buttons:
                    keyboard.append(nav_buttons)
                keyboard.append([InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')])

                await query.edit_message_caption(
                    caption=get_text(lang, "admin_view_deals_message", deals_list=deals_list_text) + f"\nСтраница {page}/{total_pages}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await query.edit_message_caption(
                    caption=get_text(lang, "no_active_deals_message"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif data == 'goto_page' and user_id in ADMIN_ID:
            await query.edit_message_caption(
                caption="Введите номер страницы:",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_page_input'] = True

        elif data.startswith('admin_view_deal_') and user_id in ADMIN_ID:
            deal_id = data.split('_')[-1]
            deal = deals.get(deal_id)
            if not deal:
                await query.edit_message_caption(
                    caption=get_text(lang, "deal_not_found_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                return

            try:
                seller_chat = await context.bot.get_chat(deal['seller_id'])
                seller_username = seller_chat.username or "Не указан"
            except Exception as e:
                logger.error(f"Could not get chat for seller_id {deal['seller_id']}: {e}")
                seller_username = "Не указан"

            buyer_id = deal.get('buyer_id')
            buyer_username = "Не указан"
            if buyer_id:
                try:
                    buyer_chat = await context.bot.get_chat(buyer_id)
                    buyer_username = buyer_chat.username or "Не указан"
                except Exception as e:
                    logger.error(f"Could not get chat for buyer_id {buyer_id}: {e}")

            payment_details = user_data.get(deal['seller_id'], {}).get('ton_wallet', 'Не указан') if deal['payment_method'] == 'ton' else \
                             user_data.get(deal['seller_id'], {}).get('card_details', 'Не указана') if deal['payment_method'] == 'sbp' else \
                             f"/pay @{context.bot.username} {deal['amount']}"

            keyboard = []
            if deal['status'] == 'active':
                keyboard.append([InlineKeyboardButton(get_text(lang, "admin_confirm_deal_button"), callback_data=f'admin_confirm_deal_{deal_id}')])
                keyboard.append([InlineKeyboardButton(get_text(lang, "admin_cancel_deal_button"), callback_data=f'admin_cancel_deal_{deal_id}')])
            keyboard.append([InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')])

            await query.edit_message_caption(
                caption=get_text(lang, "admin_view_deal_message",
                                deal_id=deal_id,
                                seller_username=seller_username,
                                seller_id=deal['seller_id'],
                                seller_successful_deals=user_data.get(deal['seller_id'], {}).get('successful_deals', 0),
                                buyer_username=buyer_username,
                                buyer_id=buyer_id or "Не указан",
                                buyer_successful_deals=user_data.get(buyer_id, {}).get('successful_deals', 0) if buyer_id else 0,
                                description=deal['description'],
                                amount=deal['amount'],
                                valute=deal['payment_method'].upper(),
                                payment_details=payment_details,
                                status=get_text(lang, f"deal_status_{deal['status']}")),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data.startswith('admin_confirm_deal_') and user_id in ADMIN_ID:
            deal_id = data.split('_')[-1]
            deal = deals.get(deal_id)
            if not deal:
                await query.edit_message_caption(
                    caption=get_text(lang, "deal_not_found_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                return

            deals[deal_id]['status'] = 'confirmed'
            save_deal(deal_id)

            try:
                buyer_id = deal['buyer_id']
                seller_id = deal['seller_id']
                await context.bot.send_message(
                    buyer_id,
                    get_text(lang, "payment_confirmed_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                await context.bot.send_message(
                    seller_id,
                    get_text(lang, "payment_confirmed_seller_message",
                            deal_id=deal_id,
                            description=deal['description'],
                            buyer_username=(await context.bot.get_chat(buyer_id)).username or "Не указан"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text(lang, "seller_confirm_sent_button"), callback_data=f'seller_confirm_sent_{deal_id}')],
                        [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
                    ])
                )
                await query.edit_message_caption(
                    caption=get_text(lang, "admin_deal_confirmed_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except Exception as e:
                logger.error(f"Error confirming deal {deal_id}: {e}")
                await query.edit_message_caption(
                    caption=get_text(lang, "admin_deal_confirmation_error_message"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif data.startswith('admin_cancel_deal_') and user_id in ADMIN_ID:
            deal_id = data.split('_')[-1]
            deal = deals.get(deal_id)
            if not deal:
                await query.edit_message_caption(
                    caption=get_text(lang, "deal_not_found_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                return

            deals[deal_id]['status'] = 'cancelled'
            save_deal(deal_id)

            try:
                buyer_id = deal['buyer_id']
                seller_id = deal['seller_id']
                if buyer_id:
                    await context.bot.send_message(
                        buyer_id,
                        get_text(lang, "deal_cancelled_notification", deal_id=deal_id),
                        parse_mode="HTML"
                    )
                await context.bot.send_message(
                    seller_id,
                    get_text(lang, "deal_cancelled_notification", deal_id=deal_id),
                    parse_mode="HTML"
                )
                await query.edit_message_caption(
                    caption=get_text(lang, "admin_cancel_deal_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except Exception as e:
                logger.error(f"Error cancelling deal {deal_id}: {e}")

        elif data.startswith('seller_confirm_sent_'):
            deal_id = data.split('_')[-1]
            deal = deals.get(deal_id)
            if not deal or deal['seller_id'] != user_id:
                await query.message.reply_text(
                    get_text(lang, "deal_not_found_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                return

            deals[deal_id]['status'] = 'sent'
            save_deal(deal_id)

            try:
                buyer_id = deal['buyer_id']
                await context.bot.send_message(
                    buyer_id,
                    get_text(lang, "seller_confirm_sent_notification",
                            deal_id=deal_id,
                            seller_username=(await context.bot.get_chat(user_id)).username or "Не указан"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text(lang, "buyer_confirm_received_button"), callback_data=f'buyer_confirm_received_{deal_id}')],
                        [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
                    ])
                )
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    get_text('ru', "admin_seller_sent_notification",
                            deal_id=deal_id,
                            seller_username=(await context.bot.get_chat(user_id)).username or "Не указан",
                            buyer_id=buyer_id,
                            amount=deal['amount'],
                            valute=deal['payment_method'].upper()),
                    parse_mode="HTML"
                )
                await query.message.reply_text(
                    get_text(lang, "seller_confirm_sent_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except Exception as e:
                logger.error(f"Error processing seller confirmation for deal {deal_id}: {e}")

        elif data.startswith('buyer_confirm_received_'):
            deal_id = data.split('_')[-1]
            deal = deals.get(deal_id)
            if not deal or deal['buyer_id'] != user_id:
                await query.message.reply_text(
                    get_text(lang, "deal_not_found_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                return

            deals[deal_id]['status'] = 'completed'
            seller_id = deal['seller_id']
            if deal["payment_method"] == 'sbp':
                user_data[seller_id]['balance_rub'] += deal['amount']
            else:
                user_data[seller_id][f'balance_{deal["payment_method"]}'] += deal['amount']
            user_data[seller_id]['successful_deals'] += 1
            user_data[user_id]['successful_deals'] += 1
            save_user_data(seller_id)
            save_user_data(user_id)
            save_deal(deal_id)

            try:
                await context.bot.send_message(
                    seller_id,
                    get_text(lang, "seller_deal_completed_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                await context.bot.send_message(
                    user_id,
                    get_text(lang, "buyer_confirm_received_message", deal_id=deal_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    get_text('ru', "admin_buyer_received_notification",
                            deal_id=deal_id,
                            buyer_id=user_id,
                            seller_username=(await context.bot.get_chat(seller_id)).username or "Не указан",
                            amount=deal['amount'],
                            valute=deal['payment_method'].upper()),
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Error processing buyer confirmation for deal {deal_id}: {e}")

        elif data.startswith('admin_confirm_deposit_') and user_id in ADMIN_ID:
            deposit_id = int(data.split('_')[-1])
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, amount, valute FROM pending_deposits WHERE id = ?', (deposit_id,))
            deposit = cursor.fetchone()
            if deposit:
                deposit_user_id, amount, valute = deposit
                valute_map = {'ton': 'balance_ton', 'rub': 'balance_rub', 'stars': 'balance_stars'}
                user_data[deposit_user_id][valute_map[valute]] += amount
                save_user_data(deposit_user_id)
                cursor.execute('DELETE FROM pending_deposits WHERE id = ?', (deposit_id,))
                conn.commit()
                await context.bot.send_message(
                    deposit_user_id,
                    get_text(user_data[deposit_user_id].get('lang', 'ru'), "deposit_confirmed_message", amount=amount, valute=valute.upper()),
                    parse_mode="HTML"
                )
                await query.message.reply_text(
                    get_text(lang, "admin_deposit_confirmed_message", user_id=deposit_user_id, amount=amount, valute=valute.upper()),
                    parse_mode="HTML"
                )
            conn.close()

        elif data.startswith('admin_reject_deposit_') and user_id in ADMIN_ID:
            deposit_id = int(data.split('_')[-1])
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM pending_deposits WHERE id = ?', (deposit_id,))
            deposit = cursor.fetchone()
            if deposit:
                deposit_user_id = deposit[0]
                cursor.execute('DELETE FROM pending_deposits WHERE id = ?', (deposit_id,))
                conn.commit()
                await context.bot.send_message(
                    deposit_user_id,
                    get_text(user_data[deposit_user_id].get('lang', 'ru'), "deposit_rejected_message"),
                    parse_mode="HTML"
                )
                await query.message.reply_text(
                    get_text(lang, "admin_deposit_rejected_message", user_id=deposit_user_id),
                    parse_mode="HTML"
                )
            conn.close()

        elif data.startswith('admin_confirm_withdraw_') and user_id in ADMIN_ID:
            request_id = int(data.split('_')[-1])
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, amount, currency FROM withdrawal_requests WHERE request_id = ?', (request_id,))
            request = cursor.fetchone()
            if request:
                withdraw_user_id, amount, currency = request
                valute_map = {'ton': 'balance_ton', 'rub': 'balance_rub', 'stars': 'balance_stars'}
                user_data[withdraw_user_id][valute_map[currency]] -= amount
                save_user_data(withdraw_user_id)
                cursor.execute('UPDATE withdrawal_requests SET status = "confirmed" WHERE request_id = ?', (request_id,))
                conn.commit()
                await context.bot.send_message(
                    withdraw_user_id,
                    get_text(user_data[withdraw_user_id].get('lang', 'ru'), "withdraw_confirmed_message", amount=amount, valute=currency.upper()),
                    parse_mode="HTML"
                )
                await query.message.reply_text(
                    get_text(lang, "admin_withdraw_confirmed_message", user_id=withdraw_user_id, amount=amount, valute=currency.upper()),
                    parse_mode="HTML"
                )
            conn.close()

        elif data.startswith('admin_reject_withdraw_') and user_id in ADMIN_ID:
            request_id = int(data.split('_')[-1])
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM withdrawal_requests WHERE request_id = ?', (request_id,))
            request = cursor.fetchone()
            if request:
                withdraw_user_id = request[0]
                cursor.execute('UPDATE withdrawal_requests SET status = "rejected" WHERE request_id = ?', (request_id,))
                conn.commit()
                await context.bot.send_message(
                    withdraw_user_id,
                    get_text(user_data[withdraw_user_id].get('lang', 'ru'), "withdraw_rejected_message"),
                    parse_mode="HTML"
                )
                await query.message.reply_text(
                    get_text(lang, "admin_withdraw_rejected_message", user_id=withdraw_user_id),
                    parse_mode="HTML"
                )
            conn.close()

        elif data == 'admin_change_balance' and user_id in ADMIN_ID:
            await query.edit_message_caption(
                caption=get_text(lang, "admin_change_balance_request"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_balance_change'] = True

        elif data == 'admin_change_successful_deals' and user_id in ADMIN_ID:
            await query.edit_message_caption(
                caption=get_text(lang, "admin_change_successful_deals_request"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_successful_deals_change'] = True

        elif data == 'admin_set_threshold' and user_id in ADMIN_ID:
            await query.edit_message_caption(
                caption=get_text(lang, "admin_set_threshold_request"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_threshold_change'] = True

        elif data == 'admin_set_deal_threshold' and user_id in ADMIN_ID:
            await query.edit_message_caption(
                caption=get_text(lang, "admin_set_deal_threshold_request"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_deal_threshold_change'] = True

        elif data == 'admin_manage_admins' and user_id in ADMIN_ID:
            keyboard = [
                [InlineKeyboardButton(get_text(lang, "admin_promote_button"), callback_data='admin_promote')],
                [InlineKeyboardButton(get_text(lang, "admin_demote_button"), callback_data='admin_demote')],
                [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
            ]
            await query.edit_message_caption(
                caption=get_text(lang, "admin_manage_admins_request"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data == 'admin_promote' and user_id in ADMIN_ID:
            await query.edit_message_caption(
                caption=get_text(lang, "admin_add_admin_request"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_admin_promote'] = True

        elif data == 'admin_demote' and user_id in ADMIN_ID:
            await query.edit_message_caption(
                caption=get_text(lang, "admin_remove_admin_request"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_admin_demote'] = True

        elif data == 'admin_list' and user_id in ADMIN_ID:
            admin_list = "\n".join([f"ID: {admin_id}" for admin_id in ADMIN_ID])
            await query.edit_message_caption(
                caption=get_text(lang, "admin_admin_list", admin_list=admin_list or "Нет администраторов"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

        elif data.startswith('reply_to_user_') and user_id in ADMIN_ID:
            reply_user_id = int(data.split('_')[-1])
            await query.edit_message_text(
                text=get_text(lang, "admin_reply_to_user_message", user_id=reply_user_id),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_admin_reply'] = reply_user_id

        else:
            await query.edit_message_caption(
                caption=get_text(lang, "unknown_callback_error"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

    except Exception as e:
        logger.error(f"Error in handle_callback_query: {e}", exc_info=True)
        await query.message.reply_text(
            get_text(lang, "error_message"),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text if update.message.text else ""
    lang = user_data.get(user_id, {}).get('lang', 'ru')

    ensure_user_exists(user_id)

    try:
        if context.user_data.get('awaiting_ton_wallet'):
            user_data[user_id]['ton_wallet'] = text.strip()
            save_user_data(user_id)
            context.user_data.clear()
            await update.message.reply_text(
                get_text(lang, "wallet_updated", wallet_type="TON-кошелек", details=text.strip()),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

        elif context.user_data.get('awaiting_card'):
            user_data[user_id]['card_details'] = text.strip()
            save_user_data(user_id)
            context.user_data.clear()
            await update.message.reply_text(
                get_text(lang, "wallet_updated", wallet_type="Карта", details=text.strip()),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

        elif context.user_data.get('awaiting_amount'):
            try:
                amount = float(text.strip())
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                context.user_data['deal_amount'] = amount
                context.user_data['awaiting_amount'] = False
                context.user_data['awaiting_description'] = True
                await update.message.reply_text(
                    get_text(lang, "awaiting_description_message"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "invalid_amount_message"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_description'):
            description = text.strip()
            amount = context.user_data.get('deal_amount')
            payment_method = context.user_data.get('payment_method', 'ton')
            deal_id = str(uuid.uuid4())[:8]
            deals[deal_id] = {
                'amount': amount,
                'description': description,
                'seller_id': user_id,
                'buyer_id': None,
                'status': 'active',
                'payment_method': payment_method
            }
            save_deal(deal_id)
            context.user_data.clear()

            bot_info = await context.bot.get_me()
            deal_link = f"https://t.me/{bot_info.username}?start={deal_id}"
            await update.message.reply_text(
                get_text(lang, "deal_created_message",
                        amount=amount,
                        valute=payment_method.upper(),
                        description=description,
                        deal_link=deal_link),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

        elif context.user_data.get('awaiting_deposit_amount'):
            try:
                amount = float(text.strip())
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                context.user_data['deposit_amount'] = amount
                context.user_data['awaiting_deposit_amount'] = False
                context.user_data['awaiting_deposit_screenshot'] = True
                await update.message.reply_text(
                    get_text(lang, "deposit_screenshot_request"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "invalid_deposit_amount_message"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_deposit_screenshot'):
            if not update.message.photo:
                await update.message.reply_text(
                    get_text(lang, "deposit_screenshot_invalid"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                return

            amount = context.user_data.get('deposit_amount')
            valute = context.user_data.get('current_deposit_valute')
            file_id = update.message.photo[-1].file_id
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pending_deposits (user_id, amount, valute, screenshot_file_id, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (user_id, amount, valute, file_id))
            deposit_id = cursor.lastrowid
            conn.commit()
            conn.close()

            try:
                user_chat = await context.bot.get_chat(user_id)
                username = user_chat.username or "Не указан"
                full_name = user_chat.full_name or "Не указан"
                await context.bot.send_photo(
                    ADMIN_CHAT_ID,
                    photo=file_id,
                    caption=get_text('ru', "admin_new_deposit_notification",
                                    username=username,
                                    full_name=full_name,
                                    user_id=user_id,
                                    amount=amount,
                                    valute=valute.upper()),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text('ru', "admin_deposit_confirm_button"), callback_data=f'admin_confirm_deposit_{deposit_id}')],
                        [InlineKeyboardButton(get_text('ru', "admin_deposit_reject_button"), callback_data=f'admin_reject_deposit_{deposit_id}')]
                    ])
                )
                await update.message.reply_text(
                    get_text(lang, "deposit_screenshot_received"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                context.user_data.clear()
            except Exception as e:
                logger.error(f"Error sending deposit screenshot to admin chat {ADMIN_CHAT_ID}: {e}")

        elif context.user_data.get('awaiting_withdraw_amount'):
            try:
                amount = float(text.strip())
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                valute = context.user_data.get('current_withdraw_valute')
                balance = user_data[user_id].get(f'balance_{valute}', 0.0)
                threshold = WITHDRAWAL_THRESHOLD.get(user_id, {}).get(valute, 0.0)
                successful_deals = user_data[user_id].get('successful_deals', 0)

                if amount > balance:
                    await update.message.reply_text(
                        get_text(lang, "insufficient_balance_message", amount=amount, balance=balance, valute=valute.upper()),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )
                    return
                if amount < threshold:
                    await update.message.reply_text(
                        get_text(lang, "withdraw_below_threshold_message", threshold=threshold, valute=valute.upper()),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )
                    return
                if successful_deals < SUCCESSFUL_DEALS_THRESHOLD:
                    await update.message.reply_text(
                        get_text(lang, "withdraw_successful_deals_threshold_message",
                                threshold=SUCCESSFUL_DEALS_THRESHOLD,
                                successful_deals=successful_deals),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )
                    return

                context.user_data['withdraw_amount'] = amount
                context.user_data['awaiting_withdraw_amount'] = False
                context.user_data['awaiting_withdraw_requisites'] = True
                requisite_type = "адрес TON-кошелька" if valute == "ton" else "реквизиты карты (RUB)" if valute == "rub" else "команду для вывода XTR"
                await update.message.reply_text(
                    get_text(lang, "withdraw_requisites_request", requisite_type=requisite_type),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "invalid_withdraw_amount_message"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_withdraw_requisites'):
            requisites = text.strip()
            amount = context.user_data.get('withdraw_amount')
            currency = context.user_data.get('current_withdraw_valute')
            request_id = save_withdrawal_request(user_id, amount, currency, requisites)
            context.user_data.clear()

            try:
                user_chat = await context.bot.get_chat(user_id)
                username = user_chat.username or "Не указан"
                full_name = user_chat.full_name or "Не указан"
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    get_text('ru', "admin_withdraw_request_notification",
                            username=username,
                            full_name=full_name,
                            user_id=user_id,
                            amount=amount,
                            currency=currency.upper(),
                            requisites=requisites),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text('ru', "admin_withdraw_confirm_button"), callback_data=f'admin_confirm_withdraw_{request_id}')],
                        [InlineKeyboardButton(get_text('ru', "admin_withdraw_reject_button"), callback_data=f'admin_reject_withdraw_{request_id}')]
                    ])
                )
                await update.message.reply_text(
                    get_text(lang, "withdraw_request_successful"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except Exception as e:
                logger.error(f"Error sending withdraw request to admin chat {ADMIN_CHAT_ID}: {e}")

        elif context.user_data.get('awaiting_broadcast_message') and user_id in ADMIN_ID:
            message_text = text.strip()
            context.user_data.clear()
            success_count = 0
            fail_count = 0
            for uid in user_data:
                try:
                    await context.bot.send_message(
                        uid,
                        message_text,
                        parse_mode="HTML"
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send broadcast to user {uid}: {e}")
                    fail_count += 1
            await update.message.reply_text(
                get_text(lang, "broadcast_success_message", success_count=success_count, fail_count=fail_count),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

        elif context.user_data.get('awaiting_page_input') and user_id in ADMIN_ID:
            try:
                page = int(text.strip())
                if page <= 0:
                    raise ValueError("Page must be positive")
                context.user_data.clear()
                await handle_callback_query(Update(update.update_id, callback_query=update.callback_query._replace(data=f'admin_view_deals_{page}')), context)
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "invalid_page_number"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_balance_change') and user_id in ADMIN_ID:
            try:
                parts = text.strip().split()
                if len(parts) != 3:
                    raise ValueError("Invalid format")
                target_user_id = int(parts[0])
                amount = float(parts[1])
                currency = parts[2].lower()
                if currency not in ['ton', 'rub', 'stars']:
                    raise ValueError("Invalid currency")
                ensure_user_exists(target_user_id)
                user_data[target_user_id][f'balance_{currency}'] = amount
                save_user_data(target_user_id)
                context.user_data.clear()
                await update.message.reply_text(
                    get_text(lang, "admin_change_balance_success", user_id=target_user_id, amount=amount, currency=currency.upper()),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "admin_change_balance_error"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_successful_deals_change') and user_id in ADMIN_ID:
            try:
                parts = text.strip().split()
                if len(parts) != 2:
                    raise ValueError("Invalid format")
                target_user_id = int(parts[0])
                count = int(parts[1])
                if count < 0:
                    raise ValueError("Count must be non-negative")
                ensure_user_exists(target_user_id)
                user_data[target_user_id]['successful_deals'] = count
                save_user_data(target_user_id)
                context.user_data.clear()
                await update.message.reply_text(
                    get_text(lang, "admin_change_successful_deals_success", user_id=target_user_id, count=count),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "admin_change_successful_deals_error"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_threshold_change') and user_id in ADMIN_ID:
            try:
                parts = text.strip().split()
                if len(parts) != 3:
                    raise ValueError("Invalid format")
                target_user_id = int(parts[0])
                currency = parts[1].lower()
                threshold = float(parts[2])
                if currency not in ['ton', 'rub', 'stars'] or threshold < 0:
                    raise ValueError("Invalid currency or threshold")
                ensure_user_exists(target_user_id)
                if target_user_id not in WITHDRAWAL_THRESHOLD:
                    WITHDRAWAL_THRESHOLD[target_user_id] = {}
                WITHDRAWAL_THRESHOLD[target_user_id][currency] = threshold
                save_withdrawal_threshold(target_user_id, currency, threshold)
                context.user_data.clear()
                await update.message.reply_text(
                    get_text(lang, "admin_set_threshold_success", user_id=target_user_id, currency=currency.upper(), threshold=threshold),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "admin_set_threshold_error"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_deal_threshold_change') and user_id in ADMIN_ID:
            try:
                threshold = int(text.strip())
                if threshold < 0:
                    raise ValueError("Threshold must be non-negative")
                save_deal_threshold(threshold)
                context.user_data.clear()
                await update.message.reply_text(
                    get_text(lang, "admin_set_deal_threshold_success", threshold=threshold),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "admin_set_deal_threshold_error"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_admin_promote') and user_id in ADMIN_ID:
            try:
                target_user_id = int(text.strip())
                if target_user_id in SUPER_ADMIN_IDS:
                    await update.message.reply_text(
                        get_text(lang, "admin_promote_super_admin_error"),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )
                    return
                ensure_user_exists(target_user_id)
                if user_data[target_user_id].get('is_admin'):
                    await update.message.reply_text(
                        get_text(lang, "admin_user_already_admin", user_id=target_user_id),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )
                    return
                user_data[target_user_id]['is_admin'] = 1
                user_data[target_user_id]['granted_by'] = user_id
                ADMIN_ID.add(target_user_id)
                save_user_data(target_user_id)
                context.user_data.clear()
                await update.message.reply_text(
                    get_text(lang, "admin_user_promoted", user_id=target_user_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "admin_user_not_found", user_id=text.strip()),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_admin_demote') and user_id in ADMIN_ID:
            try:
                target_user_id = int(text.strip())
                if target_user_id in SUPER_ADMIN_IDS:
                    await update.message.reply_text(
                        get_text(lang, "admin_demote_super_admin_error"),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )
                    return
                if target_user_id == user_id:
                    await update.message.reply_text(
                        get_text(lang, "admin_self_demote_error"),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )
                    return
                if target_user_id not in ADMIN_ID:
                    await update.message.reply_text(
                        get_text(lang, "admin_user_not_admin", user_id=target_user_id),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                    )
                    return
                user_data[target_user_id]['is_admin'] = 0
                user_data[target_user_id]['granted_by'] = None
                ADMIN_ID.remove(target_user_id)
                save_user_data(target_user_id)
                context.user_data.clear()
                await update.message.reply_text(
                    get_text(lang, "admin_user_demoted", user_id=target_user_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "admin_user_not_found", user_id=text.strip()),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text(
                    get_text(lang, "admin_user_not_found", user_id=text.strip()),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_admin_reply') and user_id in ADMIN_ID:
            try:
                reply_user_id = context.user_data.get('awaiting_admin_reply')
                reply_message = text.strip()
                context.user_data.clear()
                await context.bot.send_message(
                    reply_user_id,
                    get_text(user_data.get(reply_user_id, {}).get('lang', 'ru'), "admin_reply_message", message=reply_message),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                await update.message.reply_text(
                    get_text(lang, "admin_reply_sent_message", user_id=reply_user_id),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except Exception as e:
                logger.error(f"Error sending admin reply to user {reply_user_id}: {e}")
                await update.message.reply_text(
                    get_text(lang, "admin_reply_error"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        elif context.user_data.get('awaiting_support_message'):
            support_message = text.strip()
            context.user_data.clear()
            try:
                user_chat = await context.bot.get_chat(user_id)
                username = user_chat.username or "Не указан"
                full_name = user_chat.full_name or "Не указан"
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    get_text('ru', "admin_support_message",
                            username=username,
                            full_name=full_name,
                            user_id=user_id,
                            message=support_message),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text('ru', "admin_reply_button"), callback_data=f'reply_to_user_{user_id}')]
                    ])
                )
                await update.message.reply_text(
                    get_text(lang, "support_message_sent"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except Exception as e:
                logger.error(f"Error sending support message to admin chat {ADMIN_CHAT_ID}: {e}")
                await update.message.reply_text(
                    get_text(lang, "support_message_error"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )

        else:
            await update.message.reply_text(
                get_text(lang, "unknown_command_message"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )

    except Exception as e:
        logger.error(f"Error in handle_message: {e}", exc_info=True)
        await update.message.reply_text(
            get_text(lang, "error_message"),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}", exc_info=True)
    if update and update.effective_chat:
        lang = user_data.get(update.effective_user.id, {}).get('lang', 'ru')
        try:
            await context.bot.send_message(
                update.effective_chat.id,
                get_text(lang, "error_message"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_data.get(user_id, {}).get('lang', 'ru')
    context.user_data.clear()
    await update.message.reply_text(
        get_text(lang, "operation_cancelled"),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
    )

def main():
    init_db()
    load_data()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Starting bot...")
    try:
        app.run_polling()
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)

if __name__ == '__main__':
    main()