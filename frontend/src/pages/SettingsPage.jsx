import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import { authAPI, safetyAPI } from '../api/endpoints'
import useAuthStore from '../store/authStore'

const SettingsPage = () => {
  const { user, updateProfile } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [emergencyContacts, setEmergencyContacts] = useState([])
  const [newContact, setNewContact] = useState({ name: '', phone_number: '' })
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    bio: user?.bio || '',
    auto_sos_enabled: user?.auto_sos_enabled || true,
    check_in_interval_minutes: user?.check_in_interval_minutes || 30,
    max_session_duration_hours: user?.max_session_duration_hours || 6,
  })

  useEffect(() => {
    fetchEmergencyContacts()
  }, [])

  const fetchEmergencyContacts = async () => {
    try {
      const response = await safetyAPI.getEmergencyContacts()
      setEmergencyContacts(response.data)
    } catch (error) {
      toast.error('Failed to fetch emergency contacts')
    }
  }

  const handleProfileUpdate = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await authAPI.updateProfile(formData)
      updateProfile(formData)
      toast.success('Profile updated successfully!')
    } catch (error) {
      toast.error('Failed to update profile')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddContact = async (e) => {
    e.preventDefault()
    try {
      const response = await safetyAPI.addEmergencyContact(newContact)
      setEmergencyContacts([...emergencyContacts, response.data])
      setNewContact({ name: '', phone_number: '' })
      toast.success('Emergency contact added!')
    } catch (error) {
      toast.error('Failed to add contact')
    }
  }

  const handleDeleteContact = async (contactId) => {
    try {
      await safetyAPI.deleteEmergencyContact(contactId)
      setEmergencyContacts(emergencyContacts.filter((c) => c.id !== contactId))
      toast.success('Contact deleted')
    } catch (error) {
      toast.error('Failed to delete contact')
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">⚙️ Settings</h1>

        {/* Profile Settings */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">Profile Settings</h2>
          <form onSubmit={handleProfileUpdate} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
              <textarea
                value={formData.bio}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
                rows="3"
              />
            </div>

            <h3 className="text-lg font-bold mt-6 mb-4">Safety Preferences</h3>

            <div className="flex items-center gap-4">
              <input
                type="checkbox"
                checked={formData.auto_sos_enabled}
                onChange={(e) => setFormData({ ...formData, auto_sos_enabled: e.target.checked })}
                className="w-4 h-4 text-pink-500 rounded"
              />
              <label className="text-sm font-medium text-gray-700">Enable Auto SOS on Inactivity</label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Check-in Interval (minutes)</label>
              <input
                type="number"
                value={formData.check_in_interval_minutes}
                onChange={(e) => setFormData({ ...formData, check_in_interval_minutes: parseInt(e.target.value) })}
                min="5"
                max="120"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Max Session Duration (hours)</label>
              <input
                type="number"
                value={formData.max_session_duration_hours}
                onChange={(e) => setFormData({ ...formData, max_session_duration_hours: parseInt(e.target.value) })}
                min="1"
                max="24"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-pink-500 hover:bg-pink-600 text-white font-bold py-2 rounded-lg transition disabled:opacity-50 mt-6"
            >
              {isLoading ? 'Saving...' : 'Save Profile'}
            </button>
          </form>
        </div>

        {/* Emergency Contacts */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">🆘 Emergency Contacts</h2>

          {/* Add Contact Form */}
          <form onSubmit={handleAddContact} className="space-y-4 mb-8 pb-8 border-b">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                <input
                  type="text"
                  value={newContact.name}
                  onChange={(e) => setNewContact({ ...newContact, name: e.target.value })}
                  placeholder="Contact name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                <input
                  type="tel"
                  value={newContact.phone_number}
                  onChange={(e) => setNewContact({ ...newContact, phone_number: e.target.value })}
                  placeholder="Phone number"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
                  required
                />
              </div>
            </div>
            <button
              type="submit"
              className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition"
            >
              Add Contact
            </button>
          </form>

          {/* Contacts List */}
          <div className="space-y-3">
            {emergencyContacts.length === 0 ? (
              <p className="text-gray-600">No emergency contacts added yet</p>
            ) : (
              emergencyContacts.map((contact) => (
                <div key={contact.id} className="flex justify-between items-center bg-gray-50 p-4 rounded-lg">
                  <div>
                    <p className="font-semibold text-gray-800">{contact.name}</p>
                    <p className="text-sm text-gray-600">{contact.phone_number}</p>
                  </div>
                  <button
                    onClick={() => handleDeleteContact(contact.id)}
                    className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg transition text-sm"
                  >
                    Delete
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage
