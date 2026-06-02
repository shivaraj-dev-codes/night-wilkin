from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from core.models import (
    User, EmergencyContact, SafeLocation, WalkSession,
    LocationUpdate, SOSAlert, DangerZone, EvidenceFile, FakeCallLog
)


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Password must be at least 8 characters"
    )
    password_confirm = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Enter a valid phone number (E.164 format or local)',
            )
        ]
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'password', 'password_confirm', 'role'
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username already exists"})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
        
        if User.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError({"phone_number": "Phone number already registered"})
        
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            role=validated_data.get('role', 'walker'),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    guardian_count = serializers.SerializerMethodField()
    walker_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'role', 'is_verified', 'date_of_birth',
            'avatar', 'bio', 'preferred_language', 'auto_sos_enabled',
            'check_in_interval_minutes', 'max_session_duration_hours',
            'guardian_count', 'walker_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'role', 'is_verified', 'created_at', 'updated_at'
        ]
    
    def get_guardian_count(self, obj):
        return obj.guardians.count() if obj.is_walker() else 0
    
    def get_walker_count(self, obj):
        return obj.walkers.count() if obj.is_guardian() else 0


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user details with guardians"""
    guardians = UserProfileSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'role', 'is_verified', 'avatar', 'guardians']


class EmergencyContactSerializer(serializers.ModelSerializer):
    """Serializer for emergency contacts"""
    class Meta:
        model = EmergencyContact
        fields = ['id', 'name', 'phone_number', 'relationship', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_phone_number(self, value):
        if not value or len(value) < 9:
            raise serializers.ValidationError("Invalid phone number format")
        return value


class SafeLocationSerializer(serializers.ModelSerializer):
    """Serializer for safe locations"""
    distance_km = serializers.SerializerMethodField()
    
    class Meta:
        model = SafeLocation
        fields = [
            'id', 'name', 'location_type', 'latitude', 'longitude',
            'address', 'phone_number', 'operating_hours', 'is_partner',
            'city', 'state', 'distance_km'
        ]
    
    def get_distance_km(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user_lat') and hasattr(request, 'user_lng'):
            from geopy.distance import geodesic
            coords_1 = (request.user_lat, request.user_lng)
            coords_2 = (obj.latitude, obj.longitude)
            return round(geodesic(coords_1, coords_2).km, 2)
        return None


class LocationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for location updates"""
    class Meta:
        model = LocationUpdate
        fields = ['id', 'session', 'latitude', 'longitude', 'accuracy', 'altitude', 'speed', 'timestamp']
        read_only_fields = ['id', 'timestamp']
    
    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value
    
    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value


class WalkSessionSerializer(serializers.ModelSerializer):
    """Serializer for walk sessions"""
    duration_minutes = serializers.SerializerMethodField()
    location_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WalkSession
        fields = [
            'id', 'walker', 'start_time', 'end_time', 'is_active',
            'destination', 'destination_note', 'expected_end_time',
            'share_location', 'total_distance_km', 'average_speed_kmph',
            'duration_minutes', 'location_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'walker', 'start_time', 'created_at', 'updated_at',
            'total_distance_km', 'average_speed_kmph'
        ]
    
    def get_duration_minutes(self, obj):
        return obj.duration_minutes()
    
    def get_location_count(self, obj):
        return obj.location_updates.count()


class WalkSessionDetailSerializer(WalkSessionSerializer):
    """Detailed walk session serializer with locations"""
    location_updates = LocationUpdateSerializer(many=True, read_only=True)
    
    class Meta(WalkSessionSerializer.Meta):
        fields = WalkSessionSerializer.Meta.fields + ['location_updates']


class SOSAlertSerializer(serializers.ModelSerializer):
    """Serializer for SOS alerts"""
    walker_name = serializers.CharField(source='walker.get_full_name', read_only=True)
    
    class Meta:
        model = SOSAlert
        fields = [
            'id', 'walker', 'walker_name', 'session', 'latitude', 'longitude',
            'message', 'status', 'is_silent', 'triggered_at', 'resolved_at',
            'contacts_notified_count', 'created_at'
        ]
        read_only_fields = [
            'id', 'walker', 'triggered_at', 'resolved_at', 'contacts_notified_count', 'created_at'
        ]


class DangerZoneSerializer(serializers.ModelSerializer):
    """Serializer for danger zones"""
    distance_meters = serializers.SerializerMethodField()
    
    class Meta:
        model = DangerZone
        fields = [
            'id', 'latitude', 'longitude', 'radius_meters', 'description',
            'zone_type', 'report_count', 'is_verified', 'city', 'distance_meters'
        ]
        read_only_fields = ['id', 'report_count', 'is_verified']
    
    def get_distance_meters(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user_lat') and hasattr(request, 'user_lng'):
            from geopy.distance import geodesic
            coords_1 = (request.user_lat, request.user_lng)
            coords_2 = (obj.latitude, obj.longitude)
            return round(geodesic(coords_1, coords_2).meters, 2)
        return None


class EvidenceFileSerializer(serializers.ModelSerializer):
    """Serializer for evidence files"""
    class Meta:
        model = EvidenceFile
        fields = [
            'id', 'session', 'file', 'file_type', 'note',
            'is_encrypted', 'keep_indefinitely', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']


class FakeCallLogSerializer(serializers.ModelSerializer):
    """Serializer for fake call logs"""
    class Meta:
        model = FakeCallLog
        fields = [
            'id', 'user', 'session', 'script', 'delay_seconds',
            'was_called', 'call_timestamp', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'was_called', 'call_timestamp', 'created_at']
