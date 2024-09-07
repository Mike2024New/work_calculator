from django.shortcuts import render


def index(requests):
    context = {
        'title':'test',
    }
    return render(requests,'dispatcher/index.html',context)