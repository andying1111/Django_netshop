from ..app01 import views
from django.urls import path

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',views.publisher_list),
    path('',views.add_publisher),
]