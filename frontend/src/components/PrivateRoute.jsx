import React from 'react'
import { Navigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const PrivateRoute = () => {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export default PrivateRoute
