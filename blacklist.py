"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         BLACKLIST MODULE                                     ║
║                    Модуль для управления черным списком                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from typing import TYPE_CHECKING, Optional
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

class BlacklistModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
    
    def register_commands(self):
        self.bot.commands["чс"] = self.cmd_blacklist
    
    def parse_vk_link(self, link: str) -> Optional[int]:
        try:
            link = link.replace("https://", "").replace("http://", "")
            link = link.replace("vk.com/", "").replace("m.vk.com/", "")
            link = link.replace("vkontakte.ru/", "")
            
            if link.isdigit():
                return int(link)
            
            if link.startswith("id"):
                return int(link[2:])
            
            if link.startswith("club"):
                return -int(link[4:])
            
            if link.startswith("public"):
                return -int(link[6:])
            
            try:
                response = self.bot.vk.utils.resolveScreenName(screen_name=link)
                if response:
                    obj_id = response["object_id"]
                    obj_type = response["type"]
                    return -obj_id if obj_type == "group" else obj_id
            except:
                pass
            
            return None
        except:
            return None
    
    def cmd_blacklist(self, event, args):
        if not args:
            self.bot.send_message(event.peer_id, 
                "❌ Использование: !чс [ссылка на профиль]\nПример: !чс vk.com/id123456", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        link = args[0]
        user_id = self.parse_vk_link(link)
        
        if not user_id or user_id < 0:
            self.bot.send_message(event.peer_id, 
                "❌ Не удалось определить ID пользователя. Используйте ссылку на профиль.\nПример: !чс vk.com/id123456", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        try:
            self.bot.vk.account.banUser(owner_id=user_id)
            user_info = self.bot.vk.users.get(user_ids=user_id)[0]
            user_name = f"{user_info['first_name']} {user_info['last_name']}"
            
            self.bot.send_message(event.peer_id, 
                f"✅ Пользователь {user_name} (id{user_id}) добавлен в черный список!", 
                reply_to=event.message_id if not event.from_me else None)
            log(f"Пользователь {user_name} (id{user_id}) добавлен в ЧС", "SUCCESS")
            
        except Exception as e:
            log(f"Ошибка добавления в ЧС: {e}", "ERROR")
            self.bot.send_message(event.peer_id, f"❌ Ошибка: {str(e)}", 
                reply_to=event.message_id if not event.from_me else None)