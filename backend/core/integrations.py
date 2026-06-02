import googlemaps
import openai
from django.conf import settings
from geopy.geocoders import Nominatim
import logging

logger = logging.getLogger(__name__)


class GoogleMapsHelper:
    """Google Maps integration"""
    
    def __init__(self):
        if not settings.GOOGLE_MAPS_API_KEY:
            logger.warning("Google Maps API key not configured")
            self.client = None
        else:
            self.client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    
    def get_nearby_places(self, latitude, longitude, place_type='police', radius=5000):
        """Find nearby places (hospitals, police stations, etc.)"""
        try:
            if not self.client:
                return []
            
            places = self.client.places_nearby(
                location=(latitude, longitude),
                radius=radius,
                type=place_type,
            )
            return places.get('results', [])
        except Exception as e:
            logger.error(f"Error getting nearby places: {str(e)}")
            return []
    
    def get_directions(self, origin, destination, mode='walking'):
        """Get directions between two points"""
        try:
            if not self.client:
                return None
            
            directions = self.client.directions(
                origin=origin,
                destination=destination,
                mode=mode,
            )
            return directions[0] if directions else None
        except Exception as e:
            logger.error(f"Error getting directions: {str(e)}")
            return None
    
    def reverse_geocode(self, latitude, longitude):
        """Convert coordinates to address"""
        try:
            if not self.client:
                return None
            
            result = self.client.reverse_geocode((latitude, longitude))
            return result[0]['formatted_address'] if result else None
        except Exception as e:
            logger.error(f"Error reverse geocoding: {str(e)}")
            return None
    
    def get_distance(self, origin, destination):
        """Get distance between two points"""
        try:
            if not self.client:
                return None
            
            directions = self.client.directions(
                origin=origin,
                destination=destination,
            )
            if directions:
                return directions[0]['legs'][0]['distance']['value']  # meters
            return None
        except Exception as e:
            logger.error(f"Error getting distance: {str(e)}")
            return None


class OpenAIHelper:
    """OpenAI integration for AI features"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            logger.warning("OpenAI API key not configured")
    
    def analyze_danger_description(self, description):
        """Analyze danger zone description and extract insights"""
        try:
            if not settings.OPENAI_API_KEY:
                return {"severity": "unknown", "type": "unknown"}
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a safety assistant analyzing danger zone reports. Extract severity level (low/medium/high) and danger type."},
                    {"role": "user", "content": f"Analyze this danger report: {description}"}
                ],
                temperature=0.7,
            )
            
            # Parse response
            content = response.choices[0].message['content']
            return {
                "analysis": content,
                "severity": "high" if "high" in content.lower() else "medium" if "medium" in content.lower() else "low"
            }
        except Exception as e:
            logger.error(f"Error analyzing danger: {str(e)}")
            return {"severity": "unknown", "analysis": str(e)}
    
    def generate_sos_response(self, sos_message):
        """Generate appropriate response suggestions for SOS"""
        try:
            if not settings.OPENAI_API_KEY:
                return []
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a safety advisor. Given an SOS message, provide 2-3 brief safety recommendations."},
                    {"role": "user", "content": f"SOS situation: {sos_message}"}
                ],
                temperature=0.7,
            )
            
            return [response.choices[0].message['content']]
        except Exception as e:
            logger.error(f"Error generating SOS response: {str(e)}")
            return []
    
    def detect_safe_route(self, origin, destination, danger_zones):
        """Suggest safest route avoiding danger zones"""
        try:
            if not settings.OPENAI_API_KEY:
                return None
            
            danger_description = "\n".join([f"Zone {i}: {z.description} at {z.latitude}, {z.longitude}" 
                                          for i, z in enumerate(danger_zones)])
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a route safety analyzer."},
                    {"role": "user", "content": f"Find safest route from {origin} to {destination} avoiding: {danger_description}"}
                ],
                temperature=0.7,
            )
            
            return response.choices[0].message['content']
        except Exception as e:
            logger.error(f"Error detecting safe route: {str(e)}")
            return None


class LocationHelper:
    """Location utility functions"""
    
    @staticmethod
    def get_address_from_coordinates(latitude, longitude):
        """Get address from lat/lng"""
        try:
            geolocator = Nominatim(user_agent="night_wilkin")
            location = geolocator.reverse(f"{latitude}, {longitude}")
            return location.address
        except Exception as e:
            logger.error(f"Error getting address: {str(e)}")
            return None
    
    @staticmethod
    def get_coordinates_from_address(address):
        """Get lat/lng from address"""
        try:
            geolocator = Nominatim(user_agent="night_wilkin")
            location = geolocator.geocode(address)
            return (location.latitude, location.longitude) if location else None
        except Exception as e:
            logger.error(f"Error geocoding address: {str(e)}")
            return None
