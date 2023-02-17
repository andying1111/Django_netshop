from django.shortcuts import render
from django.views import View

from .models import *


# Create your views here.

class IndexView(View):
    def get(self,request,cid=2):

        cid = int(cid)

        # 查询所以类别信息,order_by('id')根据id排序
        categorys = Category.objects.all().order_by('id')

        #查询当前类别的作业商品信息
        goodslist = Goods.objects.filter(category_id=cid).order_by('id')

        return render(request, 'index.html',{'categorys':categorys,'goodlist':goodslist,'currentCid':cid})
# help(View)