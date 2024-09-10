from django.shortcuts import render,redirect
from dispatcher.temporary import test_moduls
from django.http import JsonResponse
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
    
    def get_moduls_by_category(self,keys_in:tuple,is_contains=True)->list:
        """
        получение модулей из модели (пока что из тестового словаря в модуле temporary.py, позже будут запросы к модели)
        keys_in -> список категорий по которым нужно извлечь значения (если содержи то извлечь)
        is_contais -> инверсия, берем те элементы которые не содержат в категории значения из keys_in
        """
        if is_contains:
            return [row for row in test_moduls if row['category'] in keys_in]
        return [row for row in test_moduls if row['category'] not in keys_in]


manager_moduls = Moduls(moduls=test_moduls)


def index(request):
    print(request.session)
    if "data" not in request.session:
        request.session['data'] = []
    moduls_list = manager_moduls.get_moduls_by_category(keys_in=('modul_left','modul_single'))
    context = {
        'title':'Диспетчерская',
        'moduls': moduls_list, # ЗНАЧЕНИЯ ДЛЯ ЗАПОЛНЕНИЯ SELECT (МОДУЛЕЙ КОТОРЫЕ МОЖНО ВЫБРАТЬ)
        'debug' : True
    }
    return render(request,'dispatcher/index.html',context)



# POST -> ИЗВЛЕЧЕНИЕ ПАРАМЕТРОВ ИЗ ФОРМЫ (НАЖАТИЕ НА КНОПКУ "РАСЧЁТ СТАНЦИИ")
def get_data(request):
    """обработчик кнопки расчёт станции, принимает post запрос с данными форм"""
    request.session['data'] = []
    extract_values = []
    # определение количества модулей
    if request.method == 'POST':
        if "all_reset" in request.POST:
            clear_session(request)
            return redirect('dispatcher:index')

        for key in request.POST:
            if 'modul_select_' in key:
                try:
                    extract_values.append(manager_moduls.extract_art(request.POST[key],True))
                except Exception as err:
                    print(f'get data-> не найден артикул в строке {request.POST[key]}, err: {err}')

        # добавление извлеченных модулей в сессию
        for i in range(len(extract_values)):
            modul = manager_moduls.get_one_modul_by_art(art=extract_values[i])
            screen = request.POST[f'option_screen_{i}'] if f'option_screen_{i}' in request.POST else False
            schine = True if f'select_schine_{i}' in request.POST else False
            request.session['data'].append({"modul":modul,"screen":screen,"schine":schine})
        print(request.session['data'])
    return redirect('dispatcher:index')


def check_parametrs(request):
    print('check_parametrs')
    print(request.POST)
    permission = True
    msg = None
    """AJAX WITH FRONTEND ПРОВЕРКА ДИНАМИЧЕСКИХ БЛОКОВ ПЕРЕД ЗАПОЛНЕНИЕМ, ЕСЛИ В ПОСЛЕДНЕМ БЛОКЕ В SELECT НЕ ВЫБРАН МОДУЛЬ ИЛИ ВЫБРАН НЕ ТОТ, ТО ЗАПРЕТИТЬ ДОБАВЛЯТЬ БЛОК"""
    if "is_add_block" in request.POST: # проверка на вставку нового блока (из ajax приходит переменная is_add_block с количеством элементов)
        last_modul = request.POST[f"modul_select_{request.POST['is_add_block']}"]
        if last_modul =="выберите модуль" :
            permission = False
            msg = "не выбран модуль"
            return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
        if int(request.POST["is_add_block"])==0:
            art = manager_moduls.extract_art(string=last_modul,one_components=True)
            res = manager_moduls.get_one_modul_by_art(art)
            if res['category']=='modul_single':
                permission = False
                msg = "нельзя добавлять модули к отдельно стоящему столу"
                return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})

                # pass
    return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})


# SESSION -> ОЧИСТИТЬ СЕССИЮ
def clear_session(request):
    request.session['data'] = [] # если запрос на удаление (кнопка сброс модулей, то очистить сессию)


# AJAX -> ОТПРАВКА СЕССИИ
def send_session(request):
    print(f"--> {request.POST['session_del']}")
    if request.POST['session_del'] == 'true': # очистка сессии (сброс)
        clear_session(request)
    return JsonResponse({'session':request.session['data']})


# AJAX -> ОТПРАВКА МОДУЛЕЙ
def get_moduls(request):
    """отправка всех модулей через ajax, для заполнения списков"""
    moduls_list = manager_moduls.get_moduls_by_category(keys_in=('modul_left','modul_single'),is_contains=False)
    return JsonResponse({'moduls':moduls_list})
