from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "added_at", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]

    def get_total_price(self, obj):
        return obj.total_price()
    

class AdminCartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    username = serializers.CharField(source="cart.user.username", read_only=True)
    email = serializers.CharField(source="cart.user.email", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "username", "email", "product_name", "quantity", "added_at"]



# class SellerCartItemSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source="cart.user.username")
#     product_name = serializers.CharField(source="product.name")

#     class Meta:
#         model = CartItem
#         fields = ["id", "username", "product_name", "quantity"]


class SellerCartItemSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="cart.user.username")
    email = serializers.CharField(source="cart.user.email")
    product_name = serializers.CharField(source="product.name")

    class Meta:
        model = CartItem
        fields = ["id", "username", "email", "product_name", "quantity", "added_at"]