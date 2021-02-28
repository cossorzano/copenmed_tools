from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.visor, name='visor'),
    # url(r'^ajax/get_links/$', views.get_links, name='get_links'),
]