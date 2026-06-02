import React from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const Dashboard = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-pink-600">Night Wilkin</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">Welcome, {user?.first_name || user?.username}</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {user?.role === 'walker' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              onClick={() => navigate('/walker/session')}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition"
            >
              <div className="text-4xl mb-4">🚶</div>
              <h2 className="text-xl font-bold mb-2">Start Walk Session</h2>
              <p className="text-gray-600">Begin tracking your walk with real-time location sharing</p>
            </div>

            <div
              onClick={() => navigate('/walker/sos')}
              className="bg-red-50 p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition border-2 border-red-300"
            >
              <div className="text-4xl mb-4">🆘</div>
              <h2 className="text-xl font-bold text-red-600 mb-2">Emergency SOS</h2>
              <p className="text-gray-600">Alert all your guardians immediately</p>
            </div>

            <div
              onClick={() => navigate('/map')}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition"
            >
              <div className="text-4xl mb-4">🗺️</div>
              <h2 className="text-xl font-bold mb-2">View Map</h2>
              <p className="text-gray-600">See safe locations and danger zones nearby</p>
            </div>

            <div
              onClick={() => navigate('/settings')}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition"
            >
              <div className="text-4xl mb-4">⚙️</div>
              <h2 className="text-xl font-bold mb-2">Settings</h2>
              <p className="text-gray-600">Manage your profile and safety preferences</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              onClick={() => navigate('/guardian/walkers')}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition"
            >
              <div className="text-4xl mb-4">👩</div>
              <h2 className="text-xl font-bold mb-2">My Walkers</h2>
              <p className="text-gray-600">Monitor and protect the women you care about</p>
            </div>

            <div
              onClick={() => navigate('/guardian/alerts')}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition"
            >
              <div className="text-4xl mb-4">🚨</div>
              <h2 className="text-xl font-bold mb-2">SOS Alerts</h2>
              <p className="text-gray-600">View and respond to emergency alerts</p>
            </div>

            <div
              onClick={() => navigate('/map')}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition"
            >
              <div className="text-4xl mb-4">🗺️</div>
              <h2 className="text-xl font-bold mb-2">View Map</h2>
              <p className="text-gray-600">See walker locations and danger zones</p>
            </div>

            <div
              onClick={() => navigate('/settings')}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition"
            >
              <div className="text-4xl mb-4">⚙️</div>
              <h2 className="text-xl font-bold mb-2">Settings</h2>
              <p className="text-gray-600">Manage your account settings</p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard
