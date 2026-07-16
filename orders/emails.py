from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core import signing

APPROVE_SALT = "order-item-approve"
TOKEN_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def generate_approve_token(order_item_id):
    return signing.dumps({"item_id": order_item_id}, salt=APPROVE_SALT)


def verify_approve_token(token, max_age=TOKEN_MAX_AGE):
    """
    Returns the order_item id if the token is valid and unexpired.
    Raises signing.BadSignature or signing.SignatureExpired otherwise.
    """
    data = signing.loads(token, salt=APPROVE_SALT, max_age=max_age)
    return data["item_id"]


def send_seller_order_notification(order_item):
    """
    Notifies the seller of a new pending order — includes BOTH:
      1. A one-click "Approve Order" button (signed link, no login needed)
      2. A reminder they can also approve from their dashboard's Orders page
    """
    product = order_item.product
    seller = order_item.owner
    buyer = order_item.order.customer

    if not seller.email:
        return

    token = generate_approve_token(order_item.id)
    backend_base = getattr(settings, "BACKEND_BASE_URL", "http://127.0.0.1:8000")
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
    approve_url = f"{backend_base}/api/orders/email-approve/{token}/"
    dashboard_url = f"{frontend_base}/orders"

    subject = f"New order for '{product.name}' on Sellora"

    text_body = (
        f"Hi {seller.username},\n\n"
        f"You have a new pending order.\n\n"
        f"Product: {product.name}\n"
        f"Ordered by: {buyer.username}\n"
        f"Quantity: {order_item.quantity}\n"
        f"Order #: {order_item.order.id}\n\n"
        f"Approve directly from this email:\n{approve_url}\n\n"
        f"Or log in to your Sellora seller dashboard and approve it from Orders:\n{dashboard_url}\n\n"
        f"This link expires in 7 days.\n\n"
        f"— Sellora"
    )

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;
                padding: 24px; border: 1px solid #e6e2d8; border-radius: 10px;">
      <h2 style="color:#2f4f3e; margin-top:0;">New Order Pending Approval</h2>
      <p>Hi <strong>{seller.username}</strong>,</p>
      <p>You have a new pending order:</p>
      <table style="width:100%; border-collapse: collapse; margin: 16px 0;">
        <tr><td style="padding:6px 0; color:#888;">Product</td>
            <td style="padding:6px 0; font-weight:bold;">{product.name}</td></tr>
        <tr><td style="padding:6px 0; color:#888;">Ordered by</td>
            <td style="padding:6px 0; font-weight:bold;">{buyer.username}</td></tr>
        <tr><td style="padding:6px 0; color:#888;">Quantity</td>
            <td style="padding:6px 0; font-weight:bold;">{order_item.quantity}</td></tr>
        <tr><td style="padding:6px 0; color:#888;">Order #</td>
            <td style="padding:6px 0; font-weight:bold;">{order_item.order.id}</td></tr>
      </table>
      <p style="text-align:center; margin: 28px 0;">
        <a href="{approve_url}"
           style="background:#1db954; color:#ffffff; text-decoration:none;
                  padding:12px 28px; border-radius:24px; font-weight:bold;
                  display:inline-block;">
          Approve Order
        </a>
      </p>
      <p style="font-size:13px; color:#888; text-align:center;">
        This link expires in 7 days. You can also
        <a href="{dashboard_url}" style="color:#2f4f3e;">log in to your seller dashboard</a>
        and approve it from your Orders page.
      </p>
    </div>
    """

    try:
        msg = EmailMultiAlternatives(
            subject, text_body, settings.DEFAULT_FROM_EMAIL, [seller.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)
    except Exception:
        # Never let an email failure break checkout
        pass
