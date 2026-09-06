import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def dispatch_email(subject, text_content, html_content, from_email, to_email, reply_to=None):
    """
    Multi-strategy cloud-proof email dispatcher:
    1. locmem Test Runner (during unit tests)
    2. Brevo REST API (HTTPS Port 443 - Global unrestricted delivery)
    3. Resend REST API (HTTPS Port 443 - Fast cloud delivery)
    4. Standard Django Email Backend (SMTP)
    5. Direct SSL Port 465 fallback
    """
    recipients = to_email if isinstance(to_email, list) else [to_email]
    from_addr = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'Aesthetic Store <ketanwagh714@gmail.com>')
    reply_addrs = reply_to if isinstance(reply_to, list) else ([reply_to] if reply_to else ['ketanwagh714@gmail.com'])

    # In automated unit test environment (locmem), route directly to outbox
    if 'locmem' in getattr(settings, 'EMAIL_BACKEND', ''):
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_addr,
                to=recipients,
                reply_to=reply_addrs
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            return True
        except Exception:
            pass

    # Strategy 1: Brevo HTTPS REST API (Port 443)
    brevo_api_key = getattr(settings, 'BREVO_API_KEY', '').strip()
    if brevo_api_key:
        try:
            import requests
            sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', 'ketanwagh714@gmail.com')
            sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'Aesthetic Store')
            to_list = [{'email': e} for e in recipients]
            payload = {
                'sender': {'name': sender_name, 'email': sender_email},
                'to': to_list,
                'subject': subject,
                'htmlContent': html_content,
                'textContent': text_content,
                'replyTo': {'email': reply_addrs[0]}
            }

            resp = requests.post(
                'https://api.brevo.com/v3/smtp/email',
                headers={
                    'api-key': brevo_api_key,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                json=payload,
                timeout=8
            )
            if resp.status_code in (200, 201):
                print(f"[EMAIL SUCCESS] Dispatched via Brevo HTTPS API to {recipients}: {resp.json()}")
                return True
            else:
                print(f"[EMAIL BREVO NOTICE] Status {resp.status_code}: {resp.text}. Trying next strategy...")
        except Exception as e_brevo:
            print(f"[EMAIL BREVO ERROR] {e_brevo}. Trying next strategy...")

    # Strategy 2: Resend HTTPS REST API (Port 443)
    resend_api_key = getattr(settings, 'RESEND_API_KEY', '').strip()
    if resend_api_key:
        try:
            import requests
            sender = getattr(settings, 'RESEND_FROM_EMAIL', 'Aesthetic Store <onboarding@resend.dev>')
            payload = {
                "from": sender,
                "to": recipients,
                "subject": subject,
                "html": html_content,
                "text": text_content,
                "reply_to": reply_addrs[0]
            }

            resp = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {resend_api_key}',
                    'Content-Type': 'application/json'
                },
                json=payload,
                timeout=8
            )
            if resp.status_code in (200, 201):
                print(f"[EMAIL SUCCESS] Dispatched via Resend HTTPS API to {recipients}: {resp.json()}")
                return True
            else:
                print(f"[EMAIL RESEND NOTICE] Status {resp.status_code}: {resp.text}. Attempting SMTP fallback...")
        except Exception as e_resend:
            print(f"[EMAIL RESEND NOTICE] {e_resend}. Attempting SMTP fallback...")

    # Strategy 3: Standard Django SMTP Backend
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_addr,
            to=recipients,
            reply_to=reply_addrs
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        print(f"[EMAIL SUCCESS] Dispatched via Django Backend to {recipients}")
        return True
    except Exception as e1:
        print(f"[EMAIL NOTE] Standard backend failed ({e1}). Attempting direct SSL Port 465 fallback...")

    # Strategy 4: Direct SSL Port 465 (Cloud-Safe Fallback)
    host_user = getattr(settings, 'EMAIL_HOST_USER', 'ketanwagh714@gmail.com').strip()
    host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', 'dsvrrdfznhtrhuqh').strip().replace(' ', '')

    if host_user and host_password:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_addr
            msg['To'] = ', '.join(recipients)
            if reply_addrs:
                msg['Reply-To'] = ', '.join(reply_addrs)

            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=12) as server:
                server.login(host_user, host_password)
                server.sendmail(host_user, recipients, msg.as_string())
            print(f"[EMAIL SUCCESS] Dispatched via Direct SSL Port 465 to {recipients}")
            return True
        except Exception as e2:
            print(f"[EMAIL ERROR] All delivery strategies failed for {recipients}: {e2}")
            logger.error(f"Email delivery error to {recipients}: {e2}")
            return False

    return False


def send_welcome_email(user, request=None):
    """Sends a warm aesthetic thank-you welcome email to the newly registered customer."""
    if not user or not user.email:
        return

    name = user.first_name or user.username or "there"
    subject = f"Welcome to Aesthetic Store, {name}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Aesthetic Store <ketanwagh714@gmail.com>')
    to_email = [user.email]
    reply_to = ['ketanwagh714@gmail.com']

    site_url = request.build_absolute_uri('/')[:-1] if request else 'https://aesthetic-store.up.railway.app'
    context = {
        'user': user,
        'site_url': site_url,
    }

    try:
        text_content = render_to_string('emails/welcome_email.txt', context)
        html_content = render_to_string('emails/welcome_email.html', context)
        dispatch_email(subject, text_content, html_content, from_email, to_email, reply_to)
    except Exception as e:
        print(f"[EMAIL TEMPLATE ERROR] Could not render welcome email: {e}")
        logger.error(f"Could not render welcome email: {e}")


def send_order_confirmation_email(order, request=None):
    """Sends a detailed receipt and order confirmation email to the purchasing customer."""
    if not order or not order.shipping_email:
        return

    subject = f"Order Confirmed #{order.order_number} - Aesthetic Store"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Aesthetic Store <ketanwagh714@gmail.com>')
    to_email = [order.shipping_email]
    reply_to = ['ketanwagh714@gmail.com']

    site_url = request.build_absolute_uri('/')[:-1] if request else 'https://aesthetic-store.up.railway.app'
    context = {
        'order': order,
        'site_url': site_url,
    }

    try:
        text_content = render_to_string('emails/order_confirmation.txt', context)
        html_content = render_to_string('emails/order_confirmation.html', context)
        dispatch_email(subject, text_content, html_content, from_email, to_email, reply_to)
        print(f"[ORDER EMAIL] Dispatched order confirmation receipt for #{order.order_number} to {order.shipping_email}")
    except Exception as e:
        print(f"[ORDER EMAIL ERROR] Could not send confirmation receipt for #{order.order_number}: {e}")
        logger.error(f"Could not send order confirmation receipt: {e}")


def send_password_reset_email(user, reset_url, request=None):
    """Sends a secure, branded password reset link to the user."""
    if not user or not user.email:
        return

    name = user.first_name or user.username or "there"
    subject = "Reset Your Aesthetic Store Password"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Aesthetic Store <ketanwagh714@gmail.com>')
    to_email = [user.email]
    reply_to = ['ketanwagh714@gmail.com']

    site_url = request.build_absolute_uri('/')[:-1] if request else 'https://aesthetic-store.up.railway.app'
    context = {
        'user': user,
        'reset_url': reset_url,
        'site_url': site_url,
    }

    try:
        text_content = render_to_string('emails/password_reset_email.txt', context)
        html_content = render_to_string('emails/password_reset_email.html', context)
        dispatch_email(subject, text_content, html_content, from_email, to_email, reply_to)
        print(f"[PASSWORD RESET EMAIL] Dispatched reset email to {user.email}")
    except Exception as e:
        print(f"[PASSWORD RESET EMAIL ERROR] Could not send password reset email to {user.email}: {e}")
        logger.error(f"Could not send password reset email: {e}")

