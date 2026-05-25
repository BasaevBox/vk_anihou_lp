"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ANIME ART MODULE v4.0                                ║
║                    Модуль для работы с VK группами                           ║
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
            -80977142,
            -185445058,

        ]
        
        self.nsfw_groups = [
            -101072212,
            -209432422,
        ]
        
        self.sfw_categories = [
            'low',
        ]
        
        self.nsfw_categories = [
            'loli',
        ]
        
        self.category_names_ru = {
            'low': 'обычный',
            'loli': 'лоли',
        }

    def set_nsfw_mode(self, enabled: bool):
        self.nsfw_mode = enabled

    def get_random_group(self) -> int:
        groups = self.nsfw_groups if self.nsfw_mode else self.sfw_groups
        if not groups:
            raise ValueError("Не добавлены группы! Добавьте ID групп в anime.py")
        return random.choice(groups)

    def get_random_attachment(self, vk_api) -> Optional[str]:
        try:
            group_id = self.get_random_group()
            
            wall = vk_api.wall.get(
                owner_id=group_id,
                count=999,
                filter='owner'
            )
            
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
            
            selected = random.choice(photos)
            
            if selected['access_key']:
                return f"photo{selected['owner_id']}_{selected['id']}_{selected['access_key']}"
            else:
                return f"photo{selected['owner_id']}_{selected['id']}"
                
        except Exception as e:
            print(f"Ошибка при получении фото из группы: {e}")
            return None

    def get_random_any(self) -> Optional[str]:
        return None  

    def get_categories(self) -> Dict[str, List[str]]:
        return {
            'лоу': self.sfw_categories,
            'лоли': self.nsfw_categories
        }

    def get_category_name_ru(self, category: str) -> str:
        return self.category_names_ru.get(category, category.capitalize())

    def get_available_categories_text(self) -> str:
        if self.nsfw_mode:
            categories = self.nsfw_categories
            mode_text = "🔞 ЛОЛИ РЕЖИМ ВКЛЮЧЕН"
        else:
            categories = self.sfw_categories
            mode_text = "👶 ОБЫЧНЫЙ РЕЖИМ"
        
        lines = [f"🎨 {mode_text}\n"]
        
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

if __name__ == "__main__":
    print("🧪 Тестирование модуля anime...")
    api = AnimeAPI()
    
    print(f"✅ SFW групп: {len(api.sfw_groups)}")
    print(f"✅ NSFW групп: {len(api.nsfw_groups)}")
    print(f"✅ Категорий: {len(api.sfw_categories)}")
