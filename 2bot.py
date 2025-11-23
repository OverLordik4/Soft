import logging
from telegram import Update, ChatJoinRequest
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes, CommandHandler

# Настройки бота для автопринятия заявок
AUTO_APPROVE_BOT_TOKEN = "8005876576:AAE3MWQ3hlollD5Tl9a1DDibrS7e7UVhl48"  # Замените на токен второго бота
CHANNEL_CHAT_ID = "-1003204433403"  # ID канала, где принимать заявки

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Статистика для бота автопринятия
auto_approve_stats = {
    "total_approved": 0,
    "errors": 0,
    "last_approval": None
}


async def approve_join_request(update: ChatJoinRequest, context: ContextTypes.DEFAULT_TYPE):
    """Автоматически принимает заявки на вступление в канал"""
    user = update.from_user
    chat = update.chat
    
    try:
        # Одобряем заявку
        await update.approve()
        
        # Обновляем статистику
        auto_approve_stats["total_approved"] += 1
        auto_approve_stats["last_approval"] = update.date.strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"✅ Заявка одобрена: {user.first_name} (ID: {user.id}) в канал: {chat.title}")
        
        # Отправляем приветственное сообщение (опционально)
        try:
            welcome_text = f"""
👋 Добро пожаловать в {chat.title}, {user.first_name}!

✅ Ваша заявка была автоматически одобрена.

📢 Теперь вы можете получить доступ к эксклюзивному контенту!
            """
            await context.bot.send_message(
                chat_id=user.id,
                text=welcome_text
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить приветственное сообщение пользователю {user.id}: {e}")
            
    except Exception as e:
        auto_approve_stats["errors"] += 1
        logger.error(f"❌ Ошибка при одобрении заявки пользователя {user.id}: {e}")


async def auto_approve_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для просмотра статистики бота автопринятия"""
    stats_text = f"""
📊 <b>Статистика бота автопринятия</b>

✅ <b>Всего одобрено заявок:</b> {auto_approve_stats['total_approved']}
❌ <b>Ошибок:</b> {auto_approve_stats['errors']}
🕒 <b>Последняя заявка:</b> {auto_approve_stats['last_approval'] or 'Еще нет'}

📢 <b>Канал:</b> {CHANNEL_CHAT_ID}
🤖 <b>Статус:</b> Активен
    """
    await update.message.reply_text(stats_text, parse_mode='HTML')


async def start_auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда старт для бота автопринятия"""
    await update.message.reply_text(
        "🤖 <b>Бот для автоматического принятия заявок</b>\n\n"
        "✅ <b>Функции:</b>\n"
        "• Автоматическое одобрение заявок в канал\n"
        "• Приветственные сообщения\n"
        "• Статистика работы\n\n"
        f"📢 <b>Канал:</b> {CHANNEL_CHAT_ID}\n"
        "⚡ <b>Статус:</b> Активен\n\n"
        "📊 Используйте /stats для просмотра статистики",
        parse_mode='HTML'
    )


def setup_auto_approve_bot():
    """Настройка и запуск бота для автопринятия заявок"""
    application = Application.builder().token(AUTO_APPROVE_BOT_TOKEN).build()
    
    # Добавляем обработчик заявок на вступление
    application.add_handler(ChatJoinRequestHandler(approve_join_request))
    
    # Добавляем команды для управления
    application.add_handler(CommandHandler("start", start_auto_approve))
    application.add_handler(CommandHandler("stats", auto_approve_stats_command))
    
    return application


def main_auto_approve():
    """Запуск бота автопринятия"""
    application = setup_auto_approve_bot()
    
    print("🤖 Бот автопринятия заявок запущен!")
    print("📢 Режим: Автоматическое принятие заявок")
    print(f"🎯 Канал: {CHANNEL_CHAT_ID}")
    print("✅ Бот готов принимать заявки...")
    
    application.run_polling()


if __name__ == "__main__":
    main_auto_approve()
