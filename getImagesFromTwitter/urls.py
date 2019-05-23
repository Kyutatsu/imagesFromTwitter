from django.urls import path
from getImagesFromTwitter import views


app_name = 'getImageFromTwitter'
urlpatterns = [
        path('', views.index, name='index'),
        path('get_token/', views.get_token, name='get_token'),
        path('login_twitter/', views.login_twitter, name='login_twitter'),
]
