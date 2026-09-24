from rest_framework import permissions

class OrderPermissons(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        action = getattr(view, 'action', None)
        if action == 'deliver':
            return user.is_staff or getattr(user, 'role', None) == 'Seller'
        if action in ('accept_delivery', 'request_revision'):
            return user.is_staff or getattr(user, 'role', None) == 'Buyer'
        if action == 'cancel':
            return user.is_staff or getattr(user, 'role', None) == 'Buyer'

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

        if getattr(view, 'action', None) == 'deliver':
            return user.is_staff or (user.role == 'Seller' and obj.service.seller_id == user.id)
        if getattr(view, 'action', None) in ('accept_delivery', 'request_revision'):
            return user.is_staff or (user.role == 'Buyer' and obj.buyer_id == user.id)
        if getattr(view, 'action', None) == 'cancel':
            return user.is_staff or (user.role == 'Buyer' and obj.buyer_id == user.id)

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
