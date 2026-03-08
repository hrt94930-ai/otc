MESSAGES = {
    'ru': {
        'start_message':
        "👋 <b>Добро пожаловать на ELF OTC – твой личный гарант в мире P2P</b>\n\n"
        "🔥 <b>Покупай и продавай что угодно:</b> от Telegram-подарков до токенов\n"
        "• Безопасные сделки с гарантом\n"
        "• Удобные кошельки\n"
        "• Рефералка для профитов\n\n"
        "📖 <b>Гайд:</b> https://t.me/OTC_instructions\n\n"
        "👇 <b>Выбирай че по душе:</b>",
        
        'add_wallet_button': '💳 Кошельки',
        'create_deal_button': '📦 Замутить сделку',
        'deposit_button': '💰 Закинуть бабла',
        'withdraw_button': '💸 Вывести лям',
        'balance_button': '💎 Мой баланс',
        'referral_button': '🤝 Рефералка (заводи друзей)',
        'change_lang_button': '🌐 Сменить язык',
        'support_button': '👨‍💻 Чатик с поддержкой',
        'menu_button': '🏠 На главную',
        
        'admin_reply_button': '💬 Ответить челу',
        'admin_reply_message': '📩 <b>Ответ от админов:</b>\n\n{message}',
        'admin_reply_message_sent': '✅ Ответ улетел к юзеру.',
        'support_message_sent': '✅ Твое сообщение ушло админам. Жди ответа.',
        'broadcast_sent': '✅ Рассылка улетела в люди.',
        
        'admin_balance_changed_message': '💰 Баланс юзера {user_id} изменен на {amount} {valute}.',
        'balance_updated_message': '💰 Твой баланс обновлен: {amount} {valute}.',
        
        'admin_successful_deals_changed_message': '🏆 У юзера {user_id} теперь {count} успешных сделок.',
        'successful_deals_updated_message': '🏆 Твои успешные сделки: {count}.',
        
        'admin_threshold_changed_message': '⚙️ Порог вывода для юзера {user_id} ({valute}) теперь {threshold}.',
        'threshold_updated_message': '⚙️ Порог вывода для {currency} = {threshold}.',
        
        'admin_deal_threshold_changed_message': '⚙️ Минимум успешных сделок для вывода = {threshold}.',
        
        'admin_promoted_success': '👑 Юзер {user_id} теперь админ. Поздравляем!',
        'admin_promoted_message': '👑 Тебя повысили до админа. Не подведи!',
        'admin_demoted_success': '👋 Юзер {user_id} больше не админ.',
        'admin_demoted_message': '👋 Тебя сняли с админки.',
        
        'admin_reply_sent': '✅ Ответ улетел юзеру {user_id}.',
        'invalid_page_number': '❌ Неверный номер страницы. Введи число > 0.',
        
        'admin_promote_super_admin_error': '❌ Супер-админ уже админ, че ты.',
        'admin_demote_super_admin_error': '❌ Супер-админа нельзя снять, сорян.',
        'admin_demote_not_admin': '❌ Этот чел и не админ вовсе.',
        
        'seller_payment_confirmation_message': '💸 Покупатель оплатил сделку #{deal_id}. Ждем подтверждения отправки.',
        'admin_reply_no_user': '❌ Юзер не найден.',
        'admin_reply_error': '❌ Ошибка при отправке ответа.',
        
        'wallet_menu_message': '💳 <b>Выбери тип кошелька:</b>',
        'add_ton_wallet_button': '💎 TON кошелек',
        'add_card_button': '💳 Карта (СБП)',
        
        'not_specified_wallet': '❌ Не указан',
        'not_specified_card': '❌ Не указана',
        
        'add_ton_wallet_message': '💎 <b>Текущий TON кошелек:</b>\n<code>{current_wallet}</code>\n\n✏️ <b>Введи новый адрес TON кошелька:</b>',
        'add_card_message': '💳 <b>Текущая карта (СБП):</b>\n<code>{current_card}</code>\n\n✏️ <b>Введи новые реквизиты карты:</b>',
        
        'wallet_updated': '✅ <b>{wallet_type} обновлен:</b>\n<code>{details}</code>',
        
        'no_requisites_message': '❌ <b>У тебя нет реквизитов для получения бабла.</b>\nДобавь кошелек или карту в разделе "Кошельки".',
        
        'choose_payment_method_message': '💸 <b>Выбери метод получения оплаты:</b>',
        'payment_ton_button': '💎 TON',
        'payment_sbp_button': '💳 Карта РФ',
        'payment_stars_button': '⭐ Звезды',
        
        'create_deal_message': '💰 <b>Введи сумму сделки в {valute}:</b>\n\n<i>Пример: 1.5</i>',
        'invalid_amount_message': '❌ <b>Сумма должна быть числом > 0.</b>\nБез букв, только цифры.',
        
        'buyer_confirm_received_notification': '✅ <b>Покупатель (ID: {buyer_id}) подтвердил получение по сделке #{deal_id}.</b>\nСделка завершена, профит!',
        
        'awaiting_description_message': '📝 <b>Введи описание сделки:</b>\n\n<i>Пример: Кепочка и Мила</i>',
        
        'admin_buyer_received_notification': '✅ <b>Покупатель (ID: {buyer_id}) получил товар по сделке #{deal_id}.</b>\nПродавец: @{seller_username}\nСумма: {amount} {valute}\nСделка закрыта.',
        
        'deal_created_message': 
        "✅ <b>Сделка создана!</b>\n\n"
        "💰 <b>Сумма:</b> {amount} {valute}\n"
        "📝 <b>Описание:</b> {description}\n\n"
        "🔗 <b>Ссылка на сделку:</b>\n{deal_link}\n\n"
        "<i>Кидай ссылку покупателю</i>",
        
        'deal_info_ton_message': 
        "💎 <b>Сделка #{deal_id}</b>\n\n"
        "👤 <b>Ты покупатель</b>\n"
        "📌 <b>Продавец:</b> @{seller_username}\n"
        "🏆 <b>Успешных сделок:</b> {successful_deals}\n"
        "📦 <b>Покупаешь:</b> {description}\n\n"
        "🏦 <b>Адрес для оплаты (TON):</b>\n<code>{wallet}</code>\n"
        "💰 <b>Сумма:</b> {amount} TON\n"
        "📝 <b>Комментарий (мемо):</b> <code>{deal_id}</code>\n\n"
        "⚠️ <b>Важно!</b> Укажи мемо при переводе!\n"
        "⏳ После оплаты жди подтверждения от админа.",
        
        'deal_info_sbp_message':
        "💳 <b>Сделка #{deal_id}</b>\n\n"
        "👤 <b>Ты покупатель</b>\n"
        "📌 <b>Продавец:</b> @{seller_username}\n"
        "🏆 <b>Успешных сделок:</b> {successful_deals}\n"
        "📦 <b>Покупаешь:</b> {description}\n\n"
        "🏦 <b>Карта для оплаты (СБП):</b>\n<code>{card}</code>\n"
        "💰 <b>Сумма:</b> {amount} RUB\n"
        "📝 <b>Комментарий:</b> <code>{deal_id}</code>\n\n"
        "⚠️ <b>Важно!</b> Укажи комментарий при переводе!\n"
        "⏳ После оплаты жди подтверждения от админа.",
        
        'deal_info_stars_message':
        "⭐ <b>Сделка #{deal_id}</b>\n\n"
        "👤 <b>Ты покупатель</b>\n"
        "📌 <b>Продавец:</b> @{seller_username}\n"
        "🏆 <b>Успешных сделок:</b> {successful_deals}\n"
        "📦 <b>Покупаешь:</b> {description}\n\n"
        "💰 <b>Сумма:</b> {amount} XTR\n"
        "📝 <b>Комментарий:</b> <code>{deal_id}</code>\n\n"
        "⚠️ <b>Важно!</b> Не забудь про комментарий!\n"
        "⏳ После оплаты жди подтверждения от админа.",
        
        'pay_from_balance_button': '💰 Оплатить с баланса',
        
        'seller_notification_message': 
        "🔔 <b>По сделке #{deal_id} появился покупатель!</b>\n\n"
        "👤 <b>Покупатель:</b> @{buyer_username}\n"
        "🏆 <b>Успешных сделок:</b> {successful_deals}\n\n"
        "<i>Жди оплаты</i>",
        
        'payment_confirmed_message': 
        "✅ <b>Оплата по сделке #{deal_id} прошла!</b>\n\n"
        "⏳ <i>Ожидай, пока продавец отправит товар</i>",
        
        'payment_confirmed_seller_message':
        "💰 <b>Оплата по сделке #{deal_id} получена!</b>\n\n"
        "📦 <b>Описание:</b> {description}\n"
        "👤 <b>Покупатель:</b> @{buyer_username}\n\n"
        "👉 <b>Отправь товар/услугу покупателю</b>",
        
        'seller_confirm_sent_button': '✅ Отправил, подтверждаю',
        'seller_confirm_sent_message': '✅ <b>Ты подтвердил отправку по сделке #{deal_id}</b>\n\n⏳ Ждем подтверждения от покупателя',
        
        'seller_confirm_sent_notification':
        "🔔 <b>Продавец (@{seller_username}) отправил товар по сделке #{deal_id}</b>\n\n"
        "👉 <b>Подтверди получение</b>",
        
        'buyer_confirm_received_button': '✅ Товар получил',
        'buyer_confirm_received_message': '✅ <b>Сделка #{deal_id} завершена!</b>\n\nСпасибо за покупку!',
        
        'insufficient_balance_message':
        "❌ <b>Не хватает бабла на балансе</b>\n\n"
        "💰 <b>Нужно:</b> {amount} {valute}\n"
        "💎 <b>Доступно:</b> {balance} {valute}",
        
        'deposit_amount_request': '💰 <b>Введи сумму пополнения в {valute}:</b>\n\n{deposit_info}',
        
        'deposit_amount_request_ton':
        "💰 <b>Введи сумму пополнения в TON:</b>\n\n"
        "🏦 <b>Адрес для пополнения:</b>\n<code>{ton_address}</code>",
        
        'deposit_amount_request_rub':
        "💰 <b>Введи сумму пополнения в RUB:</b>\n\n"
        "💳 <b>Реквизиты (СБП):</b>\n<code>{sbp_card}</code>",
        
        'deposit_amount_request_stars':
        "💰 <b>Введи сумму пополнения в XTR:</b>\n\n"
        "⭐ <i>Пополнение через Telegram Stars</i>",
        
        'choose_deposit_currency': '💰 <b>Выбери валюту для пополнения:</b>',
        'invalid_deposit_amount_message': '❌ <b>Сумма должна быть числом > 0</b>',
        
        'deposit_screenshot_request': '📸 <b>Отправь скриншот перевода</b>',
        'deposit_screenshot_invalid': '❌ <b>Нужно отправить фото (скриншот)</b>',
        
        'deposit_screenshot_received': '✅ <b>Скриншот улетел на проверку админам</b>\n⏳ Жди подтверждения',
        'deposit_confirmed_message': '✅ <b>Пополнение на {amount} {valute} подтверждено!</b>',
        'deposit_rejected_message': '❌ <b>Пополнение отклонили</b>\nСвяжись с поддержкой',
        
        'withdraw_amount_request': '💸 <b>Выбери валюту для вывода:</b>',
        'withdraw_amount_input': '💸 <b>Введи сумму вывода в {valute}:</b>',
        'invalid_withdraw_amount_message': '❌ <b>Сумма должна быть числом > 0</b>',
        
        'withdraw_below_threshold_message': 
        "❌ <b>Сумма меньше минимального порога</b>\n"
        "⚙️ <b>Порог:</b> {threshold} {valute}",
        
        'withdraw_successful_deals_threshold_message':
        "❌ <b>Для вывода нужно больше успешных сделок</b>\n"
        "🏆 <b>Нужно:</b> {threshold}\n"
        "📊 <b>У тебя:</b> {successful_deals}",
        
        'withdraw_requisites_request': '✏️ <b>Введи {requisite_type} для вывода:</b>',
        'withdraw_request_successful': '✅ <b>Запрос на вывод отправлен админам</b>\n⏳ Жди подтверждения',
        
        'withdraw_confirmed_message': '✅ <b>Вывод {amount} {valute} подтвержден!</b>',
        'withdraw_rejected_message': '❌ <b>Вывод отклонили</b>\nСвяжись с поддержкой',
        
        'balance_message':
        "💎 <b>Твой баланс:</b>\n\n"
        "• <b>TON:</b> {ton}\n"
        "• <b>RUB:</b> {rub}\n"
        "• <b>XTR:</b> {stars}",
        
        'balance_menu_message': '💎 <b>Твой баланс:</b>',
        
        'support_message_request': '📝 <b>Напиши сообщение для поддержки:</b>',
        'support_response_message': '📬 <b>Ответ от поддержки:</b>\n\n{response}',
        
        'admin_panel_message': '⚙️ <b>Админ-панель:</b>\n\nВыбери действие:',
        'admin_broadcast_button': '📢 Рассылка',
        'admin_view_deals_button': '📋 Все сделки',
        'admin_change_balance_button': '💰 Поменять баланс',
        'admin_change_successful_deals_button': '🏆 Поменять успешные сделки',
        'admin_change_valute_button': '💱 Сменить валюту',
        'admin_manage_admins_button': '👮 Управление админами',
        'admin_set_threshold_button': '⚙️ Порог вывода',
        'admin_set_deal_threshold_button': '🏆 Порог сделок',
        'admin_list_button': '📜 Список админов',
        
        'admin_broadcast_message': '📢 <b>Введи текст для рассылки:</b>',
        
        'broadcast_success_message':
        "✅ <b>Рассылка выполнена!</b>\n\n"
        "📨 <b>Успешно:</b> {success_count}\n"
        "❌ <b>Не отправилось:</b> {fail_count}",
        
        'admin_view_deals_message': '📋 <b>Активные сделки:</b>\n\n{deals_list}',
        'no_active_deals_message': '📭 <b>Нет активных сделок</b>',
        
        'admin_view_deal_message':
        "📋 <b>Сделка #{deal_id}</b>\n\n"
        "👤 <b>Продавец:</b> @{seller_username} (ID: {seller_id})\n"
        "🏆 <b>Успешных сделок:</b> {seller_successful_deals}\n\n"
        "👤 <b>Покупатель:</b> @{buyer_username} (ID: {buyer_id})\n"
        "🏆 <b>Успешных сделок:</b> {buyer_successful_deals}\n\n"
        "📦 <b>Описание:</b> {description}\n"
        "💰 <b>Сумма:</b> {amount} {valute}\n"
        "💳 <b>Реквизиты:</b> {payment_details}\n"
        "📊 <b>Статус:</b> {status}",
        
        'admin_confirm_deal_button': '✅ Подтвердить оплату',
        'admin_cancel_deal_button': '❌ Отменить сделку',
        'admin_confirm_deal_message': '✅ <b>Оплата по сделке #{deal_id} подтверждена!</b>',
        'admin_cancel_deal_message': '❌ <b>Сделка #{deal_id} отменена</b>',
        
        'deal_cancelled_notification': '❌ <b>Сделку #{deal_id} отменил админ</b>\nСвяжись с поддержкой',
        
        'admin_new_deal_notification':
        "📦 <b>Новая сделка #{deal_id}</b>\n\n"
        "👤 <b>Продавец:</b> @{seller_username} (ID: {seller_id})\n"
        "👤 <b>Покупатель:</b> @{buyer_username} (ID: {buyer_id})\n"
        "📦 <b>Описание:</b> {description}\n"
        "💰 <b>Сумма:</b> {amount} {valute}",
        
        'admin_new_deposit_notification':
        "💰 <b>Новый запрос на пополнение</b>\n\n"
        "👤 <b>Юзер:</b> @{username} ({full_name})\n"
        "🆔 <b>ID:</b> {user_id}\n"
        "💰 <b>Сумма:</b> {amount} {valute}\n\n"
        "📸 <i>Проверь скриншот</i>",
        
        'admin_deposit_confirmed_message': '✅ <b>Пополнение для {user_id} на {amount} {valute} подтверждено</b>',
        'admin_deposit_rejected_message': '❌ <b>Пополнение для {user_id} отклонено</b>',
        
        'admin_withdraw_request_notification':
        "💸 <b>Новый запрос на вывод</b>\n\n"
        "👤 <b>Юзер:</b> @{username} ({full_name})\n"
        "🆔 <b>ID:</b> {user_id}\n"
        "💰 <b>Сумма:</b> {amount} {currency}\n"
        "💳 <b>Реквизиты:</b>\n<code>{requisites}</code>",
        
        'admin_withdraw_confirmed_message': '✅ <b>Вывод для {user_id} на {amount} {valute} подтвержден</b>',
        'admin_withdraw_rejected_message': '❌ <b>Вывод для {user_id} отклонен</b>',
        
        'deal_status_active': '🟢 Активна',
        'deal_status_confirmed': '✅ Оплачена',
        'deal_status_sent': '📦 Отправлено',
        'deal_status_completed': '🎉 Завершена',
        'deal_status_cancelled': '❌ Отменена',
        
        'deal_not_found_message': '❌ <b>Сделка #{deal_id} не найдена</b>',
        
        'referral_message':
        "🤝 <b>Твоя реферальная ссылка:</b>\n\n"
        "{referral_link}\n\n"
        "<i>Заводи друзей и получай профит!</i>",
        
        'choose_lang_message': '🌐 <b>Выбери язык:</b>',
        'lang_set_message': '✅ <b>Язык изменен</b>',
        
        'unknown_callback_error': '❌ <b>Что-то пошло не так</b>\nПопробуй еще раз или вернись в меню',
        
        'contact_support_button': '👨‍💻 Написать в поддержку',
        
        'admin_reply_to_user_message': '✏️ <b>Введи ответ для юзера {user_id}:</b>',
        'admin_reply_sent_message': '✅ <b>Ответ улетел</b>',
        
        'admin_change_balance_request': '✏️ <b>Введи ID юзера и сумму</b>\n\n<i>Пример: 12345 100 TON</i>',
        'admin_change_balance_success': '✅ <b>Баланс юзера {user_id} изменен:</b> {amount} {currency}',
        'admin_change_balance_error': '❌ <b>Ошибка</b>\nПроверь формат: ID сумма ВАЛЮТА',
        
        'admin_change_successful_deals_request': '✏️ <b>Введи ID юзера и количество сделок</b>\n\n<i>Пример: 12345 5</i>',
        'admin_change_successful_deals_success': '✅ <b>У юзера {user_id} теперь {count} успешных сделок</b>',
        'admin_change_successful_deals_error': '❌ <b>Ошибка</b>\nПроверь формат: ID число',
        
        'admin_set_threshold_request': '✏️ <b>Введи ID, валюту и порог</b>\n\n<i>Пример: 12345 TON 10</i>',
        'admin_set_threshold_success': '✅ <b>Порог для юзера {user_id} ({currency}) = {threshold}</b>',
        'admin_set_threshold_error': '❌ <b>Ошибка</b>\nПроверь формат: ID ВАЛЮТА число',
        
        'admin_set_deal_threshold_request': '✏️ <b>Введи минимальное количество успешных сделок для вывода</b>\n\n<i>Пример: 3</i>',
        'admin_set_deal_threshold_success': '✅ <b>Минимум успешных сделок для вывода = {threshold}</b>',
        'admin_set_deal_threshold_error': '❌ <b>Ошибка</b>\nВведи число',
        
        'admin_manage_admins_request': '✏️ <b>Введи ID юзера:</b>',
        'admin_promote_button': '👑 Сделать админом',
        'admin_demote_button': '👋 Снять с админки',
        
        'admin_user_promoted': '✅ <b>Юзер {user_id} теперь админ!</b>',
        'admin_user_demoted': '✅ <b>Юзер {user_id} больше не админ</b>',
        'admin_user_not_found': '❌ <b>Юзер {user_id} не найден</b>',
        'admin_self_demote_error': '❌ <b>Себя нельзя снять с админки</b>',
        
        'admin_admin_list': '📜 <b>Список админов:</b>\n\n{admin_list}',
        'admin_add_admin_request': '✏️ <b>Введи ID будущего админа:</b>',
        'admin_remove_admin_request': '✏️ <b>Введи ID для снятия с админки:</b>',
        
        'admin_user_already_admin': '❌ <b>Юзер {user_id} уже админ</b>',
        'admin_user_not_admin': '❌ <b>Юзер {user_id} не админ</b>',
        
        'admin_deposit_confirm_button': '✅ Ок',
        'admin_deposit_reject_button': '❌ Отказ',
        'admin_withdraw_confirm_button': '✅ Ок',
        'admin_withdraw_reject_button': '❌ Отказ',
        
        'unknown_message_error': '❌ <b>Че-то не понял</b>\nВыбери действие из меню',
        'error_message': '❌ <b>Ошибка</b>\nПопробуй позже'
    },
    
    'en': {
        'start_message':
        "👋 <b>Welcome to ELF OTC – your P2P guarantor</b>\n\n"
        "🔥 <b>Buy and sell anything:</b> from Telegram gifts to tokens\n"
        "• Safe deals with guarantor\n"
        "• Convenient wallets\n"
        "• Referral program\n\n"
        "📖 <b>Guide:</b> https://t.me/OTC_instructions\n\n"
        "👇 <b>Choose option:</b>",
        
        'add_wallet_button': '💳 Wallets',
        'create_deal_button': '📦 Create Deal',
        'deposit_button': '💰 Deposit',
        'withdraw_button': '💸 Withdraw',
        'balance_button': '💎 My Balance',
        'referral_button': '🤝 Referral',
        'change_lang_button': '🌐 Language',
        'support_button': '👨‍💻 Support',
        'menu_button': '🏠 Main Menu',
        
        'admin_panel_message': '⚙️ <b>Admin Panel:</b>',
        'admin_broadcast_button': '📢 Broadcast',
        'admin_view_deals_button': '📋 View Deals',
        'admin_change_balance_button': '💰 Change Balance',
        'admin_change_successful_deals_button': '🏆 Change Successful Deals',
        'admin_change_valute_button': '💱 Change Currency',
        'admin_manage_admins_button': '👮 Manage Admins',
        'admin_set_threshold_button': '⚙️ Set Threshold',
        'admin_set_deal_threshold_button': '🏆 Set Deal Threshold',
        'admin_list_button': '📜 Admin List',
        
        'balance_message':
        "💎 <b>Your balance:</b>\n\n"
        "• <b>TON:</b> {ton}\n"
        "• <b>RUB:</b> {rub}\n"
        "• <b>XTR:</b> {stars}",
        
        'unknown_message_error': '❌ <b>Unknown command</b>\nChoose from menu',
        'error_message': '❌ <b>Error</b>\nTry again later',
        
        'menu_button': '🏠 Main Menu',
        'choose_lang_message': '🌐 <b>Choose language:</b>',
        'lang_set_message': '✅ <b>Language changed</b>',
        
        'deal_created_message': 
        "✅ <b>Deal created!</b>\n\n"
        "💰 <b>Amount:</b> {amount} {valute}\n"
        "📝 <b>Description:</b> {description}\n\n"
        "🔗 <b>Deal link:</b>\n{deal_link}",
        
        'pay_from_balance_button': '💰 Pay from Balance',
        'insufficient_balance_message': '❌ <b>Insufficient balance</b>',
        
        'admin_change_balance_request': '✏️ <b>Enter user ID and amount</b>\n\n<i>Example: 12345 100 TON</i>',
        'admin_change_balance_success': '✅ <b>User {user_id} balance changed:</b> {amount} {currency}',
        'admin_change_balance_error': '❌ <b>Error</b>\nCheck format: ID amount CURRENCY'
    }
}

def get_text(lang, key, **kwargs):
    texts_to_use = MESSAGES.get(lang, MESSAGES['ru'])
    message_template = texts_to_use.get(key, '')

    if not message_template:
        fallback_lang = 'en' if lang == 'ru' else 'ru'
        message_template = MESSAGES.get(fallback_lang, {}).get(key, '')

    if not message_template:
        print(f"⚠️ Warning: Text key '{key}' not found for language '{lang}'")
        return f"❌ Error: Text for '{key}' not found..."

    return message_template.format(**kwargs)