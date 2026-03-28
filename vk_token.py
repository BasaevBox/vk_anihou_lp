"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         TOKEN MODULE                                         ║
║                    Модуль для работы с токеном бота                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from typing import TYPE_CHECKING
from config import CONFIG
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

class TokenModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
    
    def register_commands(self):
        self.bot.commands["токен"] = self.cmd_token
    
    def cmd_token(self, event, args):
        try:
            token = CONFIG["TOKEN"]
            masked_token = token[:20] + "..." + token[-20:] if len(token) > 40 else "***"
            
            message = f"""🔑 𝗧𝗢𝗞𝗘𝗡 𝗕𝗢𝗧𝗔
⚠️ ВНИМАНИЕ! Это конфиденциальная информация!
Никому не передавайте этот токен!
📋 Токен:
{token}
🔐 Маскированная версия:
{masked_token}
💡 Используйте этот токен для авторизации бота."""
            
            self.bot.send_to_favorite(message)
            self.bot.send_message(event.peer_id, 
                "✅ Токен отправлен в ваши избранные сообщения!", 
                reply_to=event.message_id if not event.from_me else None)
            
            log("Токен запрошен и отправлен в избранное", "WARNING")
            
        except Exception as e:
            log(f"Ошибка отправки токена: {e}", "ERROR")
            self.bot.send_message(event.peer_id, "❌ Ошибка при отправке токена", 
                reply_to=event.message_id if not event.from_me else None)