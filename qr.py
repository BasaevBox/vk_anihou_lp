"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         QR CODE MODULE                                       ║
║                    Модуль для генерации QR-кодов                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import requests
import os
from typing import TYPE_CHECKING
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

class QRModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
    
    def register_commands(self):
        self.bot.commands["qr"] = self.cmd_qr
    
    def cmd_qr(self, event, args):
        if not args:
            self.bot.send_message(event.peer_id, 
                "❌ Использование: !qr [ссылка или текст]\nПример: !qr https://vk.com", 
                reply_to=event.message_id if not event.from_me else None)
            return
        
        text = " ".join(args)
        
        try:
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={text}"
            response = requests.get(qr_url)
            
            if response.status_code == 200:
                temp_file = "temp_qr.png"
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                
                try:
                    upload_url = self.bot.vk.photos.getMessagesUploadServer(peer_id=event.peer_id)['upload_url']
                    upload_response = requests.post(upload_url, files={'photo': open(temp_file, 'rb')})
                    upload_data = upload_response.json()
                    
                    if 'photo' in upload_data:
                        saved_photo = self.bot.vk.photos.saveMessagesPhoto(
                            photo=upload_data['photo'],
                            server=upload_data.get('server', ''),
                            hash=upload_data.get('hash', '')
                        )
                        
                        if saved_photo:
                            photo_id = f"photo{saved_photo[0]['owner_id']}_{saved_photo[0]['id']}"
                            self.bot.send_message(event.peer_id, 
                                f"✅ QR-код сгенерирован!\n\n📱 Отсканируй, чтобы перейти:\n{text}", 
                                attachment=photo_id, 
                                reply_to=event.message_id if not event.from_me else None)
                        else:
                            self.bot.send_message(event.peer_id, 
                                f"✅ QR-код готов!\n\n📱 {text}\n\n⚠️ Не удалось отправить изображение", 
                                reply_to=event.message_id if not event.from_me else None)
                    else:
                        self.bot.send_message(event.peer_id, 
                            f"✅ QR-код готов!\n\n📱 {text}", 
                            reply_to=event.message_id if not event.from_me else None)
                    
                    os.remove(temp_file)
                    
                except Exception as e:
                    log(f"Ошибка загрузки QR: {e}", "ERROR")
                    self.bot.send_message(event.peer_id, 
                        f"✅ QR-код сгенерирован!\n\n📱 {text}\n\n⚠️ Не удалось прикрепить изображение", 
                        reply_to=event.message_id if not event.from_me else None)
            else:
                self.bot.send_message(event.peer_id, "❌ Не удалось сгенерировать QR-код", 
                    reply_to=event.message_id if not event.from_me else None)
                
        except Exception as e:
            log(f"Ошибка генерации QR: {e}", "ERROR")
            self.bot.send_message(event.peer_id, "❌ Ошибка при генерации QR-кода", 
                reply_to=event.message_id if not event.from_me else None)