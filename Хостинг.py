import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.ext import MessageHandler, filters

# Настройки бота
BOT_TOKEN = "8356262671:AAFMkS5M9MAnYAPaIHvTa9gnh9ZDVjwOo0M"
CHANNEL_USERNAME = "@MansoryHolidolla"
CHANNEL_CHAT_ID = "-1003204433403"
SUPPORT_USERNAME = "@Manu_Maso"
APK_URL = "https://t.me/Mwdwdu3/2"  # ТОЛЬКО Telegram ссылка
APK_URL_2 = "https://t.me/Mwdwdu3/3"  # Ссылка на второй файл

# Названия файлов
FILE_1_NAME = "Mansory Holidolla V1.8 (Обычный)"
FILE_2_NAME = "Mansory Holidolla 1.8V (Neizzir)"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user

    keyboard = [
        [InlineKeyboardButton("📱 Скачать APK", callback_data="download_menu")],
        [InlineKeyboardButton("📢 Наш канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "🤖 Добро пожаловать в Mansory Holidolla\n\n"
        "📋 Для получения доступа к скачиванию:\n"
        "• Подпишитесь на наш канал\n"
        "• Нажмите кнопку 'Скачать APK'\n"
        "• Выберите нужный файл\n\n"
        "🛠 Если возникли проблемы - обратитесь в поддержку",
        reply_markup=reply_markup
    )


async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Проверяет, подписан ли пользователь на канал"""
    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_CHAT_ID, user_id=user_id)
        allowed_statuses = ['member', 'administrator', 'creator']

        if chat_member.status in allowed_statuses:
            logger.info(f"Пользователь {user_id} подписан на канал")
            return True
        else:
            logger.info(f"Пользователь {user_id} НЕ подписан на канал. Статус: {chat_member.status}")
            return False

    except Exception as e:
        logger.error(f"Ошибка при проверке подписки для пользователя {user_id}: {e}")
        return False


async def create_download_menu_keyboard():
    """Создает меню выбора файла для скачивания"""
    keyboard = [
        [InlineKeyboardButton(f"📱 {FILE_1_NAME}", callback_data="download_apk_1")],
        [InlineKeyboardButton(f"📱 {FILE_2_NAME}", callback_data="download_apk_2")],
        [InlineKeyboardButton("🔄 Проверить снова", callback_data="check_again")],
        [InlineKeyboardButton("💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def create_download_keyboard(version: int):
    """Создает клавиатуру для скачивания конкретного файла"""
    if version == 1:
        apk_url = APK_URL
        file_name = FILE_1_NAME
    else:
        apk_url = APK_URL_2
        file_name = FILE_2_NAME

    keyboard = [
        [InlineKeyboardButton("📥 Скачать файл", url=apk_url)],
        [InlineKeyboardButton("📱 Выбрать другой файл", callback_data="download_menu")],
        [InlineKeyboardButton("💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def create_subscription_keyboard():
    """Создает клавиатуру для подписки"""
    keyboard = [
        [InlineKeyboardButton("📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("🔄 Проверить подписку", callback_data="check_again")],
        [InlineKeyboardButton("💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    if query.data in ["download_menu", "check_again"]:
        await query.edit_message_text(
            "⏳ Проверяем подписку...",
            reply_markup=None
        )

        is_subscribed = await check_subscription(user_id, context)

        if is_subscribed:
            reply_markup = await create_download_menu_keyboard()
            await query.edit_message_text(
                "✅ Спасибо за подписку!\n\n"
                "📱 <b>Выберите файл для скачивания:</b>\n\n"
                f"• <b>{FILE_1_NAME}</b>\n"
                f"• <b>{FILE_2_NAME}</b>\n\n"
                "💡 Если не знаете какой файл выбрать - обратитесь в поддержку",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            reply_markup = await create_subscription_keyboard()
            await query.edit_message_text(
                "❌ Вы не подписаны на наш канал!\n\n"
                "Чтобы скачать файлы:\n"
                "1. Нажмите кнопку 'Подписаться на канал'\n"
                "2. Подпишитесь на канал\n"
                "3. Вернитесь в бота и нажмите 'Проверить подписку'\n\n"
                f"📢 Канал: {CHANNEL_USERNAME}\n\n"
                "🛠 Если вы уже подписаны, но бот не видит подписку:\n"
                "• Убедитесь, что подписка активна\n"
                "• Попробуйте отписаться и подпишитесь снова\n"
                "• Обратитесь в поддержку",
                reply_markup=reply_markup
            )

    elif query.data == "download_apk_1":
        reply_markup = await create_download_keyboard(1)
        await query.edit_message_text(
            f"📦 <b>{FILE_1_NAME}</b>\n\n"
            f"🔗 <b>Ссылка:</b> {APK_URL}\n\n"
            "📱 <b>Как скачать:</b>\n"
            "1. Нажмите кнопку 'Скачать файл'\n"
            "2. Откроется Telegram с файлом\n"
            "3. Нажмите на файл и выберите 'Скачать'\n\n"
            "⚠️ Если ссылка не работает, обратитесь в поддержку",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    elif query.data == "download_apk_2":
        reply_markup = await create_download_keyboard(2)
        await query.edit_message_text(
            f"📦 <b>{FILE_2_NAME}</b>\n\n"
            f"🔗 <b>Ссылка:</b> {APK_URL_2}\n\n"
            "📱 <b>Как скачать:</b>\n"
            "1. Нажмите кнопку 'Скачать файл'\n"
            "2. Откроется Telegram с файлом\n"
            "3. Нажмите на файл и выберите 'Скачать'\n\n"
            "⚠️ Если ссылка не работает, обратитесь в поддержку",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /download для прямого доступа"""
    user_id = update.effective_user.id

    check_message = await update.message.reply_text("⏳ Проверяем подписку...")

    is_subscribed = await check_subscription(user_id, context)

    if is_subscribed:
        reply_markup = await create_download_menu_keyboard()
        await check_message.edit_text(
            "✅ <b>Доступ к скачиванию открыт!</b>\n\n"
            "📱 <b>Выберите файл для скачивания:</b>\n\n"
            f"• <b>{FILE_1_NAME}</b>\n"
            f"• <b>{FILE_2_NAME}</b>\n\n"
            "💡 Если не знаете какой файл выбрать - обратитесь в поддержку",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        reply_markup = await create_subscription_keyboard()
        await check_message.edit_text(
            "❌ Для скачивания необходимо быть подписанным на наш канал!\n\n"
            f"Подпишитесь на канал: {CHANNEL_USERNAME}\n"
            "После подписки используйте команду /download еще раз или нажмите кнопку ниже.",
            reply_markup=reply_markup
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = (
        "🤖 <b>Команды бота:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/download - Скачать файлы\n"
        "/support - Связь с поддержкой\n"
        "/check - Проверить подписку\n"
        "/help - Получить справку\n\n"

        f"📦 <b>Доступные файлы:</b>\n"
        f"• {FILE_1_NAME}\n"
        f"• {FILE_2_NAME}\n\n"

        f"📢 <b>Требования:</b>\nПодписка на канал {CHANNEL_USERNAME}\n\n"
        f"🛠 <b>Поддержка:</b>\n{SUPPORT_USERNAME}"
    )

    keyboard = [
        [InlineKeyboardButton("📱 Скачать файлы", callback_data="download_menu")],
        [InlineKeyboardButton("📢 Наш канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /support"""
    support_text = (
        f"🛠 <b>Служба поддержки</b>\n\n"
        f"По всем вопросам обращайтесь: {SUPPORT_USERNAME}\n\n"

        f"📦 <b>Доступные файлы:</b>\n"
        f"• {FILE_1_NAME}\n"
        f"• {FILE_2_NAME}\n\n"

        "<b>Частые проблемы и решения:</b>\n"
        "• Не скачивается файл - проверьте интернет соединение\n"
        "• Бот не видит подписку - отпишитесь и подпишитесь снова\n"
        "• Файл не устанавливается - разрешите установку из неизвестных источников\n"
        "• Не знаете какой файл выбрать - пишите в поддержку\n"
        "• Другие проблемы - опишите подробно в поддержку"
    )

    keyboard = [
        [InlineKeyboardButton("💬 Написать в поддержку", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")],
        [InlineKeyboardButton("📱 Выбрать файл", callback_data="download_menu")],
        [InlineKeyboardButton("📢 Наш канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        support_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки подписки /check"""
    user_id = update.effective_user.id

    check_message = await update.message.reply_text("⏳ Проверяем подписку...")

    is_subscribed = await check_subscription(user_id, context)

    if is_subscribed:
        keyboard = [
            [InlineKeyboardButton("📱 Выбрать файл", callback_data="download_menu")],
            [InlineKeyboardButton("💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await check_message.edit_text(
            "✅ Вы подписаны на канал! Можете скачать файлы\n\n"
            f"<b>Доступные файлы:</b>\n"
            f"• {FILE_1_NAME}\n"
            f"• {FILE_2_NAME}\n\n"
            "Нажмите 'Выбрать файл' для скачивания",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        reply_markup = await create_subscription_keyboard()
        await check_message.edit_text(
            f"❌ Вы не подписаны на канал {CHANNEL_USERNAME}",
            reply_markup=reply_markup
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    if update.message and update.message.text:
        await update.message.reply_text(
            "🤖 Используйте команды для работы с ботом:\n\n"
            "/start - начать работу\n"
            "/download - скачать файлы\n"
            "/help - помощь\n\n"
            "Или нажмите кнопку ниже:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 Скачать файлы", callback_data="download_menu")],
                [InlineKeyboardButton("💬 Помощь", callback_data="download_menu")]
            ])
        )


def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("download", download_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(download_menu|check_again|download_apk_1|download_apk_2)$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен...")
    print(f"📦 Файл 1: {FILE_1_NAME}")
    print(f"📦 Файл 2: {FILE_2_NAME}")
    print(f"📢 Канал: {CHANNEL_USERNAME}")
    print(f"🛠 Поддержка: {SUPPORT_USERNAME}")
    print(f"🔗 Ссылка на файл 1: {APK_URL}")
    print(f"🔗 Ссылка на файл 2: {APK_URL_2}")
    application.run_polling()


if __name__ == "__main__":
    main()
