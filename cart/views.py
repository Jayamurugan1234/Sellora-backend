from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from products.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer, AdminCartItemSerializer, SellerCartItemSerializer


class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        product = Product.objects.filter(id=product_id, is_approved=True).first()
        if not product:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
        item.reminder_sent = False
        item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()
        if not item:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        new_qty = int(request.data.get("quantity", item.quantity))
        if new_qty <= 0:
            item.delete()
            return Response({"detail": "Item removed."}, status=status.HTTP_200_OK)

        item.quantity = new_qty
        item.save()
        return Response(CartSerializer(item.cart).data, status=status.HTTP_200_OK)


class RemoveFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()
        if not item:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"detail": "Item removed."}, status=status.HTTP_200_OK)
    
class AdminCartOverviewView(generics.ListAPIView):
    """Admin-only: every cart item across every user, newest first."""
    serializer_class = AdminCartItemSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return (
            CartItem.objects
            .select_related("cart__user", "product")
            .order_by("-added_at")
        )
    

class AdminRemoveCartItemView(APIView):
    """Admin-only: remove any user's cart item, regardless of ownership."""
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, item_id):
        item = CartItem.objects.filter(id=item_id).first()
        if not item:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"detail": "Item removed."}, status=status.HTTP_200_OK)
    


class SellerCartItemsView(generics.ListAPIView):
    """Seller-only: shows every cart item, across all users, for products this seller owns."""
    serializer_class = SellerCartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from cart.models import CartItem  # adjust import if CartItem lives elsewhere
        return CartItem.objects.filter(
            product__owner=self.request.user
        ).select_related("product", "cart__user").order_by("-id")
