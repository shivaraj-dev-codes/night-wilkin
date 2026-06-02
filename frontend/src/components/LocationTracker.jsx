import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { authAPI } from '../api/endpoints'
import useAuthStore from '../store/authStore'

const LocationTracker = ({ sessionId }) => {
  const [isTracking, setIsTracking] = useState(false)
  const [accuracy, setAccuracy] = useState(null)

  const startTracking = () => {
    if (!navigator.geolocation) {
      toast.error('Geolocation not supported')
      return
    }

    const watcherId = navigator.geolocation.watchPosition(
      async (position) => {
        const { latitude, longitude, accuracy } = position.coords
        setAccuracy(accuracy)
        setIsTracking(true)

        try {
          await authAPI.updateLocation({
            session: sessionId,
            latitude,
            longitude,
            accuracy,
          })
        } catch (error) {
          console.error('Failed to update location:', error)
        }
      },
      (error) => {
        toast.error(`Location error: ${error.message}`)
        setIsTracking(false)
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0,
      }
    )

    return watcherId
  }

  const stopTracking = (watcherId) => {
    navigator.geolocation.clearWatch(watcherId)
    setIsTracking(false)
  }

  return {
    startTracking,
    stopTracking,
    isTracking,
    accuracy,
  }
}

export default LocationTracker
