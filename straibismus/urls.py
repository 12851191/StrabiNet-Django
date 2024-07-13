from django.contrib import admin
from django.urls import path
from crowdsourcing import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('hello/', views.hello_view, name='hello'),
    path('contribute/', views.contribute_view, name='contribute'),
    path('upload/', views.upload_image, name='upload'),
    path('download_dataset/', views.download_dataset, name='download_dataset'), 
]
