from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def __init__(self):
        self.group_name = 'Manager'

    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name=self.group_name).exists()

class IsDeliveryCrew(BasePermission):
    def __init__(self):
        self.group_name = 'Delivery crew'

    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name=self.group_name).exists()

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and not request.user.groups.exists()

class IsCustomerOrDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user and (not request.user.groups.exists() or request.user.groups.filter(name='Delivery crew').exists())