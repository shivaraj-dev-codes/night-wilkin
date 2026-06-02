import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { walkerAPI } from '../../api/endpoints'
import useSessionStore from '../../store/sessionStore'
import useAuthStore from '../../store/authStore'

const SOSAlert = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { activeSession } = useSessionStore()
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [confirmSOS, setConfirmSOS] = useState(false)

  const handleTriggerSOS = async () => {
    if (!confirmSOS) {
      setConfirmSOS(true)
      toast('Please click SOS again to confirm', { icon: '⚠️' })
      return
    }

    setIsLoading(true)
    try {
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject)
      })

      const { latitude, longitude } = position.coords

      await walkerAPI.triggerSOS({
        latitude,
        longitude,
        message,
        session: activeSession?.id,
      })

      toast.success('SOS Alert sent to all guardians!')
      setMessage('')
      setConfirmSOS(false)
      setTimeout(() => navigate('/'), 2000)
    } catch (error) {
      toast.error('Failed to send SOS alert')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md text-center">
        <div className="text-6xl mb-4 animate-pulse">🆘</div>
        <h1 className="text-3xl font-bold text-red-600 mb-4">Emergency SOS</h1>
        <p className="text-gray-600 mb-6">Alert all your guardians immediately</p>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Add Message (Optional)</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Describe your emergency situation..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            rows="3"
          />
        </div>

        <button
          onClick={handleTriggerSOS}
          disabled={isLoading}
          className={`w-full py-3 rounded-lg font-bold text-white text-lg transition mb-4 ${
            confirmSOS
              ? 'bg-red-700 hover:bg-red-800 animate-pulse'
              : 'bg-red-600 hover:bg-red-700'
          } disabled:opacity-50`}
        >
          {isLoading ? 'Sending...' : confirmSOS ? 'Confirm SOS' : 'Trigger SOS'}
        </button>

        <button
          onClick={() => navigate('/')}
          className="w-full py-2 rounded-lg font-semibold text-gray-700 bg-gray-200 hover:bg-gray-300 transition"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}

export default SOSAlert
