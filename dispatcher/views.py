import json
from django.shortcuts import render,redirect
from dispatcher.temporary import test_moduls
from django.http import JsonResponse
from django.templatetags.static import static
from dispatcher.calculate import Calculate
from dispatcher.base_loader import Moduls

# ПЕРЕМЕННАЯ ДЛЯ ВЗАИМОДЕЙСТВИЯ С БД (В БУДУЩЕМ С МОДЕЛЬЮ)
manager_moduls = Moduls(moduls=test_moduls) # добавляем коннект с БД (пока временно json из temporary)

# перенести в шаблоны В МОДЕЛЬ
default_project_name = {
    "name":"project",
    'ldsp_price':1000, # цена не настоящая показана условно
    "ldsp_color":"Арктика серый",
    "metal_color":"RAL 7047", 
    "discount":0
    }

# INDEX -> ПЕРВЫЙ ВХОД НА СТРАНИЦУ, ИНИЦИАЛИЗАЦИЯ ПАРАМЕТРОВ СЕССИИ
def index(request):
    # request.session["project_name"] = default_project_name # обнуление сессии
    if "moduls" not in request.session:
        request.session['moduls'] = []
    if "options" not in request.session:
        request.session['options'] = {"monitor_type_1":0,"monitor_type_2":0,"monitor_type_3":0, "electric_power":0, "electric_rj45":0}
    if "project_name" not in request.session:
        request.session["project_name"] = default_project_name


    moduls_list = manager_moduls.get_moduls_by_category(keys_in=('modul_left','modul_22_left','modul_single'))

    context = {
        'title':'Диспетчерская',
        'moduls': moduls_list, # ЗНАЧЕНИЯ ДЛЯ ЗАПОЛНЕНИЯ SELECT (МОДУЛЕЙ КОТОРЫЕ МОЖНО ВЫБРАТЬ)
        'debug' : True,
        'project' : request.session["project_name"],
        'options' : request.session['options'], # мониторы,розетки, интернет
        'default' : json.dumps(default_project_name), # обязательно преобразовать в json- строку иначе java не спарсит её
    }

    return render(request,'dispatcher/index.html',context)


# POST -> ИЗВЛЕЧЕНИЕ ПАРАМЕТРОВ ИЗ ФОРМЫ (НАЖАТИЕ НА КНОПКУ "РАСЧЁТ СТАНЦИИ")
def get_data(request):
    """обработчик кнопки расчёт станции, принимает post запрос с данными форм"""
    # print(request.session["project_name"])
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
        for i in range(len(extract_values)):
            modul = manager_moduls.get_one_modul_by_art(art=extract_values[i])
            screen = request.POST[f'option_screen_{i}'] if f'option_screen_{i}' in request.POST else False
            schine = True if f'select_schine_{i}' in request.POST else False
            request.session['moduls'].append({"modul":modul,"screen":screen,"schine":schine})

        request.session['options'] = {
            "monitor_type_1":int(request.POST['monitor_type_1']),
            "monitor_type_2":int(request.POST['monitor_type_2']),
            "monitor_type_3":int(request.POST['monitor_type_3']),
            "electric_power":int(request.POST['electric_power']), 
            "electric_rj45":int(request.POST['electric_rj45']),
            }

        # ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ПРОЕКТЕ
        if request.POST["project_name"]!="":
            request.session["project_name"]["name"] = request.POST["project_name"]

        if request.POST["ldsp_color"]!="":
            request.session["project_name"]["ldsp_color"] = request.POST["ldsp_color"]

        if request.POST["ldsp_price"]!="":
            request.session["project_name"]["ldsp_price"] = request.POST["ldsp_price"]
        
        if request.POST["metal_color"]!="":
            request.session["project_name"]["metal_color"] = request.POST["metal_color"]

        if request.POST["discount"]!="":
            request.session["project_name"]["discount"] = request.POST["discount"]

    # точка вызова обработчика для расчёта стоимости
    #========================
    # обработчик вынести в отдельный модуль

    return redirect('dispatcher:show_result')


# ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА ПОЛЬЗОВАТЕЛЮ / ЗАПРАШИВАЕТ РАСЧЁТ ИЗДЕЛИЙ НА БАЗЕ ВВЕДЕННЫХ ПОЛЬЗОВАТЕЛЕМ ПАРАМЕТРОВ
def show_result(request):
    res = Calculate(names=request.session["project_name"],moduls=request.session['moduls'],options=request.session['options'])
    # show_session_consol(request)
    # print(res.output) "screen_list":[],"schine_list":[]
    context={
        "title":"результат расчёта",
        "project": res.output["project"],
        "moduls": res.output["moduls"],
        "options": res.output["options"],
        "all_price": res.output["all_price"],
        'project' : request.session["project_name"],
        "all_lens" : res.output["all_lens"],
    }
    return render(request,'dispatcher/result.html',context)


# SESSION -> ВСПОМОГАТЕЛЬНЫЙ, ПОКАЗЫВАЕТ ДАННЫЕ ХРАНЯЩИЕСЯ В СЕССИИ
def show_session_consol(request):
    print('='*50)
    print(request.session['moduls'])
    print('='*50)
    print(request.session['options'])
    print('='*50)
    print(request.session['project_name'])
    print('='*50)


# SESSION -> ОЧИСТИТЬ СЕССИЮ (УКАЗАТЬ КЛЮЧ ОЧИЩАЕМОЙ СЕССИИ)
def clear_session(request,del_key):
    if del_key == 'all_reset':
        request.session['moduls'] = [] # если запрос на удаление (кнопка сброс модулей, то очистить сессию)
        request.session['options'] = {"monitor_type_1":0,"monitor_type_2":0,"monitor_type_3":0, "electric_power":0, "electric_rj45":0}
        # заменить на ключи (добавить шаблоны)
        request.session["project_name"] = default_project_name
    elif del_key == 'del_name':
        request.session["project_name"] = default_project_name
    elif del_key == 'del_monitor':
        request.session['options'] = {
            "monitor_type_1":0,
            "monitor_type_2":0,
            "monitor_type_3":0, 
            "electric_power":request.POST["electric_power"], 
            "electric_rj45":request.POST["electric_rj45"], 
            }
    elif del_key == 'del_electric':
        request.session['options'] = {
            "monitor_type_1":request.POST["monitor_type_1"], 
            "monitor_type_2":request.POST["monitor_type_2"], 
            "monitor_type_3":request.POST["monitor_type_3"], 
            "electric_power":request.POST["electric_power"], 
            "electric_rj45":request.POST["electric_rj45"], 
            }
    elif del_key == 'del_modul':
        request.session['moduls'] = [] # если запрос на удаление (кнопка сброс модулей, то очистить сессию)
    show_session_consol(request)


# ======================= ОБРАБОТКА AJAX ЗАПРОСОВ ===============================================

# AJAX -> ПОЛУЧЕНИЕ КАРТИНКИ НА СТРАНИЦУ
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

# AJAX -> ПРОВЕРКА ПАРАМЕТРОВ В ФОРМЕ (ПОСЛЕ ТОГО КАК ПОЛЬЗОВАТЕЛЬ НАЖАЛ РАСЧЁТ СТАНЦИИ)
def check_parametrs(request):
    print('check_parametrs')
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
        
        elif res['category'] in ('modul_right','modul_22_right'):
            permission = False
            msg = "правый модуль является закрывающим, если нужно продолжить выберите угловой или промежутнчный."
        return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
        
    """AJAX МЕТОД ДЛЯ ПРОВЕРКИ ФОРМЫ ПЕРЕД ОТПРАВКОЙ POST ЗАПРОСА В get_data"""
    if "is_send_form" in request.POST:

        # ПРОВЕРКА, ЧТО УКАЗАНЫ МОНИТОРЫ
        if any([int(request.POST[key])>0 for key in request.POST if "monitor_type_" in key]):
            # print(request.POST)
            for key in request.POST:
                if "select_schine_" in key:
                    break
            else:
                permission = False
                msg = "Добавлены мониторы, но нет шин монтажных"
                return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
            
        if not any([int(request.POST[key])>0 for key in request.POST if "monitor_type_" in key]):
            schine_list = [key for key in request.POST if "select_schine_" in key]
            print(f"************{schine_list}")
            if schine_list:
                permission = False
                msg = "Указаны шины монтажные но нет мониторов"
                return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})

        
        # ПРОВЕРКА, МОДУЛЕЙ
        if "выберите модуль" in [request.POST[key] for key in request.POST if 'modul_select_' in key]:
            permission = False
            msg = "Не выбран один из модулей."
            return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
        
        moduls = [request.POST[key] for key in request.POST if 'modul_select_' in key]
        for i in range(len(moduls)-1):
            if "правый" in moduls[i]:
                permission = False
                msg = "В центре не должно быть правых модулей. Правый модуль всегда в конце."
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
        
        if res["category"] not in ['modul_right','modul_22_right'] and int(request.POST['is_send_form'])>0:
            permission = False
            msg = "закрывающий (последний) модуль должен быть правым"
        return JsonResponse({'check_info':{'is_check':permission,'msg': msg}})
    
    return JsonResponse({'check_info':{'is_check':permission,'msg': msg}}) # все проверки пройдены всё ок


# AJAX -> ОТПРАВКА СЕССИИ
def send_session(request):
    print('send_session')
    if request.POST['session_del'] == 'true': # очистка сессии (сброс)
        if request.POST['session_del_key']=='all_reset':
            clear_session(request,del_key = 'all_reset')
        elif request.POST['session_del_key']=='del_name':
            clear_session(request,del_key = 'del_name')
        elif request.POST['session_del_key']=='del_monitor':
            clear_session(request,del_key = 'del_monitor')
        elif request.POST['session_del_key']=='del_electric':
            clear_session(request,del_key = 'del_electric')
        elif request.POST['session_del_key']=='del_modul':
            clear_session(request,del_key = 'del_modul')
    return JsonResponse({'session':request.session['moduls']})


# AJAX -> ОТПРАВКА МОДУЛЕЙ
def get_moduls(request):
    """отправка всех модулей через ajax, для заполнения списков"""
    print("get_moduls")
    moduls_list = manager_moduls.get_moduls_by_category(keys_in=(
        'modul_right',
        'modul_center',
        'modul_angle_90',
        'modul_22_right',
        'modul_22_center'
        ),is_contains=True)
    return JsonResponse({'moduls':moduls_list})
