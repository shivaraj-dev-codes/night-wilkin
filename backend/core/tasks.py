from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta
from django.core.mail import send_mail
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

from core.models import (
    WalkSession, SOSAlert, CheckInRequest, DangerZone, LocationUpdate
)
from core.notifications import send_sms, send_push_notification

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@shared_task(bind=True, max_retries=3)
def send_sos_notifications(self, sos_alert_id):
    """Send SOS notifications to all guardians"""
    try:
        alert = SOSAlert.objects.get(id=sos_alert_id)
        walker = alert.walker
        
        # Get all guardians
        guardians = walker.guardians.all()
        if not guardians:
            logger.warning(f"Walker {walker.id} has no guardians for SOS alert")
            return
        
        # Get emergency contacts if no guardians
        if not guardians:
            emergency_contacts = walker.emergency_contacts.all()
            contacts_to_notify = [ec.phone_number for ec in emergency_contacts]
        else:
            contacts_to_notify = [g.phone_number for g in guardians]
        
        # Send SMS to all contacts
        message = f"SOS Alert from {walker.get_full_name()}! Location: {alert.latitude}, {alert.longitude}. Message: {alert.message}"
        for phone in contacts_to_notify:
            send_sms.delay(phone, message)
        
        # Send push notifications to guardians via WebSocket
        for guardian in guardians:
            room_name = f'guardian_{guardian.id}'
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'walker_sos',
                    'walker_id': str(walker.id),
                    'walker_name': walker.get_full_name(),
                    'latitude': alert.latitude,
                    'longitude': alert.longitude,
                    'message': alert.message,
                    'timestamp': now().isoformat()
                }
            )
        
        alert.contacts_notified_count = len(contacts_to_notify)
        alert.save()
        logger.info(f"SOS notifications sent for alert {sos_alert_id}")
    except SOSAlert.DoesNotExist:
        logger.error(f"SOS Alert {sos_alert_id} not found")
    except Exception as exc:
        logger.error(f"Error sending SOS notifications: {str(exc)}")
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_check_in_request(self, session_id):
    """Send periodic check-in requests"""
    try:
        session = WalkSession.objects.get(id=session_id)
        if not session.is_active:
            return
        
        # Create check-in request
        check_in = CheckInRequest.objects.create(session=session)
        
        # Send via WebSocket
        room_name = f'location_{session_id}'
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'check_in_request',
                'check_in_id': str(check_in.id),
                'message': 'Are you safe? Please confirm.'
            }
        )
        
        logger.info(f"Check-in request sent for session {session_id}")
    except WalkSession.DoesNotExist:
        logger.error(f"Session {session_id} not found")
    except Exception as exc:
        logger.error(f"Error sending check-in: {str(exc)}")
        self.retry(exc=exc, countdown=60)


@shared_task
def check_expected_end_times():
    """Check if walkers exceeded expected end time"""
    overdue_sessions = WalkSession.objects.filter(
        is_active=True,
        expected_end_time__lt=now()
    )
    
    for session in overdue_sessions:
        # Create SOS alert
        SOSAlert.objects.create(
            walker=session.walker,
            session=session,
            latitude=0,
            longitude=0,
            message="Expected end time exceeded - walker not responded",
            is_silent=True
        )
        
        # Notify guardians
        for guardian in session.walker.guardians.all():
            room_name = f'guardian_{guardian.id}'
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'walker_missing',
                    'walker_id': str(session.walker.id),
                    'walker_name': session.walker.get_full_name(),
                    'last_location': f"{session.location_updates.last().latitude}, {session.location_updates.last().longitude}" if session.location_updates.exists() else "Unknown",
                    'missing_duration': f"{(now() - session.expected_end_time).seconds // 60} minutes"
                }
            )
        
        logger.info(f"Overdue session detected: {session.id}")


@shared_task
def auto_end_long_sessions():
    """Auto-end sessions exceeding max duration"""
    long_sessions = WalkSession.objects.filter(
        is_active=True,
        start_time__lt=now() - timedelta(hours=6)  # Default max is 6 hours
    )
    
    for session in long_sessions:
        session.is_active = False
        session.end_time = now()
        session.save()
        logger.info(f"Auto-ended long session: {session.id}")


@shared_task
def check_danger_zones():
    """Periodically check if walkers are in danger zones"""
    from geopy.distance import geodesic
    
    active_sessions = WalkSession.objects.filter(is_active=True)
    
    for session in active_sessions:
        # Get latest location
        latest_location = session.location_updates.latest('timestamp')
        if not latest_location:
            continue
        
        walker_coords = (latest_location.latitude, latest_location.longitude)
        danger_zones = DangerZone.objects.filter(is_verified=True)
        
        for zone in danger_zones:
            zone_coords = (zone.latitude, zone.longitude)
            distance = geodesic(walker_coords, zone_coords).meters
            
            if distance < zone.radius_meters:
                # Notify guardians
                for guardian in session.walker.guardians.all():
                    room_name = f'guardian_{guardian.id}'
                    async_to_sync(channel_layer.group_send)(
                        room_name,
                        {
                            'type': 'danger_zone_alert',
                            'walker_id': str(session.walker.id),
                            'danger_description': zone.description,
                            'location': f"{zone.latitude}, {zone.longitude}"
                        }
                    )
                logger.info(f"Walker {session.walker.id} in danger zone")


@shared_task
def anonymize_old_locations():
    """Anonymize location data older than 30 days"""
    cutoff_date = now() - timedelta(days=30)
    old_locations = LocationUpdate.objects.filter(timestamp__lt=cutoff_date)
    
    # Set latitude/longitude to approximate city center
    old_locations.update(
        latitude=0,
        longitude=0,
        accuracy=None
    )
    logger.info(f"Anonymized {old_locations.count()} old locations")


@shared_task
def cleanup_expired_check_ins():
    """Clean up expired check-in requests"""
    cutoff_time = now() - timedelta(minutes=15)
    expired = CheckInRequest.objects.filter(
        requested_at__lt=cutoff_time,
        status='pending'
    )
    expired.update(status='expired')
    logger.info(f"Expired {expired.count()} check-in requests")
