from rest_framework import serializers
from .models import CustomUser, OwnerProfile
from orders.models import Order, OrderItem, Product

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "phone", "is_owner_approved"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "role", "phone"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=validated_data.get("role", "CUSTOMER"),
            phone=validated_data.get("phone", ""),
        )
        return user
    

class AdminOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "price_at_purchase"]


class AdminOrderSerializer(serializers.ModelSerializer):
    items = AdminOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total_amount", "created_at", "items"]


class AdminCustomerSerializer(serializers.ModelSerializer):
    orders = AdminOrderSerializer(many=True, read_only=True)
    order_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "phone", "date_joined", "order_count", "orders"]

    def get_order_count(self, obj):
        return obj.orders.count()


class AdminSellerProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "is_approved", "created_at"]


class AdminSellerSerializer(serializers.ModelSerializer):
    products = AdminSellerProductSerializer(many=True, read_only=True)
    store_name = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "phone", "store_name", "is_owner_approved", "product_count", "products"]

    def get_store_name(self, obj):
        profile = getattr(obj, "owner_profile", None)
        return profile.store_name if profile else None

    def get_product_count(self, obj):
        return obj.products.count()