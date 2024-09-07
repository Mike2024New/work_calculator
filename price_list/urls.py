from django.urls import path
from price_list import views

app_name = "price_list"

urlpatterns = [
    path('price_list/',view=views.index,name='index')
]
