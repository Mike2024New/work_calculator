"""
Для упрощения разработки, этот файл временно имитирует БД и модели
в целях соблюдения коммерческой тайны, цены изменены на выдуманные
"""

test_moduls = [
    # ОДИНОЧНЫЕ СТОЛЫ:
    {"art": "ФЛ-1001", "name": "стол для диспетчера 80х100х76 см, RAL7047", "price": 0, "category": "modul_single",
     "url_image": "https://www.unitex.ru/images/dispetch/stoly/ФЛ-1001.jpg", "lens":80, "for_select":"ФЛ-1001 стол для диспетчера 80х100х76 см, RAL7047"},

    {"art": "ФЛ-1002", "name": "стол для диспетчера 100х100х76 см, RAL7047", "price": 0, "category": "modul_single",
     "url_image": "https://www.unitex.ru/images/dispetch/stoly/ФЛ-1002.jpg", "lens":100, "for_select":"ФЛ-1002 стол для диспетчера 100х100х76 см, RAL7047"},

    {"art": "ФЛ-1003", "name": "стол для диспетчера 120х100х76 см, RAL7047", "price": 0, "category": "modul_single",
     "url_image": "https://www.unitex.ru/images/dispetch/stoly/ФЛ-1003.jpg", "lens":120, "for_select":"ФЛ-1003 стол для диспетчера 120х100х76 см, RAL7047"},


    # СТОЛ ПРАВЫЙ:
    {"art": "ФЛ-1101", "name": "Модуль стола для диспетчера левый 60х100х76 см, RAL7047", "price": 0, "category": "modul_left",
     "url_image": "https://www.unitex.ru/images/dispetch/stoly/ФЛ-1101-ФЛ-1102-л.jpg", "lens":60},


    # СТОЛ ЛЕВЫЙ:
    {"art": "ФЛ-1102", "name": "Модуль стола для диспетчера правый 60х100х76 см, RAL7047", "price": 0, "category": "modul_right",
    "url_image": "https://www.unitex.ru/images/dispetch/stoly/%D0%A4%D0%9B-1101-%D0%A4%D0%9B-1102-%D0%BF.jpg", "lens":60},


    # СТОЛ ПРОМЕЖУТОЧНЫЙ: // В ПРАЙСЕ НЕ УКАЗАНО СЛОВО ПРОМЕЖУТОЧНЫЙ, НУЖНО ДОБАВЛЯТЬ ПРОГРАММНО В МОДУЛЕ PRICE
    {"art": "ФЛ-1151", "name": "Модуль стола для диспетчера промежуточный 100х100х76 см, RAL7047", "price": 0, "category": "modul_center",
    "url_image": "https://www.unitex.ru/images/dispetch/stoly/%D0%A4%D0%9B-1151.jpg", "lens":60},

]


def get_simple_modul():
    return [row for row in test_moduls if "simple_modul" == row["category"]]