import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.ext import MessageHandler, filters

# Настройки бота
BOT_TOKEN = "8356262671:AAEo7mblRDjM6iGVmHe7785N6AGlHa_oBFI"
CHANNEL_USERNAME = "@MansoryHolidolla"
CHANNEL_INVITE_LINK = "https://t.me/+gBFIXpBbpl1jNzJi"  # Новая ссылка для первого канала
CHANNEL_CHAT_ID = "-1003204433403"  # ID для проверки подписки
CHANNEL_2_USERNAME = "@HataMasona"
CHANNEL_2_CHAT_ID = "@HataMasona"
CHANNEL_3_USERNAME = "@HolidollaModz"
CHANNEL_3_CHAT_ID = "@HolidollaModz"
SUPPORT_USERNAME = "@Manu_Maso"
APK_URL = "https://t.me/manko1112"

# Название файла
FILE_NAME = "Mansory Holidolla V1.9"

# Простая статистика в памяти
bot_stats = {
    "total_users": 0,
    "total_downloads": 0,
    "users": set()
}

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_main_keyboard():
    """Создает основную клавиатуру"""
    keyboard = [
        ["🎁 Получить APK", "ℹ️ Помощь"],
        ["📢 Наши каналы", "💬 Поддержка"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Выберите действие...")


async def check_all_subscriptions(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> dict:
    """Проверяет подписку на все каналы"""
    subscriptions = {}

    channels = [
        (CHANNEL_USERNAME, CHANNEL_CHAT_ID),
        (CHANNEL_2_USERNAME, CHANNEL_2_CHAT_ID),
        (CHANNEL_3_USERNAME, CHANNEL_3_CHAT_ID)
    ]

    for channel_username, channel_id in channels:
        try:
            chat_member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            subscriptions[channel_username] = chat_member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            logger.error(f"Ошибка при проверке канала {channel_username}: {e}")
            subscriptions[channel_username] = False

    return subscriptions


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user

    # Добавляем пользователя в статистику
    bot_stats["total_users"] += 1
    bot_stats["users"].add(user.id)

    welcome_text = f"""
👋 <b>Добро пожаловать, {user.first_name}!</b>

🤖 <b>Mansory Holidolla</b> - премиум мод для вашего устройства!

⭐ <b>Преимущества:</b>
• 🚀 Улучшенная производительность
• 👑 Расширенные возможности  
• 🛡️ Стабильная работа
• 🎁 Эксклюзивные функции

💬 <b>Поддержка:</b> {SUPPORT_USERNAME}

👇 <b>Используйте кнопки ниже для навигации</b>
    """

    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений с кнопок"""
    user_id = update.effective_user.id
    text = update.message.text

    if text == "🎁 Получить APK":
        await update.message.reply_text("🔄 <b>Проверяем подписки...</b>", parse_mode='HTML')

        subscriptions = await check_all_subscriptions(user_id, context)
        all_subscribed = all(subscriptions.values())

        if all_subscribed:
            keyboard = [
                [InlineKeyboardButton(f"📥 Скачать {FILE_NAME}", callback_data="download_apk")],
                [InlineKeyboardButton(f"💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
            ]
            inline_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "✅ <b>Доступ открыт!</b>\n\n"
                f"🚀 <b>{FILE_NAME}</b> готов к скачиванию!\n\n"
                "📥 Нажмите кнопку ниже для скачивания",
                reply_markup=inline_markup,
                parse_mode='HTML'
            )
        else:
            status1 = '✅' if subscriptions[CHANNEL_USERNAME] else '❌'
            status2 = '✅' if subscriptions[CHANNEL_2_USERNAME] else '❌'
            status3 = '✅' if subscriptions[CHANNEL_3_USERNAME] else '❌'

            keyboard = [
                [InlineKeyboardButton(f"📢 {CHANNEL_USERNAME}", url=CHANNEL_INVITE_LINK)],  # Используем новую ссылку
                [InlineKeyboardButton(f"📢 {CHANNEL_2_USERNAME}", url=f"https://t.me/{CHANNEL_2_USERNAME[1:]}")],
                [InlineKeyboardButton(f"📢 {CHANNEL_3_USERNAME}", url=f"https://t.me/{CHANNEL_3_USERNAME[1:]}")],
                [InlineKeyboardButton(f"🔄 Проверить подписки", callback_data="check_again")],
                [InlineKeyboardButton(f"💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
            ]
            inline_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "❌ <b>Требуется подписка на все каналы!</b>\n\n"
                "🔒 <b>Необходимо подписаться:</b>\n"
                f"📢 {CHANNEL_USERNAME} {status1}\n"
                f"📢 {CHANNEL_2_USERNAME} {status2}\n"
                f"📢 {CHANNEL_3_USERNAME} {status3}\n\n"
                "📥 <b>Как получить доступ:</b>\n"
                "1. Нажмите на кнопки каналов ниже\n"
                "2. Подпишитесь на ВСЕ каналы\n"
                "3. Вернитесь и нажмите 'Проверить подписки'",
                reply_markup=inline_markup,
                parse_mode='HTML'
            )

    elif text == "📢 Наши каналы":
        keyboard = [
            [InlineKeyboardButton(f"📢 {CHANNEL_USERNAME}", url=CHANNEL_INVITE_LINK)],  # Используем новую ссылку
            [InlineKeyboardButton(f"📢 {CHANNEL_2_USERNAME}", url=f"https://t.me/{CHANNEL_2_USERNAME[1:]}")],
            [InlineKeyboardButton(f"📢 {CHANNEL_3_USERNAME}", url=f"https://t.me/{CHANNEL_3_USERNAME[1:]}")],
            [InlineKeyboardButton(f"🔄 Проверить подписки", callback_data="check_again")],
            [InlineKeyboardButton("🎁 Получить APK", callback_data="download_menu")]
        ]
        inline_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "📢 <b>Наши каналы</b>\n\n"
            "⭐ <b>Обязательные для подписки:</b>\n\n"
            f"📢 <b>{CHANNEL_USERNAME}</b>\n"
            "• Основные обновления\n"
            "• Новости проекта\n\n"
            f"📢 <b>{CHANNEL_2_USERNAME}</b>\n"
            "• Эксклюзивный контент\n"
            "• Дополнительные материалы\n\n"
            f"📢 <b>{CHANNEL_3_USERNAME}</b>\n"
            "• Эксклюзивный контент\n"
            "• Дополнительные материалы\n\n"
            "⚠️ <i>Подпишитесь на ВСЕ каналы для доступа к APK</i>",
            reply_markup=inline_markup,
            parse_mode='HTML'
        )

    elif text == "💬 Поддержка":
        keyboard = [
            [InlineKeyboardButton(f"💬 Написать в поддержку", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")],
            [InlineKeyboardButton("🎁 Получить APK", callback_data="download_menu")]
        ]
        inline_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "💬 <b>Техническая поддержка</b>\n\n"
            "🔥 <b>Служба поддержки:</b>\n"
            f"{SUPPORT_USERNAME}\n\n"
            "⏰ <b>Режим работы:</b> 24/7\n\n"
            "⚠️ <b>Перед обращением проверьте:</b>\n"
            "• Подписку на все каналы\n"
            "• Стабильность интернет-соединения\n"
            "• Достаточно места на устройстве",
            reply_markup=inline_markup,
            parse_mode='HTML'
        )

    elif text == "ℹ️ Помощь":
        help_text = f"""
ℹ️ <b>Центр помощи</b>

⚙️ <b>Основные команды:</b>
/start - начать работу
/download - получить APK
/help - помощь

📦 <b>Доступная версия:</b>
🚀 {FILE_NAME}

🔒 <b>Требования для доступа:</b>
📢 Подписка на каналы:
• {CHANNEL_USERNAME}
• {CHANNEL_2_USERNAME}  
• {CHANNEL_3_USERNAME}

💬 <b>Поддержка:</b> {SUPPORT_USERNAME}

⚠️ <b>Частые вопросы:</b>
• Не скачивается файл - проверьте интернет
• Не устанавливается - разрешите установку из неизвестных источников
• Не видит подписку - отпишитесь и подпишитесь заново
        """

        await update.message.reply_text(
            help_text,
            reply_markup=get_main_keyboard(),
            parse_mode='HTML'
        )

    else:
        await update.message.reply_text(
            "👋 <b>Используйте кнопки ниже для навигации</b>\n\n"
            "🤖 Или выберите нужный раздел:",
            reply_markup=get_main_keyboard(),
            parse_mode='HTML'
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на инлайн-кнопки"""
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    if query.data in ["download_menu", "check_again"]:
        await query.edit_message_text("🔄 <b>Проверяем подписки...</b>", reply_markup=None, parse_mode='HTML')

        subscriptions = await check_all_subscriptions(user_id, context)
        all_subscribed = all(subscriptions.values())

        if all_subscribed:
            keyboard = [
                [InlineKeyboardButton(f"📥 Скачать {FILE_NAME}", callback_data="download_apk")],
                [InlineKeyboardButton(f"💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "✅ <b>Доступ открыт!</b>\n\n"
                f"🚀 <b>{FILE_NAME}</b> готов к скачиванию!\n\n"
                "📥 Нажмите кнопку ниже для скачивания",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            status1 = '✅' if subscriptions[CHANNEL_USERNAME] else '❌'
            status2 = '✅' if subscriptions[CHANNEL_2_USERNAME] else '❌'
            status3 = '✅' if subscriptions[CHANNEL_3_USERNAME] else '❌'

            keyboard = [
                [InlineKeyboardButton(f"📢 {CHANNEL_USERNAME}", url=CHANNEL_INVITE_LINK)],  # Используем новую ссылку
                [InlineKeyboardButton(f"📢 {CHANNEL_2_USERNAME}", url=f"https://t.me/{CHANNEL_2_USERNAME[1:]}")],
                [InlineKeyboardButton(f"📢 {CHANNEL_3_USERNAME}", url=f"https://t.me/{CHANNEL_3_USERNAME[1:]}")],
                [InlineKeyboardButton(f"🔄 Проверить подписки", callback_data="check_again")],
                [InlineKeyboardButton(f"💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "❌ <b>Требуется подписка!</b>\n\n"
                "🔒 <b>Необходимо подписаться:</b>\n"
                f"📢 {CHANNEL_USERNAME} {status1}\n"
                f"📢 {CHANNEL_2_USERNAME} {status2}\n"
                f"📢 {CHANNEL_3_USERNAME} {status3}\n\n"
                "📥 <b>Как получить доступ:</b>\n"
                "1. Нажмите на кнопки каналов\n"
                "2. Подпишитесь на ВСЕ каналы\n"
                "3. Вернитесь и нажмите 'Проверить подписки'",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

    elif query.data == "download_apk":
        # Добавляем скачивание в статистику
        bot_stats["total_downloads"] += 1

        keyboard = [
            [InlineKeyboardButton(f"📥 Скачать файл", url=APK_URL)],
            [InlineKeyboardButton("🔄 Проверить снова", callback_data="check_again")],
            [InlineKeyboardButton(f"💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🚀 <b>{FILE_NAME}</b>\n\n"
            f"🔗 <b>Ссылка для скачивания:</b>\n{APK_URL}\n\n"
            f"📥 <b>Инструкция по установке:</b>\n"
            "1. Нажмите кнопку 'Скачать файл'\n"
            "2. В открывшемся Telegram нажмите на файл\n"
            "3. Выберите 'Скачать' или 'Download'\n"
            "4. После скачивания установите APK\n"
            "5. Разрешите установку из неизвестных источников",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("download", lambda u, c: handle_message(u, c)))
    application.add_handler(CommandHandler("help", lambda u, c: handle_message(u, c)))
    application.add_handler(CommandHandler("support", lambda u, c: handle_message(u, c)))

    # Обработчики callback'ов
    application.add_handler(CallbackQueryHandler(button_handler,
                                                 pattern="^(download_menu|check_again|download_apk)$"))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен и готов к работе!")
    print(f"📦 Файл: {FILE_NAME}")
    print(f"📢 Каналы: {CHANNEL_USERNAME}, {CHANNEL_2_USERNAME}, {CHANNEL_3_USERNAME}")
    print(f"🔗 Ссылка первого канала: {CHANNEL_INVITE_LINK}")
    print(f"💬 Поддержка: {SUPPORT_USERNAME}")

    application.run_polling()


if __name__ == "__main__":
    main()

