#coding=utf-8
from django.http import HttpResponse
from django.views import View

from .cartmanager import *


class CartView(View):
    def post(self,request):
        #获取当前用户操作类型变量值
        flag = request.POST.get('flag','')

        #判断用户当前操作类型
        if flag == 'add':
            #获取cartManager对象
            cartManager = getCartManger(request)
            #加入购物车操作
            cartManager.add(**request.POST.dict())
        return HttpResponse('加入购物车操作')