# Обновить названия тегов на русские (для БД, где 0003 уже применялась с fallback на английский)

from django.db import migrations

# Полный список slug -> русское название (дублируем из 0003 для независимости миграции)
TAG_NAMES_RU = {
    "museum": "Музей", "gallery": "Галерея", "theater": "Театр", "cinema": "Кинотеатр",
    "concert_hall": "Концертный зал", "library": "Библиотека", "church": "Храм",
    "cathedral": "Собор", "mosque": "Мечеть", "temple": "Святилище", "monastery": "Монастырь",
    "castle": "Замок", "fortress": "Крепость", "palace": "Дворец", "manor": "Усадьба",
    "monument": "Памятник", "memorial": "Мемориал", "statue": "Скульптура", "park": "Парк",
    "garden": "Сад", "square": "Площадь", "street": "Улица", "market": "Рынок", "bazaar": "Базар",
    "shopping_mall": "Торговый центр", "cafe": "Кафе", "restaurant": "Ресторан", "bar": "Бар",
    "brewery": "Пивоварня", "winery": "Винодельня", "hotel": "Отель", "hostel": "Хостел",
    "viewpoint": "Смотровая площадка", "bridge": "Мост", "fountain": "Фонтан", "beach": "Пляж",
    "lake": "Озеро", "river": "Река", "mountain": "Гора", "forest": "Лес",
    "nature_reserve": "Заповедник", "zoo": "Зоопарк", "aquarium": "Аквариум",
    "amusement_park": "Парк развлечений", "stadium": "Стадион", "sports_complex": "Спортивный комплекс",
    "bathhouse": "Баня", "spa": "Спа", "walking": "Прогулка", "hiking": "Поход", "cycling": "Велосипед",
    "photography": "Фотографии", "sightseeing": "Осмотр достопримечательностей", "shopping": "Шопинг",
    "dining": "Еда", "nightlife": "Ночная жизнь", "entertainment": "Развлечения", "education": "Образование",
    "workshop": "Мастер-класс", "guided_tour": "Экскурсия", "swimming": "Плавание", "boating": "Катание на лодке",
    "fishing": "Рыбалка", "picnic": "Пикник", "camping": "Кемпинг", "climbing": "Скалолазание",
    "skiing": "Лыжи", "skating": "Катание на коньках", "birdwatching": "Наблюдение за птицами",
    "stargazing": "Наблюдение за звёздами", "meditation": "Медитация", "yoga": "Йога",
    "family": "Семья", "kids": "Дети", "couples": "Пары", "romantic": "Романтика",
    "solo_traveler": "Соло-путешественник", "groups": "Группы", "elderly": "Пожилые", "students": "Студенты",
    "business_traveler": "Бизнес-путешественник", "indoor": "В помещении", "outdoor": "На улице",
    "covered": "Под навесом", "open_air": "На открытом воздухе", "audio_guide": "Аудиогид",
    "interactive": "Интерактивно", "hands_on": "Можно трогать", "exhibition": "Выставка",
    "permanent_collection": "Постоянная экспозиция", "temporary_exhibition": "Временная выставка",
    "free_entry": "Бесплатный вход", "paid_entry": "Платный вход", "donation_based": "За пожертвование",
    "reservation_required": "По записи", "no_reservation": "Без записи", "parking": "Парковка",
    "public_transport": "Общественный транспорт", "wifi": "Wi-Fi", "restroom": "Туалет",
    "food_available": "Есть еда", "gift_shop": "Сувенирный магазин",
    "wheelchair_accessible": "Доступно для колясок", "pet_friendly": "Можно с животными",
    "family_restroom": "Семейная комната", "changing_table": "Пеленальный столик", "elevator": "Лифт",
    "stairs_only": "Только лестница", "historic": "Историческое", "modern": "Современное",
    "traditional": "Традиционное", "contemporary": "Современное", "artistic": "Артистичное",
    "cultural": "Культура", "religious": "Религиозное", "scientific": "Научное", "industrial": "Индустриальное",
    "architectural": "Архитектурное", "quiet": "Тихое", "lively": "Оживлённое", "crowded": "Многолюдно",
    "secluded": "Уединённое", "instagrammable": "Инстаграмное", "local_favorite": "Любимое местными",
    "tourist_trap": "Туристическая ловушка", "hidden_gem": "Секретное место", "morning": "Утро",
    "afternoon": "День", "evening": "Вечер", "night": "Ночь", "year_round": "Круглый год",
    "seasonal": "Сезонный", "summer": "Лето", "winter": "Зима", "spring": "Весна", "autumn": "Осень",
    "sunset_spot": "На закат", "sunrise_spot": "На рассвет", "free": "Бесплатно", "budget": "Бюджетно",
    "mid_range": "Средний ценник", "premium": "Премиум", "quick_visit": "До 30 мин", "short_visit": "30–60 мин",
    "medium_visit": "1–2 часа", "long_visit": "2+ часа", "full_day": "Целый день", "history": "История",
    "art": "Искусство", "science": "Наука", "nature": "Природа", "food": "Еда", "crafts": "Ремёсла",
    "military": "Военная тематика", "literature": "Литература", "music": "Музыка", "folklore": "Фольклор",
    "urban": "Городское", "rural": "Сельское",
}


def update_tag_names_ru(apps, schema_editor):
    Tag = apps.get_model("places", "Tag")
    for slug, name in TAG_NAMES_RU.items():
        Tag.objects.filter(slug=slug).update(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ("places", "0003_initial_tags"),
    ]

    operations = [
        migrations.RunPython(update_tag_names_ru, migrations.RunPython.noop),
    ]
