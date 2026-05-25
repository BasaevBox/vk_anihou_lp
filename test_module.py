"""
Автоматически созданный модуль: test
Создан: 25.05.2026 02:26:54
"""
from typing import TYPE_CHECKING
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

class TestModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot

    def register_commands(self):
        self.bot.commands["hello"] = lambda e, a: self.bot.send_message(e.peer_id, "help me")
        log(f"Модуль test загружен", "SUCCESS")

    def stop(self):
        log("Модуль test остановлен", "WARNING")

def create_module(bot):
    m = TestModule(bot)
    m.register_commands()
    return m
