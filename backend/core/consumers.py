import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import now
from core.models import WalkSession, LocationUpdate, CheckInRequest

logger = logging.getLogger(__name__)


class LocationTrackingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time location tracking"""
    
    async def connect(self):
        self.user = self.scope["user"]
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'location_{self.session_id}'
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Verify user owns this session
        if not await self.user_owns_session():
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"User {self.user.id} connected to session {self.session_id}")
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"User {self.user.id} disconnected from session {self.session_id}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'location_update':
                await self.handle_location_update(data)
            elif message_type == 'check_in_response':
                await self.handle_check_in_response(data)
            elif message_type == 'sos_trigger':
                await self.handle_sos_trigger(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def handle_location_update(self, data):
        """Handle incoming location update"""
        try:
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
            accuracy = data.get('accuracy')
            
            # Save location to database
            location = await self.save_location(
                latitude, longitude, accuracy
            )
            
            # Broadcast to guardians
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_broadcast',
                    'latitude': latitude,
                    'longitude': longitude,
                    'accuracy': accuracy,
                    'timestamp': location.timestamp.isoformat()
                }
            )
        except (ValueError, KeyError) as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid location data'
            }))
    
    async def handle_check_in_response(self, data):
        """Handle check-in response from walker"""
        confirmed = data.get('confirmed', False)
        
        if confirmed:
            await self.confirm_check_in()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'check_in_confirmed',
                    'message': 'Walker confirmed safe'
                }
            )
    
    async def handle_sos_trigger(self, data):
        """Handle SOS trigger"""
        message = data.get('message', '')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'sos_alert',
                'message': message,
                'timestamp': now().isoformat()
            }
        )
    
    # Event handlers
    async def location_broadcast(self, event):
        """Send location update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'accuracy': event['accuracy'],
            'timestamp': event['timestamp']
        }))
    
    async def check_in_request(self, event):
        """Send check-in request to walker"""
        await self.send(text_data=json.dumps({
            'type': 'check_in_request',
            'check_in_id': event['check_in_id'],
            'message': 'Are you safe? Please confirm.'
        }))
    
    async def check_in_confirmed(self, event):
        """Notify of check-in confirmation"""
        await self.send(text_data=json.dumps({
            'type': 'check_in_confirmed',
            'message': event['message']
        }))
    
    async def sos_alert(self, event):
        """Send SOS alert to guardians"""
        await self.send(text_data=json.dumps({
            'type': 'sos_alert',
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    # Database operations
    @database_sync_to_async
    def user_owns_session(self):
        """Check if user owns the walk session"""
        try:
            session = WalkSession.objects.get(id=self.session_id)
            # Allow walker or their guardians
            return session.walker == self.user or self.user in session.walker.guardians.all()
        except WalkSession.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_location(self, latitude, longitude, accuracy):
        """Save location update to database"""
        session = WalkSession.objects.get(id=self.session_id)
        return LocationUpdate.objects.create(
            session=session,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy
        )
    
    @database_sync_to_async
    def confirm_check_in(self):
        """Confirm pending check-in"""
        CheckInRequest.objects.filter(
            session__id=self.session_id,
            status='pending'
        ).update(status='confirmed', confirmed_at=now())


class GuardianNotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for guardian notifications"""
    
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = f'guardian_{self.user.id}'
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"Guardian {self.user.id} connected to notifications")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
    
    # Notification handlers
    async def walker_sos(self, event):
        """Send SOS notification to guardian"""
        await self.send(text_data=json.dumps({
            'type': 'walker_sos',
            'walker_id': event['walker_id'],
            'walker_name': event['walker_name'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    async def walker_missing(self, event):
        """Send missing walker notification"""
        await self.send(text_data=json.dumps({
            'type': 'walker_missing',
            'walker_id': event['walker_id'],
            'walker_name': event['walker_name'],
            'last_location': event['last_location'],
            'missing_duration': event['missing_duration']
        }))
    
    async def danger_zone_alert(self, event):
        """Send danger zone alert"""
        await self.send(text_data=json.dumps({
            'type': 'danger_zone_alert',
            'walker_id': event['walker_id'],
            'danger_description': event['danger_description'],
            'location': event['location']
        }))
