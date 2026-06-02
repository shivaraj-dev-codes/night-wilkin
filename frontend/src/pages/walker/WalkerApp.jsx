import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { walkerAPI } from '../../api/endpoints'
import useSessionStore from '../../store/sessionStore'
import useAuthStore from '../../store/authStore'

const WalkerApp = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { activeSession, setActiveSession } = useSessionStore()
  const [destination, setDestination] = useState('')
  const [expectedTime, setExpectedTime] = useState('')
  const [isStarting, setIsStarting] = useState(false)
  const [isEnding, setIsEnding] = useState(false)

  const handleStartSession = async (e) => {
    e.preventDefault()
    setIsStarting(true)

    try {
      const response = await walkerAPI.startSession({
        destination,
        expected_end_time: expectedTime || null,
        share_location: true,
      })
      setActiveSession(response.data)
      toast.success('Walk session started!')
      navigate('/walker/session')
    } catch (error) {
      toast.error('Failed to start session')
    } finally {
      setIsStarting(false)
    }
  }

  const handleEndSession = async () => {
    if (!activeSession) return

    setIsEnding(true)
    try {
      await walkerAPI.endSession(activeSession.id)
      setActiveSession(null)
      toast.success('Session ended safely!')
      navigate('/')
    } catch (error) {
      toast.error('Failed to end session')
    } finally {
      setIsEnding(false)
    }
  }

  if (activeSession?.is_active) {
    return (
      <div className="min-h-screen bg-gray-100 p-6">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="flex items-center justify-between mb-8">
              <h1 className="text-3xl font-bold text-green-600">🚶 Active Walk Session</h1>
              <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
            </div>

            <div className="bg-green-50 border-2 border-green-300 rounded-lg p-6 mb-8">
              <p className="text-lg font-semibold text-gray-700 mb-4">Session Details</p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-600">Destination</p>
                  <p className="text-xl font-bold">{activeSession.destination || 'Not specified'}</p>
                </div>
                <div>
                  <p className="text-gray-600">Duration</p>
                  <p className="text-xl font-bold">{activeSession.duration_minutes} minutes</p>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => navigate('/walker/sos')}
                className="flex-1 bg-red-500 hover:bg-red-600 text-white font-bold py-3 rounded-lg transition"
              >
                🆘 Emergency SOS
              </button>
              <button
                onClick={handleEndSession}
                disabled={isEnding}
                className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded-lg transition disabled:opacity-50"
              >
                {isEnding ? 'Ending...' : '✓ End Session'}
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-8">🚶 Start a Walk Session</h1>

          <form onSubmit={handleStartSession} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Destination</label>
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="Where are you going?"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Expected Return Time (Optional)</label>
              <input
                type="datetime-local"
                value={expectedTime}
                onChange={(e) => setExpectedTime(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
            </div>

            <div className="bg-blue-50 border border-blue-300 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                ℹ️ Your location will be shared with your guardians in real-time during this session.
              </p>
            </div>

            <button
              type="submit"
              disabled={isStarting}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-lg transition disabled:opacity-50"
            >
              {isStarting ? 'Starting session...' : 'Start Walk Session'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default WalkerApp
