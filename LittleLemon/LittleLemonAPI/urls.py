from django.urls import path

from .views import ManagerGroupView, SingleManagerView, DeliveryCrewGroupView, SingleDeliveryCrewView, MenuItemView, \
    CategoryView, SingleMenuItemView, CartView, OrdersView

urlpatterns = [
    path('groups/manager/users', ManagerGroupView.as_view(), name='manager_group'),
    path('groups/manager/users/<str:username>', SingleManagerView.as_view(), name='single_manager'),
    path('groups/delivery-crew/users', DeliveryCrewGroupView.as_view(), name='deliverycrew_group'),
    path('groups/delivery-crew/users/<str:username>', SingleDeliveryCrewView.as_view(), name='single_deliverycrew'),

    path('category', CategoryView.as_view(), name='categories'),

    path('menu-items', MenuItemView.as_view(
        {'get': 'list', 'post': 'create', 'put': 'update', 'delete': 'destroy', 'patch': 'partial_update'}
    ), name='menu_items'),
    path('menu-items/<int:pk>', SingleMenuItemView.as_view(),
        name='single_menu_item'),

    path('cart/menu-items', CartView.as_view(), name='cart'),

    path('orders', OrdersView.as_view(), name='orders'),

]