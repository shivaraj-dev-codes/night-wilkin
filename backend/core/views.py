from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils.timezone import now
from django.db.models import Q
from geopy.distance import geodesic
import logging

from core.models import (
    User, EmergencyContact, SafeLocation, WalkSession,
    LocationUpdate, SOSAlert, DangerZone, EvidenceFile,
    GuardianInvite, CheckInRequest, FakeCallLog
)
from core.serializers import (
    UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer,
    UserDetailSerializer, EmergencyContactSerializer, SafeLocationSerializer,
    WalkSessionSerializer, WalkSessionDetailSerializer, LocationUpdateSerializer,
    SOSAlertSerializer, DangerZoneSerializer, EvidenceFileSerializer,
    FakeCallLogSerializer
)
from core.permissions import (
    IsWalker, IsGuardian, IsVerifiedUser, IsWalkerOwner, IsGuardianOfWalker
)
from core.tasks import send_sos_notifications, check_walker_check_in

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'message': 'Registration successful. Please verify your phone number.'
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """User login endpoint"""
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.filter(email=serializer.validated_data['email']).first()
        if not user or not user.check_password(serializer.validated_data['password']):
            return Response(
                {'detail': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class UserViewSet(viewsets.ModelViewSet):
    """User profile management"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """Get or update user profile"""
        user = request.user
        
        if request.method == 'GET':
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_guardian(self, request):
        """Add a guardian (for walkers)"""
        if not request.user.is_walker():
            return Response(
                {'detail': 'Only walkers can add guardians'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        guardian_id = request.data.get('guardian_id')
        try:
            guardian = User.objects.get(id=guardian_id, role='guardian')
            request.user.guardians.add(guardian)
            return Response({'detail': 'Guardian added successfully'})
        except User.DoesNotExist:
            return Response(
                {'detail': 'Guardian not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def remove_guardian(self, request):
        """Remove a guardian"""
        guardian_id = request.data.get('guardian_id')
        try:
            guardian = User.objects.get(id=guardian_id)
            request.user.guardians.remove(guardian)
            return Response({'detail': 'Guardian removed successfully'})
        except User.DoesNotExist:
            return Response(
                {'detail': 'Guardian not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def my_guardians(self, request):
        """Get list of guardians for walker"""
        guardians = request.user.guardians.all()
        serializer = UserProfileSerializer(guardians, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_walkers(self, request):
        """Get list of walkers for guardian"""
        walkers = request.user.walkers.all()
        serializer = UserProfileSerializer(walkers, many=True)
        return Response(serializer.data)


class EmergencyContactViewSet(viewsets.ModelViewSet):
    """Emergency contacts management"""
    permission_classes = [IsAuthenticated]
    serializer_class = EmergencyContactSerializer
    
    def get_queryset(self):
        return EmergencyContact.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def set_primary(self, request):
        """Set a contact as primary"""
        contact_id = request.data.get('contact_id')
        try:
            contact = EmergencyContact.objects.get(id=contact_id, user=request.user)
            EmergencyContact.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
            contact.is_primary = True
            contact.save()
            return Response({'detail': 'Primary contact updated'})
        except EmergencyContact.DoesNotExist:
            return Response({'detail': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)


class SafeLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """Safe locations nearby"""
    permission_classes = [IsAuthenticated]
    serializer_class = SafeLocationSerializer
    queryset = SafeLocation.objects.all()
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get nearby safe locations"""
        lat = request.query_params.get('latitude')
        lng = request.query_params.get('longitude')
        radius_km = float(request.query_params.get('radius', 5))
        
        if not lat or not lng:
            return Response(
                {'detail': 'latitude and longitude required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_coords = (float(lat), float(lng))
            all_locations = SafeLocation.objects.all()
            nearby = []
            
            for loc in all_locations:
                loc_coords = (loc.latitude, loc.longitude)
                distance = geodesic(user_coords, loc_coords).km
                if distance <= radius_km:
                    nearby.append((loc, distance))
            
            nearby.sort(key=lambda x: x[1])
            locations = [loc[0] for loc in nearby]
            
            serializer = SafeLocationSerializer(
                locations, many=True,
                context={'request': request}
            )
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )


class WalkSessionViewSet(viewsets.ModelViewSet):
    """Walk session management"""
    permission_classes = [IsAuthenticated, IsWalker]
    serializer_class = WalkSessionSerializer
    
    def get_queryset(self):
        if self.request.user.is_walker():
            return WalkSession.objects.filter(walker=self.request.user)
        return WalkSession.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(walker=self.request.user)
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """End an active walk session"""
        session = self.get_object()
        if session.walker != request.user:
            return Response(
                {'detail': 'You can only end your own sessions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session.is_active = False
        session.end_time = now()
        session.save()
        
        return Response({
            'detail': 'Session ended',
            'duration_minutes': session.duration_minutes(),
            'total_distance_km': session.total_distance_km,
        })
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get detailed session with all locations"""
        session = self.get_object()
        serializer = WalkSessionDetailSerializer(session)
        return Response(serializer.data)


class LocationUpdateViewSet(viewsets.ModelViewSet):
    """Location updates during walk"""
    permission_classes = [IsAuthenticated, IsWalker]
    serializer_class = LocationUpdateSerializer
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        if session_id:
            return LocationUpdate.objects.filter(session__walker=self.request.user, session_id=session_id)
        return LocationUpdate.objects.filter(session__walker=self.request.user)
    
    def perform_create(self, serializer):
        session_id = self.request.data.get('session')
        try:
            session = WalkSession.objects.get(id=session_id, walker=self.request.user)
            serializer.save(session=session)
        except WalkSession.DoesNotExist:
            raise serializers.ValidationError({'session': 'Session not found or not yours'})
    
    @action(detail=False, methods=['post'])
    def batch_update(self, request):
        """Batch update multiple locations"""
        locations_data = request.data.get('locations', [])
        session_id = request.data.get('session')
        
        try:
            session = WalkSession.objects.get(id=session_id, walker=request.user)
        except WalkSession.DoesNotExist:
            return Response({'detail': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
        created_locations = []
        for loc_data in locations_data:
            serializer = LocationUpdateSerializer(data=loc_data)
            if serializer.is_valid():
                serializer.save(session=session)
                created_locations.append(serializer.data)
        
        return Response({
            'detail': f'{len(created_locations)} locations created',
            'locations': created_locations
        }, status=status.HTTP_201_CREATED)


class SOSAlertViewSet(viewsets.ModelViewSet):
    """SOS alerts"""
    permission_classes = [IsAuthenticated]
    serializer_class = SOSAlertSerializer
    
    def get_queryset(self):
        if self.request.user.is_walker():
            return SOSAlert.objects.filter(walker=self.request.user)
        elif self.request.user.is_guardian():
            return SOSAlert.objects.filter(walker__guardians=self.request.user)
        return SOSAlert.objects.none()
    
    def perform_create(self, serializer):
        alert = serializer.save(walker=self.request.user)
        # Send notifications to guardians
        send_sos_notifications.delay(str(alert.id))
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge SOS alert (guardian action)"""
        alert = self.get_object()
        if not request.user.is_guardian():
            return Response(
                {'detail': 'Only guardians can acknowledge alerts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        alert.status = 'acknowledged'
        alert.save()
        return Response({'detail': 'Alert acknowledged'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve SOS alert"""
        alert = self.get_object()
        if not (request.user == alert.walker or request.user.is_admin_user()):
            return Response(
                {'detail': 'You cannot resolve this alert'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        alert.status = 'resolved'
        alert.resolved_at = now()
        alert.resolved_by = request.user
        alert.save()
        return Response({'detail': 'Alert resolved'})


class DangerZoneViewSet(viewsets.ModelViewSet):
    """Danger zones"""
    permission_classes = [IsAuthenticated]
    serializer_class = DangerZoneSerializer
    queryset = DangerZone.objects.filter(is_verified=True)
    
    @action(detail=False, methods=['post'])
    def report_danger(self, request):
        """Report a new danger zone"""
        serializer = DangerZoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get nearby danger zones"""
        lat = request.query_params.get('latitude')
        lng = request.query_params.get('longitude')
        radius_km = float(request.query_params.get('radius', 2))
        
        if not lat or not lng:
            return Response(
                {'detail': 'latitude and longitude required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_coords = (float(lat), float(lng))
            all_zones = DangerZone.objects.filter(is_verified=True)
            nearby = []
            
            for zone in all_zones:
                zone_coords = (zone.latitude, zone.longitude)
                distance = geodesic(user_coords, zone_coords).km
                if distance <= (radius_km + zone.radius_meters / 1000):
                    nearby.append((zone, distance))
            
            nearby.sort(key=lambda x: x[1])
            zones = [zone[0] for zone in nearby]
            
            serializer = DangerZoneSerializer(
                zones, many=True,
                context={'request': request}
            )
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )


class EvidenceFileViewSet(viewsets.ModelViewSet):
    """Evidence files management"""
    permission_classes = [IsAuthenticated, IsWalker]
    serializer_class = EvidenceFileSerializer
    
    def get_queryset(self):
        return EvidenceFile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FakeCallLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Fake call logs"""
    permission_classes = [IsAuthenticated, IsWalker]
    serializer_class = FakeCallLogSerializer
    
    def get_queryset(self):
        return FakeCallLog.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def trigger_fake_call(self, request):
        """Trigger a fake call"""
        script = request.data.get('script')
        delay = request.data.get('delay_seconds', 5)
        session_id = request.data.get('session')
        
        try:
            session = WalkSession.objects.get(id=session_id, walker=request.user) if session_id else None
        except WalkSession.DoesNotExist:
            session = None
        
        fake_call = FakeCallLog.objects.create(
            user=request.user,
            session=session,
            script=script,
            delay_seconds=delay
        )
        
        return Response({
            'id': fake_call.id,
            'detail': f'Fake call will be triggered in {delay} seconds',
            'script': script
        }, status=status.HTTP_201_CREATED)
