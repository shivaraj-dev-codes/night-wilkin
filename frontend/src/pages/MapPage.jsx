import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import { safetyAPI, walkerAPI } from '../api/endpoints'
import LocationMap from '../components/LocationMap'
import useLocationStore from '../store/locationStore'

const MapPage = () => {
  const { currentLocation } = useLocationStore()
  const [nearbyLocations, setNearbyLocations] = useState([])
  const [dangerZones, setDangerZones] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (currentLocation) {
      fetchNearbyData(currentLocation.latitude, currentLocation.longitude)
    }
  }, [currentLocation])

  const fetchNearbyData = async (lat, lng) => {
    setIsLoading(true)
    try {
      const [locationsRes, dangerRes] = await Promise.all([
        safetyAPI.getNearbyLocations(lat, lng),
        safetyAPI.getNearbyDangerZones(lat, lng),
      ])
      setNearbyLocations(locationsRes.data)
      setDangerZones(dangerRes.data)
    } catch (error) {
      toast.error('Failed to fetch nearby data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReportDanger = async () => {
    if (!currentLocation) {
      toast.error('Please enable location access')
      return
    }

    const description = prompt('Describe the danger situation:')
    if (!description) return

    try {
      await safetyAPI.reportDanger({
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        description,
        zone_type: 'user_reported',
        city: 'Unknown',
      })
      toast.success('Danger zone reported! Thank you for keeping others safe.')
    } catch (error) {
      toast.error('Failed to report danger')
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">🗺️ Safety Map</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-lg shadow-lg overflow-hidden h-96">
            {currentLocation ? (
              <LocationMap
                center={[currentLocation.latitude, currentLocation.longitude]}
                walkerLocations={nearbyLocations}
                dangerZones={dangerZones}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-gray-600">Enable location access to see the map</p>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <button
              onClick={handleReportDanger}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-3 rounded-lg transition"
            >
              ⚠️ Report Danger
            </button>

            <div className="bg-white rounded-lg shadow-lg p-4">
              <h3 className="font-bold text-lg mb-4 text-green-600">✅ Safe Locations</h3>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {nearbyLocations.length === 0 ? (
                  <p className="text-sm text-gray-600">No safe locations nearby</p>
                ) : (
                  nearbyLocations.map((loc) => (
                    <div key={loc.id} className="text-sm border-l-4 border-green-500 pl-3">
                      <p className="font-semibold">{loc.name}</p>
                      <p className="text-gray-600 text-xs">{loc.location_type}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-4">
              <h3 className="font-bold text-lg mb-4 text-red-600">⚠️ Danger Zones</h3>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {dangerZones.length === 0 ? (
                  <p className="text-sm text-gray-600">No danger zones in this area</p>
                ) : (
                  dangerZones.map((zone) => (
                    <div key={zone.id} className="text-sm border-l-4 border-red-500 pl-3">
                      <p className="font-semibold">⚠️ {zone.zone_type}</p>
                      <p className="text-gray-600 text-xs">{zone.description}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MapPage
