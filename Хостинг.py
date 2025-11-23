import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ─────────────────────────────────────
# НАСТРОЙКИ БОТА
# ─────────────────────────────────────
BOT_TOKEN = "8356262671:AAFMkS5M9MAnYAPaIHvTa9gnh9ZDVjwOo0M"
APK_URL = "https://t.me/mammamaa12"
FILE_NAME = "Mansory Holidolla V1.9"

SUPPORT = "@Manu_Maso"

CHANNELS = [
    ("@MansoryHolidolla", "-1003204433403"),
    ("@HataMasona", "-1002510814806"),
    ("@HolidollaModz", "-1002371853221"),
]

# ─────────────────────────────────────
# ЛОГИ
# ─────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────
# ГЛАВНАЯ КНОПКА
# ─────────────────────────────────────
def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["⬇️ Скачать мод", "📢 Каналы"],
            ["💬 Поддержка", "ℹ️ Помощь"]
        ],
        resize_keyboard=True
    )


# ─────────────────────────────────────
# ПРОВЕРКА ПОДПИСОК
# ─────────────────────────────────────
async def check_subs(user_id, context):
    result = {}
    for username, chat_id in CHANNELS:
        try:
            sub = await context.bot.get_chat_member(chat_id, user_id)
            result[username] = sub.status in ["member", "administrator", "creator"]
        except:
            result[username] = False
    return result


# ─────────────────────────────────────
# START
# ─────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name}!\n\n"
        f"Добро пожаловать в Mansory Holidolla!",
        reply_markup=main_keyboard()
    )


# ─────────────────────────────────────
# ОБРАБОТКА НАЖАТИЙ НА КНОПКИ
# ─────────────────────────────────────
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    user_id = update.callback_query.from_user.id
    await update.callback_query.answer()

    # Повторная проверка
    if data == "check":
        subs = await check_subs(user_id, context)
        good = all(subs.values())

        if good:
            await update.callback_query.edit_message_text(
                "🎉 Вы подписаны!\nМожете скачать:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬇️ Скачать APK", url=APK_URL)]
                ])
            )
        else:
            buttons = [
                [InlineKeyboardButton(name, url=f"https://t.me/{name[1:]}")]
                for name, _ in CHANNELS
            ]
            buttons.append([InlineKeyboardButton("✔ Проверить снова", callback_data="check")])

            await update.callback_query.edit_message_text(
                "❌ Вы не подписаны на все каналы!\n\nПодпишитесь и нажмите проверить.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )


# ─────────────────────────────────────
# ТЕКСТОВЫЕ КОМАНДЫ (КНОПКИ)
# ─────────────────────────────────────
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user.id

    # Скачать
    if text == "⬇️ Скачать мод":
        subs = await check_subs(user, context)
        good = all(subs.values())

        if good:
            await update.message.reply_text(
                "🎉 Вы можете скачать мод:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬇️ Скачать APK", url=APK_URL)]
                ])
            )
        else:
            buttons = [
                [InlineKeyboardButton(name, url=f"https://t.me/{name[1:]}")]
                for name, _ in CHANNELS
            ]
            buttons.append([InlineKeyboardButton("✔ Проверить снова", callback_data="check")])

            await update.message.reply_text(
                "❌ Чтобы получить файл — подпишитесь на каналы:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    # Каналы
    elif text == "📢 Каналы":
        buttons = [
            [InlineKeyboardButton(name, url=f"https://t.me/{name[1:]}")]
            for name, _ in CHANNELS
        ]
        await update.message.reply_text(
            "📢 Наши каналы:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # Поддержка
    elif text == "💬 Поддержка":
        await update.message.reply_text(
            f"💬 Связаться с поддержкой:\n{SUPPORT}"
        )

    # Помощь
    elif text == "ℹ️ Помощь":
        await update.message.reply_text(
            "ℹ️ Справка:\n\n"
            "• ⬇ Скачать — получение APK\n"
            "• Подписка на 3 канала обязательна\n"
            f"• Поддержка: {SUPPORT}",
        )

    # Всё остальное
    else:
        await update.message.reply_text(
            "Выберите действие из меню 👇",
            reply_markup=main_keyboard()
        )


# ─────────────────────────────────────
# MAIN
# ─────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
