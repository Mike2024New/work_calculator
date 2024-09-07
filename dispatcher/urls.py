from django.urls import path
from dispatcher import views

app_name = "dispatcher"

urlpatterns = [
    path('dispathcer/',view = views.index, name = 'index')
]
