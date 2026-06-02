import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: (user, accessToken, refreshToken) => set({
        user,
        accessToken,
        refreshToken,
        isAuthenticated: true,
      }),

      logout: () => set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
      }),

      setLoading: (isLoading) => set({ isLoading }),

      updateProfile: (profile) => set((state) => ({
        user: { ...state.user, ...profile }
      })),
    }),
    {
      name: 'auth-storage',
    }
  )
)

export default useAuthStore
