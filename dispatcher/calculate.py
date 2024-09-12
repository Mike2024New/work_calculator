from helpers import count_elements
from dispatcher.base_loader import Moduls
from dispatcher.temporary import test_moduls # подключение базы данных (пока что тестовый Json, потом будет модель)

manager_moduls = Moduls(moduls=test_moduls) # добавляем коннект с БД (пока временно json из temporary)

class Calculate:
    def __init__(self,names,moduls,options) -> None:
        """
        Принимает данные из сессии:
        names - общие параметры расчёта: название проекта, цвет ЛДСП, цвет Метала, скидка
        moduls - принимает список комплектующих введенных пользователем в форму
        options - опциональные коплектующие (мониторы, блоки розеток, rj45)
        """
        # инициализация
        self._names = names
        self._get_moduls = moduls
        self._options = options
        self.output = {"project":self._names,"moduls":[],"options":[],"all_price":[]} # выходные параметры
        # вычисляемые параметры (для сессии moduls)
        self._moduls = []
        self._screen = []
        self._schine = []
        # расчёт
        self._extract_moduls() # извлечение экранов и модулей
        # self._add_moduls() # добавление модулей (столов модульных)
        self._add_screen() # добавление экранов
        self._add_options() # добавление опциональных комплектующих
        self._caunt_duplicate() # подсчёт дублей
        self._get_detal_by_art() # загрузка изделий по артикулам


    def _extract_moduls(self):
        # print("="*50)
        # print(self._get_moduls)
        # print("="*50)
        for row in self._get_moduls:
            modul_category = None
            modul_len = None # ключ для подбора длины экранов и шины монтажной
            for key in row:
                if key == "modul":
                    add_dict_modul = {
                        "header":row[key]['name'], 
                        "modul": f"{row[key]['art']} {row[key]['name']}{row[key]['art']}. С/с: {row[key]['price']} руб./шт.", 
                        "screen": False, 
                        "schine":False, 
                        "table":None}
                    self._moduls.append(add_dict_modul)
                    modul_len = int(row[key]['lens']) # ключ для подбора длины экранов и шины монтажной
                    modul_category = row[key]['category'] # получить категорию модуля (для сортировки шин и экранов)
                if key == "screen":
                    self._screen.append((int(row[key]), modul_len,modul_category)) # 1 - высота экрана 2 - длина экрана
                if key == "schine":
                    self._schine.append((row[key], modul_len,modul_category)) # 1 - наличие шины true/false 2 - длина экрана


    def _add_screen(self):
        """ПОИСК ЭКРАНОВ В МОДЕЛИ И ДОБАВЛЕНИЕ ИХ В МОДУЛИ"""
        for i in range(len(self._screen)):
            if int(self._screen[i][0])!=0: # ЕСЛИ ВЫСОТА ЭКРАНА НЕ РАВНА 0, ТО ЕСТЬ ЭКРАН ПРИСУТСТВУЕТ
                lens = self._screen[i][1] # ИЗВЛЕКАЕМ ДЛИНУ ЭКРАНА
                category = self._screen[i][-1].replace('modul','screen') # ТАК КАК КАТЕГОРИИ МОДУЛЕЙ И ЭКРАНОВ ОТЛИЧАЮТСЯ ВСЕГО 1 СЛОВОМ, ПРОСТО МЕНЯЕМ ЕГО И ПОЛУЧАЕМ НУЖНЫЙ ТИП КАТЕГОРИИ
                category = f"{category}_{self._screen[i][0]}" # ДОБАВЛЯЕМ ВЫСОТУ САМОГО ЭКРАНА
                self._moduls[i]['screen'] = manager_moduls.get_art_component_by_category_and_lens(category,lens) # ПОЛУЧАЕМ ИСКОМЫЙ ТОВАР В БД




        print('='*50)
        print(self._moduls)
        print('='*50)

        print('='*50)
        print(self._screen)
        print('='*50)

        print('='*50)
        print(self._schine)
        print('='*50)


    def _add_options(self):
        """добавление мониторов и кронштейнов"""
        if self._options['monitor_type_1']>0: # тип 1 -> 1 монитор на низкой стойке
            for _  in range(self._options['monitor_type_1']):
                self.output['options'].append('ФЛ-1721')
                self.output['options'].append('ФЛ-1715.45')

        if self._options['monitor_type_2']>0: # тип 2 -> 2 монитора на высокой стойке
            for _  in range(self._options['monitor_type_2']):
                [self.output['options'].append('ФЛ-1721') for _ in range(2)] # кронштейны в таком образом добавляются 2 раза
                self.output['options'].append('ФЛ-1715.85')

        if self._options['monitor_type_3']>0: # тип 3 -> 1 монитор на высокой стойке
            for _  in range(self._options['monitor_type_1']):
                self.output['options'].append('ФЛ-1721')
                self.output['options'].append('ФЛ-1715.85')

        if self._options['electric_power']>0: # добавить блок розеток
            for _  in range(self._options['electric_power']):
                self.output['options'].append('ФЛ-1731') # добавить блоки розеток
            self.output['options'].append('ФЛ-1733') # добавить шину заземления

        
        if self._options['electric_rj45']>0: # добавить блок розеток
            for _  in range(self._options['electric_rj45']):
                self.output['options'].append('ФЛ-1732')

    def _caunt_duplicate(self):
        """удалить дубликаты подсчитав кол-во совпадающих модулей"""
        self.output["options"] = count_elements(self.output["options"])

    def _get_detal_by_art(self):
        for i in range(len(self.output["options"])):
            modul = manager_moduls.get_one_modul_by_art(self.output["options"][i][0]) # получение изделия по артикулу
            count = self.output["options"][i][1] # количество изделий
            self.output["options"][i] = (modul,count)