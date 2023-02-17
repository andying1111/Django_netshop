from django.db import models

# Create your models here.
class Category(models.Model):
    cname = models.CharField(max_length=10)

    def __unicode__(self):
        return u'Category:%s'%self.cname

class Goods(models.Model):
    gname = models.CharField(max_length=100)
    gdesc = models.CharField(max_length=100)
    oldprice = models.DecimalField(max_digits=6,decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # 通过查看ForeignKey类，可以看到一个多对一关系中，要求至少两个参数：模型要关联的类、on_delete选项。
    # CASCADE：级联删除，模仿SQL约束ON DELETE CASCADE ，同时删除关联数据；
    # PROTECT：防止删除，当删除关联数据时，报错（ProtectedError）；
    # SET_NULL：当删除关联数据时，将外键设置为null ；
    # SET_DEFAULT：当删除关联数据时，将外键设置为默认值，该默认值必须设置；
    # SET()：通过执行SET中的方法，获取返回的值；
    # DO_NOTHING：什么都不做。
    category = models.ForeignKey(Category,on_delete=models.CASCADE)

    def __unicode__(self):
        return u'Goods:%s'%self.gname

    #获取商品预览图
    def getGImg(self):
        return self.inventory_set.first().color.colorurl

class GoodsDetailName(models.Model):
    gdname = models.CharField(max_length=30)

    def __unicode__(self):
        return u'GoodsDetailName'%self.gdname

class GoodsDetail(models.Model):
    gdurl = models.ImageField(upload_to='')
    gdname = models.ForeignKey(GoodsDetailName,on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods,on_delete=models.CASCADE)

class Size(models.Model):
    sname = models.CharField(max_length=10)

    def __unicode__(self):
        return u'Size'%self.sname

class Color(models.Model):
    colorname = models.CharField(max_length=10)
    colorurl = models.ImageField(upload_to='color/')

class Inventory(models.Model):
    count = models.PositiveIntegerField()
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)