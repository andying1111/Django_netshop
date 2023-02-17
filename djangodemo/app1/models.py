
from django.db import models


# Create your models here.

# 出版社类
class Publisher(models.Model):
    id = models.AutoField('序号',primary_key=True)
    name = models.CharField('名称',max_length=64)
    addr = models.CharField('地址',max_length=64)


class Book(models.Model):
    # 书名
    bookName = models.CharField(max_length=100, blank=True)
    # 分类
    type = models.CharField(max_length=20, blank=True)
    # 出版社
    bookAddress = models.CharField(max_length=200, blank=True)
    # 出版日期
    bookDate = models.CharField(max_length=100, blank=True)
    # 作者
    author = models.CharField(max_length=100, blank=True)
    # 详情信息
    info = models.TextField()
    # 图片地址
    image = models.CharField(max_length=100, blank=True)


class Student(models.Model):
    # 学号
    number = models.CharField(max_length=10, blank=True)
    # 姓名
    name = models.CharField(max_length=20, blank=True)
    # 密码
    psd = models.CharField(max_length=20, blank=True)
    # 手机号
    phone = models.CharField(max_length=11, blank=True)


# 借阅信息表
class UserBookInfo(models.Model):
    # 学号
    number = models.CharField(max_length=10, blank=True)
    # 图书id
    bookId = models.IntegerField()
    # 借阅开始时间
    startDate = models.CharField(max_length=100, blank=True)
    # 借阅结束时间
    endDate = models.CharField(max_length=100, blank=True)
    # 借阅状态
    state = models.IntegerField()