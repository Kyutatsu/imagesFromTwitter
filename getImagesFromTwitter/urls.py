from django.urls import path
from getImagesFromTwitter import views


urlpatterns = [
        path('', views.index, name='index'),
]
