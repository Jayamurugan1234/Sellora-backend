from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("buy-now/", views.BuyNowView.as_view(), name="buy_now"),
    path("my-orders/", views.MyOrdersListView.as_view(), name="my_orders"),
    path("admin/all/", views.AdminOrdersListView.as_view(), name="admin_all_orders"),
    path("seller/orders/", views.SellerOrdersView.as_view(), name="seller_orders"),
    path("admin/delete/<int:pk>/", views.AdminDeleteOrderView.as_view(), name="admin_delete_order"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("seller/approve/<int:pk>/", views.SellerApproveOrderItemView.as_view(), name="seller_approve_order_item"),
    # NEW: public, no-login link clicked from the seller's email
    path("email-approve/<str:token>/", views.EmailApproveOrderItemView.as_view(), name="email_approve_order_item"),
]