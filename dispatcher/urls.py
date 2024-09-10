from django.urls import path
from dispatcher import views

app_name = "dispatcher"

urlpatterns = [
    path('dispathcer/',view = views.index, name = 'index'),
    path('dispatcher/get_data/', view = views.get_data, name = "get_data"),
    path('dispatcher/get_moduls/', view = views.get_moduls, name = "get_moduls"),
    path('dispatcher/send_session/', view = views.send_session, name = "send_session"),
    path('dispatcher/check_parametrs/', view = views.check_parametrs, name = "check_parametrs"),
]
