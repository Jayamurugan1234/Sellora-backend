from django.utils import timezone
from django.http import HttpResponse
from django.core import signing
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer, AdminOrderSerializer, SellerOrderItemSerializer
from .emails import send_seller_order_notification, verify_approve_token


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        items = cart.items.select_related("product")
        total = sum(item.subtotal() for item in items)

        order = Order.objects.create(
            customer=request.user,
            total_amount=total,
            address=request.data.get("address", "")
        )

        for item in items:
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                owner=item.product.owner,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
            )
            item.product.stock = max(0, item.product.stock - item.quantity)
            item.product.save()

            # Notify the seller by email — includes both a one-click approve
            # link and a reminder they can approve from their dashboard.
            send_seller_order_notification(order_item)

        items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class MyOrdersListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by("-created_at")


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)



class BuyNowView(APIView):
    """Direct purchase — bypasses the cart entirely."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from products.models import Product

        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        product = Product.objects.filter(id=product_id, is_approved=True).first()

        if not product:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        if product.stock < quantity:
            return Response({"detail": "Not enough stock."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            customer=request.user,
            total_amount=product.price * quantity,
            address=request.data.get("address", "")
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            owner=product.owner,
            quantity=quantity,
            price_at_purchase=product.price,
        )
        product.stock -= quantity
        product.save()

        # Notify the seller by email
        send_seller_order_notification(order_item)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class AdminOrdersListView(generics.ListAPIView):
    """Admin-only: every order across every customer, newest first."""
    serializer_class = AdminOrderSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return (
            Order.objects
            .select_related("customer")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )



class AdminDeleteOrderView(generics.DestroyAPIView):
    """Admin-only: delete any order, regardless of which customer placed it."""
    queryset = Order.objects.all()
    serializer_class = AdminOrderSerializer
    permission_classes = [permissions.IsAdminUser]


class SellerOrdersView(generics.ListAPIView):
    """Seller-only: order items belonging to this seller's products, across all customers."""
    serializer_class = SellerOrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(
            owner=self.request.user
        ).select_related("order", "order__customer", "product").order_by("-order__created_at")


def _approve_item_and_maybe_confirm_order(item):
    """Shared logic used by both the dashboard button and the email link."""
    if not item.approved:
        item.approved = True
        item.approved_at = timezone.now()
        item.save()

        order = item.order
        if not order.items.filter(approved=False).exists():
            order.status = Order.Status.CONFIRMED
            order.save()

    item.refresh_from_db()
    return item


class SellerApproveOrderItemView(APIView):
    """
    Dashboard approve button (requires login).
    Seller-only: approve their own order item.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            item = OrderItem.objects.select_related("order", "owner", "product").get(pk=pk)
        except OrderItem.DoesNotExist:
            return Response({"detail": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

        if item.owner != request.user:
            return Response(
                {"detail": "You do not have permission to approve this order item."},
                status=status.HTTP_403_FORBIDDEN,
            )

        item = _approve_item_and_maybe_confirm_order(item)
        return Response(SellerOrderItemSerializer(item).data, status=status.HTTP_200_OK)


class EmailApproveOrderItemView(APIView):
    """
    Public, one-click approve link clicked directly from the seller's email.
    No login required — the signed, time-limited token IS the credential,
    the same pattern most "approve via email" flows use.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # skip JWT auth entirely for this public link

    def get(self, request, token):
        try:
            item_id = verify_approve_token(token)
        except signing.SignatureExpired:
            return self._html_response(
                "This approval link has expired. Please log in to your Sellora "
                "dashboard to approve this order instead.",
                success=False,
            )
        except signing.BadSignature:
            return self._html_response("This approval link is invalid.", success=False)

        try:
            item = OrderItem.objects.select_related("order", "product").get(pk=item_id)
        except OrderItem.DoesNotExist:
            return self._html_response("Order item not found.", success=False)

        item = _approve_item_and_maybe_confirm_order(item)

        return self._html_response(
            f"Order approved: {item.quantity} × {item.product.name} "
            f"(Order #{item.order.id}).",
            success=True,
        )

    def _html_response(self, message, success=True):
        color = "#1db954" if success else "#b3432f"
        heading = "✓ Approved" if success else "Action Needed"
        html = f"""
        <html>
        <head><title>Sellora — Order Approval</title></head>
        <body style="font-family: Arial, sans-serif; background:#faf8f2; padding:60px 20px; text-align:center;">
          <div style="max-width:420px; margin:0 auto; background:#fff; border-radius:12px;
                      padding:32px; border:1px solid #e6e2d8;">
            <h2 style="color:{color};">{heading}</h2>
            <p style="color:#333;">{message}</p>
            <a href="http://localhost:5173/orders"
               style="display:inline-block; margin-top:16px; color:#1db954;
                      text-decoration:none; font-weight:bold;">
              Go to Sellora Dashboard →
            </a>
          </div>
        </body>
        </html>
        """
        return HttpResponse(html)
