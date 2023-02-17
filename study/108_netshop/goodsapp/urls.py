#coding=utf-8
from django.conf.urls import url
from django.urls import path

from . import views
urlpatterns = [
    url(r'', views.IndexView.as_view()),
    url(r'category/(P<cid>\d+)', views.IndexView.as_view()),
    url(r'category/(?P<cid>\d+)/page/(?P<num>\d+)', views.IndexView.as_view()),
    url(r'goods/goodsdetails/(\d+)', views.DetailView.as_view()),

]











