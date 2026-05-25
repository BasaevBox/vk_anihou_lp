"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      AUTO POSTER MODULE                                                    ║
║                    Модуль для автоматической публикации в группу                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import threading
import time
from typing import TYPE_CHECKING, Optional
from utils import log

if TYPE_CHECKING:
    from bot import VKBot


class AutoPosterModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
        self.auto_post_enabled = False
        self.auto_post_thread = None
        self.interval = 120  # интервал в секундах (можно изменить)
        self.group_id = -64758790  # ЗДЕСЬ УКАЖИТЕ ID ГРУППЫ (с минусом)
        self.message = "❤️ Подпишусь на вас без отписки \n🌹 С вас отзыв в группе\n⭐ В ЛС\nгруппа: vk.com/anihou_des"  # сообщение для публикации
        self.attachments = ""  # вложения (опционально)
        
    def register_commands(self):
        self.bot.commands.update({
            "автопост": self.cmd_auto_post,
            "autopost": self.cmd_auto_post,
            "пост": self.cmd_post_now,
            "post": self.cmd_post_now,
            "постнастройки": self.cmd_post_settings,
            "postsettings": self.cmd_post_settings,
        })
    
    def cmd_auto_post(self, event, args):
        """Управление автопостингом"""
        if not args:
            status = "✅ Включен" if self.auto_post_enabled else "❌ Выключен"
            self.bot.send_message(event.peer_id, 
                f"📢 𝗔𝗩𝗧𝗢𝗣𝗢𝗦𝗧𝗜𝗡𝗚:\n"
                f"🔘 Статус: {status}\n"
                f"⏱ Интервал: {self.interval} сек.\n"
                f"👥 Группа: {self.group_id}\n"
                f"📝 Сообщение: {self.message[:50]}...\n\n"
                f"Команды:\n"
                f"!автопост вкл - Включить\n"
                f"!автопост выкл - Выключить\n"
                f"!пост - Отправить сообщение сейчас\n"
                f"!постнастройки [интервал/группа/сообщение] - Настроить", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        action = args[0].lower()
        
        if action in ["вкл", "on", "1"]:
            if not self.auto_post_enabled:
                self.auto_post_enabled = True
                self.auto_post_thread = threading.Thread(target=self.auto_post_loop, daemon=True)
                self.auto_post_thread.start()
                self.bot.send_message(event.peer_id, 
                    f"✅ Автопостинг включен!\n"
                    f"📢 Сообщения будут публиковаться в группу {self.group_id}\n"
                    f"⏱ Интервал: {self.interval} сек.", 
                    reply_to=event.message_id if not event.from_me else None)
                log(f"Автопостинг включен (интервал: {self.interval}с, группа: {self.group_id})", "SUCCESS")
            else:
                self.bot.send_message(event.peer_id, "⚡ Автопостинг уже работает", 
                    reply_to=event.message_id if not event.from_me else None)
                
        elif action in ["выкл", "off", "0"]:
            self.auto_post_enabled = False
            self.bot.send_message(event.peer_id, "❌ Автопостинг выключен", 
                reply_to=event.message_id if not event.from_me else None)
            log("Автопостинг выключен", "WARNING")
    
    def cmd_post_now(self, event, args):
        """Отправить сообщение прямо сейчас"""
        if not self.group_id:
            self.bot.send_message(event.peer_id, 
                "❌ ID группы не указан! Используйте !постнастройки группа [id]", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        # Если есть аргументы, используем их как текст сообщения
        if args:
            custom_message = " ".join(args)
        else:
            custom_message = self.message
        
        success, error = self.send_post(custom_message)
        
        if success:
            self.bot.send_message(event.peer_id, 
                f"✅ Сообщение опубликовано в группу {self.group_id}!", 
                reply_to=event.message_id if not event.from_me else None)
        else:
            self.bot.send_message(event.peer_id, 
                f"❌ Ошибка публикации: {error}", 
                reply_to=event.message_id if not event.from_me else None)
    
    def cmd_post_settings(self, event, args):
        """Настройка автопостинга"""
        if not args:
            self.bot.send_message(event.peer_id, 
                f"📋 𝗧𝗘𝗞𝗨𝗦𝗛𝗜𝗘 𝗡𝗔𝗦𝗧𝗥𝗢𝗬𝗞𝗜:\n"
                f"⏱ Интервал: {self.interval} сек.\n"
                f"👥 Группа: {self.group_id}\n"
                f"📝 Сообщение: {self.message[:100]}{'...' if len(self.message) > 100 else ''}\n\n"
                f"Команды:\n"
                f"!постнастройки интервал [сек] - Изменить интервал\n"
                f"!постнастройки группа [id] - Изменить группу\n"
                f"!постнастройки сообщение [текст] - Изменить сообщение", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        setting = args[0].lower()
        
        if len(args) < 2:
            self.bot.send_message(event.peer_id, 
                f"❌ Укажите значение для настройки '{setting}'", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        value = args[1]
        
        if setting in ["интервал", "interval"]:
            try:
                new_interval = int(value)
                if new_interval < 5:
                    self.bot.send_message(event.peer_id, 
                        "⚠️ Интервал не может быть меньше 5 секунд! Установлено 5 сек.", 
                        reply_to=event.message_id if not event.from_me else None)
                    new_interval = 5
                self.interval = new_interval
                self.bot.send_message(event.peer_id, 
                    f"✅ Интервал изменен на {self.interval} сек.", 
                    reply_to=event.message_id if not event.from_me else None)
                log(f"Интервал автопостинга изменен на {self.interval} сек.", "SUCCESS")
            except ValueError:
                self.bot.send_message(event.peer_id, 
                    "❌ Интервал должен быть числом!", 
                    reply_to=event.message_id if not event.from_me else None)
                    
        elif setting in ["группа", "group"]:
            try:
                group_id = int(value)
                if group_id > 0:
                    group_id = -group_id
                self.group_id = group_id
                self.bot.send_message(event.peer_id, 
                    f"✅ Группа изменена на {self.group_id}", 
                    reply_to=event.message_id if not event.from_me else None)
                log(f"Группа для автопостинга изменена на {self.group_id}", "SUCCESS")
            except ValueError:
                self.bot.send_message(event.peer_id, 
                    "❌ ID группы должен быть числом! (например: 123456789)", 
                    reply_to=event.message_id if not event.from_me else None)
                    
        elif setting in ["сообщение", "message", "текст", "text"]:
            new_message = " ".join(args[1:])
            if len(new_message) > 500:
                self.bot.send_message(event.peer_id, 
                    "⚠️ Сообщение слишком длинное! Обрезано до 500 символов.", 
                    reply_to=event.message_id if not event.from_me else None)
                new_message = new_message[:500]
            self.message = new_message
            self.bot.send_message(event.peer_id, 
                f"✅ Сообщение изменено на:\n{self.message[:100]}{'...' if len(self.message) > 100 else ''}", 
                reply_to=event.message_id if not event.from_me else None)
            log(f"Сообщение автопостинга изменено", "SUCCESS")
        else:
            self.bot.send_message(event.peer_id, 
                f"❌ Неизвестная настройка: {setting}\nДоступно: интервал, группа, сообщение", 
                reply_to=event.message_id if not event.from_me else None)
    
    def send_post(self, message: str) -> tuple:
        """Отправляет пост в группу"""
        try:
            params = {
                "owner_id": self.group_id,
                "message": message,
            }
            if self.attachments:
                params["attachments"] = self.attachments
            
            result = self.bot.vk.wall.post(**params)
            log(f"Пост опубликован в группу {self.group_id}: {message[:50]}...", "SUCCESS")
            return True, None
        except Exception as e:
            error_msg = str(e)
            if "access_denied" in error_msg:
                error_msg = "Нет доступа к группе. Проверьте права токена!"
            elif "owner_id" in error_msg:
                error_msg = "Неверный ID группы"
            log(f"Ошибка публикации поста: {e}", "ERROR")
            return False, error_msg
    
    def auto_post_loop(self):
        """Цикл автопостинга"""
        while self.auto_post_enabled:
            try:
                success, error = self.send_post(self.message)
                
                if not success:
                    log(f"Ошибка автопостинга: {error}", "ERROR")
                    self.bot.send_to_favorite(f"⚠️ Ошибка автопостинга: {error}")
                
                time.sleep(self.interval)
                
            except Exception as e:
                log(f"Ошибка в цикле автопостинга: {e}", "ERROR")
                time.sleep(10)
    
    def stop(self):
        """Остановка автопостинга"""
        self.auto_post_enabled = False
        log("Автопостинг остановлен", "WARNING")