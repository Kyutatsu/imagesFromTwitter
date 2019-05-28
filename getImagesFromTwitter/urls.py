from django.urls import path
from getImagesFromTwitter import views


app_name = 'getImagesFromTwitter'
urlpatterns = [
        path('', views.index, name='index'),
        path('get_token/', views.get_token, name='get_token'),
        path('login_twitter/', views.login_twitter, name='login_twitter'),
        path('get_images/', views.get_images_from_name, name='get_images'),
        path('label_to_images/', views.label_to_images, name='label'),
]
