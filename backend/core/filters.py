import django_filters
from core.models import WalkSession, SOSAlert, DangerZone, SafeLocation


class WalkSessionFilter(django_filters.FilterSet):
    start_time = django_filters.DateTimeFromToRangeFilter()
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = WalkSession
        fields = ['is_active', 'start_time', 'share_location']


class SOSAlertFilter(django_filters.FilterSet):
    triggered_at = django_filters.DateTimeFromToRangeFilter()
    status = django_filters.ChoiceFilter(choices=SOSAlert.STATUS_CHOICES)
    
    class Meta:
        model = SOSAlert
        fields = ['status', 'triggered_at', 'is_silent']


class DangerZoneFilter(django_filters.FilterSet):
    zone_type = django_filters.ChoiceFilter(choices=DangerZone.ZONE_TYPE_CHOICES)
    city = django_filters.CharFilter(lookup_expr='icontains')
    is_verified = django_filters.BooleanFilter()
    
    class Meta:
        model = DangerZone
        fields = ['zone_type', 'city', 'is_verified']


class SafeLocationFilter(django_filters.FilterSet):
    location_type = django_filters.ChoiceFilter(choices=SafeLocation.LOCATION_TYPE_CHOICES)
    city = django_filters.CharFilter(lookup_expr='icontains')
    is_partner = django_filters.BooleanFilter()
    
    class Meta:
        model = SafeLocation
        fields = ['location_type', 'city', 'is_partner']
