from django.urls import path
from .views import RegisterView, MeView, PendingOwnersListView, ApproveOwnerView, RequestPasswordResetView, ConfirmPasswordResetView, AdminCustomerListView, AdminSellerListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("pending-owners/", PendingOwnersListView.as_view(), name="pending_owners"),
    path("approve-owner/<int:pk>/", ApproveOwnerView.as_view(), name="approve_owner"),
    path("request-password-reset/", RequestPasswordResetView.as_view(), name="request_password_reset"),
    path("confirm-password-reset/", ConfirmPasswordResetView.as_view(), name="confirm_password_reset"),
    path("admin/customers/", AdminCustomerListView.as_view(), name="admin_customers"),
    path("admin/sellers/", AdminSellerListView.as_view(), name="admin_sellers"),

]