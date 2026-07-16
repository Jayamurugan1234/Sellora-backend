from rest_framework import generics, permissions
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer, ProductImageSerializer,ProductImageUploadSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
import re

from rest_framework.pagination import PageNumberPagination

class ProductPagination(PageNumberPagination):
    page_size = 20


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ProductPagination 

    def get_queryset(self):
        qs = Product.objects.filter(is_approved=True)
        search = self.request.query_params.get("search", "")
        category = self.request.query_params.get("category", "")
        min_price = self.request.query_params.get("min_price", "")
        max_price = self.request.query_params.get("max_price", "")
        sort = self.request.query_params.get("sort", "")

        if search:
            qs = qs.filter(name__icontains=search)
        if category:
            qs = qs.filter(category__slug=category)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if sort == "price_asc":
            qs = qs.order_by("price", "id")
        elif sort == "price_desc":
            qs = qs.order_by("-price", "id")
        elif sort == "newest":
            qs = qs.order_by("-created_at", "id")
        else:
            qs = qs.order_by("-created_at", "id")  # default ordering — required for stable pagination

        return qs

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_approved=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class MyProductListCreateView(generics.ListCreateAPIView):
    """Owner-only: list/create their own products."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # serializer.save(owner=self.request.user)
        serializer.save(owner=self.request.user, is_approved=True)


class MyProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Owner-only: edit/delete their own product."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)
    

class PendingProductsListView(generics.ListAPIView):
    """Admin-only: list products awaiting approval."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Product.objects.filter(is_approved=False)


class ApproveProductView(generics.UpdateAPIView):
    """Admin-only: approve a specific product."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_approved = True
        product.save()
        return Response(ProductSerializer(product).data)
    

class ProductImageUploadView(generics.CreateAPIView):
    serializer_class = ProductImageUploadSerializer  # ← changed
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        product_id = self.request.data.get("product")
        product = Product.objects.filter(id=product_id, owner=self.request.user).first()
        if not product:
            raise PermissionDenied("You can only upload images for your own products.")
        serializer.save(product=product)


class CategoryGetOrCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"error": "Name required"}, status=400)
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        category, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
        return Response({"id": category.id, "name": category.name})
    


class AdminProductDeleteView(generics.DestroyAPIView):
    """Admin-only: delete any product outright."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]