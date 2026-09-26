import os
import smtplib
from email.message import EmailMessage
from flask import current_app
from app.models import db
from app.feature_models import NotificationLog


def send_email(user, subject, message, event_id=None):
    recipient = user.email
    server = os.environ.get('MAIL_SERVER')
    username = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')
    port = int(os.environ.get('MAIL_PORT', '587'))
    use_tls = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'

    if not server or not username or not password:
        db.session.add(NotificationLog(user_id=user.id, event_id=event_id, channel='email',
                                        recipient=recipient, subject=subject, message=message,
                                        status='skipped', error='SMTP credentials are not configured'))
        return False
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = recipient
        msg.set_content(message)
        with smtplib.SMTP(server, port, timeout=15) as smtp:
            if use_tls:
                smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        db.session.add(NotificationLog(user_id=user.id, event_id=event_id, channel='email',
                                        recipient=recipient, subject=subject, message=message, status='sent'))
        return True
    except Exception as exc:
        db.session.add(NotificationLog(user_id=user.id, event_id=event_id, channel='email',
                                        recipient=recipient, subject=subject, message=message,
                                        status='failed', error=str(exc)))
        return False


def send_sms(user, message, event_id=None):
    recipient = user.phone
    sid = os.environ.get('TWILIO_ACCOUNT_SID')
    token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_FROM_NUMBER')
    if not recipient or not sid or not token or not from_number:
        db.session.add(NotificationLog(user_id=user.id, event_id=event_id, channel='sms',
                                        recipient=recipient or '', message=message,
                                        status='skipped', error='Twilio credentials or user phone are not configured'))
        return False
    try:
        from twilio.rest import Client
        Client(sid, token).messages.create(body=message, from_=from_number, to=recipient)
        db.session.add(NotificationLog(user_id=user.id, event_id=event_id, channel='sms',
                                        recipient=recipient, message=message, status='sent'))
        return True
    except Exception as exc:
        db.session.add(NotificationLog(user_id=user.id, event_id=event_id, channel='sms',
                                        recipient=recipient, message=message, status='failed', error=str(exc)))
        return False


def notify_user(user, subject, message, event_id=None, email=True, sms=True):
    if email:
        send_email(user, subject, message, event_id)
    if sms:
        send_sms(user, message[:320], event_id)


def cloud_upload(local_path, key=None):
    """Upload a file to an S3-compatible bucket when cloud credentials are configured.
    Returns the object URL, or None when cloud storage is not configured.
    """
    bucket = os.environ.get('CLOUD_STORAGE_BUCKET')
    region = os.environ.get('CLOUD_STORAGE_REGION')
    if not bucket or not os.path.exists(local_path):
        return None
    try:
        import boto3
        client = boto3.client('s3', region_name=region or None)
        key = key or os.path.basename(local_path)
        extra = {'ContentType': 'application/octet-stream'}
        client.upload_file(local_path, bucket, key, ExtraArgs=extra)
        base = os.environ.get('CLOUD_STORAGE_PUBLIC_BASE_URL')
        return f"{base.rstrip('/')}/{key}" if base else f"s3://{bucket}/{key}"
    except Exception as exc:
        current_app.logger.warning('Cloud upload failed: %s', exc)
        return None
