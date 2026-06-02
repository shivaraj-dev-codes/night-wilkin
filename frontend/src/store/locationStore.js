import { create } from 'zustand'

const useLocationStore = create((set) => ({
  currentLocation: null,
  watcherId: null,
  isTracking: false,

  setCurrentLocation: (location) => set({ currentLocation: location }),

  startTracking: (watcherId) => set({
    isTracking: true,
    watcherId,
  }),

  stopTracking: () => set({
    isTracking: false,
    watcherId: null,
  }),
}))

export default useLocationStore
