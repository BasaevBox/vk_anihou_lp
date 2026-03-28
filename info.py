"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         INFO MODULE                                          ║
║                    Модуль для информационных команд                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import time
import random
from datetime import datetime
from typing import TYPE_CHECKING
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

class InfoModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
    
    def register_commands(self):
        self.bot.commands.update({
            "помощь": self.cmd_help,
            "help": self.cmd_help,
            "инфо": self.cmd_info,
            "info": self.cmd_info,
            "пинг": self.cmd_ping,
            "ping": self.cmd_ping,
            "время": self.cmd_time,
            "time": self.cmd_time,
            "погода": self.cmd_weather,
            "weather": self.cmd_weather,
            "шутка": self.cmd_joke,
            "joke": self.cmd_joke,
            "цитата": self.cmd_quote,
            "quote": self.cmd_quote,
            "рандом": self.cmd_random,
            "random": self.cmd_random,
            "кто": self.cmd_who,
            "who": self.cmd_who,
            "выбери": self.cmd_choose,
            "choose": self.cmd_choose,
            "логи": self.cmd_logs,
            "logs": self.cmd_logs,
            "стоп": self.cmd_stop,
            "stop": self.cmd_stop,
        })
    
    def cmd_help(self, event, args):
        help_text = """🤖 𝗩𝗞 𝗔𝗡𝗜𝗠𝗘 𝗟𝗣 𝗕𝗢𝗧 - Список команд:
📊 𝗢𝗦𝗡𝗢𝗩𝗡𝗬𝗘:
!помощь - Показать это сообщение
!инфо - Информация о боте
!пинг - Проверка работоспособности
!время - Текущее время
⚡ 𝗔𝗩𝗧𝗢𝗠𝗔𝗧𝗜𝗭𝗔𝗖𝗜𝗬:
!автостатус [вкл/выкл/анимация] - Автоматический статус
!анимация [название] - Сменить анимацию статуса
🎭 𝗥𝗣 𝗞𝗢𝗠𝗔𝗡𝗗𝗬:
!рп [действие] - РП действие (ответом на сообщение)
!обнять, !поцеловать, !пнуть, !убить - Быстрые РП
🎯 𝗥𝗔𝗭𝗩𝗟𝗘𝗖𝗛𝗘𝗡𝗜𝗬:
!шутка - Случайная шутка
!цитата - Мудрая цитата
!рандом [число] - Случайное число
!кто [вопрос] - Выбор случайного участника
!выбери [вариант1] или [вариант2]
🌤 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗖𝗜𝗬:
!погода [город] - Погода (примерная)
🎨 𝗡𝗢𝗩𝗬𝗘 𝗙𝗨𝗡𝗞𝗖𝗜𝗜:
!qr [ссылка] - Сгенерировать QR-код
!видео [ссылка] - Скачать видео с YouTube
!аниме [тег] - Случайный аниме арт
!чс [ссылка] - Добавить в черный список
!токен - Получить токен бота
!команда [название] [описание] [ответ] - Создать команду
!моикоманды - Список ваших команд
!удалитькоманду [название] - Удалить команду
⚙️ 𝗦𝗜𝗦𝗧𝗘𝗠𝗡𝗬𝗘:
!дов +\- (ссылка) - добавить человека в доверенные
!логи - История команд
!стоп - Остановить автоматические функции"""
        self.bot.send_message(event.peer_id, help_text, 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_info(self, event, args):
        uptime = time.time() - getattr(self.bot, 'start_time', time.time())
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        info_text = f"""🤖 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗖𝗜𝗬 𝗢 𝗕𝗢𝗧𝗘
👤 Владелец: {self.bot.user_info['first_name']} {self.bot.user_info['last_name']}
🆔 ID: {self.bot.user_id}
⏱ Аптайм: {hours}ч {minutes}м
📦 Кастомных команд: {len(self.bot.custom_commands_module.custom_commands)}
🐍 Python 3.x
📡 VK API LongPoll
🔄 Многопоточность: Активна"""
        self.bot.send_message(event.peer_id, info_text, 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_ping(self, event, args):
        self.bot.send_message(event.peer_id, "🏓 Понг!", 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_time(self, event, args):
        now = datetime.now()
        time_text = f"""⏰ 𝗧𝗘𝗞𝗨𝗦𝗛𝗘𝗘 𝗩𝗥𝗘𝗠𝗬𝗔
🕐 {now.strftime("%H:%M:%S")}
📅 {now.strftime("%d.%m.%Y")}
📆 День недели: {['Пн','Вт','Ср','Чт','Пт','Сб','Вс'][now.weekday()]}"""
        self.bot.send_message(event.peer_id, time_text, 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_weather(self, event, args):
        city = " ".join(args) if args else "Москва"
        conditions = ["☀️ Солнечно", "⛅ Облачно", "🌧 Дождь", "❄️ Снег", "🌤 Переменная облачность"]
        temps = range(-15, 31)
        
        random.seed(city + str(datetime.now().date()))
        condition = random.choice(conditions)
        temp = random.choice(list(temps))
        
        weather_text = f"""🌤 𝗣𝗢𝗚𝗢𝗗𝗔: {city}
{condition}
🌡 Температура: {temp}°C
💨 Ветер: {random.randint(0, 20)} м/с
💧 Влажность: {random.randint(30, 90)}%
⚠️ Примечание: данные условные для демонстрации"""
        self.bot.send_message(event.peer_id, weather_text, 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_joke(self, event, args):
        jokes = [
            "— Почему программисты путают Хэллоуин и Рождество?\n— Потому что 31 OCT = 25 DEC",
            "— Какой язык программирования самый оптимистичный?\n— Java — потому что всегда в хорошем настроении",
            "— Почему Python-программисты не носят очки?\n— Потому что у них отступы и так в порядке",
            "— Сколько программистов нужно, чтобы поменять лампочку?\n— Ни одного, это hardware problem",
        ]
        joke = random.choice(jokes)
        self.bot.send_message(event.peer_id, f"😄 𝗦𝗛𝗨𝗧𝗞𝗔:\n\n{joke}", 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_quote(self, event, args):
        quotes = [
            "«Программирование — это искусство учить компьютер делать то, что ты сам не хочешь делать.»",
            "«Лучший способ предсказать будущее — создать его.» — Алан Кей",
            "«Простота — это сложность, которую удалось решить.»",
            "«Код читается гораздо чаще, чем пишется.»",
        ]
        quote = random.choice(quotes)
        self.bot.send_message(event.peer_id, f"📜 𝗖𝗜𝗧𝗔𝗧𝗔:\n\n{quote}", 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_random(self, event, args):
        try:
            if args:
                max_num = int(args[0])
                result = random.randint(1, max_num)
                self.bot.send_message(event.peer_id, f"🎲 𝗥𝗔𝗡𝗗𝗢𝗠 (1-{max_num}):\n\n✨ {result}", 
                    reply_to=event.message_id if not event.from_me else None)
            else:
                result = random.randint(1, 100)
                self.bot.send_message(event.peer_id, f"🎲 𝗥𝗔𝗡𝗗𝗢𝗠 (1-100):\n\n✨ {result}", 
                    reply_to=event.message_id if not event.from_me else None)
        except:
            self.bot.send_message(event.peer_id, "❌ Укажите число: !рандом 50", 
                reply_to=event.message_id if not event.from_me else None)
    
    def cmd_who(self, event, args):
        question = " ".join(args) if args else "кто самый крутой?"
        try:
            if event.peer_id > 2000000000:
                members = self.bot.vk.messages.getConversationMembers(peer_id=event.peer_id)
                users = members.get("profiles", [])
                if users:
                    random_user = random.choice(users)
                    name = f"[id{random_user['id']}|{random_user['first_name']} {random_user['last_name']}]"
                else:
                    name = "никто"
            else:
                name = "ты сам"
            
            self.bot.send_message(event.peer_id, f"🎯 {question}\n\n👤 {name}", 
                reply_to=event.message_id if not event.from_me else None)
        except Exception as e:
            log(f"Ошибка в команде кто: {e}", "ERROR")
            self.bot.send_message(event.peer_id, f"🎯 {question}\n\n👤 Не могу определить", 
                reply_to=event.message_id if not event.from_me else None)
    
    def cmd_choose(self, event, args):
        text = " ".join(args)
        if " или " in text:
            options = text.split(" или ")
            choice = random.choice(options).strip()
            self.bot.send_message(event.peer_id, f"🤔 Выбираю...\n\n✅ {choice}", 
                reply_to=event.message_id if not event.from_me else None)
        else:
            self.bot.send_message(event.peer_id, "❌ Использование: !выбери пицца или бургер", 
                reply_to=event.message_id if not event.from_me else None)
    
    def cmd_logs(self, event, args):
        if not self.bot.command_history:
            self.bot.send_message(event.peer_id, "📋 История команд пуста", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        recent = self.bot.command_history[-10:]
        logs_text = "📋 𝗣𝗢𝗦𝗟𝗘𝗗𝗡𝗜𝗘 𝗞𝗢𝗠𝗔𝗡𝗗𝗬:\n\n"
        for entry in recent:
            logs_text += f"⏰ {entry['time']}\n💬 {entry['command']}\n👤 {entry['user']}\n\n"
        
        self.bot.send_message(event.peer_id, logs_text, 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_stop(self, event, args):
        if hasattr(self.bot, 'animation_module'):
            self.bot.animation_module.stop()
        
        self.bot.auto_like_enabled = False
        self.bot.auto_like_targets.clear()
        
        self.bot.send_message(event.peer_id, "🛑 Все автоматические функции остановлены", 
            reply_to=event.message_id if not event.from_me else None)
