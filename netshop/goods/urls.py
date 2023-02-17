#coding=utf-8

from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns=[
    # 新版本url不能用了
    path(r'',views.IndexView.as_view())
]