from django.urls import path
from . import views

app_name = 'checker'

urlpatterns = [
    path('', views.index, name='index'),
]