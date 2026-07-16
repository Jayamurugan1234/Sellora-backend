from django.urls import path
from .views import (
    ProductListView, ProductDetailView, CategoryListView,
    MyProductListCreateView, MyProductDetailView,
    PendingProductsListView, ApproveProductView, ProductImageUploadView, CategoryGetOrCreateView,
    AdminProductDeleteView,
)

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("mine/", MyProductListCreateView.as_view(), name="my_products"),
    path("mine/<int:pk>/", MyProductDetailView.as_view(), name="my_product_detail"),
    path("pending/", PendingProductsListView.as_view(), name="pending_products"),
    path("approve/<int:pk>/", ApproveProductView.as_view(), name="approve_product"),
    path("upload-image/", ProductImageUploadView.as_view(), name="upload_image"),
    path("categories/get-or-create/", CategoryGetOrCreateView.as_view(), name="category_get_or_create"),
    path("admin/delete/<int:pk>/", AdminProductDeleteView.as_view(), name="admin_delete_product"),

    path("<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
]