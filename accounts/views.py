from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer, AdminCustomerSerializer, AdminSellerSerializer
from .models import CustomUser
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework import status


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    

class PendingOwnersListView(generics.ListAPIView):
    """Admin-only: list owners awaiting approval."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return CustomUser.objects.filter(role="OWNER", is_owner_approved=False)


class ApproveOwnerView(generics.UpdateAPIView):
    """Admin-only: approve a specific owner."""
    queryset = CustomUser.objects.filter(role="OWNER")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, *args, **kwargs):
        owner = self.get_object()
        owner.is_owner_approved = True
        owner.save()
        return Response(UserSerializer(owner).data)
    

class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user = CustomUser.objects.filter(email=email).first()

        # Always return success, even if email doesn't exist — avoids leaking which emails are registered
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"http://localhost:5173/reset-password/{uid}/{token}/"

            send_mail(
                subject="Reset your Sellora password",
                message=f"Hi {user.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, ignore this email.",
                from_email="noreply@sellora.com",
                recipient_list=[user.email],
            )

        return Response(
            {"detail": "If that email exists, a reset link has been sent."},
            status=status.HTTP_200_OK
        )


class ConfirmPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=user_id)
        except (CustomUser.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "This reset link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)

        if not new_password or len(new_password) < 8:
            return Response({"detail": "Password must be at least 8 characters."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
    
class AdminCustomerListView(generics.ListAPIView):
    """Admin-only: every customer with their order history."""
    serializer_class = AdminCustomerSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return (
            CustomUser.objects.filter(role="CUSTOMER")
            .prefetch_related("orders__items__product")
            .order_by("-date_joined")
        )


class AdminSellerListView(generics.ListAPIView):
    """Admin-only: every seller/owner with their uploaded products."""
    serializer_class = AdminSellerSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return (
            CustomUser.objects.filter(role="OWNER")
            .select_related("owner_profile")
            .prefetch_related("products")
            .order_by("-date_joined")
        )

