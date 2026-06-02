import { create } from 'zustand'

const useSessionStore = create((set) => ({
  activeSession: null,
  sessions: [],
  isLoading: false,

  setActiveSession: (session) => set({ activeSession: session }),

  setSessionActive: (isActive) => set((state) => ({
    activeSession: state.activeSession ? { ...state.activeSession, is_active: isActive } : null
  })),

  setSessions: (sessions) => set({ sessions }),

  addSession: (session) => set((state) => ({
    sessions: [session, ...state.sessions]
  })),

  setLoading: (isLoading) => set({ isLoading }),
}))

export default useSessionStore
