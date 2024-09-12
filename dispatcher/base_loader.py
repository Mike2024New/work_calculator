from dispatcher.temporary import test_moduls # подключение базы данных (пока что тестовый Json, потом будет модель)
import re

class Moduls:
    """этот класс работает с комплектующими 
    позже вынести в отдельный модуль
    """
    def __init__(self,moduls) -> None:
        self.moduls = moduls

    @staticmethod
    def extract_art(string:str,one_components)->str:
        """
        извлечение артикула из входных параметров заполненных полей (для динамических модулей (Стол/Экран/Шина))
        string -> строка в которой нужно найти артикул
        one_components -> True артикул состоит из 1 компонента например ФЛ-1001 / False арт состоит из двух компонентов ФЛ-1530.85
        возвращает извлеченный артикул
        """
        if one_components:
            return re.search(r"(?P<art>ФЛ-\d{4})",string)['art']
        return re.search(r"(?P<art>ФЛ-\d{4}.\d{2})",string)['art']
    
    def get_one_modul_by_art(self, art:str)->dict:
        """получение модуля по артикулу"""
        return [row for row in test_moduls if art == row["art"]][0]
    
    def get_art_component_by_category_and_lens(self, category, lens)->dict:
        """
        получение компонента по категории и длине
        """
        print(f"Ищем совпадение: category={category}|lens={lens}")
        for row in test_moduls:
            if row["category"]==category and row["lens"]==lens:
                return row["art"]
    
    def get_moduls_by_category(self,keys_in:tuple,is_contains=True)->list:
        """
        получение модулей из модели (пока что из тестового словаря в модуле temporary.py, позже будут запросы к модели)
        keys_in -> список категорий по которым нужно извлечь значения (если содержи то извлечь)
        is_contais -> инверсия, берем те элементы которые не содержат в категории значения из keys_in
        """
        if is_contains:
            return [row for row in test_moduls if row['category'] in keys_in]
        return [row for row in test_moduls if row['category'] not in keys_in]
    
if __name__=="__main__":
    print(123)