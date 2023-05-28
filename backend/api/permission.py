from rest_framework import permissions


class RecipiesPermisionUserAutherAdmin(permissions.BasePermission):
    """Разрешения на доступ к объекту автору или администратору"""
    def has_object_permission(self, request, view, obj):
        return (
            (request.method in permissions.SAFE_METHODS)
            or request.user == obj.author
            or request.user.is_staff
        )
