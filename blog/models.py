from django.db import models
from django.contrib.auth.models import  AbstractBaseUser, BaseUserManager, PermissionsMixin,AbstractUser
# Create your models here.



class CustomUser(AbstractUser):
    zfb = models.CharField(blank=True, null=True, max_length=100)
    wx = models.CharField(blank=True, null=True, max_length=100)
    def __str__(self) -> str:
        return str(self.username)

    
class ArticleSet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(blank=False, null=False,max_length=60,verbose_name="标题")
    description = models.TextField(null=True,verbose_name="描述")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.title
class ArticleTags(models.Model):
    tag_name = models.CharField(blank=False, null=False,max_length=24,verbose_name="标签名", unique=True)

    def __str__(self) -> str:
        return self.tag_name
    
class Article(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    title = models.CharField(blank=False, null=False,max_length=60,verbose_name="标题")
    description = models.TextField(null=True,verbose_name="描述")
    content =  models.TextField(verbose_name="正文",null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    article_set = models.ForeignKey(ArticleSet,null=True,on_delete=models.SET_NULL)
    tag = models.ManyToManyField(ArticleTags,default=None,blank=True)
    def __str__(self) -> str:
        return self.title



