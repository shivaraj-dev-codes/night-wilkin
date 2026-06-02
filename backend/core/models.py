from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class User(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = [
        ('walker', 'Walker - Women seeking safety'),
        ('guardian', 'Guardian - Emergency contact/monitor'),
        ('admin', 'Administrator'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('kn', 'Kannada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='walker')
    is_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    preferred_language = models.CharField(
        max_length=5, 
        choices=LANGUAGE_CHOICES, 
        default='en'
    )
    
    # Safety settings
    auto_sos_enabled = models.BooleanField(default=True)
    check_in_interval_minutes = models.IntegerField(default=30)
    max_session_duration_hours = models.IntegerField(default=6)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Guardian relationships
    guardians = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='walkers',
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['role']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def is_walker(self):
        return self.role == 'walker'
    
    def is_guardian(self):
        return self.role == 'guardian'
    
    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff


class EmergencyContact(models.Model):
    """Emergency contacts for walkers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'phone_number'],
                name='unique_contact_per_user'
            ),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.phone_number}"
    
    def save(self, *args, **kwargs):
        # Ensure max 5 contacts per user
        if not self.pk:
            contact_count = EmergencyContact.objects.filter(user=self.user).count()
            if contact_count >= 5:
                raise ValueError("Maximum 5 emergency contacts allowed")
        super().save(*args, **kwargs)


class SafeLocation(models.Model):
    """Safe locations like police stations, hospitals, public safe zones"""
    LOCATION_TYPE_CHOICES = [
        ('police', 'Police Station'),
        ('hospital', 'Hospital'),
        ('public_zone', 'Public Safe Zone'),
        ('partner_business', 'Partner Business'),
        ('government_office', 'Government Office'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True)
    operating_hours = models.CharField(max_length=100, blank=True, help_text="e.g., 24x7 or 9 AM - 5 PM")
    
    # Partner business fields
    is_partner = models.BooleanField(default=False)
    partner_trained = models.BooleanField(default=False)
    
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['city', 'location_type']
        indexes = [
            models.Index(fields=['city', 'location_type']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.location_type}"


class WalkSession(models.Model):
    """Active walk session tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    walker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='walk_sessions')
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Optional details
    destination = models.CharField(max_length=255, blank=True)
    destination_note = models.CharField(max_length=255, blank=True)
    expected_end_time = models.DateTimeField(null=True, blank=True)
    
    # Share location settings
    share_location = models.BooleanField(default=True)
    
    # Statistics
    total_distance_km = models.FloatField(default=0)
    average_speed_kmph = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['walker', 'is_active']),
            models.Index(fields=['start_time']),
        ]
    
    def __str__(self):
        return f"Walk by {self.walker.get_full_name()} - {self.start_time}"
    
    def duration_minutes(self):
        end = self.end_time or now()
        return int((end - self.start_time).total_seconds() / 60)
    
    def is_overdue(self):
        if self.expected_end_time and self.is_active:
            return now() > self.expected_end_time
        return False


class LocationUpdate(models.Model):
    """Real-time location updates during walk session"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(WalkSession, on_delete=models.CASCADE, related_name='location_updates')
    
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    accuracy = models.FloatField(null=True, blank=True, help_text="Accuracy in meters")
    altitude = models.FloatField(null=True, blank=True, help_text="Altitude in meters")
    speed = models.FloatField(null=True, blank=True, help_text="Speed in m/s")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Location at {self.latitude}, {self.longitude} - {self.timestamp}"


class SOSAlert(models.Model):
    """SOS emergency alert"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('false_alarm', 'False Alarm'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    walker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sos_alerts')
    session = models.ForeignKey(
        WalkSession, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sos_alerts'
    )
    
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    
    message = models.TextField(blank=True, help_text="Details about the emergency")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    is_silent = models.BooleanField(default=False, help_text="Silent SOS - no UI indication on phone")
    
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_sos_alerts'
    )
    
    contacts_notified_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['walker', 'status']),
            models.Index(fields=['triggered_at']),
        ]
    
    def __str__(self):
        return f"SOS from {self.walker.get_full_name()} - {self.triggered_at}"


class DangerZone(models.Model):
    """User-reported and crime data danger zones"""
    ZONE_TYPE_CHOICES = [
        ('user_reported', 'User Reported'),
        ('crime_data', 'Crime Database'),
        ('ai_flagged', 'AI Flagged'),
        ('admin_marked', 'Admin Marked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    radius_meters = models.IntegerField(default=500, help_text="Radius of danger zone in meters")
    
    description = models.TextField(blank=True)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES, default='user_reported')
    
    report_count = models.IntegerField(default=1)
    is_verified = models.BooleanField(default=False)
    
    city = models.CharField(max_length=100)
    
    last_reported = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-report_count', '-last_reported']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['city', 'is_verified']),
        ]
    
    def __str__(self):
        return f"Danger Zone in {self.city} - Type: {self.zone_type}"


class EvidenceFile(models.Model):
    """Encrypted evidence files (audio/image) for sessions"""
    FILE_TYPE_CHOICES = [
        ('audio', 'Audio Recording'),
        ('image', 'Photo'),
        ('video', 'Video'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(WalkSession, on_delete=models.CASCADE, related_name='evidence_files')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evidence_files')
    
    file = models.FileField(upload_to='evidence/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    
    note = models.TextField(blank=True)
    
    is_encrypted = models.BooleanField(default=True)
    file_hash = models.CharField(max_length=256, blank=True, help_text="SHA-256 hash")
    
    keep_indefinitely = models.BooleanField(default=False)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['session', 'uploaded_at']),
            models.Index(fields=['user', 'uploaded_at']),
        ]
    
    def __str__(self):
        return f"Evidence - {self.file_type} by {self.user.get_full_name()}"


class GuardianInvite(models.Model):
    """Guardian invitation tokens"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    invited_phone = models.CharField(max_length=20)
    
    token = models.CharField(max_length=100, unique=True)
    is_accepted = models.BooleanField(default=False)
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_invites'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invite from {self.invited_by.get_full_name()} to {self.invited_phone}"


class CheckInRequest(models.Model):
    """Periodic check-in requests during walk session"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(WalkSession, on_delete=models.CASCADE, related_name='check_ins')
    
    requested_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Check-in for {self.session} - {self.status}"


class FakeCallLog(models.Model):
    """Log of fake call triggers"""
    SCRIPT_CHOICES = [
        ('worried_boyfriend', 'Worried Boyfriend'),
        ('strict_father', 'Strict Father'),
        ('police_officer', 'Police Officer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fake_calls')
    session = models.ForeignKey(
        WalkSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fake_calls'
    )
    
    script = models.CharField(max_length=50, choices=SCRIPT_CHOICES)
    delay_seconds = models.IntegerField(default=5)
    
    was_called = models.BooleanField(default=False)
    call_timestamp = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Fake call - {self.script} by {self.user.get_full_name()}"
