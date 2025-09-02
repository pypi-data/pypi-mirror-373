from rest_framework.permissions import IsAuthenticated


class IsCommissionAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.has_perm("wbcommission.administrate_commission")
