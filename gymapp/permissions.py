from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    allowed_roles = set()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role in self.allowed_roles)


class IsAdmin(RolePermission):
    allowed_roles = {"admin"}


class IsStaffRole(RolePermission):
    allowed_roles = {"admin", "coach", "reception"}
