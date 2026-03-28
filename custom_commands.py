"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      CUSTOM COMMANDS MODULE                                  ║
║                    Модуль для создания кастомных команд                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import re
from datetime import datetime
from typing import TYPE_CHECKING, Dict
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

class CustomCommandsModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
        self.custom_commands_file = "custom_commands.json"
        self.custom_commands: Dict[str, dict] = {}
        self.load_custom_commands()
    
    def register_commands(self):
        self.bot.commands.update({
            "команда": self.cmd_custom_command,
            "моикоманды": self.cmd_list_custom_commands,
            "удалитькоманду": self.cmd_delete_custom_command,
        })
    
    def load_custom_commands(self):
        try:
            if os.path.exists(self.custom_commands_file):
                with open(self.custom_commands_file, 'r', encoding='utf-8') as f:
                    self.custom_commands = json.load(f)
                log(f"Загружено {len(self.custom_commands)} кастомных команд", "SUCCESS")
        except Exception as e:
            log(f"Ошибка загрузки кастомных команд: {e}", "ERROR")
            self.custom_commands = {}
    
    def save_custom_commands(self):
        try:
            with open(self.custom_commands_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_commands, f, ensure_ascii=False, indent=2)
            log("Кастомные команды сохранены", "SUCCESS")
        except Exception as e:
            log(f"Ошибка сохранения кастомных команд: {e}", "ERROR")
    
    def register_custom_command(self, cmd_name: str):
        self.bot.commands[cmd_name] = lambda e, a, name=cmd_name: self.execute_custom_command(e, a, name)
    
    def cmd_custom_command(self, event, args):
        if len(args) < 3:
            self.bot.send_message(event.peer_id, 
                """❌ Использование: !команда [название] [описание] [ответ]
Пример:
!команда привет Приветствую пользователя Привет! Как дела?
Где:
название: имя команды (без !)
описание: краткое описание
ответ: текст, который будет отправлен при вызове команды""", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        cmd_name = args[0].lower()
        cmd_desc = args[1]
        cmd_response = " ".join(args[2:])
        
        if cmd_name in self.bot.commands or cmd_name in self.custom_commands:
            self.bot.send_message(event.peer_id, 
                f"❌ Команда '{cmd_name}' уже существует!", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        if not re.match(r'^[a-zа-яё0-9_]+$', cmd_name):
            self.bot.send_message(event.peer_id, 
                "❌ Название команды может содержать только буквы, цифры и подчеркивание!", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        self.custom_commands[cmd_name] = {
            "description": cmd_desc,
            "response": cmd_response,
            "created_by": self.bot.user_id,
            "created_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        }
        
        self.save_custom_commands()
        self.register_custom_command(cmd_name)
        
        self.bot.send_message(event.peer_id, 
            f"""✅ Команда '{cmd_name}' создана!
📝 Описание: {cmd_desc}
💬 Ответ: {cmd_response}
Используйте: !{cmd_name}""", 
            reply_to=event.message_id if not event.from_me else None)
        log(f"Создана кастомная команда: {cmd_name}", "SUCCESS")
    
    def execute_custom_command(self, event, args, cmd_name):
        if cmd_name in self.custom_commands:
            cmd_data = self.custom_commands[cmd_name]
            response = cmd_data["response"]
            
            response = response.replace("{user}", f"[id{event.user_id}|Пользователь]")
            response = response.replace("{me}", f"[id{self.bot.user_id}|{self.bot.user_info['first_name']}]")
            
            self.bot.send_message(event.peer_id, response, 
                reply_to=event.message_id if not event.from_me else None)
    
    def cmd_list_custom_commands(self, event, args):
        if not self.custom_commands:
            self.bot.send_message(event.peer_id, 
                "📋 У вас пока нет кастомных команд.\n\nСоздайте команду: !команда [название] [описание] [ответ]", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        commands_list = "📋 𝗩𝗔𝗦𝗛𝗜 𝗞𝗢𝗠𝗔𝗡𝗗𝗬:\n\n"
        for name, data in self.custom_commands.items():
            commands_list += f"❗ !{name}\n   📝 {data['description']}\n\n"
        
        commands_list += f"\nВсего команд: {len(self.custom_commands)}"
        
        self.bot.send_message(event.peer_id, commands_list, 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_delete_custom_command(self, event, args):
        if not args:
            self.bot.send_message(event.peer_id, 
                "❌ Использование: !удалитькоманду [название]", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        cmd_name = args[0].lower()
        
        if cmd_name not in self.custom_commands:
            self.bot.send_message(event.peer_id, 
                f"❌ Команда '{cmd_name}' не найдена!", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        del self.custom_commands[cmd_name]
        if cmd_name in self.bot.commands:
            del self.bot.commands[cmd_name]
        
        self.save_custom_commands()
        
        self.bot.send_message(event.peer_id, 
            f"✅ Команда '{cmd_name}' удалена!", 
            reply_to=event.message_id if not event.from_me else None)
        log(f"Удалена кастомная команда: {cmd_name}", "SUCCESS")