"""
Celery tasks for email sending.
"""

from app.core.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="app.tasks.email_tasks.send_email",
    max_retries=3,
    default_retry_delay=60,
)
def send_email(self, to_email: str, subject: str, body: str, html: bool = True):
    """Send an email asynchronously via Celery."""
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        from app.core import get_settings
        settings = get_settings()

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email

        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())

        return {"status": "sent", "to": to_email}

    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.email_tasks.send_welcome_email",
    max_retries=3,
)
def send_welcome_email(to_email: str, first_name: str):
    """Send a welcome email to a new user."""
    subject = "Welcome to our E-Commerce Platform!"
    body = f"""
    <html>
    <body>
        <h2>Welcome, {first_name}!</h2>
        <p>Thank you for joining our platform. We're excited to have you on board.</p>
        <p>Start exploring our products and enjoy shopping!</p>
    </body>
    </html>
    """
    send_email.delay(to_email, subject, body)


@celery_app.task(
    name="app.tasks.email_tasks.send_order_confirmation",
    max_retries=3,
)
def send_order_confirmation(to_email: str, order_id: int, total_amount: float):
    """Send order confirmation email."""
    subject = f"Order #{order_id} Confirmed!"
    body = f"""
    <html>
    <body>
        <h2>Order Confirmed!</h2>
        <p>Your order <strong>#{order_id}</strong> has been confirmed.</p>
        <p>Total: ₹{total_amount:,.2f}</p>
        <p>You can track your order status in your account.</p>
    </body>
    </html>
    """
    send_email.delay(to_email, subject, body)
