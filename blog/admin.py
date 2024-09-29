from django.contrib import admin
from blog.models import CustomUser,Article
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Article)
