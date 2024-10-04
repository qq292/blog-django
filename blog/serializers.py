
from rest_framework import serializers, viewsets,generics
from blog.models import CustomUser as User
from blog.models import Article,ArticleSet,ArticleTags
from rest_framework.authentication import SessionAuthentication, BasicAuthentication  
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.response import Response
from blog.permissions import IsAuthenticatedOrReadOnlyOrWirte,IsAuthenticatedWithWirte,ReadPublic_WriteSelf,IsAdminUserOrReadOnly
from django.utils.timesince import timesince
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAuthenticatedOrReadOnly,IsAdminUser
from rest_framework import status
from rest_framework.pagination import PageNumberPagination



# 人类可阅读的时间日期
class TimeSerializer(serializers.HyperlinkedModelSerializer):
    created_date = serializers.SerializerMethodField()
    last_modified = serializers.SerializerMethodField()
    def get_created_date(self,obj):
        return timesince(obj.created_date)
    def get_last_modified(self,obj):
        return timesince(obj.last_modified) 
   

#分页类
class CustomPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'  
    max_page_size = 50  
   


from rest_framework import serializers

class CsrfExemptSessionAuthentication(SessionAuthentication): 
    def enforce_csrf(self, request): 
        return  # To not perform the csrf check previously happening

# 用户
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}, 'url': {'view_name': 'user-detail'}}


from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty
)
from rest_framework.relations import Hyperlink, PKOnlyObject 
from captcha.fields import CaptchaField
# 用户
class UserCreateSerializer(UserSerializer):
    captcha = serializers.ListField(
        child=serializers.CharField(),  
        allow_empty=True, 
        required=True
        
    )
    class Meta(UserSerializer.Meta):
        fields = ('url', 'username', 'email', 'password','captcha')
        extra_kwargs = {'captcha': {'write_only': True},'password': {'write_only': True}, 'url': {'view_name': 'user-detail'}}
        
    def create(self, validated_data):
        validated_data.pop('captcha',None)
        user = User(**validated_data) 
        user.set_password(validated_data['password'])
        user.save() 
        return user
    def validate_captcha(self, value):
        captcha_field = CaptchaField()
        try:
            captcha_field.clean(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError("验证码无效或已过期。")
        return value
    
    def to_representation(self, instance):
        ret = {}
        fields = self._readable_fields
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except AttributeError:
                continue
            except SkipField:
                continue
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)
        return ret
    
# 超级用户
class SuperUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        extra_kwargs = {'url': {'view_name': 'superuser-detail'}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.is_superuser = True
        user.is_staff = True
        user.set_password(validated_data['password'])
        user.save()
        return user        


class ArticleSerializer(TimeSerializer):
    class Meta:
        model = Article
        fields = ['id','url','title','content','article_set','user','created_date','last_modified','public','tag']


    
class ArticleListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ['id','url','title','description','created_date','last_modified','public','tag']
    
        
class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ArticleTags   
        fields=['tag_name','id','url']


class ArticleTagListSerializer(TimeSerializer):
    class Meta:
        model = Article
        fields = ['id','url','title','description','created_date','last_modified','public']

class TagArticleListSerializer(serializers.ModelSerializer):
    article_set = ArticleTagListSerializer(many=True,read_only=False,required=False)
    class Meta:
        model = ArticleTags
        fields = ['tag_name','id','url','article_set']
    
        



class ArticleSetSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.SerializerMethodField()
    class Meta:
        model = ArticleSet
        fields = ['id','url','title','description','created_date','last_modified','username']
    
    def get_username(self,obj):
        return obj.user.username
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)
    


class TagsViewSet(viewsets.ModelViewSet):
    queryset = ArticleTags.objects.all()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,OAuth2Authentication)
    serializer_class = TagArticleListSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        _queryset = instance.article_set.all()
        paginator = CustomPagination()  
        page = paginator.paginate_queryset(_queryset, request)  
        serializer = ArticleTagListSerializer(page, many=True,context={'request': request})
        if page is not None:
            return paginator.get_paginated_response(serializer.data)  
        
        return Response(serializer.data)

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,OAuth2Authentication)
    permission_classes = [IsAuthenticatedOrReadOnly]


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,OAuth2Authentication)
    permission_classes = [AllowAny]  # 允许任何人访问
    
    def perform_create(self, serializer):
        serializer.validated_data.pop('captcha', None)
        serializer.save()
    

class SuperUserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,OAuth2Authentication)
    serializer_class = SuperUserSerializer
    permission_classes = [IsAdminUser]  # 仅允许管理员访问

    
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-id')
    serializer_class = ArticleSerializer
    authentication_classes = (OAuth2Authentication,CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = [ReadPublic_WriteSelf]
    pagination_class = CustomPagination
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = ArticleTagListSerializer(page, many=True,context={'request': request})
        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    
    def create_Article(self,request,pk):
        data ={'error':'你没有权限创建文章.'}
        statu=status.HTTP_403_FORBIDDEN
        try:
            articleSet=ArticleSet.objects.get(pk=pk)
            if articleSet.user == request.user:
                instance = self.queryset.create(article_set=articleSet,user=request.user,title=request.data['title'])
                serializer = self.get_serializer(instance)
                data = serializer.data
                statu = status.HTTP_201_CREATED
        except Exception as e:
            data = {'error':e.args}
        
        return Response(data,statu)
    
    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        
        if not(request.user and request.user.is_staff) and (not article.public and request.user != article.user):
            return Response({'error':'未公开文章，仅管理员与作者自己可见..'},status=status.HTTP_403_FORBIDDEN)
            
    
        return Response(self.get_serializer(article).data,status=status.HTTP_200_OK)
    
    
class ArticleSetViewSet(viewsets.ModelViewSet):
    queryset = ArticleSet.objects.all()
    serializer_class = ArticleSetSerializer
    permission_classes =[IsAuthenticatedWithWirte]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,OAuth2Authentication)
    
    def article_list(self,request,pk):
        a_set = self.queryset.get(pk=pk)
        as_set=a_set.article_set.all()
        serializer = ArticleListSerializer(as_set,many=True,context={'request': request})
        return Response(serializer.data)
    
    
 