"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ANIME ART MODULE v4.0                                ║
║                    Модуль для работы с VK группами                           ║
║                    Берём арты из VK сообществ                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import random
from typing import Optional, List, Dict


class AnimeAPI:
    
    def __init__(self):
        self.nsfw_mode = False

        self.sfw_groups = [
            -89528768,
            -210485938,

        ]
        
        self.nsfw_groups = [
            -101072212
        ]
        
        # Категории для совместимости
        self.sfw_categories = [
            'waifu', 'neko', 'shinobu', 'megumin', 'bully', 'cuddle', 
            'cry', 'hug', 'awoo', 'kiss', 'lick', 'pat', 'smug', 'bonk',
            'yeet', 'blush', 'smile', 'wave', 'highfive', 'handhold',
            'nom', 'bite', 'glomp', 'slap', 'kill', 'kick', 'happy',
            'wink', 'poke', 'dance', 'cringe'
        ]
        
        self.nsfw_categories = [
            'waifu', 'neko', 'trap', 'blowjob'
        ]
        
        # Русские названия
        self.category_names_ru = {
            'waifu': 'Вайфу',
            'neko': 'Неко (кошкодевочка)',
            'shinobu': 'Шинобу',
            'megumin': 'Мегумин',
            'bully': 'Задирание',
            'cuddle': 'Обнимашки',
            'cry': 'Плач',
            'hug': 'Объятия',
            'awoo': 'Волчий вой',
            'kiss': 'Поцелуй',
            'lick': 'Лизнуть',
            'pat': 'Погладить',
            'smug': 'Самодовольный',
            'bonk': 'Удар',
            'yeet': 'Бросок',
            'blush': 'Смущение',
            'smile': 'Улыбка',
            'wave': 'Помахать',
            'highfive': 'Дай пять',
            'handhold': 'Держаться за руки',
            'nom': 'Есть',
            'bite': 'Укусить',
            'glomp': 'Прыжок на шею',
            'slap': 'Пощечина',
            'kill': 'Убить',
            'kick': 'Пинок',
            'happy': 'Счастье',
            'wink': 'Подмигнуть',
            'poke': 'Ткнуть',
            'dance': 'Танец',
            'cringe': 'Кринж',
            'trap': 'Трап (18+)',
            'blowjob': 'Минет (18+)'
        }

    def set_nsfw_mode(self, enabled: bool):
        """Установить режим 18+"""
        self.nsfw_mode = enabled

    def get_random_group(self) -> int:
        """Получить случайную группу в зависимости от режима"""
        groups = self.nsfw_groups if self.nsfw_mode else self.sfw_groups
        if not groups:
            raise ValueError("Не добавлены группы! Добавьте ID групп в anime.py")
        return random.choice(groups)

    def get_random_attachment(self, vk_api) -> Optional[str]:
        """
        Получить случайное фото из VK групп
        
        Args:
            vk_api: Экземпляр VK API
        
        Returns:
            Строка в формате "photo-owner_id_photo_id" или None
        """
        try:
            group_id = self.get_random_group()
            
            # Получаем записи со стены группы
            wall = vk_api.wall.get(
                owner_id=group_id,
                count=50,  # Получаем последние 50 записей
                filter='owner'
            )
            
            # Собираем все фото из записей
            photos = []
            for post in wall['items']:
                if 'attachments' in post:
                    for attach in post['attachments']:
                        if attach['type'] == 'photo':
                            photo = attach['photo']
                            photos.append({
                                'owner_id': photo['owner_id'],
                                'id': photo['id'],
                                'access_key': photo.get('access_key', '')
                            })
            
            if not photos:
                return None
            
            # Выбираем случайное фото
            selected = random.choice(photos)
            
            # Формируем строку для вложения
            if selected['access_key']:
                return f"photo{selected['owner_id']}_{selected['id']}_{selected['access_key']}"
            else:
                return f"photo{selected['owner_id']}_{selected['id']}"
                
        except Exception as e:
            print(f"Ошибка при получении фото из группы: {e}")
            return None

    def get_random_any(self) -> Optional[str]:
        """Получить случайное изображение (для совместимости)"""
        return None  # Теперь используем get_random_attachment

    def get_categories(self) -> Dict[str, List[str]]:
        """Получить список доступных категорий"""
        return {
            'sfw': self.sfw_categories,
            'nsfw': self.nsfw_categories
        }

    def get_category_name_ru(self, category: str) -> str:
        """Получить русское название категории"""
        return self.category_names_ru.get(category, category.capitalize())

    def get_available_categories_text(self) -> str:
        """Получить текст со списком доступных категорий"""
        if self.nsfw_mode:
            categories = self.nsfw_categories
            mode_text = "🔞 18+ РЕЖИМ ВКЛЮЧЕН"
        else:
            categories = self.sfw_categories
            mode_text = "👶 ОБЫЧНЫЙ РЕЖИМ"
        
        lines = [f"🎨 {mode_text}\n"]
        
        # Группируем по 4 в строку
        row = []
        for i, cat in enumerate(categories, 1):
            row.append(f"• {cat}")
            if i % 4 == 0:
                lines.append("   ".join(row))
                row = []
        
        if row:
            lines.append("   ".join(row))
        
        return "\n".join(lines)

    def get_info_text(self) -> str:
        """Получить информационное сообщение"""
        sfw_count = len(self.sfw_groups)
        nsfw_count = len(self.nsfw_groups)
        
        return f"""📊 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗦𝗜𝗬𝗔 𝗢 𝗕𝗢𝗧𝗘

📂 Групп с SFW артами: {sfw_count}
🔞 Групп с NSFW артами: {nsfw_count}

🎯 Бот берёт случайные арты из этих групп!

🔧 Управление режимом:
!аниме nsfw - включить 18+ режим
!аниме sfw - выключить 18+ режим

💡 Примеры:
!аниме - случайный арт
!аниме waifu - арт вайфу
!аниме neko - арт неко"""


# ==================== ТЕСТ ====================
if __name__ == "__main__":
    print("🧪 Тестирование модуля anime...")
    api = AnimeAPI()
    
    print(f"✅ SFW групп: {len(api.sfw_groups)}")
    print(f"✅ NSFW групп: {len(api.nsfw_groups)}")
    print(f"✅ Категорий: {len(api.sfw_categories)}")