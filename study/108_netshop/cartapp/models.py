# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from userapp.models import UserInfo


class CartItem(models.Model):
    goodsid=models.PositiveIntegerField()
    colorid=models.PositiveIntegerField()
    sizeid=models.PositiveIntegerField()
    count=models.PositiveIntegerField()
    isdelete=models.BooleanField(default=False)
    user=models.ForeignKey(UserInfo, on_delete=models.CASCADE)




