from django.shortcuts import render


def index(requests):
    context = {
        'title':'test',
    }
    return render(requests,'price_list/index.html',context)