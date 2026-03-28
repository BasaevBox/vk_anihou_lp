"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         YOUTUBE MODULE                                       ║
║                    Модуль для скачивания видео с YouTube                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import os
import re
import time
import threading
from typing import TYPE_CHECKING, Optional, Tuple
from datetime import datetime
from utils import log

try:
    from yt_dlp import YoutubeDL
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    log("yt-dlp не установлен. Установите: pip install yt-dlp", "ERROR")

if TYPE_CHECKING:
    from bot import VKBot


class YouTubeModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
        self.download_folder = "downloads"
        self.downloading = {}  # Словарь для отслеживания загрузок: {peer_id: bool}
        
        # Создаем папку для загрузок если её нет
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
        
        # Очищаем старые файлы при запуске
        self.clean_old_files()
    
    def register_commands(self):
        self.bot.commands["видео"] = self.cmd_video
        self.bot.commands["youtube"] = self.cmd_video
        self.bot.commands["ютуб"] = self.cmd_video
    
    def clean_old_files(self, max_age_hours: int = 24):
        """Очищает старые загруженные файлы"""
        try:
            current_time = time.time()
            for filename in os.listdir(self.download_folder):
                filepath = os.path.join(self.download_folder, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age_hours * 3600:
                        os.remove(filepath)
                        log(f"Удален старый файл: {filename}", "INFO")
        except Exception as e:
            log(f"Ошибка очистки файлов: {e}", "ERROR")
    
    def validate_youtube_url(self, url: str) -> bool:
        """Проверяет, является ли ссылка ссылкой на YouTube"""
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/',
            r'(https?://)?(m\.)?(youtube\.com|youtu\.be)/',
            r'(https?://)?(music\.youtube\.com)/',
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Извлекает ID видео из ссылки YouTube"""
        patterns = [
            r'youtube\.com/watch\?v=([^&]+)',
            r'youtu\.be/([^?]+)',
            r'youtube\.com/embed/([^?]+)',
            r'youtube\.com/v/([^?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_info(self, url: str) -> Optional[dict]:
        """Получает информацию о видео без скачивания"""
        if not YTDLP_AVAILABLE:
            return None
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Без названия'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Неизвестен'),
                    'views': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:200],
                }
        except Exception as e:
            log(f"Ошибка получения информации о видео: {e}", "ERROR")
            return None
    
    def format_duration(self, seconds: int) -> str:
        """Форматирует длительность в читаемый вид"""
        if seconds <= 0:
            return "Неизвестно"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}ч {minutes}м {secs}с"
        elif minutes > 0:
            return f"{minutes}м {secs}с"
        else:
            return f"{secs}с"
    
    def format_size(self, size_bytes: int) -> str:
        """Форматирует размер файла в читаемый вид"""
        if size_bytes <= 0:
            return "Неизвестно"
        
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} ТБ"
    
    def download_video(self, url: str, peer_id: int, message_id: int) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Скачивает видео с YouTube
        
        Returns:
            (success, filepath, error_message)
        """
        if not YTDLP_AVAILABLE:
            return False, None, "yt-dlp не установлен. Установите: pip install yt-dlp"
        
        # Генерируем уникальное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_id = self.extract_video_id(url) or "video"
        filename = f"youtube_{video_id}_{timestamp}.mp4"
        filepath = os.path.join(self.download_folder, filename)
        
        ydl_opts = {
            'format': 'best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best',
            'outtmpl': filepath,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'restrictfilenames': True,
            'noplaylist': True,
            'geo_bypass': True,
        }
        
        try:
            # Отправляем уведомление о начале загрузки
            self.bot.send_message(peer_id, 
                "📥 𝗡𝗔𝗖𝗛𝗔𝗟𝗢 𝗭𝗔𝗚𝗥𝗨𝗭𝗞𝗜...\n\n"
                "⏳ Пожалуйста, подождите. Видео может быть большим!\n"
                "💡 Это может занять несколько минут.",
                reply_to=message_id)
            
            with YoutubeDL(ydl_opts) as ydl:
                # Скачиваем видео
                info = ydl.extract_info(url, download=True)
                
                # Проверяем размер файла
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    max_size = 200 * 1024 * 1024  # 200 МБ (ограничение VK)
                    
                    if file_size > max_size:
                        os.remove(filepath)
                        return False, None, f"Видео слишком большое ({self.format_size(file_size)}). Максимум: 200 МБ"
                    
                    return True, filepath, None
                else:
                    return False, None, "Файл не был создан"
                    
        except Exception as e:
            error_msg = str(e)
            if "Video unavailable" in error_msg:
                error_msg = "Видео недоступно (возможно, приватное или удалено)"
            elif "Private video" in error_msg:
                error_msg = "Это приватное видео"
            elif "Copyright" in error_msg:
                error_msg = "Видео защищено авторскими правами"
            
            log(f"Ошибка скачивания видео: {e}", "ERROR")
            return False, None, error_msg
    
    def upload_video_to_vk(self, peer_id: int, filepath: str, title: str) -> Optional[str]:
        """Загружает видео в VK"""
        try:
            # Получаем сервер для загрузки
            upload_server = self.bot.vk.video.getUploadServer()
            upload_url = upload_server['upload_url']
            
            # Загружаем видео
            with open(filepath, 'rb') as f:
                files = {'video_file': f}
                response = self.bot.vk_session.http.post(upload_url, files=files)
                upload_data = response.json()
            
            # Сохраняем видео
            if 'video_id' in upload_data:
                saved_video = self.bot.vk.video.save(
                    video_id=upload_data['video_id'],
                    owner_id=upload_data['owner_id'],
                    name=title[:100]  # Ограничение длины названия
                )
                
                if saved_video:
                    video_owner_id = saved_video['owner_id']
                    video_id = saved_video['id']
                    return f"video{video_owner_id}_{video_id}"
            
            return None
            
        except Exception as e:
            log(f"Ошибка загрузки видео в VK: {e}", "ERROR")
            return None
    
    def cmd_video(self, event, args):
        """Обработка команды !видео"""
        if not YTDLP_AVAILABLE:
            self.bot.send_message(event.peer_id, 
                "❌ Модуль yt-dlp не установлен!\n"
                "📦 Установите: pip install yt-dlp",
                reply_to=event.message_id if not event.from_me else None)
            return
        
        if not args:
            self.bot.send_message(event.peer_id, 
                "❌ 𝗜𝗦𝗣𝗢𝗟𝗡𝗭𝗢𝗩𝗔𝗡𝗜𝗘:\n"
                "!видео [ссылка на YouTube]\n\n"
                "📝 𝗣𝗥𝗜𝗠𝗘𝗥:\n"
                "!видео https://youtu.be/dQw4w9WgXcQ\n"
                "!видео https://www.youtube.com/watch?v=...",
                reply_to=event.message_id if not event.from_me else None)
            return
        
        url = args[0]
        
        # Проверяем, что ссылка на YouTube
        if not self.validate_youtube_url(url):
            self.bot.send_message(event.peer_id, 
                "❌ Пожалуйста, введите корректную ссылку на YouTube!\n"
                "📎 Примеры: https://youtu.be/... или https://www.youtube.com/watch?v=...",
                reply_to=event.message_id if not event.from_me else None)
            return
        
        # Проверяем, не идет ли уже загрузка в этом чате
        if self.downloading.get(event.peer_id, False):
            self.bot.send_message(event.peer_id, 
                "⏳ Загрузка видео уже выполняется!\n"
                "💡 Пожалуйста, подождите завершения текущей загрузки.",
                reply_to=event.message_id if not event.from_me else None)
            return
        
        # Запускаем загрузку в отдельном потоке
        self.downloading[event.peer_id] = True
        
        def download_and_send():
            try:
                # Получаем информацию о видео
                video_info = self.get_video_info(url)
                
                if video_info:
                    title = video_info['title']
                    duration = self.format_duration(video_info['duration'])
                    uploader = video_info['uploader']
                    views = f"{video_info['views']:,}" if video_info['views'] else "Неизвестно"
                    
                    # Отправляем информацию о видео
                    info_msg = f"""📹 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗦𝗜𝗬𝗔 𝗢 𝗩𝗜𝗗𝗘𝗢:

🎬 Название: {title}
⏱ Длительность: {duration}
👤 Автор: {uploader}
👁 Просмотров: {views}

📥 Начинаю скачивание..."""
                    
                    self.bot.send_message(event.peer_id, info_msg,
                        reply_to=event.message_id if not event.from_me else None)
                
                # Скачиваем видео
                success, filepath, error = self.download_video(url, event.peer_id, event.message_id)
                
                if not success:
                    self.bot.send_message(event.peer_id, 
                        f"❌ 𝗢𝗦𝗛𝗜𝗕𝗞𝗔 𝗭𝗔𝗚𝗥𝗨𝗭𝗞𝗜:\n\n{error}",
                        reply_to=event.message_id if not event.from_me else None)
                    return
                
                # Получаем информацию о файле
                file_size = os.path.getsize(filepath)
                size_str = self.format_size(file_size)
                
                # Отправляем уведомление о загрузке видео
                self.bot.send_message(event.peer_id, 
                    f"📤 𝗭𝗔𝗚𝗥𝗨𝗭𝗞𝗔 𝗭𝗔𝗩𝗘𝗥𝗦𝗛𝗘𝗡𝗔!\n\n"
                    f"📦 Размер: {size_str}\n"
                    f"⏫ Загружаю в VK...",
                    reply_to=event.message_id if not event.from_me else None)
                
                # Пытаемся загрузить видео в VK
                video_attachment = self.upload_video_to_vk(event.peer_id, filepath, video_info['title'] if video_info else "Видео")
                
                # Удаляем временный файл
                try:
                    os.remove(filepath)
                except:
                    pass
                
                if video_attachment:
                    self.bot.send_message(event.peer_id, 
                        f"✅ 𝗩𝗜𝗗𝗘𝗢 𝗨𝗦𝗣𝗘𝗦𝗛𝗡𝗢 𝗭𝗔𝗚𝗥𝗨𝗭𝗛𝗘𝗡𝗢!\n\n"
                        f"🎬 {video_info['title'] if video_info else 'Видео'}\n"
                        f"📦 Размер: {size_str}",
                        attachment=video_attachment,
                        reply_to=event.message_id if not event.from_me else None)
                else:
                    # Если не удалось загрузить в VK, отправляем как файл
                    try:
                        # Для отправки файла нужно использовать документы
                        upload_server = self.bot.vk.docs.getMessagesUploadServer(type='doc', peer_id=event.peer_id)
                        upload_url = upload_server['upload_url']
                        
                        with open(filepath, 'rb') as f:
                            files = {'file': f}
                            response = self.bot.vk_session.http.post(upload_url, files=files)
                            upload_data = response.json()
                        
                        if 'file' in upload_data:
                            saved_doc = self.bot.vk.docs.save(file=upload_data['file'], title=f"{video_info['title'][:50]}.mp4")
                            if saved_doc:
                                doc_owner_id = saved_doc[0]['owner_id']
                                doc_id = saved_doc[0]['id']
                                attachment = f"doc{doc_owner_id}_{doc_id}"
                                
                                self.bot.send_message(event.peer_id, 
                                    f"✅ 𝗩𝗜𝗗𝗘𝗢 𝗨𝗦𝗣𝗘𝗦𝗛𝗡𝗢 𝗭𝗔𝗚𝗥𝗨𝗭𝗛𝗘𝗡𝗢!\n\n"
                                    f"🎬 {video_info['title'] if video_info else 'Видео'}\n"
                                    f"📦 Размер: {size_str}\n"
                                    f"⚠️ Видео отправлено как документ (ограничения VK)",
                                    attachment=attachment,
                                    reply_to=event.message_id if not event.from_me else None)
                                return
                        
                        # Если не удалось отправить как документ, отправляем ссылку
                        self.bot.send_message(event.peer_id, 
                            f"✅ 𝗩𝗜𝗗𝗘𝗢 𝗨𝗦𝗣𝗘𝗦𝗛𝗡𝗢 𝗭𝗔𝗚𝗥𝗨𝗭𝗛𝗘𝗡𝗢!\n\n"
                            f"🎬 {video_info['title'] if video_info else 'Видео'}\n"
                            f"📦 Размер: {size_str}\n"
                            f"⚠️ Но не удалось отправить в VK из-за ограничений.\n"
                            f"📎 Оригинальная ссылка: {url}",
                            reply_to=event.message_id if not event.from_me else None)
                            
                    except Exception as e:
                        log(f"Ошибка отправки документа: {e}", "ERROR")
                        self.bot.send_message(event.peer_id, 
                            f"✅ 𝗩𝗜𝗗𝗘𝗢 𝗨𝗦𝗣𝗘𝗦𝗛𝗡𝗢 𝗭𝗔𝗚𝗥𝗨𝗭𝗛𝗘𝗡𝗢!\n\n"
                            f"🎬 {video_info['title'] if video_info else 'Видео'}\n"
                            f"📦 Размер: {size_str}\n"
                            f"⚠️ Но не удалось отправить в VK\n"
                            f"📎 Оригинальная ссылка: {url}",
                            reply_to=event.message_id if not event.from_me else None)
                
            except Exception as e:
                log(f"Ошибка в потоке загрузки видео: {e}", "ERROR")
                self.bot.send_message(event.peer_id, 
                    f"❌ 𝗢𝗦𝗛𝗜𝗕𝗞𝗔: {str(e)}",
                    reply_to=event.message_id if not event.from_me else None)
            finally:
                self.downloading[event.peer_id] = False
        
        # Запускаем загрузку в отдельном потоке
        thread = threading.Thread(target=download_and_send, daemon=True)
        thread.start()


# ==================== ТЕСТ ====================
if __name__ == "__main__":
    print("🧪 Тестирование модуля YouTube...")
    print(f"✅ yt-dlp доступен: {YTDLP_AVAILABLE}")