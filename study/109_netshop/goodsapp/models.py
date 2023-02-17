# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import collections


# Create your models here.
class Category(models.Model):
    cname = models.CharField(max_length=10)

    def __unicode__(self):
        return u'<Category:%s>'%self.cname


class Goods(models.Model):
    gname = models.CharField(max_length=100,unique=True)
    gdesc = models.CharField(max_length=100)
    oldprice = models.DecimalField(max_digits=5,decimal_places=2)
    price = models.DecimalField(max_digits=5,decimal_places=2)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)

    def __unicode__(self):
        return u'<Goods:%s>'%self.gname


    def getColorImg(self):
        return self.inventory_set.first().color.colorurl

    def getColors(self):
        colors = []
        for inventory in self.inventory_set.all():
            color = inventory.color
            if color not in colors:
                colors.append(color)
        return colors

    def getSizes(self):
        sizes = []
        for inventory in self.inventory_set.all():
            size = inventory.size
            if size not in sizes:
                sizes.append(size)
        return sizes

    # def getDetailInfo(self):
    #     #创建有序字典对象用于存放商品详情展示信息
    #     datas = collections.OrderedDict()
    #
    #     #遍历当前这款商品所有详情信息
    #     for detail in self.gooddetail_set.all():
    #         #获取详情名称（参数规格/整体款式/模特实拍）
    #         gdname = detail.getName()
    #         #判断当前详情名称是否在字典中存在
    #         if not datas.has_key(gdname):
    #             datas[gdname] = [detail.gdurl]
    #         else:
    #             datas[gdname].append(detail.gdurl)
    #
    #     return datas





class GoodsDetailName(models.Model):
    gdname = models.CharField(max_length=30)



class GoodDetail(models.Model):
    gdurl= models.ImageField(upload_to='')
    goodsdname = models.ForeignKey(GoodsDetailName, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)

    def getName(self):
        return self.goodsdname.gdname

class Size(models.Model):
    sname = models.CharField(max_length=10)


class Color(models.Model):
    colorname = models.CharField(max_length=10)
    colorurl = models.ImageField(upload_to='color/')


class Inventory(models.Model):
    count = models.PositiveIntegerField(default=100)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)




