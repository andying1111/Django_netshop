from django.shortcuts import render, redirect

import models




# Create your views here.

# 出版社展示列表
def publisher_list(request):
    publisher = models.Publisher.objects.all()
    return render(request,'pub_list.html',{'pub_list':publisher})

# 添加出版社
def add_publisher(request):
    if request.method == 'POST':
        new_publisher_name = request.POST.get('name')
        new_publisher_addr = request.POST.get('addr')
        models.Publisher.objects.create(name=new_publisher_name,addr=new_publisher_addr)
        return redirect('/pub_list/')
    return render(request,'pub_add.html')


