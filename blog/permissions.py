from rest_framework.permissions import BasePermission,SAFE_METHODS





'''

只读权限，或者写权限
'''
class IsAuthenticatedOrReadOnlyOrWirte(BasePermission):
    def has_object_permission(self, request, view, obj):
        
        return request.method in SAFE_METHODS or request.user == obj.user
        
        

'''
读权限 公开
写权限 登陆用户自己
'''
class ReadPublic_WriteSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        
        return bool(request.method in SAFE_METHODS or  request.user == obj.user ) 
    # def has_permission(self, request, view):
    #     return bool(request.method in SAFE_METHODS or  request.user == view.user ) 
    

'''
读权限 登陆用户自己
写权限 登陆用户自己

'''
class IsAuthenticatedWithWirte(ReadPublic_WriteSelf):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            view.queryset =  view.queryset.filter(user=request.user)
            return True
        return False
        

class IsAdminUserOrReadOnly(BasePermission):
    """
    读权限是允许所有请求(GET)
    写权限只有管理员才允许(POST等)
    """
    

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or request.user and request.user.is_staff)

























