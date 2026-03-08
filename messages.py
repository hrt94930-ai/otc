# Тексты на русском языке
RU_TEXTS = {
    "start_message": (
        "Добро пожаловать в ELF OTC – надежный P2P гарант\n\n"
        "💼 Покупайте и продавайте всё, что угодно – безопасно!\n"
        "От Telegram-подарков и NFT до токенов и фиата – сделки проходят легко и без риска.\n\n"
        "🔹 Удобное управление кошельками\n"
        "🔹 Реферальная система\n"
        "📖 Как пользоваться?\n"
        "Ознакомьтесь с инструкцией — https://t.me/otcgifttg/71034/71035\n\n"
        "Выберите нужный раздел ниже:"
    ),
    "wallet_message": (
        "💼 Ваш текущий кошелек: {wallet}\n\n"
        "Отправьте новые реквизиты кошелька для изменения или нажмите кнопку ниже для возврата в меню."
    ),
    "create_deal_message": (
        "💼 Создание сделки\n\n"
        "Введите сумму {valute} сделки в формате: `100.5`"
    ),
    "referral_message": (
        "🔗 Ваша реферальная ссылка:\n{referral_link}\n\n"
        "👥 Количество рефералов: 0\n"
        "💰 Заработано с рефералов: 0 {valute}\n"
        "40% от комиссии бота"
    ),
    "withdraw_message": (
        "💸 Вывод средств\n\n"
        "💰 Ваш баланс: {balance} {valute}\n"
        "Минимальная сумма вывода: 3000 {valute}\n\n"
        "{status_message}"
    ),
    "withdraw_minimum_error": (
        "❌ Минимальная сумма для вывода — 3000 {valute}\n"
        "Ваш текущий баланс: {balance} {valute}"
    ),
    "withdraw_available": (
        "✅ Вы можете вывести средства!\n\n"
        "Нажмите кнопку ниже для вывода средств:"
    ),
    "withdraw_success": (
        "✅ Заявка на вывод средств создана!\n\n"
        "💰 Сумма: {amount} {valute}\n"
        "⏱ Статус: В обработке\n\n"
        "Средства будут отправлены на ваш кошелек после проверки администратором."
    ),
    "change_lang_message": (
        "🌍 Выберите язык:\n\n"
        "Выберите язык:"
    ),
    "lang_set_message": "Язык изменен на русский.",
    "deal_created_message": (
        "✅ Сделка успешно создана!\n\n"
        "💰 Сумма: {amount} {valute}\n"
        "📜 Описание: {description}\n"
        "🔗 Ссылка для покупателя: {deal_link}"
    ),
    "payment_confirmed_message": (
        "✅ Оплата подтверждена для сделки #{deal_id}\n\n"
        "💰 Сумма: {amount} {valute}\n"
        "📜 Описание: {description}\n"
        "🔗 Сделка завершена."
    ),
    "payment_confirmed_seller_message": (
        "✅ Оплата подтверждена для сделки #{deal_id}\n\n"
        "Описание: {description}\n\n"
        "⚠️ Передача подарка напрямую — это мошенничество!\n"
        "• Нельзя передавать напрямую. Как только сделка создана, передавайте подарок только на официальный аккаунт @ElfiSupport\n\n"
        "⚠️ Отправляйте подарок только тому, кто указан в сделке. В случае отправки подарка другому человеку возврата не будет. Обязательно записывайте на видео момент передачи.\n\n"
        "После отправки подарка нажмите кнопку ниже, чтобы средства поступили на ваш баланс:"
    ),
    "seller_notification_message": (
        "Пользователь @{buyer_username} присоединился к сделке #{deal_id}\n"
        "• Успешные сделки: {successful_deals}\n\n"
        "⚠️ Проверьте, что это тот же пользователь, с которым вы вели диалог ранее!"
    ),
    "gift_sent_confirmation_message": (
        "✅ Вы подтвердили отправку подарка по сделке #{deal_id}\n\n"
        "Средства в размере {amount} {valute} зачислены на ваш баланс.\n"
        "Спасибо за использование сервиса!"
    ),
    "gift_sent_buyer_notification": (
        "✅ Продавец подтвердил отправку подарка по сделке #{deal_id}\n\n"
        "Сделка успешно завершена. Спасибо за использование сервиса!"
    ),
    "insufficient_balance_message": "❌ Недостаточно средств на балансе!",
    "wallet_updated_message": "💼 Ваш кошелек обновлен: {wallet}",
    "admin_panel_message": "Админ-панель:",
    "admin_view_deals_message": "Активные сделки:\n{deals_list}",
    "admin_change_balance_message": "Введите ID пользователя и новый баланс в формате: user_id баланс",
    "admin_change_successful_deals_message": "Введите ID пользователя и количество успешных сделок в формате: user_id количество",
    "admin_change_valute_message": "Введите новую валюту (например, USD, EUR, RUB):",
    "menu_button": "🔙Вернуться в меню",
    "pay_from_balance_button": "Оплатить с баланса",
    "add_wallet_button": "🪙Добавить/изменить кошелёк",
    "create_deal_button": "📄Создать сделку",
    "referral_button": "🧷Реферальная ссылка",
    "withdraw_button": "💸 Вывод средств",
    "confirm_withdraw_button": "💸 Вывести средства",
    "change_lang_button": "🌐Change language",
    "support_button": "📞Поддержка",
    "gift_sent_button": "✅ Я отправил подарок",
    "english_lang_button": "English",
    "russian_lang_button": "Русский",
    "admin_view_deals_button": "Просмотр сделок",
    "admin_change_balance_button": "Изменить баланс пользователя",
    "admin_change_successful_deals_button": "Изменить успешные сделки",
    "admin_change_valute_button": "Изменить валюту",
    "deal_info_message": (
        "💳 Информация о сделке #{deal_id}\n\n"
        "👤 Вы покупатель в сделке.\n"
        "📌 Продавец: @{seller_username}\n"
        "• Успешные сделки: {successful_deals}\n\n"
        "• Вы покупаете: {description}\n\n"
        "🏦 Адрес для оплаты: {wallet}\n\n"
        "💰 Сумма к оплате: {amount} {valute}\n"
        "📝 Комментарий к платежу(мемо): {deal_id}\n\n"
        "⚠️ Пожалуйста, убедитесь в правильности данных перед оплатой. Комментарий(мемо) обязателен!\n\n"
        "После оплаты ожидайте автоматического подтверждения."
    ),
    "awaiting_description_message": (
        "📝 Укажите, что вы предлагаете в этой сделке:\n\n"
        "`Пример: 10 Кепок и Пепе...`"
    ),
}

# Тексты на английском языке
EN_TEXTS = {
    "start_message": (
        "Welcome to ELF OTC – a reliable P2P guarantor\n\n"
        "💼 Buy and sell anything – safely!\n"
        "From Telegram gifts and NFTs to tokens and fiat – transactions are easy and risk-free.\n\n"
        "🔹 Convenient wallet management\n"
        "🔹 Referral system\n"
        "📖 How to use?\n"
        "Read the instructions — https://t.me/otcgifttg/71034/71035\n\n"
        "Choose the desired section below:"
    ),
    "wallet_message": (
        "💼 Your current wallet: {wallet}\n\n"
        "Send new wallet details to update or click the button below to return to the menu."
    ),
    "create_deal_message": (
        "💼 Create a deal\n\n"
        "Enter the amount of {valute} in the format: `100.5`"
    ),
    "referral_message": (
        "🔗 Your referral link:\n{referral_link}\n\n"
        "👥 Number of referrals: 0\n"
        "💰 Earned from referrals: 0 {valute}\n"
        "40% of the bot's commission"
    ),
    "withdraw_message": (
        "💸 Withdrawal\n\n"
        "💰 Your balance: {balance} {valute}\n"
        "Minimum withdrawal amount: 3000 {valute}\n\n"
        "{status_message}"
    ),
    "withdraw_minimum_error": (
        "❌ Minimum withdrawal amount is 3000 {valute}\n"
        "Your current balance: {balance} {valute}"
    ),
    "withdraw_available": (
        "✅ You can withdraw funds!\n\n"
        "Click the button below to withdraw funds:"
    ),
    "withdraw_success": (
        "✅ Withdrawal request created!\n\n"
        "💰 Amount: {amount} {valute}\n"
        "⏱ Status: Processing\n\n"
        "Funds will be sent to your wallet after admin verification."
    ),
    "change_lang_message": (
        "🌍 Choose your language:\n\n"
        "Choose language:"
    ),
    "lang_set_message": "Language set to English.",
    "deal_created_message": (
        "✅ Deal successfully created!\n\n"
        "💰 Amount: {amount} {valute}\n"
        "📜 Description: {description}\n"
        "🔗 Buyer link: {deal_link}"
    ),
    "payment_confirmed_message": (
        "✅ Payment confirmed for deal #{deal_id}\n\n"
        "💰 Amount: {amount} {valute}\n"
        "📜 Description: {description}\n"
        "🔗 Deal completed."
    ),
    "payment_confirmed_seller_message": (
        "✅ Payment confirmed for deal #{deal_id}\n\n"
        "Description: {description}\n\n"
        "⚠️ Direct gift transfer is fraud!\n"
        "• Do not transfer directly. Once a deal is created, only send the gift to the official account @ElfiSupport\n\n"
        "⚠️ Send the gift only to the person specified in the deal. If you send the gift to someone else, there will be no refund. Be sure to record the moment of transfer on video.\n\n"
        "After sending the gift, click the button below to receive the funds to your balance:"
    ),
    "seller_notification_message": (
        "User @{buyer_username} has joined the deal #{deal_id}\n"
        "• Successful deals: {successful_deals}\n\n"
        "⚠️ Make sure this is the same user you were talking to earlier!"
    ),
    "gift_sent_confirmation_message": (
        "✅ You have confirmed the gift delivery for deal #{deal_id}\n\n"
        "Funds in the amount of {amount} {valute} have been credited to your balance.\n"
        "Thank you for using our service!"
    ),
    "gift_sent_buyer_notification": (
        "✅ The seller has confirmed the gift delivery for deal #{deal_id}\n\n"
        "The deal has been successfully completed. Thank you for using our service!"
    ),
    "insufficient_balance_message": "❌ Insufficient balance!",
    "wallet_updated_message": "💼 Your wallet has been updated: {wallet}",
    "admin_panel_message": "Admin panel:",
    "admin_view_deals_message": "Active deals:\n{deals_list}",
    "admin_change_balance_message": "Enter user ID and new balance in the format: user_id balance",
    "admin_change_successful_deals_message": "Enter user ID and number of successful deals in the format: user_id count",
    "admin_change_valute_message": "Enter new currency (e.g., USD, EUR, RUB):",
    "menu_button": "🔙Back to menu",
    "pay_from_balance_button": "Pay from balance",
    "add_wallet_button": "🪙Add/change wallet",
    "create_deal_button": "📄Create deal",
    "referral_button": "🧷Referral link",
    "withdraw_button": "💸 Withdraw",
    "confirm_withdraw_button": "💸 Withdraw funds",
    "change_lang_button": "🌐Change language",
    "support_button": "📞Support",
    "gift_sent_button": "✅ I sent the gift",
    "english_lang_button": "English",
    "russian_lang_button": "Русский",
    "admin_view_deals_button": "View deals",
    "admin_change_balance_button": "Change user balance",
    "admin_change_successful_deals_button": "Change successful deals",
    "admin_change_valute_button": "Change currency",
    "deal_info_message": (
        "💳 Deal information #{deal_id}\n\n"
        "👤 You are the buyer in this deal.\n"
        "📌 Seller: @{seller_username}\n"
        "• Successful deals: {successful_deals}\n\n"
        "• You are buying: {description}\n\n"
        "🏦 Payment address: {wallet}\n\n"
        "💰 Amount to pay: {amount} {valute}\n"
        "📝 Payment comment (memo): {deal_id}\n\n"
        "⚠️ Please ensure the data is correct before payment. The comment (memo) is mandatory!\n\n"
        "After payment, wait for automatic confirmation."
    ),
    "awaiting_description_message": (
        "📝 Specify what you are offering in this deal:\n\n"
        "`Example: 10 Caps and Pepe...`"
    ),
}

# Функция для получения текста на выбранном языке
def get_text(lang, key, **kwargs):
    if lang == 'ru':
        return RU_TEXTS.get(key, '').format(**kwargs)
    elif lang == 'en':
        return EN_TEXTS.get(key, '').format(**kwargs)
    return ''