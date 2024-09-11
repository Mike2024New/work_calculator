from django.shortcuts import render,redirect
from dispatcher.temporary import test_moduls
from django.http import JsonResponse
from django.templatetags.static import static
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
    if "moduls" not in request.session:
        request.session['moduls'] = []
    if "options" not in request.session:
        request.session['options'] = {"monitor_type_1":0,"monitor_type_2":0,"monitor_type_3":0, "electric_power":0, "electric_rj45":0}
    if "project_name" not in request.session:
        request.session["project_name"] = {"project_name":"project",}
    
    print(f"==> {request.session['project_name']}")

    moduls_list = manager_moduls.get_moduls_by_category(keys_in=('modul_left','modul_single'))

    context = {
        'title':'Диспетчерская',
        'moduls': moduls_list, # ЗНАЧЕНИЯ ДЛЯ ЗАПОЛНЕНИЯ SELECT (МОДУЛЕЙ КОТОРЫЕ МОЖНО ВЫБРАТЬ)
        'debug' : True,
        'project' : request.session["project_name"],
        'options' : request.session['options'], # мониторы,розетки, интернет
    }

    return render(request,'dispatcher/index.html',context)


def show_result(request):
    context={
        "title":"результат расчёта",
        'project' : request.session["project_name"],
    }
    return render(request,'dispatcher/result.html',context)

# POST -> ИЗВЛЕЧЕНИЕ ПАРАМЕТРОВ ИЗ ФОРМЫ (НАЖАТИЕ НА КНОПКУ "РАСЧЁТ СТАНЦИИ")
def get_data(request):
    """обработчик кнопки расчёт станции, принимает post запрос с данными форм"""
    request.session['moduls'] = []
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
                    print(f'get moduls-> не найден артикул в строке {request.POST[key]}, err: {err}')

        # ДОБАВЛЕНИЕ ИЗВЛЕЧЕННЫХ ДАННЫХ В СЕССИЮ
        print(request.POST)
        for i in range(len(extract_values)):
            modul = manager_moduls.get_one_modul_by_art(art=extract_values[i])
            screen = request.POST[f'option_screen_{i}'] if f'option_screen_{i}' in request.POST else False
            schine = True if f'select_schine_{i}' in request.POST else False
            request.session['moduls'].append({"modul":modul,"screen":screen,"schine":schine})

        request.session['options'] = {
            "monitor_type_1":request.POST['monitor_type_1'],
            "monitor_type_2":request.POST['monitor_type_2'],
            "monitor_type_3":request.POST['monitor_type_3'], 
            "electric_power":request.POST['electric_power'], 
            "electric_rj45":request.POST['electric_rj45'],
            }
        

        # ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ПРОЕКТЕ
        if request.POST["project_name"]!="":
            request.session["project_name"]["name"] = request.POST["project_name"]
    return redirect('dispatcher:show_result')


def get_one_modul(request):
    if 'value_request' in request.POST:
        select_value = request.POST['value_request']
        try:
            art = manager_moduls.extract_art(string=select_value,one_components=True)
            modul = manager_moduls.get_one_modul_by_art(art)
            return JsonResponse({"url_image":modul['url_image'],"img_len":modul['lens']})
        except:
            url_image_default = static("images/select_modul.png")
            return JsonResponse({"url_image":url_image_default,"img_len":0})   


def check_parametrs(request):
    print('check_parametrs')
    print(request.POST)
    permission = True
    msg = None
    """AJAX WITH FRONTEND ПРОВЕРКА ДИНАМИЧЕСКИХ БЛОКОВ ПЕРЕД ЗАПОЛНЕНИЕМ, ЕСЛИ В ПОСЛЕДНЕМ БЛОКЕ В SELECT НЕ ВЫБРАН МОДУЛЬ ИЛИ ВЫБРАН НЕ ТОТ, ТО ЗАПРЕТИТЬ ДОБАВЛЯТЬ БЛОК"""
    if "is_add_block" in request.POST: # проверка на вставку нового блока (из ajax приходит переменная is_add_block с количеством элементов)
        if "выберите модуль" in [request.POST[key] or "" in request.POST[key] for key in request.POST if 'modul_select_' in key]:
            permission = False
            msg = "Не выбран один из модулей."
            return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})

        last_modul = request.POST[f"modul_select_{request.POST['is_add_block']}"]
        art = manager_moduls.extract_art(string=last_modul,one_components=True)
        res = manager_moduls.get_one_modul_by_art(art)
       
        if res['category']=='modul_single':
            permission = False
            msg = "нельзя добавлять модули к отдельно стоящему столу"
        
        elif res['category']=='modul_right':
            permission = False
            msg = "правый модуль является закрывающим, если нужно продолжить выберите угловой или промежутнчный."
        return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
        
    """AJAX МЕТОД ДЛЯ ПРОВЕРКИ ФОРМЫ ПЕРЕД ОТПРАВКОЙ POST ЗАПРОСА В get_data"""
    if "is_send_form" in request.POST:

        # ПРОВЕРКА, ЧТО УКАЗАНЫ МОНИТОРЫ
        if any([int(request.POST[key])>0 for key in request.POST if "monitor_type_" in key]):
            print(request.POST)
            for key in request.POST:
                if "select_schine_" in key:
                    break
            else:
                permission = False
                msg = "Добавлены мониторы, но нет шин монтажных"
                return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
        
        # ПРОВЕРКА, МОДУЛЕЙ
        if "выберите модуль" in [request.POST[key] for key in request.POST if 'modul_select_' in key]:
            permission = False
            msg = "Не выбран один из модулей."
            return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
            
        # ПРОВЕРКА ЧТО ПЕРВЫЙ МОДУЛЬ НЕ ЯВЛЯЕТСЯ ОТДЕЛЬНЫМ СТОЛОМ
        first_modul = request.POST[f"modul_select_0"]
        first_art = manager_moduls.extract_art(string=first_modul,one_components=True)
        first_res = manager_moduls.get_one_modul_by_art(first_art)
        if first_res['category']=='modul_single' and int(request.POST['is_send_form'])>0:
            permission = False
            msg = "нельзя добавлять модули к отдельно стоящему столу"

        last_modul = request.POST[f"modul_select_{request.POST['is_send_form']}"]
        if last_modul == "выберите модуль":
                permission = False
                msg = "Не выбран один из модулей."
                return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
        
        art = manager_moduls.extract_art(string=last_modul,one_components=True)
        res = manager_moduls.get_one_modul_by_art(art)


        if res['category']=='modul_left':
            permission = False
            msg = "если модуль всего 1 то это дожен быть отдельно стоящий стол но не левый"

        if last_modul =="выберите модуль" :
            permission = False
            msg = "есть не выбранные модули"
        
        if res["category"]!='modul_right' and int(request.POST['is_send_form'])>0:
            permission = False
            msg = "закрывающий (последний) модуль должен быть правым"
        return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
    
    return JsonResponse({'check_info':{'is_check':permission,'msg': msg}}) # все проверки пройдены всё ок


# SESSION -> ОЧИСТИТЬ СЕССИЮ
def clear_session(request):
    request.session['moduls'] = [] # если запрос на удаление (кнопка сброс модулей, то очистить сессию)
    request.session['options'] = {"monitor_type_1":0,"monitor_type_2":0,"monitor_type_3":0, "electric_power":0, "electric_rj45":0}
    request.session["project_name"]["name"] = "project"


# AJAX -> ОТПРАВКА СЕССИИ
def send_session(request):
    if request.POST['session_del'] == 'true': # очистка сессии (сброс)
        clear_session(request)
    return JsonResponse({'session':request.session['moduls']})


# AJAX -> ОТПРАВКА МОДУЛЕЙ
def get_moduls(request):
    """отправка всех модулей через ajax, для заполнения списков"""
    moduls_list = manager_moduls.get_moduls_by_category(keys_in=('modul_left','modul_single'),is_contains=False)
    return JsonResponse({'moduls':moduls_list})
