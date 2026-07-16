from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="cart_detail"),
    path("add/<int:product_id>/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("update/<int:item_id>/", views.UpdateCartItemView.as_view(), name="update_cart_item"),
    path("remove/<int:item_id>/", views.RemoveFromCartView.as_view(), name="remove_from_cart"),
    path("admin/all/", views.AdminCartOverviewView.as_view(), name="admin_cart_overview"),
    path("seller/items/", views.SellerCartItemsView.as_view(), name="seller_cart_items"),

    path("admin/remove/<int:item_id>/", views.AdminRemoveCartItemView.as_view(), name="admin_remove_cart_item"),
]
