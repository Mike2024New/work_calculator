import re
"""
ЗАДАЧА ЭТОГО МОДУЛЯ: ОБЕСПЕЧЕНИЕ ИЗВЛЕЧЕНИЯ ДАННЫХ ИЗ СТРОК ЗАГРУЖЕННЫХ ПОЛЬЗОВАТЕЛЕМ В ПРАЙС-ЛИСТ, И КОНТРОЛЬ ТОГО, 
ЧТОБЫ ПОЛЬЗОВАТЕЛЬ НЕ ВВЕЛ НЕ ПРАВИЛЬНЫХ АРТИКУЛОВ.
ПОЗЖЕ БУДЕТ ДОРАБОТКА И ПОЛЬЗОВАТЕЛЬ СМОЖЕТ ДОБАВЛЯТЬ РАЗРЕШЕННЫЕ АРТИКУЛЫ
"""

patterns_dict = {
    "table": {  # шаблоны для обработки столов и модулей диспетчера
        "arts": {
            'modul_single': r"ФЛ-([1][0][0][1-8])",
            'modul_left': r"ФЛ-([1][1][0-3][13579])",
            'modul_right': r"ФЛ-([1][1][0-3][02468])",
            'modul_center': r"ФЛ-([1][1][5-6][0-9])",
            'modul_22_left': r"ФЛ-1141",
            'modul_22_right': r"ФЛ-1142",
            'modul_22_center': r"ФЛ-1171",
            'modul_angle_90': r"ФЛ-1170"
        },
        "extract_data": {
            "name": r"ФЛ-\d{4}\s(?P<name>.+?)\s\d{1,3}\s\d{3}",
            "data": r"(?P<art>ФЛ-\d{4}).+?\s(?P<lens>\d{2,3})[хxX*]100[хxX*]76.+?(?P<price>\d{1,3}\s\d{3})\s\D"
        }
    },

    "screen": {  # шаблоны для обработки экранов
        "arts": {

        },
        "extract_data": {
            "name": "",
            "data": "",
        }
    }
}


class ExtractComponent:

    @staticmethod
    def extract_data_from_row(string: str, category: str) -> dict:
        """
        извлекает значения из строки компонента: артикулы, длину, прайс, name.
        Работает с шаблонами из коллекции patterns_dict

        :param string: строка с компонентом
        :param category: категория товара
        :return: коллекция типа: {'art': '...', 'lens': 0, 'price': 0, 'name': '...', 'url_image': '',
         'category': '...'}
        """
        match_data = None
        match_name = None
        if re.search(patterns_dict["table"]["extract_data"]["data"], string):
            match_data = re.search(patterns_dict["table"]["extract_data"]["data"], string)
        if re.search(patterns_dict["table"]["extract_data"]["name"], string):
            match_name = re.search(patterns_dict["table"]["extract_data"]["name"], string)
        if not match_data or not match_name:
            raise Exception("не найдено совпадений")
        lens = int(match_data["lens"])
        price = int(match_data["price"].replace(" ", ""))
        return {
            "art": match_data["art"], "lens": lens, "price": price,
            "name": match_name["name"], "url_image": "", "category": category
        }

    @classmethod
    def extract_table(cls, components) -> list:
        """
        принимает на вход список изделий столы, проверяет совпадение с артикулами из словаря patterns_list
        за тем отправляет строки на извлечение в случае корректности введенных данных

        :param components: список строк с компонентами (обычно полученными из поля прайс введенные пользователем)
        :return: массив словарей типа: {'art': '...', 'lens': 0, 'price': 0, 'name': '...', 'url_image': '',
         'category': '...'}
        Данные готовы для записи в БД, чуть позже добавить обработчик для модулей, который будет получать картинки
        модулей с сайта
        """
        output_list = []
        for row in components:
            for key in patterns_dict["table"]["arts"]:
                if re.search(patterns_dict["table"]["arts"][key], row):
                    try:
                        output_list.append(cls.extract_data_from_row(string=row, category=key))
                        break
                    except Exception as err:
                        output_list.append({"error": "строка не добавлена", "row": row})
                        print(f"Строка {row} не обработана, {err}")
                        break
        return output_list

    @classmethod
    def extract_screen(cls):
        """извлечение экранов"""
        pass


if __name__ == '__main__':
    pass
    # res = ExtractComponent.extract_table(data)
    # print(res)