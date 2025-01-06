from contextlib import nullcontext

from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from djoser.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics, viewsets, throttling

from .permissions import IsManager, IsDeliveryCrew, IsCustomerOrDeliveryCrew, IsCustomer
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer

class ManagerGroupView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        managers = User.objects.filter(groups__name='Manager')
        serialized_data = UserSerializer(managers, many=True)
        return Response(serialized_data.data, status= status.HTTP_200_OK)

    def post(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            manager_grp = Group.objects.get(name='Manager')
            manager_grp.user_set.add(user)
            return Response({"message":"Manager added!!"}, status=status.HTTP_200_OK)
        return Response({"message":"Missing or invalid username"},
                        status=status.HTTP_400_BAD_REQUEST)

class SingleManagerView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, username):
        manager = get_object_or_404(User, username=username)
        #Checking if user is a manager
        if not manager.groups.filter(name='Manager').exists():
            return Response({"message": "User is not a manager!!"}, status=status.HTTP_400_BAD_REQUEST)
        serialized_data = UserSerializer(manager)
        return Response(serialized_data.data, status= status.HTTP_200_OK)

    def delete(self, request, username):
        manager = get_object_or_404(User, username=username)
        manager_grp = Group.objects.get(name='Manager')
        manager_grp.user_set.remove(manager)
        return Response({"message": "User removed from manager group!!"},status=status.HTTP_200_OK)

class DeliveryCrewGroupView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        delivery_crews = User.objects.filter(groups__name='Delivery crew')
        serialized_data = UserSerializer(delivery_crews, many=True)
        return Response(serialized_data.data, status= status.HTTP_200_OK)

    def post(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew_grp = Group.objects.get(name='Delivery crew')
            delivery_crew_grp.user_set.add(user)
            return Response({"message":"Delivery Crew added!!"}, status=status.HTTP_200_OK)
        return Response({"message":"Missing or invalid username"},
                        status=status.HTTP_400_BAD_REQUEST)

class SingleDeliveryCrewView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, username):
        delivery_crew = get_object_or_404(User, username=username)
        #Checking if user is a delivery crew
        if not delivery_crew.groups.filter(name='Delivery crew').exists():
            return Response({"message": "User is not a delivery crew!!"}, status=status.HTTP_400_BAD_REQUEST)
        serialized_data = UserSerializer(delivery_crew)
        return Response(serialized_data.data, status= status.HTTP_200_OK)

    def delete(self, request, username):
        delivery_crew = get_object_or_404(User, username=username)
        delivery_crew_grp = Group.objects.get(name='Delivery crew')
        delivery_crew_grp.user_set.remove(delivery_crew)
        return Response({"message": "User removed from delivery crew group!!"},status=status.HTTP_200_OK)

class MenuItemView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [throttling.UserRateThrottle]
    ordering_fields = ['title', 'price']
    searching_fields = ['title']
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def list(self, request, *args, **kwargs):
        menu_items = MenuItem.objects.all()
        serialized_data = MenuItemSerializer(menu_items, many=True)
        return Response(serialized_data.data, status= status.HTTP_200_OK)


    def update(self, request, *args, **kwargs):
        return Response({"message":"You are not allowed to update menu items!!"},
                        status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super().create(request, *args, **kwargs)
        return Response({"message":"You are not allowed to create menu items!!"},
                        status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        return Response({"message":"You are not allowed to delete menu items!!"},
                        status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        return Response({"message":"You are not allowed to update menu items here!!"},
                        status=status.HTTP_403_FORBIDDEN)

class CategoryView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serialized_data = CategorySerializer(categories, many=True)
        return Response(serialized_data.data, status= status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super().create(request, *args, **kwargs)
        return Response({"message":"You are not allowed to create categories!!"},
                        status=status.HTTP_403_FORBIDDEN)

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [throttling.UserRateThrottle]

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super().update(request, *args, **kwargs)
        return Response({"message":"You are not allowed to update menu items!!"},
                        status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super().destroy(request, *args, **kwargs)
        return Response({"message":"You are not allowed to delete menu items!!"},
                        status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super().partial_update(request, *args, **kwargs)
        return Response({"message":"You are not allowed to update menu items here!!"},
                        status=status.HTTP_403_FORBIDDEN)


class CartView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        cart = Cart.objects.filter(user=request.user)
        serialized_data = CartSerializer(cart, many=True)
        return Response(serialized_data.data, status=status.HTTP_200_OK)

    def post(self, request):
        menu_item_id = request.data['menuitem_id']
        quantity = int(request.data['quantity'])
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        unit_price = menu_item.price
        price = unit_price * quantity
        cart = Cart(user=request.user, menuitem=menu_item, quantity=quantity, unit_price=unit_price, price=price)
        cart.save()
        return Response({"message":"Item added to cart!!"}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user)
        cart.delete()
        return Response({"message":"Cart cleared!!"}, status=status.HTTP_200_OK)

class OrdersView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [throttling.UserRateThrottle]

    def get(self, request):
        orders = Order.objects.all()
        if request.user.groups.filter(name='Delivery crew').exists():
            orders = orders.filter(delivery_crew=request.user)
        elif request.user.groups.filter(name='Manager').exists():
            pass
        else:
            orders = orders.filter(user=request.user)
        response = {}
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            serialized_data_item = OrderItemSerializer(order_items, many=True)
            response[order.id] = {"order": OrderSerializer(order).data, "order-items": serialized_data_item.data}
        # order_items=OrderItem.objects.filter(order__in=orders)
        # serialized_data = OrderSerializer(orders, many=True)
        # serialized_data_item = OrderItemSerializer(order_items, many=True)
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.groups.filter(name='Delivery crew').exists() or request.user.groups.filter(
                name='Manager').exists():
            return Response({"message": "You are not allowed to create orders!!"},
                            status=status.HTTP_403_FORBIDDEN)

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"message": "Your cart is empty!"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.price for item in cart_items)
        new_order = Order(
            user=request.user,
            total=total_price,
            date=timezone.now()
        )
        new_order.save()

        for item in cart_items:
            OrderItem.objects.create(
                order=new_order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )

        cart_items.delete()
        return Response({"message": "Order created successfully!"}, status=status.HTTP_201_CREATED)

class SingleOrderView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [throttling.UserRateThrottle]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.user != request.user:
            return Response({"message": "You do not have permission to view this order."}, status=status.HTTP_403_FORBIDDEN)

        order_items = OrderItem.objects.filter(order=order)
        serialized_order = OrderSerializer(order)
        serialized_order_items = OrderItemSerializer(order_items, many=True)

        return Response({"order": serialized_order.data, "order-items": serialized_order_items.data}, status=status.HTTP_200_OK)

    def put(self, request,pk):
            if request.user.groups.filter(name='Delivery crew').exists():
                return Response({"message": "You are not allowed to update complete order!!"},status=status.HTTP_403_FORBIDDEN)
            order = get_object_or_404(Order, pk=pk)
            if request.user.groups.filter(name='Manager').exists():
                delivery_crew_id = request.data.get('delivery_crew_id')
                or_status = request.data.get('status')

                if delivery_crew_id is not None:
                    delivery_crew = get_object_or_404(User, id=delivery_crew_id)
                    order.delivery_crew = delivery_crew

                if or_status is not None:
                    if or_status in [0, 1]:
                        order.status = or_status
                    else:
                        return Response({"message": "Invalid status value. It should be 0 or 1."},
                                        status=status.HTTP_400_BAD_REQUEST)

                order.save()
                return Response({"message": "Order updated successfully!"}, status=status.HTTP_200_OK)

            return Response({"message": "You are not allowed to update orders!!"}, status=status.HTTP_403_FORBIDDEN)


    def patch(self, request, pk):
            order = get_object_or_404(Order, pk=pk)
            if request.user.groups.filter(name='Manager').exists():
                delivery_crew_id = request.data.get('delivery_crew_id')
                or_status = request.data.get('status')

                if delivery_crew_id is not None:
                    delivery_crew = get_object_or_404(User, id=delivery_crew_id)
                    order.delivery_crew = delivery_crew

                if or_status is not None:
                    if or_status in [0, 1]:
                        order.status = or_status
                    else:
                        return Response({"message": "Invalid status value. It should be 0 or 1."},
                                        status=status.HTTP_400_BAD_REQUEST)

                order.save()
                return Response({"message": "Order updated successfully!"}, status=status.HTTP_200_OK)
            if request.user.groups.filter(name='Delivery crew').exists():

                or_status = request.data.get('status')

                if or_status is not None:
                    if or_status in [0, 1]:
                        order.status = or_status
                        order.save()
                        return Response({"message": "Order status updated successfully!"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message": "Invalid status value. It should be 0 or 1."},
                                        status=status.HTTP_400_BAD_REQUEST)
                return Response({"message": "Status value is required."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "You are not allowed to update orders!!"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            order = get_object_or_404(Order, pk=pk)
            order.delete()
            return Response({"message": "Order deleted successfully!"}, status=status.HTTP_200_OK)
        return Response({"message": "You are not allowed to delete orders!!"}, status=status.HTTP_403_FORBIDDEN)


