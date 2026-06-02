from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    RegisterView, LoginView, UserViewSet, EmergencyContactViewSet,
    SafeLocationViewSet, WalkSessionViewSet, LocationUpdateViewSet,
    SOSAlertViewSet, DangerZoneViewSet, EvidenceFileViewSet, FakeCallLogViewSet
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'emergency-contacts', EmergencyContactViewSet, basename='emergency-contact')
router.register(r'safe-locations', SafeLocationViewSet, basename='safe-location')
router.register(r'walk-sessions', WalkSessionViewSet, basename='walk-session')
router.register(r'location-updates', LocationUpdateViewSet, basename='location-update')
router.register(r'sos-alerts', SOSAlertViewSet, basename='sos-alert')
router.register(r'danger-zones', DangerZoneViewSet, basename='danger-zone')
router.register(r'evidence-files', EvidenceFileViewSet, basename='evidence-file')
router.register(r'fake-calls', FakeCallLogViewSet, basename='fake-call')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
