"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      VK ANIME LP BOT v5.0 MODULAR                            ║
║                        копирование файла запрещено                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import threading
import time
import random
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
from collections import defaultdict
from config import CONFIG
from utils import log, Colors

try:
    from anime import AnimeAPI
    ANIME_MODULE_AVAILABLE = True
    anime_api = AnimeAPI()
except ImportError:
    ANIME_MODULE_AVAILABLE = False
    print("⚠️ Модуль anime.py не найден.")

from anim import AnimationModule
from qr import QRModule
from blacklist import BlacklistModule
from vk_token import TokenModule
from custom_commands import CustomCommandsModule
from rp import RPModule
from info import InfoModule
from youtube import YouTubeModule


class VKBot:
    def __init__(self):
        self.vk_session = None
        self.vk = None
        self.longpoll = None
        self.user_info = None
        self.user_id = None
        
        self.auto_like_targets: Dict[int, dict] = {}
        self.auto_like_thread = None
        self.auto_like_enabled = False
        
        self.command_history = []
        self.commands: Dict[str, callable] = {}
        
        self.trusted_file = "trusted_users.json"
        self.trusted_users: Set[int] = set()
        self.load_trusted_users()
        
        self.animation_module = AnimationModule(self)
        self.qr_module = QRModule(self)
        self.blacklist_module = BlacklistModule(self)
        self.token_module = TokenModule(self)
        self.custom_commands_module = CustomCommandsModule(self)
        self.rp_module = RPModule(self)
        self.info_module = InfoModule(self)
        self.youtube_module = YouTubeModule(self)
        
        self._register_all_commands()
        
        self.commands["дов"] = self.cmd_trust
        self.commands["trust"] = self.cmd_trust
        
        if ANIME_MODULE_AVAILABLE:
            self.commands["аниме"] = self.cmd_anime
        
        self.init_vk()
    
    def load_trusted_users(self):
        try:
            if os.path.exists(self.trusted_file):
                with open(self.trusted_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.trusted_users = set(data.get("trusted_users", []))
                log(f"Загружено {len(self.trusted_users)} доверенных пользователей", "SUCCESS")
            else:
                self.trusted_users = set()
                if self.user_id:
                    self.trusted_users.add(self.user_id)
                    self.save_trusted_users()
                log("Создан новый файл доверенных пользователей", "INFO")
        except Exception as e:
            log(f"Ошибка загрузки доверенных пользователей: {e}", "ERROR")
            self.trusted_users = set()
    
    def save_trusted_users(self):
        try:
            data = {
                "trusted_users": list(self.trusted_users),
                "last_updated": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            }
            with open(self.trusted_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            log("Список доверенных пользователей сохранен", "SUCCESS")
        except Exception as e:
            log(f"Ошибка сохранения доверенных пользователей: {e}", "ERROR")
    
    def is_trusted(self, user_id: int) -> bool:
        return user_id in self.trusted_users or user_id == self.user_id
    
    def cmd_trust(self, event, args):
        if event.from_me:
            return
        
        if not args:
            if self.trusted_users:
                trusted_list = "\n".join([f"• [id{uid}|Пользователь]" for uid in sorted(self.trusted_users)])
                self.bot.send_message(event.peer_id, 
                    f"🔒 𝗗𝗢𝗩𝗘𝗥𝗘𝗡𝗡𝗬𝗘 𝗣𝗢𝗟𝗡𝗭𝗢𝗩𝗔𝗧𝗘𝗟𝗜 ({len(self.trusted_users)}):\n\n{trusted_list}", 
                    reply_to=event.message_id if not event.from_me else None)
            else:
                self.bot.send_message(event.peer_id, 
                    "🔒 Список доверенных пользователей пуст", 
                    reply_to=event.message_id if not event.from_me else None)
            return
        
        action = args[0].lower()
    
        if event.user_id != self.user_id:
            self.send_message(event.peer_id, 
                "❌ Только владелец бота может управлять списком доверенных пользователей!", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        if len(args) < 2:
            self.send_message(event.peer_id, 
                "❌ Использование: !дов + [id или ссылка] - добавить\n!дов - [id или ссылка] - удалить\n!дов - показать список", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        target = args[1]
        target_id = self.parse_user_id(target)
        
        if not target_id:
            self.send_message(event.peer_id, 
                "❌ Не удалось определить ID пользователя. Используйте ссылку или числовой ID", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        if action == "+" or action == "add":
            if target_id == self.user_id:
                self.send_message(event.peer_id, 
                    "👑 Владелец бота всегда в доверенных!", 
                    reply_to=event.message_id if not event.from_me else None)
                return
            
            if target_id in self.trusted_users:
                self.send_message(event.peer_id, 
                    f"⚠️ Пользователь [id{target_id}|уже] в доверенных!", 
                    reply_to=event.message_id if not event.from_me else None)
                return
            
            self.trusted_users.add(target_id)
            self.save_trusted_users()
            
            try:
                user_info = self.vk.users.get(user_ids=target_id)[0]
                user_name = f"{user_info['first_name']} {user_info['last_name']}"
                self.send_message(event.peer_id, 
                    f"✅ Пользователь {user_name} (id{target_id}) добавлен в доверенные!\n\nТеперь он может использовать команды бота.", 
                    reply_to=event.message_id if not event.from_me else None)
                log(f"Добавлен доверенный пользователь: {user_name} (id{target_id})", "SUCCESS")
            except:
                self.send_message(event.peer_id, 
                    f"✅ Пользователь id{target_id} добавлен в доверенные!", 
                    reply_to=event.message_id if not event.from_me else None)
        
        elif action == "-" or action == "remove" or action == "del":
            if target_id == self.user_id:
                self.send_message(event.peer_id, 
                    "👑 Нельзя удалить владельца бота из доверенных!", 
                    reply_to=event.message_id if not event.from_me else None)
                return
            
            if target_id not in self.trusted_users:
                self.send_message(event.peer_id, 
                    f"⚠️ Пользователь id{target_id} не в доверенных!", 
                    reply_to=event.message_id if not event.from_me else None)
                return
            
            self.trusted_users.discard(target_id)
            self.save_trusted_users()
            
            try:
                user_info = self.vk.users.get(user_ids=target_id)[0]
                user_name = f"{user_info['first_name']} {user_info['last_name']}"
                self.send_message(event.peer_id, 
                    f"❌ Пользователь {user_name} (id{target_id}) удален из доверенных!\n\nТеперь он НЕ может использовать команды бота.", 
                    reply_to=event.message_id if not event.from_me else None)
                log(f"Удален доверенный пользователь: {user_name} (id{target_id})", "WARNING")
            except:
                self.send_message(event.peer_id, 
                    f"❌ Пользователь id{target_id} удален из доверенных!", 
                    reply_to=event.message_id if not event.from_me else None)
        else:
            self.send_message(event.peer_id, 
                "❌ Использование: !дов + [id] - добавить\n!дов - [id] - удалить", 
                reply_to=event.message_id if not event.from_me else None)
    
    def parse_user_id(self, user_input: str) -> Optional[int]:
        """Парсит ID пользователя из ссылки или числа"""
        try:
            if user_input.lstrip('-').isdigit():
                return int(user_input)
            
            user_input = user_input.replace("https://", "").replace("http://", "")
            user_input = user_input.replace("vk.com/", "").replace("m.vk.com/", "")
            user_input = user_input.replace("vkontakte.ru/", "")
            
            if user_input.startswith("id"):
                return int(user_input[2:])
            
            try:
                response = self.vk.utils.resolveScreenName(screen_name=user_input)
                if response and response["type"] == "user":
                    return response["object_id"]
            except:
                pass
            
            return None
        except:
            return None

    def _register_all_commands(self):
        self.animation_module.register_commands()
        self.qr_module.register_commands()
        self.blacklist_module.register_commands()
        self.token_module.register_commands()
        self.custom_commands_module.register_commands()
        self.rp_module.register_commands()
        self.info_module.register_commands()
        self.youtube_module.register_commands()

    def init_vk(self):
        try:
            self.vk_session = vk_api.VkApi(token=CONFIG["TOKEN"])
            self.vk = self.vk_session.get_api()
            self.longpoll = VkLongPoll(self.vk_session)
            
            self.user_info = self.vk.users.get(fields="first_name,last_name,sex")[0]
            self.user_id = self.user_info["id"]
            CONFIG["ADMIN_ID"] = self.user_id
            
            if not self.trusted_users:
                self.trusted_users.add(self.user_id)
                self.save_trusted_users()
            
            log(f"Бот авторизован как {self.user_info['first_name']} {self.user_info['last_name']} (ID: {self.user_id})", "SUCCESS")
            self.send_to_favorite("🤖 Бот успешно запущен и готов к работе!\nИспользуй !помощь для списка команд")
            
        except Exception as e:
            log(f"Ошибка инициализации: {e}", "ERROR")
            raise

    def send_message(self, peer_id: int, message: str, attachment: str = None, reply_to: int = None):
        try:
            params = {
                "peer_id": peer_id,
                "message": message,
                "random_id": random.randint(-2147483648, 2147483647)
            }
            if attachment:
                params["attachment"] = attachment
            if reply_to:
                params["reply_to"] = reply_to
            
            self.vk.messages.send(**params)
            return True
        except Exception as e:
            log(f"Ошибка отправки сообщения: {e}", "ERROR")
            return False

    def send_to_favorite(self, message: str):
        try:
            self.vk.messages.send(
                peer_id=self.user_id,
                message=message,
                random_id=random.randint(-2147483648, 2147483647)
            )
        except:
            pass

    def log_command(self, command: str, args: list, peer_id: int, from_id: int):
        try:
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            user_info = self.vk.users.get(user_ids=from_id)[0]
            user_name = f"{user_info['first_name']} {user_info['last_name']}"
            
            trusted_status = "✅ Доверенный" if self.is_trusted(from_id) else "❌ НЕ доверенный"
            
            log_msg = (
                f"📋 ЛОГ КОМАНДЫ\n"
                f"⏰ Время: {timestamp}\n"
                f"👤 Пользователь: {user_name} (профиль: vk.ru/id{from_id})\n"
                f"🔒 Статус: {trusted_status}\n"
                f"💬 Команда: {command}\n"
                f"📎 Аргументы: {' '.join(args) if args else 'нет'}\n"
                f"🆔 Peer ID: {peer_id}"
            )
            
            self.send_to_favorite(log_msg)
            self.command_history.append({
                "time": timestamp,
                "command": command,
                "user": user_name,
                "user_id": from_id,
                "trusted": self.is_trusted(from_id)
            })
        except Exception as e:
            log(f"Ошибка логирования: {e}", "ERROR")

    def cmd_anime(self, event, args):
        if not ANIME_MODULE_AVAILABLE:
            self.send_message(event.peer_id, "❌ Модуль аниме недоступен.", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        if not args:
            info_text = anime_api.get_info_text()
            self.send_message(event.peer_id, info_text,
                reply_to=event.message_id if not event.from_me else None)
            return
        
        subcommand = args[0].lower()
        
        if subcommand == "nsfw":
            anime_api.set_nsfw_mode(True)
            self.send_message(event.peer_id, 
                "🔞 𝗘𝗚𝗜𝗠 𝟭𝟴+ 𝗩𝗞𝗟𝗬𝗨𝗖𝗛𝗘𝗡!\n\n"
                "⚠️ Теперь арты будут из NSFW групп\n"
                "👶 Для отключения: !аниме sfw",
                reply_to=event.message_id if not event.from_me else None)
            return
        
        if subcommand == "sfw":
            anime_api.set_nsfw_mode(False)
            self.send_message(event.peer_id, 
                "👶 𝗢𝗬𝗖𝗛𝗡𝗝 𝗥𝗘𝗚𝗜𝗠 𝗩𝗞𝗟𝗬𝗛𝗘!\n\n"
                "✅ 18+ режим отключен\n"
                "🔞 Для включения: !аниме nsfw",
                reply_to=event.message_id if not event.from_me else None)
            return
        
        if subcommand in ["категории", "categories", "список", "list", "инфо", "info"]:
            categories_text = anime_api.get_available_categories_text()
            self.send_message(event.peer_id, categories_text,
                reply_to=event.message_id if not event.from_me else None)
            return
        mode_text = "🔞 (18+ режим)" if anime_api.nsfw_mode else "👶 (обычный режим)"
        self.send_message(event.peer_id, 
            f"⏳ 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗦𝗜𝗬 𝗔𝗥𝗧𝗔...\n\n"
            f"🎭 Режим: {mode_text}\n"
            f"📂 Ищем арты в группах...",
            reply_to=event.message_id if not event.from_me else None)
        
        try:
            attachment = anime_api.get_random_attachment(self.vk)
            
            if attachment:
                category = random.choice(anime_api.sfw_categories if not anime_api.nsfw_mode else anime_api.nsfw_categories)
                category_name = anime_api.get_category_name_ru(category)
                
                self.send_message(event.peer_id, 
                    f"🎨 𝗡𝗜𝗠𝗘 𝗔𝗥𝗧\n\n"
                    f"📂 Категория: {category_name}\n"
                    f"💖 Приятного просмотра!", 
                    attachment=attachment)
            else:
                self.send_message(event.peer_id, 
                    "❌ Не удалось найти арты в группах.\n"
                    "⚠️ Проверьте, добавлены ли группы в anime.py",
                    reply_to=event.message_id if not event.from_me else None)
            
        except Exception as e:
            log(f"Ошибка получения аниме: {e}", "ERROR")
            self.send_message(event.peer_id, 
                "❌ Ошибка при получении аниме арта\n"
                f"🔧 Детали: {str(e)}",
                reply_to=event.message_id if not event.from_me else None)

    def parse_vk_link(self, link: str):
        return self.blacklist_module.parse_vk_link(link)

    def auto_like_loop(self):
        while self.auto_like_enabled:
            try:
                for target_id, target_info in list(self.auto_like_targets.items()):
                    try:
                        posts = self.vk.wall.get(
                            owner_id=target_id,
                            count=5,
                            filter="owner"
                        )
                        
                        for post in posts["items"]:
                            post_id = post["id"]
                            
                            if post_id > target_info["last_post_id"]:
                                self.vk.likes.add(
                                    type="post",
                                    owner_id=target_id,
                                    item_id=post_id
                                )
                                
                                log(f"Лайк поставлен: {target_id}_{post_id}", "SUCCESS")
                                target_info["last_post_id"] = post_id
                                self.send_to_favorite(f"💚 Автолайк: поставлен лайк посту {target_id}_{post_id}")
                                
                                time.sleep(1)
                        
                    except Exception as e:
                        log(f"Ошибка автолайка для {target_id}: {e}", "ERROR")
                
                time.sleep(CONFIG["AUTO_LIKE_CHECK_INTERVAL"])
                
            except Exception as e:
                log(f"Ошибка цикла автолайка: {e}", "ERROR")
                time.sleep(10)

    def process_message(self, event):
        text = event.text.strip()
        
        if not text.startswith(CONFIG["COMMAND_PREFIX"]):
            return
        
        text = text[len(CONFIG["COMMAND_PREFIX"]):]
        parts = text.split()
        
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        if command not in ["дов", "trust"]:
            if not self.is_trusted(event.user_id):
                self.send_message(event.peer_id, 
                    "🔒 𝗗𝗢𝗦𝗧𝗨𝗣 𝗭𝗔𝗣𝗥𝗘𝗦𝗛𝗘𝗡!\n\n"
                    "⚠️ Вы не в списке доверенных пользователей.\n"
                    "📝 Для получения доступа обратитесь к владельцу бота.\n"
                    f"👑 Владелец: [id{self.user_id}|{self.user_info['first_name']} {self.user_info['last_name']}]", 
                    reply_to=event.message_id if not event.from_me else None)
                return
        
        self.log_command(command, args, event.peer_id, event.user_id)
        log(f"Команда: {command} | Аргументы: {args} | Peer: {event.peer_id} | Доверенный: {self.is_trusted(event.user_id)}", "COMMAND")
        
        if command in self.commands:
            try:
                self.commands[command](event, args)
            except Exception as e:
                log(f"Ошибка выполнения команды {command}: {e}", "ERROR")
                self.send_message(event.peer_id, f"❌ Ошибка: {str(e)}", 
                    reply_to=event.message_id if not event.from_me else None)
        else:
            self.send_message(event.peer_id, "❌ Неизвестная команда. Используйте !помощь", 
                reply_to=event.message_id if not event.from_me else None)

    def run(self):
        self.start_time = time.time()
        log("=" * 60, "INFO")
        log("БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ", "SUCCESS")
        log("=" * 60, "INFO")
        
        self.send_to_favorite("🚀 Бот запущен и слушает сообщения...")
        
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.text and event.text.startswith(CONFIG["COMMAND_PREFIX"]):
                            self.process_message(event)
                            
            except Exception as e:
                log(f"Ошибка в главном цикле: {e}", "ERROR")
                self.send_to_favorite(f"⚠️ Ошибка в работе бота: {str(e)}\nПереподключаюсь...")
                time.sleep(5)
                try:
                    self.init_vk()
                except:
                    pass


if __name__ == "__main__":
    try:
        bot = VKBot()
        bot.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Бот остановлен пользователем{Colors.ENDC}")
    except Exception as e:
        log(f"Критическая ошибка: {e}", "ERROR")
        input("Нажмите Enter для выхода...")
