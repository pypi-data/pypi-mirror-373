from django.urls import path

from isapilib.views import index

urlpatterns = [
    path('', index, name='index'),
]
