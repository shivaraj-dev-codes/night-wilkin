from rest_framework.permissions import BasePermission


class IsWalker(BasePermission):
    """Permission to check if user is a walker"""
    message = "Only walkers can access this resource."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_walker()


class IsGuardian(BasePermission):
    """Permission to check if user is a guardian"""
    message = "Only guardians can access this resource."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_guardian()


class IsVerifiedUser(BasePermission):
    """Permission to check if user is verified"""
    message = "Only verified users can access this resource."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_verified


class IsOwnerOrReadOnly(BasePermission):
    """Permission to check if user owns the object"""
    message = "You do not have permission to modify this resource."
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'walker'):
            return obj.walker == request.user
        return False


class IsWalkerOwner(BasePermission):
    """Permission to verify walker owns the session/alert"""
    message = "You can only access your own sessions and alerts."
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'walker'):
            return obj.walker == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsGuardianOfWalker(BasePermission):
    """Permission to check if guardian is linked to walker"""
    message = "You are not a guardian of this walker."
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_guardian()):
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'walker'):
            walker = obj.walker
        elif hasattr(obj, 'user'):
            walker = obj.user
        else:
            return False
        
        return request.user in walker.guardians.all()
