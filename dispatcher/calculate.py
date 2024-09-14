import re
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
        self.output = {"project":self._names,"moduls":[],"options":[],"all_price":0,"all_lens":0} # выходные параметры
        # вычисляемые параметры (для сессии moduls)
        self._moduls = []
        self._screen = []
        self._schine = []
        # расчёт модулей
        self._extract_moduls() # извлечение экранов и модулей // в этой же точке добавляются столы модульные и формируется объект модуль
        self._generate_name() # задать имя столу
        self._add_screen() # добавление экранов
        self._add_schine() # добавление шины монтажной
        self._add_table() # добавление столешниц из ЛДСП
        self.output['moduls'] = self._moduls # добавление модулей в выходную коллекцию
        # расчёт опций
        self._add_holder_screen() # добавление стоек экранов
        self._add_holder_modul() # добавить опоры промежуточные (ФЛ-1701)
        self._add_options() # добавление опциональных комплектующих
        self._caunt_duplicate() # подсчёт дублей
        self._get_detal_by_art() # загрузка изделий по артикулам
        self._left_right_ldsp() # добавить боковины из ЛДСП добавлять в самую последнюю очередь (это как в том видосе: вода льётся в душе, если на кухне открыть дверцу шкафа)
        self.output['all_price']=int(self.output['all_price'])
        self._show_parametrs_for_debug() # вывод результата в консоль


    # ИЗВЛЕЧЕНИЕ МОДУЛЕЙ, СОЗДАНИЕ НОВОГО ОБЪЕКТА МОДУЛЯ
    def _extract_moduls(self):
        """ИЗВЛЕЧЕНИЕ МОДУЛЕЙ, СОЗДАНИЕ НОВОГО ОБЪЕКТА МОДУЛЯ"""
        for row in self._get_moduls:
            modul_category = None
            modul_len = None # ключ для подбора длины экранов и шины монтажной
            for key in row:
                if key == "modul":
                    add_dict_modul = { # создание модуля
                        "header":self._modul_to_string(art=row[key]['art'],is_header=True), # преобразование имени модуля в заголовок модуля
                        "modul": self._modul_to_string(art=row[key]['art']), # конвертер модуля в строку
                        "screen": False, # экран
                        "schine":False, # шина монтажная
                        "table":None, # столешница
                        "price": int(self._discount(row[key]['price'])), # цена модуля (все комплектующие входящие в него) / добавляем сразу цену стола (экраны шины и столешн добавим дальше)
                        "img":row[key]['url_image'], # подгрузка картинки модуля
                        "lens":row[key]['lens'], # габарит по длине (для указания на схеме эскизе)
                        }
                    # print(f"$$$$output={self.output['all_price']} | + {row[key]['price']}")
                    self.output['all_price'] += self._discount(row[key]['price']) # добавить цену в итоговый подсчёт
                    self._moduls.append(add_dict_modul)
                    modul_len = int(row[key]['lens']) # ключ для подбора длины экранов и шины монтажной
                    modul_category = row[key]['category'] # получить категорию модуля (для сортировки шин и экранов)
                if key == "screen":
                    self._screen.append((int(row[key]), modul_len,modul_category)) # 1 - высота экрана 2 - длина экрана
                if key == "schine":
                    self._schine.append((row[key], modul_len,modul_category)) # 1 - наличие шины true/false 2 - длина шины
        


    def _generate_name(self):
        gabs = {"x":0,"y":100}
        key = "x"
        for i in range(len(self._schine)):
            if '22' in self._screen[i][-1]:
                self.output['all_lens'] = f"Стол диспетчера, угловой:"        
                return

            # линейно прибавляет длину модуля
            gabs[key] += self._schine[i][1]
            
            if self._screen[i][-1] in ['modul_angle_90']: # если встретился угловой модуль меняем направление приращения на противоположную ось
                key = "x" if key == "y" else "y"
        self.output['all_lens'] = f"Стол диспетчера, {gabs['x']}*{gabs['y']}*75:"

    # ДОБАВЛЕНИЕ ЭКРАНОВ
    def _add_screen(self):
        """ПОИСК ЭКРАНОВ В МОДЕЛИ И ДОБАВЛЕНИЕ ИХ В МОДУЛИ"""
        for i in range(len(self._screen)):
            if int(self._screen[i][0])!=0: # ЕСЛИ ВЫСОТА ЭКРАНА НЕ РАВНА 0, ТО ЕСТЬ ЭКРАН ПРИСУТСТВУЕТ
                lens = self._screen[i][1] # ИЗВЛЕКАЕМ ДЛИНУ ЭКРАНА
                category = self._screen[i][-1].replace('modul','screen') # ТАК КАК КАТЕГОРИИ МОДУЛЕЙ И ЭКРАНОВ ОТЛИЧАЮТСЯ ВСЕГО 1 СЛОВОМ, ПРОСТО МЕНЯЕМ ЕГО И ПОЛУЧАЕМ НУЖНЫЙ ТИП КАТЕГОРИИ
                category = f"{category}_{self._screen[i][0]}" # ДОБАВЛЯЕМ ВЫСОТУ САМОГО ЭКРАНА
                screen = manager_moduls.get_art_component_by_category_and_lens(category,lens) # ПОЛУЧАЕМ ИСКОМЫЙ ТОВАР В БД
                # print(f"*********{screen}**************")
                self._add_modul_price(row = i, art = screen, count = 1) # добавление цены в итог модуля и в общий итог
                screen = self._modul_to_string(screen,add_value=self._screen[i][0])
                self._moduls[i]['screen'] = screen


    # ДОБАВЛЕНИЕ ШИН МОНТАЖНЫХ
    def _add_schine(self):
        """ПОИСК ШИН МОНТАЖНЫХ И ДОБАЛЕНИЕ ИХ В МОДУЛИ"""
        for i in range(len(self._schine)):
            if int(self._schine[i][0])!=0:
                schine_type = self._schine[i][-1]
                category = 'schine_montage'
                if schine_type=='modul_left' or schine_type=='modul_right':
                    lens = self._schine[i][1]-10 # ИЗВЛЕЧЕНИЕ ДЛИНЫ ШИНЫ МОНТАЖНОЙ 
                    schine = manager_moduls.get_art_component_by_category_and_lens(category,lens)
                    self._add_modul_price(row = i, art = schine, count = 1) # добавление цены в итог модуля и в общий итог
                    schine = self._modul_to_string(schine,1,add_value="да")
                    self._moduls[i]['schine'] = schine

                elif schine_type=='modul_single':
                    lens = self._schine[i][1]-20 # ИЗВЛЕЧЕНИЕ ДЛИНЫ ШИНЫ МОНТАЖНОЙ 
                    schine = manager_moduls.get_art_component_by_category_and_lens(category,lens)
                    self._add_modul_price(row = i, art = schine, count = 1) # добавление цены в итог модуля и в общий итог
                    schine = self._modul_to_string(schine,1,add_value="да") # эта строка должна распологаться строго после предыдущей
                    self._moduls[i]['schine'] = schine

                elif schine_type=='modul_center':
                    lens = self._schine[i][1] # ИЗВЛЕЧЕНИЕ ДЛИНЫ ШИНЫ МОНТАЖНОЙ 
                    schine = manager_moduls.get_art_component_by_category_and_lens(category,lens)
                    self._add_modul_price(row = i, art = schine, count = 1) # добавление цены в итог модуля и в общий итог
                    schine = self._modul_to_string(schine,1,add_value="да")
                    self._moduls[i]['schine'] = schine

                elif schine_type in ("modul_22_left","modul_22_right","modul_22_center"):
                    schine = manager_moduls.get_art_component_by_category_and_lens(category,lens=97)
                    self._add_modul_price(row = i, art = schine, count = 1) # добавление цены в итог модуля и в общий итог
                    schine = self._modul_to_string(schine,1,add_value="да")
                    self._moduls[i]['schine'] = schine
                
                elif schine_type=='modul_angle_90': # ФЛ-1919
                    lens = self._schine[i][1] # ИЗВЛЕЧЕНИЕ ДЛИНЫ ШИНЫ МОНТАЖНОЙ 
                    schine = manager_moduls.get_art_component_by_category_and_lens(category,lens=97)
                    self._add_modul_price(row = i, art = schine, count = 2) # добавить цену в прайс
                    schine = self._modul_to_string(schine,2,add_value="да") # -> для углового модуля идёт две шины монтажные
                    self._moduls[i]['schine'] = schine


    # ДОБАВЛЕНИЕ СТОЛЕШНИЦЫ
    def _add_table(self):
        """длина столешницы подбирается через коллекцию с шинами (используется параметр 1 - длина)"""
        for i in range(len(self._schine)):
            table = ""
            lens = self._schine[i][1]
            
            if "modul_single" == self._schine[i][-1]:
                table = f"Столешница стола диспетчера, {lens}*100*3.2,"
            
            elif "modul_left" == self._schine[i][-1]:
                table = f"Столешница стола диспетчера левая, {lens}*100*3.2,"
            
            elif "modul_right" == self._schine[i][-1]:
                table = f"Столешница стола диспетчера правая, {lens}*100*3.2,"
            
            elif "modul_angle_90" == self._schine[i][-1]:
                table = f"Столешница стола диспетчера угловая 90°, {lens}*100*3.2,"

            elif "modul_center" == self._schine[i][-1]:
                table = f"Столешница стола диспетчера промежуточная, {lens}*100*3.2,"
            

            # table = f"Столешница стола диспетчера, {lens}*100*3.2," # в будущем добавить параметр толщины столешницы (может и глубину)
            table += f" {self._names['ldsp_color']}. С/с:" # цвет столешницы
            # вычисление цены столешинцы
            price = int(self._names["ldsp_price"])
            price = (lens/100 * 1) * price
            self._add_modul_price(row=i,art=None, count=1, price=price) # к столешницам скидка не применяется
            # self._moduls[i]['table'] = table

            table_added = {"part1":table,"part2":int(price),"part3":"руб./шт."}
            self._moduls[i]['table'] = table_added
            

    def _left_right_ldsp(self):
            price = int(self._names["ldsp_price"])
            sidewall_name = "ФЛ-091 Комплект боковин (лев+прав),"
            sidewall_decor = f" {self._names['ldsp_color']}. С/с:" # цвет боковин (такой же как и у столешниц)
            sidewall_price = int(((75/100 * 1) * price)*2)

            sidewall_added = {"part1":sidewall_name + sidewall_decor,"part2":sidewall_price,"part3":"руб./кт."}
            self.output['options'].append(sidewall_added)
            # self.output['options'].append('ФЛ-1715.85')


    # ПРИМЕНЕНИЕ СКИДКИ (К ИЗДЕЛИЯМ ИЗ ЛДСП НЕ ПРИМЕНЯЕТСЯ)
    def _discount(self,price):
        """применение скидки (к ценам на все комплектующие кроме)"""
        discount = int(self._names['discount'])
        if discount:
            return price - (price / 100 ) * discount
        return price


    # ДОБАВЛЕНИЕ ЦЕН МОДУЛЯ В ИТОГ МОДУЛЯ И В ИТОГОВУЮ СТОИМОСТЬ ВСЕЙ МЕБЕЛИ
    def _add_modul_price(self,row,art,count=1,price=None):
        """добавление цен в модуль и общую статистику"""
        if not price:
            price = int(manager_moduls.get_price_by_art(art)) # ПОЛУЧЕНИЕ ЦЕНЫ ИЗДЕЛИЯ ПО АРТИКУЛУ
        for _ in range(count):
            self._moduls[row]['price'] += int(price) # добавим цену изделия в прайс модуля
            self.output['all_price']+= int(price) # добавить цену в итоговый подсчёт


    # КОНВЕРТАЦИЯ МОДУЛЯ В СТРОКУ КОТОРАЯ БУДЕТ ПОКАЗАНА ПОЛЬЗОВАТЕЛЮ / ДОБАВЛЕНИЕ МНОЖИТЕЛЯ К ДУБЛЯМ
    def _modul_to_string(self,art,count=1,is_header=False,add_value=None):
        res = manager_moduls.get_one_modul_by_art(art)
        if is_header:
            output_string = f"{res['name']}:"
            metal_decor = re.search(r'(?P<metal_decor>RAL\d{2,5})',output_string)
            if metal_decor:
                output_string = output_string.replace(metal_decor['metal_decor'], self._names['metal_color'])
            return output_string


        # ВСЕ СТРОКИ С ПОЗИЦИОННЫМИ ИЗДЕЛИЯМИ ПОДЕЛЕНЫ НА СЕГМЕНТЫ ДЛЯ УПРАВЛЕНИЯ ИХ СТИЛЯМИ В HTML
        if res:
            price = int(self._discount(res['price']))
            name = res['name']
            metal_decor = re.search(r'(?P<metal_decor>RAL\d{2,5})',name)
            if metal_decor:
                name = name.replace(metal_decor['metal_decor'], self._names['metal_color'])
            output = {"part1":f"{res['art']} {name}. С/с:","part2":int(price),"part3":"руб./шт."} # этот формат потом удобно обрабатывать в html для применения стилей
        
        if res and count>1:
            output['part4'] = f"|==>x{count}==> "
            output['part5'] = int(self._discount(res['price'])*count)
            output['part6'] = "руб."

        if add_value:
            output['add_value'] = add_value
        
        return output
        

    # ВСПОМОГАТЕЛЬНАЯ (ВЫВОДИТ ВСЕ ТЕКУЩИЕ ПАРАМЕТРЫ ДЛЯ ДЕБАГА)     
    def _show_parametrs_for_debug(self):
        """показать параметры (функция для отладки)"""
        print(self._names)
        print('\n'+'='*20+'CALCULATE'+'='*20 +'\n')
        print(self.output)
        print('='*50)

        print('='*50)
        print(self._screen)
        print('='*50)

        print('='*50)
        print(self._schine)
        print('='*50)

        print('='*50)
        print(self.output['options'])
        print('='*50)

        print(self.output)

        print('\n'+'='*18+'END CALCULATE'+'='*18 +'\n')


    # ДОБАВЛЕНИЕ СТОЕК ЭКРАНА
    def _add_holder_screen(self):
        screen_list = []
        if len(self._screen)==1:
            return
        for i in range(len(self._screen)-1):
            print(f"---> {self._screen[i]}")
            screen_types = self._screen[i][-1]
            screen_height = self._screen[i][0] if self._screen[i+1][0]<self._screen[i][0] else self._screen[i+1][0]
            # обработка первого экрана
            if screen_types == "modul_left" and screen_height != 0:
                screen_list.append(f"Стойка h={screen_height}")
                self.output['options'].append(f'ФЛ-1711.{screen_height}')
            
            # обработка промежуточных модулей экранов
            elif i < len(self._screen)-1:
                if screen_height != 0:
                    if self._screen[i][0]-1==0: # если у предыдущий экран отстутствует, то добавляем доп стойку
                        screen_list.append(f"Стойка h={screen_height}")
                        self.output['options'].append(f'ФЛ-1711.{screen_height}')
                    screen_list.append(f"Стойка h={screen_height}")
                    self.output['options'].append(f'ФЛ-1711.{screen_height}')

        print(f"===>screen_list: {screen_list}")
            


    # ДОБАВЛЕНИЕ СТОЕК ЭКРАНА
    def _add_holder_modul(self):
        """ДОБАВИТЬ ОПОРУ ПРОМЕЖУТОЧНУЮ"""
        counts = len(self._schine)-1
        if counts>0:
            for _ in range(counts):
                self.output['options'].append('ФЛ-1701')


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
            for _  in range(self._options['monitor_type_3']):
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
            # print(f"---->mod={modul['art']}| count={count}")
            name_pos = f"{modul['art']} {modul['name']}. C/c: "
            price_pos = int(self._discount(modul['price']))
            self.output["options"][i] = {"part1":name_pos,"part2":price_pos,"part3":"руб./шт."}
            if count>1:
                add_price = int(self._discount(modul['price'])*count)
                self.output['all_price'] += int(add_price)
                # adder_option += f" |==>x{count}==> {add_price} руб."
                self.output["options"][i]['part4'] = f" |==>x{count}==>"
                self.output["options"][i]['part5'] = int(add_price)
                self.output["options"][i]['part6'] = "руб."
            