from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from .models import CartItem
from notifications.models import Notification

REMINDER_DELAY = timedelta(hours=2)   # short delay for testing — change to hours/days later


@shared_task
def check_abandoned_carts():
    cutoff = timezone.now() - REMINDER_DELAY
    stale_items = CartItem.objects.filter(
        added_at__lte=cutoff,
        reminder_sent=False
    ).select_related("cart__user", "product")

    users_to_notify = {}
    for item in stale_items:
        users_to_notify.setdefault(item.cart.user, []).append(item)

    for user, items in users_to_notify.items():
        product_names = ", ".join(i.product.name for i in items)

        send_mail(
            subject="You left something in your cart!",
            message=f"Hi {user.username}, you still have {product_names} waiting in your cart. Complete your order!",
            from_email="noreply@sellora.com",
            recipient_list=[user.email] if user.email else [],
            
        )
        Notification.objects.create(
            user=user,
            title="You left something in your cart!",
            message=f"You still have {product_names} waiting in your cart. Complete your order!"
        )

        for item in items:
            item.reminder_sent = True
        CartItem.objects.bulk_update(items, ["reminder_sent"])

    return f"Checked {len(stale_items)} stale items, notified {len(users_to_notify)} users."