from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_sms(self, phone_number, message):
    """Send SMS via Twilio"""
    try:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("Twilio credentials not configured")
            return
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message_obj = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        logger.info(f"SMS sent to {phone_number}: {message_obj.sid}")
        return message_obj.sid
    except Exception as exc:
        logger.error(f"Error sending SMS: {str(exc)}")
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_email(self, recipient_email, subject, message, html_message=None):
    """Send email notification"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient_email}")
    except Exception as exc:
        logger.error(f"Error sending email: {str(exc)}")
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_push_notification(self, user_id, title, message, data=None):
    """Send push notification"""
    try:
        # Implementation depends on push notification service
        # Firebase Cloud Messaging, OneSignal, etc.
        logger.info(f"Push notification sent to user {user_id}")
    except Exception as exc:
        logger.error(f"Error sending push notification: {str(exc)}")
        self.retry(exc=exc, countdown=60)


@shared_task
def send_verification_sms(phone_number, verification_code):
    """Send SMS with verification code"""
    message = f"Your Night Wilkin verification code is: {verification_code}"
    send_sms.delay(phone_number, message)


@shared_task
def send_guardian_invite_sms(phone_number, invite_link, walker_name):
    """Send SMS with guardian invitation"""
    message = f"Hi! {walker_name} invited you to be their safety guardian on Night Wilkin. Accept: {invite_link}"
    send_sms.delay(phone_number, message)
