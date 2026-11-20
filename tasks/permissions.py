from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view, edit, or delete it.
    """
    message = "You do not have permission to access or modify this record."

    def has_object_permission(self, request, view, obj):
        # Read or write permissions are only granted to the owner of the object.
        return obj.user == request.user
