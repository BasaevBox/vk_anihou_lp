"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         UPLP MODULE v1.0                                                  ║
║                    Модуль для автоматического продвижения бота                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import threading
import time
import random
import json
import os
from datetime import datetime
from typing import TYPE_CHECKING, List, Dict, Optional
from utils import log

if TYPE_CHECKING:
    from bot import VKBot


class UplpModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
        self.enabled = False
        self.thread = None
        self.group_id = -226360803  
        self.post_time = "12:00"  
        self.last_post_date = None  
        self.posted_indices = []  
        self.posts_file = "uplp_posts.json"  
        self.promote_link = "vk.com/anihou"
        self.price = "100р навсегда"
        self.support_period = "месяц"
        
        self.post_templates = self._init_post_templates()
        
        self.load_state()
    
    def _init_post_templates(self) -> List[Dict[str, str]]:
        templates = []
        
        buy_texts = [
            "💎 КУПИТЬ БОТА: {link}\n💰 Цена: {price}\n✅ Доступ навсегда\n🎁 Поддержка {support}",
            "🛒 Приобрести бота: {link}\n💵 Стоимость: {price}\n📞 Поддержка {support}",
            "🔥 Бот в наличии! {link}\n💸 {price} — полный доступ\n🤝 Гарантия {support}",
            "🎯 Хочешь такого же бота? {link}\n💎 Всего {price} навсегда!\n📱 Поддержка {support}",
            "✨ Эксклюзивное предложение! {link}\n💰 {price} — и бот твой!\n🛡 Поддержка {support}",
            "🚀 Мощный VK бот за {price}! {link}\n🎁 В подарок: поддержка {support}",
            "💫 Твой личный ассистент в VK! {link}\n💸 {price} — и ты владелец!\n📞 Поддержка {support}",
            "⭐ Полный доступ к боту: {price}\n🔗 {link}\n🤝 Поддержка {support}",
            "🎉 Спеццена: {price} навсегда! {link}\n✅ Поддержка {support} в подарок",
            "💎 Премиум бот за {price}! {link}\n🎁 Поддержка {support}",
        ]
        
        features_texts = [
            "🎨 Возможности бота:\n• Аниме арты (SFW/NSFW)\n• RP команды (20+ действий)\n• Кастомные команды\n• QR-коды\n• YouTube скачивание\n• Автостатус с анимацией\n• И многое другое!\n\n💎 Купить: {link}",
            "🤖 ЧТО УМЕЕТ БОТ:\n✓ Аниме арты из VK групп\n✓ RP команды (обнять, поцеловать и др.)\n✓ Создание своих команд\n✓ Генерация QR-кодов\n✓ Скачивание видео с YouTube\n✓ Анимированный статус\n✓ Черный список\n✓ Система доверенных\n\n💰 {price} — {link}",
            "📋 ФУНКЦИОНАЛ:\n1. Аниме арты (свой NSFW режим)\n2. 20+ RP команд\n3. Кастомные команды\n4. YouTube загрузчик\n5. QR генератор\n6. Анимации статуса\n7. Автопостинг\n8. Погода, шутки, цитаты\n\n💵 {price} — {link}",
            "⚡ МОДУЛИ БОТА:\n• Anime — арты из групп\n• RP — ролевые игры\n• Custom Commands — свои команды\n• YouTube — скачивание видео\n• QR — генератор кодов\n• Animation — статус анимация\n• Auto Poster — автопубликации\n\n💰 {price} навсегда! {link}",
            "🔥 ТОП ФИШЕК:\n🔹 Аниме арты (SFW/NSFW)\n🔹 20+ RP команд\n🔹 Свои команды за 2 секунды\n🔹 Скачивание YouTube видео\n🔹 Генерация QR-кодов\n🔹 Анимированный статус\n\n💎 Цена: {price}\n🔗 {link}",
            "✨ ПОЛНЫЙ СПИСОК:\n🎭 RP: обнять, поцеловать, пнуть, убить, погладить, кусь, шлепнуть и др.\n🎨 Аниме: случайные арты из групп\n🛠 Инструменты: QR, YouTube, автостатус\n📝 Кастомные команды\n\n💰 {price} — {link}",
            "🤖 Бот умеет ВСЁ:\n✅ Аниме контент\n✅ RP взаимодействия\n✅ Свои команды\n✅ Работу с видео\n✅ Генерацию QR\n✅ Автоматизацию\n\n💸 Всего {price}!\n🔗 {link}",
        ]
        
        updates_texts = [
            "🔄 НОВОЕ ОБНОВЛЕНИЕ v5.0!\n• Добавлен модуль автопостинга\n• Улучшена система доверенных\n• Новые RP команды\n• Исправлены баги\n\n💎 Купить: {link}",
            "✨ АПДЕЙТ БОТА:\n• YouTube модуль теперь стабильнее\n• Добавлены новые анимации статуса\n• Оптимизирована работа с артами\n\n💰 {price} — {link}",
            "🚀 СВЕЖЕЕ ОБНОВЛЕНИЕ:\n• Автопостинг в группу\n• Улучшенный QR генератор\n• Новые тексты для продвижения\n• Исправления ошибок\n\n💵 {price} навсегда! {link}",
            "📢 ВЫШЛО ОБНОВЛЕНИЕ 5.1:\n• Добавлен модуль UPLP (автопродвижение)\n• Ускорена загрузка YouTube видео\n• Новые RP команды: прижать, поиграть\n\n🔗 {link} | {price}",
            "⚙️ ТЕХНИЧЕСКОЕ ОБНОВЛЕНИЕ:\n• Улучшена стабильность LongPoll\n• Оптимизирована память\n• Добавлены новые анимации\n\n💰 {price} — {link}",
        ]
        
        # ========== Рекламные тексты ==========
        promo_texts = [
            "🌟 Хочешь своего бота в VK?\n🎯 Полный функционал: аниме, RP, YouTube, QR и многое другое!\n💸 Всего {price} навсегда!\n🔗 {link}",
            "💎 ВК БОТ ПРЕМИУМ КЛАССА!\n🎨 Аниме арты\n🎭 RP команды\n📹 YouTube скачивание\n✨ Кастомные команды\n\n💰 {price} — {link}",
            "🔥 ТВОЙ ЛИЧНЫЙ БОТ В VK!\n✅ Работает 24/7\n✅ Легкая настройка\n✅ Полный исходный код\n✅ Поддержка {support}\n\n💸 {price} — {link}",
            "🎁 УНИКАЛЬНОЕ ПРЕДЛОЖЕНИЕ!\nПолучи мощного VK бота с:\n• Аниме артами\n• RP командой\n• YouTube загрузчиком\n• QR генератором\n\n💎 {price} навсегда!\n🔗 {link}",
            "✨ СТАНЬ ВЛАДЕЛЬЦЕМ БОТА!\nБез ежемесячной платы!\nОдин платеж — вечный доступ!\nПоддержка {support} в подарок!\n\n💰 {price} — {link}",
            "🤖 ВК БОТ ДЛЯ АНИМЕ ФАНАТОВ!\n• Арты из групп\n• RP команды\n• YouTube видео\n• Свои команды\n\n💸 {price} — {link}",
            "🎯 ИДЕАЛЬНЫЙ БОТ ДЛЯ БЕСЕДЫ!\nРазвлечения, автоматизация, инструменты!\nВсего за {price} навсегда!\n\n🔗 {link}",
            "💫 ЛУЧШЕЕ ВЛОЖЕНИЕ В ВАШУ БЕСЕДУ!\nМощный функционал, стабильная работа!\nПоддержка {support} в комплекте!\n\n💰 {price} — {link}",
        ]
        
        # ========== Тексты с эмодзи ==========
        emoji_texts = [
            "🤖 | VK ANIME LP BOT\n\n🎨 Аниме арты\n🎭 RP команды\n📹 YouTube скачивание\n🔗 QR коды\n⚡ Автостатус\n\n💸 {price}\n🔗 {link}",
            "💎 | PREMIUM VK BOT\n\n✨ Фишки:\n• Аниме (SFW/NSFW)\n• 20+ RP действий\n• YouTube загрузчик\n• Кастомные команды\n\n💰 {price} навсегда!\n🔗 {link}",
            "🚀 | VK БОТ 5.0\n\n⭐ Возможности:\n✓ Аниме арты\n✓ RP команды\n✓ Свои команды\n✓ YouTube\n✓ QR\n✓ Автостатус\n\n💵 {price}\n🔗 {link}",
            "🎯 | ГОТОВЫЙ БОТ В VK\n\n📦 Модули:\n• Anime API\n• RP System\n• YouTube Downloader\n• QR Generator\n• Custom Commands\n\n💰 {price} — {link}",
        ]
        
        # ========== Вопрос-ответ ==========
        qa_texts = [
            "❓ ЧАСТЫЕ ВОПРОСЫ:\n\n❔ Сколько стоит?\n✅ {price} навсегда!\n\n❔ Есть поддержка?\n✅ Да, {support}\n\n❔ Что умеет бот?\n✅ Аниме, RP, YouTube, QR и др.\n\n🔗 {link}",
            "📌 FAQ:\n\nQ: Цена?\nA: {price} — разово!\n\nQ: Поддержка?\nA: {support}\n\nQ: Как купить?\nA: {link}\n\nQ: Сложно настроить?\nA: Нет, все просто!",
            "❓ ВОПРОСЫ И ОТВЕТЫ:\n\n• Стоимость: {price}\n• Поддержка: {support}\n• Обновления: бесплатно\n• Токен: нужен свой\n\nКупить: {link}",
        ]
        
        # ========== Сравнение ==========
        compare_texts = [
            "🏆 ПОЧЕМУ ЭТОТ БОТ?\n\n✅ Без ежемесячной платы\n✅ Полный исходный код\n✅ Легкая настройка\n✅ Регулярные обновления\n✅ Поддержка {support}\n\n💰 {price} — {link}",
            "⭐ ПРЕИМУЩЕСТВА:\n\n• Вечная лицензия за {price}\n• Модульная архитектура\n• Работает на любом хостинге\n• Поддержка {support}\n\n🔗 {link}",
        ]
        
        # ========== Короткие тексты ==========
        short_texts = [
            "🔥 VK Бот за {price}! {link}\n🎨 Аниме | 🎭 RP | 📹 YouTube | 🔗 QR",
            "💎 {price} — и ты владелец бота! {link}\n✅ Поддержка {support}",
            "✨ Лучший VK бот для аниме тусовки! {link}\n💰 {price} навсегда!",
            "🤖 Хочешь такого же бота? {link}\n💸 Всего {price}!",
            "🎯 Бот для VK с аниме артами и RP! {link}\n💵 {price} навсегда!",
            "⚡ VK ANIME LP BOT — {link}\n💰 {price} | Поддержка {support}",
            "🔥 Аниме арты | RP команды | YouTube | QR\nВсе это за {price}! {link}",
        ]
        
        # ========== Тексты с отзывами ==========
        review_texts = [
            "📢 ОТЗЫВ ПОКУПАТЕЛЯ:\n\"Бот супер! Аниме арты качаются быстро, RP команды работают отлично. Поддержка помогла с настройкой за 5 минут!\"\n\n💰 {price} — {link}",
            "⭐ ОТЗЫВ:\n\"Пользуюсь месяц, все работает стабильно. Обновления выходят часто, автопостинг удобная штука. Спасибо!\"\n\n🔗 {link} | {price}",
            "💬 ЧТО ГОВОРЯТ КЛИЕНТЫ:\n\"YouTube скачивание работает отлично, даже с ютуб шортс. QR генератор пригодился. Рекомендую!\"\n\n💰 {price} — {link}",
        ]
        
        # ========== Тексты о поддержке ==========
        support_texts = [
            "🛡 ПОДДЕРЖКА {support}\n✅ Помощь с настройкой\n✅ Решение проблем\n✅ Обновления\n✅ Консультации\n\n💎 Купить: {link} | {price}",
            "📞 ТЕХПОДДЕРЖКА {support}\nОтвечаю на все вопросы!\nПомогаю с установкой и настройкой!\n\n💰 {price} — {link}",
        ]
        
        # ========== Инструкции ==========
        instruction_texts = [
            "📖 КАК ПОЛЬЗОВАТЬСЯ БОТОМ:\n\n1️⃣ Купить бота: {link}\n2️⃣ Получить токен VK\n3️⃣ Запустить bot.py\n4️⃣ Наслаждаться!\n\n💸 {price} навсегда!",
            "🚀 БЫСТРЫЙ СТАРТ:\n1. {link} — покупка\n2. Вставить токен в config.py\n3. Запустить: python bot.py\n\n💰 {price} | Поддержка {support}",
        ]
        
        # ========== Сезонные/акционные ==========
        seasonal_texts = [
            "🎉 АКЦИЯ! {price} навсегда!\n🔗 {link}\n🎁 Поддержка {support} в подарок!",
            "💥 СКИДКА! Только сегодня!\n💰 {price} — вечный доступ!\n🔗 {link}",
            "🎄 ПРЕДНОВОГОДНЕЕ ПРЕДЛОЖЕНИЕ!\nБот за {price} навсегда!\n🔗 {link}",
        ]
        
        # Собираем все тексты в один список с подстановкой переменных
        all_texts = (
            buy_texts + features_texts + updates_texts + promo_texts +
            emoji_texts + qa_texts + compare_texts + short_texts +
            review_texts + support_texts + instruction_texts + seasonal_texts
        )
        
        # Добавляем переменные в каждый текст
        for text in all_texts:
            templates.append({
                "text": text,
                "type": self._detect_text_type(text)
            })
        
        # Добавляем еще несколько уникальных текстов для достижения 100+
        extra_texts = [
            "🎯 ВК БОТ ДЛЯ БЕСЕДЫ:\n\n✔ Аниме арты из пабликов\n✔ RP команды (20+)\n✔ Свои команды\n✔ YouTube видео\n✔ QR коды\n✔ Автостатус\n\n💰 {price} навсегда!\n🔗 {link}",
            "💎 ФУНКЦИОНАЛ PREMIUM БОТА:\n\n📸 Аниме арты (SFW/NSFW)\n🎭 RP команды\n🎬 Скачивание YouTube\n🔳 QR генератор\n⚡ Анимированный статус\n📝 Кастомные команды\n🤖 Автопостинг\n\n💸 {price} — {link}",
            "🔥 ГОРЯЧЕЕ ПРЕДЛОЖЕНИЕ!\n\nVK бот с уникальным функционалом:\n• Аниме арты из VK групп\n• RP команды (обнять, поцеловать и др.)\n• Скачивание YouTube видео\n• Генерация QR-кодов\n• Анимации статуса\n\n💰 Всего {price}!\n🔗 {link}",
            "✨ ИДЕАЛЬНЫЙ БОТ ДЛЯ ВАШЕЙ БЕСЕДЫ!\n\nРазвлекательный модуль с аниме артами\nRP взаимодействия для общения\nYouTube загрузчик для видео\nQR генератор для ссылок\nКастомные команды под себя\n\n💎 {price} — {link}",
            "🤖 VK ANIME LP BOT v5.0\n\nМощный LongPoll бот для VK:\n• Аниме арты из групп\n• RP команды\n• YouTube скачивание\n• QR коды\n• Анимированный статус\n• Автопостинг\n• Система доверенных\n\n💰 {price}\n🔗 {link}",
            "📢 АВТОМАТИЧЕСКОЕ ПРОДВИЖЕНИЕ!\n\nБот сам публикует информацию о себе!\n100+ уникальных текстов\nПубликации каждый день\nНикаких лишних действий\n\n💎 Купить бота: {link}\n💰 {price}",
        ]
        
        for text in extra_texts:
            templates.append({
                "text": text,
                "type": self._detect_text_type(text)
            })
        
        return templates
    
    def _detect_text_type(self, text: str) -> str:
        """Определяет тип текста для логирования"""
        if "КУПИТЬ" in text or "купить" in text or "цена" in text or "Цена" in text:
            return "buy"
        elif "обновлени" in text or "АПДЕЙТ" in text or "v5" in text:
            return "update"
        elif "возможност" in text or "умеет" in text or "функци" in text:
            return "features"
        elif "отзыв" in text:
            return "review"
        elif "вопрос" in text or "FAQ" in text:
            return "faq"
        else:
            return "promo"
    
    def register_commands(self):
        """Регистрация команд модуля"""
        self.bot.commands.update({
            "продвигать": self.cmd_promote,
            "promote": self.cmd_promote,
        })
    
    def cmd_promote(self, event, args):
        """Команда управления автопродвижением"""
        if not args:
            status = "✅ Включено" if self.enabled else "❌ Выключено"
            info = f"""📢 𝗔𝗩𝗧𝗢𝗣𝗥𝗢𝗗𝗩𝗜𝗭𝗛𝗘𝗡𝗜𝗘

🔘 Статус: {status}
👥 Группа: {self.group_id if self.group_id else 'Не указана'}
⏰ Время публикации: {self.post_time}
📊 Всего текстов: {len(self.post_templates)}
📝 Опубликовано: {len(self.posted_indices)}
🎯 Ссылка: {self.promote_link}
💰 Цена: {self.price}
🛡 Поддержка: {self.support_period}

⚙️ Команды:
!продвигать вкл [id_группы] [время] - Включить
!продвигать выкл - Выключить
!продвигать время [ЧЧ:ММ] - Изменить время
!продвигать сброс - Сбросить историю постов
!продвигать тест - Тестовая публикация"""
            
            self.bot.send_message(event.peer_id, info,
                reply_to=event.message_id if not event.from_me else None)
            return
        
        action = args[0].lower()
        
        if action in ["вкл", "on", "1"]:
            if len(args) < 2:
                self.bot.send_message(event.peer_id,
                    "❌ Укажите ID группы!\nПример: !продвигать вкл -123456789 14:30",
                    reply_to=event.message_id if not event.from_me else None)
                return
            
            try:
                group_id = int(args[1])
                if group_id > 0:
                    group_id = -group_id
                self.group_id = group_id
                
                if len(args) >= 3:
                    time_str = args[2]
                    if self._validate_time(time_str):
                        self.post_time = time_str
                    else:
                        self.bot.send_message(event.peer_id,
                            "⚠️ Неверный формат времени. Используйте ЧЧ:ММ (например 14:30)",
                            reply_to=event.message_id if not event.from_me else None)
                
                if not self.enabled:
                    self.enabled = True
                    self.thread = threading.Thread(target=self.promote_loop, daemon=True)
                    self.thread.start()
                    self.save_state()
                    
                    self.bot.send_message(event.peer_id,
                        f"""✅ 𝗔𝗩𝗧𝗢𝗣𝗥𝗢𝗗𝗩𝗜𝗭𝗛𝗘𝗡𝗜𝗘 𝗩𝗞𝗟𝗬𝗖𝗛𝗘𝗡𝗢!

📢 Группа: {self.group_id}
⏰ Время публикации: {self.post_time}
📊 Всего текстов: {len(self.post_templates)}

💡 Бот будет публиковать новый пост каждый день в указанное время.
📝 Каждый пост уникален и не повторяется.""",
                        reply_to=event.message_id if not event.from_me else None)
                    log(f"Автопродвижение включено (группа: {self.group_id}, время: {self.post_time})", "SUCCESS")
                else:
                    self.bot.send_message(event.peer_id,
                        f"✅ Настройки обновлены!\nГруппа: {self.group_id}\nВремя: {self.post_time}",
                        reply_to=event.message_id if not event.from_me else None)
                    
            except ValueError:
                self.bot.send_message(event.peer_id,
                    "❌ ID группы должен быть числом!",
                    reply_to=event.message_id if not event.from_me else None)
        
        elif action in ["выкл", "off", "0"]:
            self.enabled = False
            self.save_state()
            self.bot.send_message(event.peer_id,
                "❌ 𝗔𝗩𝗧𝗢𝗣𝗥𝗢𝗗𝗩𝗜𝗭𝗛𝗘𝗡𝗜𝗘 𝗩𝗬𝗞𝗟𝗬𝗖𝗛𝗘𝗡𝗢!",
                reply_to=event.message_id if not event.from_me else None)
            log("Автопродвижение выключено", "WARNING")
        
        elif action in ["время", "time"]:
            if len(args) < 2:
                self.bot.send_message(event.peer_id,
                    f"⏰ Текущее время: {self.post_time}\nИспользуйте: !продвигать время 14:30",
                    reply_to=event.message_id if not event.from_me else None)
                return
            
            time_str = args[1]
            if self._validate_time(time_str):
                self.post_time = time_str
                self.save_state()
                self.bot.send_message(event.peer_id,
                    f"✅ Время публикации изменено на {self.post_time}",
                    reply_to=event.message_id if not event.from_me else None)
            else:
                self.bot.send_message(event.peer_id,
                    "❌ Неверный формат! Используйте ЧЧ:ММ (например 14:30)",
                    reply_to=event.message_id if not event.from_me else None)
        
        elif action in ["сброс", "reset"]:
            self.posted_indices = []
            self.save_state()
            self.bot.send_message(event.peer_id,
                f"✅ История постов сброшена! Теперь можно публиковать все {len(self.post_templates)} текстов заново.",
                reply_to=event.message_id if not event.from_me else None)
        
        elif action in ["тест", "test"]:
            if not self.group_id:
                self.bot.send_message(event.peer_id,
                    "❌ Сначала укажите группу: !продвигать вкл [id_группы]",
                    reply_to=event.message_id if not event.from_me else None)
                return
            
            post = self._get_next_post()
            if post:
                success, error = self._send_post(post)
                if success:
                    self.bot.send_message(event.peer_id,
                        "✅ Тестовый пост опубликован!",
                        reply_to=event.message_id if not event.from_me else None)
                else:
                    self.bot.send_message(event.peer_id,
                        f"❌ Ошибка: {error}",
                        reply_to=event.message_id if not event.from_me else None)
            else:
                self.bot.send_message(event.peer_id,
                    "⚠️ Нет доступных текстов для публикации. Используйте !продвигать сброс",
                    reply_to=event.message_id if not event.from_me else None)
    
    def _validate_time(self, time_str: str) -> bool:
        """Проверяет корректность формата времени"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except:
            return False
    
    def _get_next_post(self) -> Optional[Dict[str, str]]:
        """Получает следующий пост для публикации (еще не использованный)"""
        available_indices = [i for i in range(len(self.post_templates)) if i not in self.posted_indices]
        
        if not available_indices:
            # Если все тексты использованы, сбрасываем историю
            self.posted_indices = []
            available_indices = list(range(len(self.post_templates)))
            log("Все тексты использованы, история сброшена", "INFO")
        
        # Выбираем случайный индекс из доступных
        idx = random.choice(available_indices)
        self.posted_indices.append(idx)
        self.save_state()
        
        post_data = self.post_templates[idx].copy()
        # Подставляем переменные
        post_data["text"] = post_data["text"].format(
            link=self.promote_link,
            price=self.price,
            support=self.support_period
        )
        return post_data
    
    def _send_post(self, post_data: Dict[str, str]) -> tuple:
        """Отправляет пост в группу"""
        try:
            result = self.bot.vk.wall.post(
                owner_id=self.group_id,
                message=post_data["text"],
                from_group=1  # От имени группы
            )
            log(f"Пост опубликован в группу {self.group_id} (тип: {post_data['type']})", "SUCCESS")
            return True, None
        except Exception as e:
            error_msg = str(e)
            if "access_denied" in error_msg:
                error_msg = "Нет доступа к группе. Проверьте права токена!"
            elif "owner_id" in error_msg:
                error_msg = "Неверный ID группы"
            log(f"Ошибка публикации: {e}", "ERROR")
            return False, error_msg
    
    def promote_loop(self):
        """Основной цикл автопродвижения"""
        log(f"Цикл автопродвижения запущен (группа: {self.group_id}, время: {self.post_time})", "INFO")
        
        while self.enabled:
            try:
                now = datetime.now()
                target_hour, target_minute = map(int, self.post_time.split(':'))
                
                # Проверяем, нужно ли публиковать сегодня
                today_str = now.strftime("%Y%m%d")
                should_post = (
                    now.hour == target_hour and
                    now.minute == target_minute and
                    self.last_post_date != today_str
                )
                
                if should_post:
                    post_data = self._get_next_post()
                    if post_data:
                        success, error = self._send_post(post_data)
                        if success:
                            self.last_post_date = today_str
                            self.save_state()
                            log(f"Автопродвижение: опубликован пост (тип: {post_data['type']})", "SUCCESS")
                        else:
                            log(f"Ошибка автопродвижения: {error}", "ERROR")
                            self.bot.send_to_favorite(f"⚠️ Ошибка автопродвижения: {error}")
                
                # Спим минуту, чтобы не нагружать процессор
                time.sleep(60)
                
            except Exception as e:
                log(f"Ошибка в цикле автопродвижения: {e}", "ERROR")
                time.sleep(300)  # При ошибке ждем 5 минут
    
    def save_state(self):
        """Сохраняет состояние модуля"""
        try:
            state = {
                "enabled": self.enabled,
                "group_id": self.group_id,
                "post_time": self.post_time,
                "last_post_date": self.last_post_date,
                "posted_indices": self.posted_indices
            }
            with open(self.posts_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log(f"Ошибка сохранения состояния UPLP: {e}", "ERROR")
    
    def load_state(self):
        """Загружает сохраненное состояние"""
        try:
            if os.path.exists(self.posts_file):
                with open(self.posts_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.enabled = state.get("enabled", False)
                    self.group_id = state.get("group_id")
                    self.post_time = state.get("post_time", "12:00")
                    self.last_post_date = state.get("last_post_date")
                    self.posted_indices = state.get("posted_indices", [])
                log(f"Загружено состояние UPLP: опубликовано {len(self.posted_indices)} постов", "SUCCESS")
        except Exception as e:
            log(f"Ошибка загрузки состояния UPLP: {e}", "ERROR")
            self.posted_indices = []
    
    def stop(self):
        """Остановка модуля"""
        self.enabled = False
        self.save_state()
        log("UPLP модуль остановлен", "WARNING")