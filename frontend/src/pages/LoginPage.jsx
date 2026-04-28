import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { verifyOTP } from '../utils/api'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [step, setStep] = useState('phone')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSendOTP(e) {
    e.preventDefault()
    setStep('otp')
  }

  async function handleVerify(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await verifyOTP('dev-token')
      login(res.data.token)
      navigate('/')
    } catch {
      setError('Login failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center',background:'linear-gradient(135deg,#060d18,#0d1f35)'}}>
      <div style={{background:'#0d1f35',border:'1px solid rgba(56,189,248,0.2)',borderRadius:16,padding:40,width:380,boxShadow:'0 0 60px rgba(14,165,233,0.1)'}}>
        <div style={{textAlign:'center',marginBottom:32}}>
          <div style={{fontSize:48,marginBottom:8}}>🛡️</div>
          <h1 style={{fontSize:24,fontWeight:700,color:'#e8f4fd'}}>CallGuard</h1>
          <p style={{color:'#7ba4c0',fontSize:14,marginTop:4}}>AI-Powered Spam Call Detection</p>
        </div>

        {step === 'phone' ? (
          <form onSubmit={handleSendOTP}>
            <label style={{display:'block',color:'#7ba4c0',fontSize:12,marginBottom:6,textTransform:'uppercase',letterSpacing:1}}>Phone Number</label>
            <input
              type="tel"
              placeholder="+919876543210"
              value={phone}
              onChange={e => setPhone(e.target.value)}
              style={{width:'100%',background:'#060d18',border:'1px solid rgba(56,189,248,0.2)',borderRadius:10,padding:'12px 16px',color:'#e8f4fd',fontSize:14,marginBottom:16,outline:'none'}}
              required
            />
            <button type="submit" style={{width:'100%',background:'#0ea5e9',border:'none',borderRadius:10,padding:'12px',color:'white',fontWeight:600,fontSize:14,cursor:'pointer'}}>
              Send OTP →
            </button>
            <p style={{color:'#f59e0b',fontSize:12,marginTop:12,textAlign:'center'}}>🛠 Dev mode — any number works</p>
          </form>
        ) : (
          <form onSubmit={handleVerify}>
            <label style={{display:'block',color:'#7ba4c0',fontSize:12,marginBottom:6,textTransform:'uppercase',letterSpacing:1}}>Enter OTP</label>
            <input
              type="text"
              placeholder="Enter any 6 digits"
              value={otp}
              onChange={e => setOtp(e.target.value)}
              style={{width:'100%',background:'#060d18',border:'1px solid rgba(56,189,248,0.2)',borderRadius:10,padding:'12px 16px',color:'#e8f4fd',fontSize:14,marginBottom:16,outline:'none',textAlign:'center',letterSpacing:8,fontSize:20}}
              maxLength={6}
              required
            />
            {error && <p style={{color:'#ef4444',fontSize:13,marginBottom:12}}>{error}</p>}
            <button type="submit" disabled={loading} style={{width:'100%',background:'#0ea5e9',border:'none',borderRadius:10,padding:'12px',color:'white',fontWeight:600,fontSize:14,cursor:'pointer',opacity:loading?0.6:1}}>
              {loading ? 'Verifying...' : '🔐 Verify & Sign In'}
            </button>
            <button type="button" onClick={() => setStep('phone')} style={{width:'100%',background:'none',border:'none',color:'#7ba4c0',marginTop:12,cursor:'pointer',fontSize:13}}>
              ← Use different number
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
