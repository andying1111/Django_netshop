from django.http import HttpResponse
from django.shortcuts import render

from .models import Publisher


# Create your views here.
def test(request):
    student_name = ["卢本伟"]
    # return render(request,"demo1.html",{"student_list":student_name})
    return render(request,"demo2.html")

def add_pub(request):
    return render(request,"add_pub.html")


def Pubadd(request):
    # bd = Publisher

    # if request.method == "POST":
    name = request.POST.get("name")
    addr = request.POST.get("addr")
    Publisher.objects.create(name = name,addr = addr)
    # print(name)
    # bd.name = name
    # bd.addr = addr
    # bd.save()
    return HttpResponse('succer')


