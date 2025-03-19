"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers, permissions
from django.conf import settings
from django.contrib.staticfiles.urls import static, staticfiles_urlpatterns
from django.urls import include
import os
from dotenv import load_dotenv
from api.views import FileUploadViewSet, CompanyViewSet, EmployeeViewSet

load_dotenv()

schema_view = get_schema_view(
    openapi.Info(
        title="Excel To Database API",
        default_version='v1',
        description="Excel To Database API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url= os.getenv('API_URL')
)

router = routers.DefaultRouter()
router.register(r'upload', FileUploadViewSet, basename='upload')
router.register(r'companies', CompanyViewSet)
router.register(r'employees', EmployeeViewSet)
re_path(
    r'^swagger(?P<format>\.json|\.yaml)$',
    schema_view.without_ui(cache_timeout=0),
    name='schema-json'
),
re_path(
    r'^swagger/$',
    schema_view.with_ui('swagger', cache_timeout=0),
    name='schema-swagger-ui'
),
re_path(
    r'^redoc/$',
    schema_view.with_ui('redoc', cache_timeout=0),
    name='schema-redoc'
),

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)