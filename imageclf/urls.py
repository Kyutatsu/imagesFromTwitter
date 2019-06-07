from django.urls import path
from imageclf import views


app_name = 'imageclf'
urlpatterns = [
        path('', views.index, name='index'),
]
