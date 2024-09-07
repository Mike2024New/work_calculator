from django.shortcuts import render


def index(requests):
    context = {
        'title':'test',
    }
    return render(requests,'main/index.html',context)


def custom_404_view(requests,exception):
    print(exception)# точка логгирования исключения
    return render(requests,'404.html', status=404)