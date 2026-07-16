from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("products/", views.OwnerProductListView.as_view(), name="product_list"),
    path("products/add/", views.OwnerProductCreateView.as_view(), name="product_add"),
    path("products/<int:pk>/edit/", views.OwnerProductUpdateView.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", views.OwnerProductDeleteView.as_view(), name="product_delete"),
    path("orders/", views.OwnerOrdersView.as_view(), name="owner_orders"),
]