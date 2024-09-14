from django.shortcuts import render
from dispatcher.base_loader import Moduls # менеджер для работы с базой
from dispatcher.temporary import test_moduls # импортируем тестовую базу данных
from price_list.models import CATEGORY_DESCRIPTIONS

# ПЕРЕМЕННАЯ ДЛЯ ВЗАИМОДЕЙСТВИЯ С БД (В БУДУЩЕМ С МОДЕЛЬЮ)
dispathcer_manager_moduls = Moduls(moduls=test_moduls) # добавляем коннект с БД (пока временно json из temporary)

def index(request):
    dispathcer_manager_moduls.get_all_moduls()
    context = {
        'title':'test',
    }
    return render(request,'price_list/index.html',context)


def load_price(request):
    if request.method == "POST":
        print(f"{'=' * 25} load_price {'=' * 25}")
        components = [i.replace('\n','').strip() for i in request.POST['load_components'].split('\n') if i!=""]
        [print(row) for row in components]
        print(f"{'=' * 25} end load_price {'=' * 25}")
    context = {
        'title':'test',
        'categories': CATEGORY_DESCRIPTIONS
    }
    return render(request,'price_list/load_price.html',context)
    