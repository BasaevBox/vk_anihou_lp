"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ANIMATION MODULE                                     ║
║                    Модуль для управления анимациями статуса                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import threading
import time
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from config import STATUS_ANIMATIONS, CONFIG
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

class AnimationModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
        self.auto_status_enabled = False
        self.status_animation_running = False
        self.current_animation = "wave"
        self.auto_status_thread = None
    
    def register_commands(self):
        self.bot.commands.update({
            "анимация": self.cmd_animation,
            "animation": self.cmd_animation,
            "статус": self.cmd_status_list,
            "автостатус": self.cmd_auto_status,
        })
    
    def cmd_animation(self, event, args):
        if not args:
            anims = ", ".join(STATUS_ANIMATIONS.keys())
            self.bot.send_message(event.peer_id, 
                f"🎨 Доступные анимации:\n{anims}\n\nТекущая: {self.current_animation}", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        anim_name = args[0].lower()
        if anim_name in STATUS_ANIMATIONS:
            self.current_animation = anim_name
            self.bot.send_message(event.peer_id, 
                f"✅ Анимация изменена на: {anim_name}", 
                reply_to=event.message_id if not event.from_me else None)
        else:
            self.bot.send_message(event.peer_id, "❌ Такой анимации нет", 
                reply_to=event.message_id if not event.from_me else None)
    
    def cmd_status_list(self, event, args):
        anims = "\n".join([f"• {name}" for name in STATUS_ANIMATIONS.keys()])
        self.bot.send_message(event.peer_id, 
            f"🎨 𝗗𝗢𝗦𝗧𝗨𝗣𝗡𝗬𝗘 𝗔𝗡𝗜𝗠𝗔𝗖𝗜𝗜:\n\n{anims}\n\nТекущая: {self.current_animation}", 
            reply_to=event.message_id if not event.from_me else None)
    
    def cmd_auto_status(self, event, args):
        if not args:
            status = "✅ Включен" if self.auto_status_enabled else "❌ Выключен"
            self.bot.send_message(event.peer_id, 
                f"⚡ Автостатус: {status}\nАнимация: {self.current_animation}\n\n"
                f"Использование:\n!автостатус вкл - Включить\n!автостатус выкл - Выключить", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        action = args[0].lower()
        
        if action in ["вкл", "on", "1"]:
            if not self.auto_status_enabled:
                self.auto_status_enabled = True
                self.status_animation_running = True
                self.auto_status_thread = threading.Thread(target=self.status_animation_loop, daemon=True)
                self.auto_status_thread.start()
                self.bot.send_message(event.peer_id, 
                    f"✅ Автостатус включен!\n🎨 Анимация: {self.current_animation}", 
                    reply_to=event.message_id if not event.from_me else None)
            else:
                self.bot.send_message(event.peer_id, "⚡ Автостатус уже работает", 
                    reply_to=event.message_id if not event.from_me else None)
                
        elif action in ["выкл", "off", "0"]:
            self.auto_status_enabled = False
            self.status_animation_running = False
            try:
                self.bot.vk.status.set(text="")
            except:
                pass
            self.bot.send_message(event.peer_id, "❌ Автостатус выключен", 
                reply_to=event.message_id if not event.from_me else None)
    
    def status_animation_loop(self):
        frame_index = 0
        animation = STATUS_ANIMATIONS[self.current_animation]
        
        while self.status_animation_running and self.auto_status_enabled:
            try:
                frame = animation[frame_index % len(animation)]
                now = datetime.now()
                time_str = now.strftime("%H:%M")
                status_text = f"{frame} | {time_str}"
                
                self.bot.vk.status.set(text=status_text)
                log(f"Статус обновлен: {status_text[:30]}...", "ANIMATION")
                
                frame_index += 1
                time.sleep(CONFIG["STATUS_UPDATE_INTERVAL"])
                
            except Exception as e:
                log(f"Ошибка автостатуса: {e}", "ERROR")
                time.sleep(5)
    
    def stop(self):
        self.auto_status_enabled = False
        self.status_animation_running = False