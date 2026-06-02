import React, { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const defaultIcon = L.icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const dangerIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

const LocationMap = ({ 
  center = [20.5937, 78.9629], 
  zoom = 13, 
  walkerLocations = [], 
  dangerZones = [],
  onLocationClick = null,
}) => {
  return (
    <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />

      {/* Walker Locations */}
      {walkerLocations.map((location, idx) => (
        <Marker key={idx} position={[location.latitude, location.longitude]} icon={defaultIcon}>
          <Popup>
            <div>
              <p className="font-bold">{location.walker_name}</p>
              <p className="text-sm text-gray-600">Accuracy: {Math.round(location.accuracy)}m</p>
              <p className="text-xs text-gray-500">{new Date(location.timestamp).toLocaleTimeString()}</p>
            </div>
          </Popup>
        </Marker>
      ))}

      {/* Danger Zones */}
      {dangerZones.map((zone, idx) => (
        <Circle
          key={idx}
          center={[zone.latitude, zone.longitude]}
          radius={zone.radius_meters}
          color="red"
          fillColor="#ff6b6b"
          fillOpacity={0.2}
        >
          <Popup>
            <div>
              <p className="font-bold text-red-600">⚠️ Danger Zone</p>
              <p className="text-sm">{zone.description}</p>
              <p className="text-xs text-gray-500">Type: {zone.zone_type}</p>
            </div>
          </Popup>
        </Circle>
      ))}
    </MapContainer>
  )
}

export default LocationMap
