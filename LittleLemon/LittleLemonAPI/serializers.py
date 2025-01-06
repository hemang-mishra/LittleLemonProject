from django.contrib.auth.models import User
from djoser.serializers import UserSerializer
from rest_framework.validators import UniqueValidator

from .models import Order, OrderItem, MenuItem, Cart, Category
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']
        extra_kwargs = {
            'title': {
                'validators': [UniqueValidator(queryset=Category.objects.all())]
            }
        }


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category',
                                                     write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    menuitem = MenuItemSerializer()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    menuitem_id = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), source='menuitem',
                                                     write_only=True)

    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price', 'user_id', 'menuitem_id']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    delivery_crew = UserSerializer()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    delivery_crew_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='delivery_crew',
                                                          write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'user_id', 'delivery_crew_id']


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), source='order', write_only=True)
    menuitem_id = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), source='menuitem',
                                                     write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price', 'order_id', 'menuitem_id']
