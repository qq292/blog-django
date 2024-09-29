"""
URL configuration for MyBlog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from oauth2_provider import urls as oauth2_urls
from django.contrib import admin
from django.urls import path,include
from captcha import views as captcha_views
from rest_framework import routers   
from blog.serializers import UserViewSet,ArticleViewSet,ArticleSetViewSet,TagsViewSet,UserCreateView,SuperUserCreateView
from oauth2_provider.views.base import RevokeTokenView
from django.views.decorators.csrf import csrf_exempt
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'articlesets', ArticleSetViewSet)
router.register(r'tags', TagsViewSet)

urlpatterns = [
    path("list_articleset/<int:pk>/",ArticleSetViewSet.as_view({'get':'article_list'})),
    path("create_article/<int:pk>/",ArticleViewSet.as_view({'post':'create_Article'})),
    
    path('user/', UserCreateView.as_view(), name='user-create'),
    path('user/<int:pk>/', UserCreateView.as_view(), name='user-detail'),
    path('superuser/', SuperUserCreateView.as_view(), name='superuser-create'),
    path('superuser/<int:pk>/', SuperUserCreateView.as_view(), name='superuser-detail'),
    #  path('captcha/', captcha_views.captcha_refresh, name='captcha'),  # 用于获取验证码
    # path('captcha/', include('captcha.urls')),
    path('captcha/refresh/', csrf_exempt(captcha_views.captcha_refresh), name='captcha_refresh'),
     
     
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('blog/',include("blog.urls")),
    path('captcha/', include('captcha.urls')), 
    path('api-auth/', include('rest_framework.urls',namespace='rest_framework')),
    path("o/", include(oauth2_urls)),
    
]

