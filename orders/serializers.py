from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price_at_purchase", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total_amount", "address", "items", "created_at"]


class AdminOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "price_at_purchase"]


class AdminOrderSerializer(serializers.ModelSerializer):
    items = AdminOrderItemSerializer(many=True, read_only=True)
    customer_username = serializers.CharField(source="customer.username", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "customer_username", "customer_email",
            "status", "total_amount", "address", "created_at", "items"
        ]


class SellerOrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id")
    customer_username = serializers.CharField(source="order.customer.username")
    product_name = serializers.CharField(source="product.name")
    order_date = serializers.DateTimeField(source="order.created_at")
    status = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "order_id", "customer_username", "product_name",
            "quantity", "price_at_purchase", "order_date", "status",
            "approved", "approved_at",
        ]

    def get_status(self, obj):
        """
        Per-item status from THIS seller's point of view — not the whole
        order's shared status. An order can contain products from multiple
        sellers, and the order only becomes CONFIRMED once every seller has
        approved. From a single seller's perspective, once they've approved
        their own item it should read CONFIRMED regardless of what other
        sellers on the same order have or haven't done yet.

        If the order has moved further (SHIPPED/DELIVERED/CANCELLED) via
        some other flow, that takes precedence and is shown as-is.
        """
        order_status = obj.order.status
        if order_status != Order.Status.PENDING:
            return order_status
        return Order.Status.CONFIRMED if obj.approved else Order.Status.PENDING