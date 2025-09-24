from rest_framework import permissions

class OrderPermissons(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser or user.is_staff:
            if request.method == 'POST':
                return False
            return True

        if request.method == 'POST' and getattr(user, 'role', None) == 'Buyer':
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True

        return False
    
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        if user.role == 'Seller':
            if request.method in permissions.SAFE_METHODS:
                return obj.service.seller == user
            return False  # Seller cannot modify

        if user.role == 'Buyer':
            if request.method in permissions.SAFE_METHODS:
                return obj.buyer == user
            if request.method == 'DELETE':
                return obj.buyer == user
            return False

        return False
