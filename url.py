from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",include('Product.urls')),
    path('api/exam/',include('exam.urls')),  #API前缀
    path('api-auth/',include('rest_framework.urls')) #DRF登录页面
]

# 开发环境下的媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
