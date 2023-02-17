# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.views import View

from .models import Category, Goods
from django.core.paginator import Paginator
import math


class IndexView(View):
    def get(self,request,cid=1,num=1):
        cid = int(cid)
        num = int(num)

        #查询所有类别信息
        categoryList = Category.objects.all()

        #查询当前类别下的所有商品信息
        goodsList = Goods.objects.filter(category_id=cid).order_by('id')

        #创建分页器对象
        paginator_obj = Paginator(goodsList,8)

        #获取某页数据对象
        page_obj = paginator_obj.page(num)

        #获取每一页显示的页码范围
        begin = num - int(math.ceil(10.0/2))
        if begin < 1:
            begin = 1

        end = begin + 9

        if end > paginator_obj.num_pages:
            end = paginator_obj.num_pages

        if end < 10:
            begin = 1
        else:
            begin = end -9

        page_list = range(begin,end+1)


        return render(request,'index.html',{'categoryList':categoryList,'cid':cid,'goodsList':page_obj,'page_list':page_list,'num':num})

def recommend_view(func):
    def _wrapper(detailView,request,goodsid,*args,**kwargs):
        #从cookie中获取用户访问的所有商品id
        c_goodsid = request.COOKIES.get('rem','')


        #存放用户访问商品的goodsid列表
        #['1','2','3'] = '1 2 3'
        goodsIdList = [gid for gid in c_goodsid.split() if gid.strip()]

        #最终推荐商品列表
        goodsObjList = [Goods.objects.get(id=vgoodsid) for vgoodsid in goodsIdList if Goods.objects.get(id=vgoodsid).category_id==Goods.objects.get(id=goodsid).category_id and vgoodsid!=goodsid][:4]
        #调用相应修饰的函数
        response = func(detailView,request,goodsid,goodsObjList,*args,**kwargs)

        #判断用户访问商品是否存在goodsIdList中
        if goodsid in goodsIdList:
            goodsIdList.remove(goodsid)
            goodsIdList.insert(0,goodsid)
        else:
            goodsIdList.insert(0,goodsid)


        #将用户访问的商品id存放至cookie
        response.set_cookie('rem',' '.join(goodsIdList),max_age=3*24*60*60)

        return response

    return _wrapper








class DetailView(View):
    @recommend_view
    def get(self,request,goodsid,recommend_list=[]):
        goodsid = int(goodsid)

        #根据商品id查询商品详情
        goods = Goods.objects.get(id=goodsid)

        return render(request, 'detail.html', {'goods': goods, 'recommend_list': recommend_list})
