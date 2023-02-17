#coding=utf-8
from django.conf.urls import url
from cartapp import views


urlpatterns = [
    url(r'^$', views.CartView.as_view()),
]