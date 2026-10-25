"""Transactional emails: welcome, payment receipt, abandoned-cart reminder.

If SMTP_HOST is empty the email is printed to the console (handy in development).
"""
import logging
import smtplib
from email.message import EmailMessage
from html import escape

from .config import settings

log = logging.getLogger("emails")


def money(cents: int) -> str:
    return f"${cents / 100:,.2f}"


def send_email(to: str, subject: str, html: str) -> None:
    if not settings.SMTP_HOST:
        print(f"\n--- EMAIL (console) ---\nTo: {to}\nSubject: {subject}\n{html}\n-----------------------\n")
        return
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content("Please view this email in an HTML-capable client.")
    msg.add_alternative(html, subtype="html")
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as s:
            if settings.SMTP_TLS:
                s.starttls()
            if settings.SMTP_USER:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.send_message(msg)
    except Exception:  # never break a request because email failed
        log.exception("Failed to send email to %s", to)


def _layout(title: str, body: str, cta_text: str | None = None, cta_url: str | None = None) -> str:
    button = ""
    if cta_text and cta_url:
        button = (
            f'<p style="margin:32px 0"><a href="{escape(cta_url)}" style="background:#000;color:#fff;'
            f'padding:16px 28px;text-decoration:none;font-weight:700;letter-spacing:1px;'
            f'text-transform:uppercase;display:inline-block">{escape(cta_text)} &rarr;</a></p>'
        )
    return f"""<!doctype html><html><body style="margin:0;background:#f4f4f4;font-family:Helvetica,Arial,sans-serif;color:#111">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff">
<tr><td style="background:#000;color:#fff;padding:20px 32px;font-size:22px;font-weight:900;letter-spacing:4px">{settings.BRAND}</td></tr>
<tr><td style="padding:32px"><h1 style="margin:0 0 16px;font-size:28px;text-transform:uppercase;letter-spacing:1px">{title}</h1>
{body}{button}</td></tr>
<tr><td style="padding:20px 32px;font-size:12px;color:#777;border-top:1px solid #eee">&copy; {settings.BRAND}. You received this email because you have an account with us.</td></tr>
</table></td></tr></table></body></html>"""


def _rows(items) -> str:
    rows = ""
    for name, qty, unit in items:
        rows += (
            f'<tr><td style="padding:10px 0;border-bottom:1px solid #eee">{escape(name)} &times; {qty}</td>'
            f'<td align="right" style="padding:10px 0;border-bottom:1px solid #eee">{money(unit * qty)}</td></tr>'
        )
    return f'<table width="100%" cellpadding="0" cellspacing="0" style="font-size:15px">{rows}</table>'


def send_welcome_email(to: str, full_name: str) -> None:
    body = (
        f"<p>Hi {escape(full_name)},</p><p>Your account is ready. Welcome to the team &mdash; "
        "order tracking, member-only deals and fast checkout are now yours.</p>"
    )
    send_email(to, f"Welcome to {settings.BRAND}", _layout("You're in.", body, "Start shopping", f"{settings.FRONTEND_URL}/products"))


def send_payment_success_email(to: str, full_name: str, order_id: int, items, total_cents: int) -> None:
    body = (
        f"<p>Hi {escape(full_name)}, thanks for your order! We've received your payment.</p>"
        f"<p><strong>Order #{order_id}</strong></p>{_rows(items)}"
        f'<p style="text-align:right;font-size:18px"><strong>Total: {money(total_cents)}</strong></p>'
    )
    send_email(to, f"Payment received - order #{order_id}", _layout("Payment successful", body, "View your orders", f"{settings.FRONTEND_URL}/orders"))


def send_abandoned_cart_email(to: str, full_name: str, items, total_cents: int) -> None:
    body = (
        f"<p>Hi {escape(full_name)},</p><p>You left something behind. Your appliances are still waiting, "
        "but we can't hold stock forever.</p>"
        f"{_rows(items)}"
        f'<p style="text-align:right;font-size:18px"><strong>Total: {money(total_cents)}</strong></p>'
    )
    send_email(to, "Still thinking it over? Your cart is waiting", _layout("Forgot something?", body, "Complete your order", f"{settings.FRONTEND_URL}/cart"))
