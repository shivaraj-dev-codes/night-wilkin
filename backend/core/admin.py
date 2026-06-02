from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import (
    User, EmergencyContact, SafeLocation, WalkSession,
    LocationUpdate, SOSAlert, DangerZone, EvidenceFile,
    GuardianInvite, CheckInRequest, FakeCallLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Night Wilkin Profile', {
            'fields': ('phone_number', 'role', 'is_verified', 'date_of_birth', 
                      'avatar', 'bio', 'preferred_language')
        }),
        ('Safety Settings', {
            'fields': ('auto_sos_enabled', 'check_in_interval_minutes', 
                      'max_session_duration_hours')
        }),
        ('Guardians', {
            'fields': ('guardians',)
        }),
    )
    list_display = ('email', 'get_full_name', 'phone_number', 'role', 'is_verified', 'created_at')
    list_filter = ('role', 'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'phone_number', 'first_name', 'last_name')


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'user', 'relationship', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('name', 'phone_number', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SafeLocation)
class SafeLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_type', 'city', 'phone_number', 'is_partner')
    list_filter = ('location_type', 'city', 'is_partner', 'partner_trained')
    search_fields = ('name', 'address', 'city')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WalkSession)
class WalkSessionAdmin(admin.ModelAdmin):
    list_display = ('walker', 'start_time', 'end_time', 'is_active', 'destination', 'duration_minutes')
    list_filter = ('is_active', 'start_time', 'share_location')
    search_fields = ('walker__email', 'destination')
    readonly_fields = ('created_at', 'updated_at', 'duration_minutes')


@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('session', 'latitude', 'longitude', 'timestamp', 'accuracy')
    list_filter = ('timestamp',)
    search_fields = ('session__walker__email',)
    readonly_fields = ('created_at',)


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ('walker', 'status', 'triggered_at', 'resolved_at', 'is_silent', 'contacts_notified_count')
    list_filter = ('status', 'is_silent', 'triggered_at')
    search_fields = ('walker__email', 'message')
    readonly_fields = ('created_at', 'triggered_at')


@admin.register(DangerZone)
class DangerZoneAdmin(admin.ModelAdmin):
    list_display = ('city', 'zone_type', 'report_count', 'is_verified', 'last_reported')
    list_filter = ('zone_type', 'city', 'is_verified', 'last_reported')
    search_fields = ('city', 'description')
    readonly_fields = ('created_at', 'last_reported')


@admin.register(EvidenceFile)
class EvidenceFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_type', 'session', 'uploaded_at', 'is_encrypted')
    list_filter = ('file_type', 'uploaded_at', 'is_encrypted', 'keep_indefinitely')
    search_fields = ('user__email', 'note')
    readonly_fields = ('created_at', 'uploaded_at')


@admin.register(GuardianInvite)
class GuardianInviteAdmin(admin.ModelAdmin):
    list_display = ('invited_by', 'invited_phone', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('invited_phone', 'invited_by__email')
    readonly_fields = ('created_at', 'accepted_at')


@admin.register(CheckInRequest)
class CheckInRequestAdmin(admin.ModelAdmin):
    list_display = ('session', 'status', 'requested_at', 'confirmed_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('session__walker__email',)
    readonly_fields = ('requested_at',)


@admin.register(FakeCallLog)
class FakeCallLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'script', 'delay_seconds', 'was_called', 'created_at')
    list_filter = ('script', 'was_called', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at',)
