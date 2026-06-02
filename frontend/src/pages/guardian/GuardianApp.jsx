import React, { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { guardianAPI } from '../../api/endpoints'

const GuardianApp = () => {
  const [walkers, setWalkers] = useState([])
  const [selectedWalker, setSelectedWalker] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    fetchWalkers()
  }, [])

  const fetchWalkers = async () => {
    setIsLoading(true)
    try {
      const response = await guardianAPI.getWalkers()
      setWalkers(response.data)
    } catch (error) {
      toast.error('Failed to fetch walkers')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await guardianAPI.acknowledgeSOSAlert(alertId)
      toast.success('Alert acknowledged')
    } catch (error) {
      toast.error('Failed to acknowledge alert')
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">👩 Guardian Dashboard</h1>

        {isLoading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading walkers...</p>
          </div>
        ) : walkers.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600">You are not monitoring any walkers yet.</p>
            <p className="text-sm text-gray-500 mt-2">Ask a walker to add you as their guardian.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {walkers.map((walker) => (
              <div key={walker.id} className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-2">{walker.first_name} {walker.last_name}</h3>
                <p className="text-sm text-gray-600 mb-4">{walker.email}</p>
                <p className="text-sm text-gray-600 mb-4">📱 {walker.phone_number}</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedWalker(walker)}
                    className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 rounded-lg transition"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default GuardianApp
