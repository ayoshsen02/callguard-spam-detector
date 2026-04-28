import { Routes, Route, Navigate } from 'react-router-dom'
import { createContext, useContext, useState, useEffect } from 'react'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'

export const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

function PrivateRoute({ children }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('cg_token') || '')
  const [theme, setTheme] = useState('dark')

  useEffect(() => {
    document.documentElement.classList.toggle('light', theme === 'light')
  }, [theme])

  const login = (t) => { setToken(t); localStorage.setItem('cg_token', t) }
  const logout = () => { setToken(''); localStorage.removeItem('cg_token') }
  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark')

  return (
    <AuthContext.Provider value={{ token, login, logout, theme, toggleTheme }}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthContext.Provider>
  )
}
