#coding=utf-8
from django.conf.urls import url
from goodsapp import views
urlpatterns = [
    url(r'^$', views.IndexView.as_view()),
    url(r'^category/(?P<cid>\d+)$', views.IndexView.as_view()),
    url(r'^category/(?P<cid>\d+)/page/(?P<num>\d+)$', views.IndexView.as_view()),
    url(r'^goodsdetails/(\d+)$', views.DetailView.as_view()),

]











