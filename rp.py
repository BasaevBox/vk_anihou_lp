"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         RP MODULE                                            ║
║                    Модуль для RP команд                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from typing import TYPE_CHECKING
from config import RP_COMMANDS
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

class RPModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
    
    def register_commands(self):
        self.bot.commands.update({
            "рп": self.cmd_rp,
            "rp": self.cmd_rp,
        })
        
        for cmd_name in RP_COMMANDS.keys():
            self.bot.commands[cmd_name] = lambda e, a, name=cmd_name: self.cmd_rp_direct(e, a, name)
    
    def cmd_rp(self, event, args):
        if not args:
            rp_list = "\n".join([f"!рп {cmd}" for cmd in list(RP_COMMANDS.keys())[:10]])
            self.bot.send_message(event.peer_id, 
                f"🎭 𝗥𝗣 𝗞𝗢𝗠𝗔𝗡𝗗𝗬:\n\n{rp_list}\n\n...и еще {len(RP_COMMANDS)-10} команд\nИспользуйте ответом на сообщение!", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        action = args[0].lower()
        
        if action not in RP_COMMANDS:
            self.bot.send_message(event.peer_id, 
                "❌ Неизвестное РП действие. Используйте !рп для списка", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        self._send_rp_action(event, action)
    
    def cmd_rp_direct(self, event, args, action):
        self._send_rp_action(event, action)
    
    def _send_rp_action(self, event, action):
        reply_message_id = None
        target_name = None
        
        try:
            msg_info = self.bot.vk.messages.getById(message_ids=event.message_id)
            if msg_info["items"]:
                msg = msg_info["items"][0]
                if "reply_message" in msg:
                    reply_msg = msg["reply_message"]
                    reply_message_id = reply_msg["id"]
                    target_id = reply_msg["from_id"]
                    
                    if target_id > 0:
                        user = self.bot.vk.users.get(user_ids=target_id)[0]
                        target_name = f"[id{target_id}|{user['first_name']} {user['last_name']}]"
                    else:
                        target_name = "группу"
        except:
            pass
        
        rp_info = RP_COMMANDS[action]
        my_name = f"[id{self.bot.user_id}|{self.bot.user_info['first_name']}]"
        
        if target_name:
            text = f"{rp_info['emoji']} {my_name} {rp_info['text']} {target_name}"
        else:
            text = f"{rp_info['emoji']} {my_name} {rp_info['text']} воздух"
        
        self.bot.send_message(event.peer_id, text, 
            reply_to=reply_message_id if reply_message_id else event.message_id if not event.from_me else None)