import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeCall } from '../utils/api'
import { useAuth } from '../App'

const SAMPLE_SPAM = "This is the IRS calling. A warrant has been issued in your name for unpaid taxes. You must pay $3,200 immediately or face arrest within 24 hours. Press 1 now."
const SAMPLE_SAFE = "Hi, this is Dr. Smith's office calling to confirm your appointment tomorrow at 2 PM. Please call us back at 555-0100 if you need to reschedule."

export default function Dashboard() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAnalyze() {
    if (text.trim().length < 10) return setError('Please enter at least 10 characters.')
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await analyzeCall(text)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Is the backend running on port 8000?')
    } finally { setLoading(false) }
  }

  const isSpam = result?.label === 'spam'

  return (
    <div style={{minHeight:'100vh',background:'#060d18'}}>
      {/* Navbar */}
      <nav style={{borderBottom:'1px solid rgba(56,189,248,0.15)',padding:'0 24px',height:56,display:'flex',alignItems:'center',justifyContent:'space-between',background:'rgba(6,13,24,0.9)'}}>
        <span style={{fontWeight:700,fontSize:18,color:'#e8f4fd'}}>🛡️ CallGuard</span>
        <button onClick={() => { logout(); navigate('/login') }} style={{background:'none',border:'1px solid rgba(239,68,68,0.3)',borderRadius:8,padding:'6px 14px',color:'#f87171',cursor:'pointer',fontSize:13}}>
          Sign Out
        </button>
      </nav>

      <div style={{maxWidth:760,margin:'0 auto',padding:32}}>
        {/* Header */}
        <div style={{marginBottom:24}}>
          <h1 style={{fontSize:28,fontWeight:700,color:'#e8f4fd'}}>Analyse a Call</h1>
          <p style={{color:'#7ba4c0',fontSize:14,marginTop:4}}>Paste a call transcript. Our AI detects spam and fraud instantly.</p>
        </div>

        {/* Input Card */}
        <div style={{background:'#0d1f35',border:'1px solid rgba(56,189,248,0.15)',borderRadius:16,padding:24,marginBottom:20}}>
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
            <span style={{color:'#e8f4fd',fontWeight:600}}>Call Transcript</span>
            <div style={{display:'flex',gap:8}}>
              <button onClick={() => setText(SAMPLE_SPAM)} style={{background:'rgba(239,68,68,0.1)',border:'1px solid rgba(239,68,68,0.3)',borderRadius:8,padding:'5px 12px',color:'#f87171',cursor:'pointer',fontSize:12}}>
                Sample Spam
              </button>
              <button onClick={() => setText(SAMPLE_SAFE)} style={{background:'rgba(34,197,94,0.1)',border:'1px solid rgba(34,197,94,0.3)',borderRadius:8,padding:'5px 12px',color:'#4ade80',cursor:'pointer',fontSize:12}}>
                Sample Safe
              </button>
            </div>
          </div>

          <textarea
            rows={7}
            placeholder="Paste or type the call conversation here…"
            value={text}
            onChange={e => setText(e.target.value)}
            style={{width:'100%',background:'#060d18',border:'1px solid rgba(56,189,248,0.15)',borderRadius:10,padding:14,color:'#e8f4fd',fontSize:14,resize:'none',outline:'none',fontFamily:'inherit',lineHeight:1.6}}
          />

          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:12}}>
            <span style={{color:'#7ba4c0',fontSize:12}}>{text.length} / 5000</span>
            <div style={{display:'flex',gap:10}}>
              <button onClick={() => { setText(''); setResult(null) }} style={{background:'none',border:'1px solid rgba(56,189,248,0.2)',borderRadius:10,padding:'10px 18px',color:'#7ba4c0',cursor:'pointer',fontSize:13}}>
                Clear
              </button>
              <button onClick={handleAnalyze} disabled={loading || !text.trim()} style={{background:'#0ea5e9',border:'none',borderRadius:10,padding:'10px 24px',color:'white',fontWeight:600,cursor:'pointer',fontSize:13,opacity:(loading||!text.trim())?0.5:1,display:'flex',alignItems:'center',gap:8}}>
                {loading ? '⏳ Analysing…' : '🔍 Analyse Call'}
              </button>
            </div>
          </div>

          {error && <p style={{color:'#f87171',fontSize:13,marginTop:12}}>⚠️ {error}</p>}
        </div>

        {/* Result Card */}
        {result && (
          <div style={{background:'#0d1f35',border:`2px solid ${isSpam ? 'rgba(239,68,68,0.4)' : 'rgba(34,197,94,0.4)'}`,borderRadius:16,padding:24,boxShadow:`0 0 40px ${isSpam ? 'rgba(239,68,68,0.08)' : 'rgba(34,197,94,0.08)'}`}}>
            {/* Verdict */}
            <div style={{display:'flex',alignItems:'center',gap:16,marginBottom:20}}>
              <div style={{fontSize:48}}>{isSpam ? '⚠️' : '✅'}</div>
              <div>
                <div style={{fontSize:24,fontWeight:700,color: isSpam ? '#f87171' : '#4ade80'}}>
                  {isSpam ? 'SPAM / FRAUD CALL' : 'SAFE CALL'}
                </div>
                <p style={{color:'#7ba4c0',fontSize:14,marginTop:4}}>
                  {isSpam ? 'Do not share personal information. This call shows fraud indicators.' : 'No significant spam signals detected. Call appears legitimate.'}
                </p>
              </div>
            </div>

            {/* Confidence Bar */}
            <div style={{marginBottom:20}}>
              <div style={{display:'flex',justifyContent:'space-between',marginBottom:8}}>
                <span style={{color:'#7ba4c0',fontSize:12,textTransform:'uppercase',letterSpacing:1}}>Confidence</span>
                <span style={{color: isSpam ? '#f87171' : '#4ade80',fontWeight:700,fontSize:18}}>{Math.round(result.confidence * 100)}%</span>
              </div>
              <div style={{height:8,background:'#060d18',borderRadius:4,overflow:'hidden'}}>
                <div style={{height:'100%',width:`${Math.round(result.confidence*100)}%`,background: isSpam ? '#ef4444' : '#22c55e',borderRadius:4,transition:'width 0.7s ease',boxShadow:`0 0 10px ${isSpam ? 'rgba(239,68,68,0.6)' : 'rgba(34,197,94,0.6)'}`}} />
              </div>
            </div>

            {/* Probabilities */}
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12,marginBottom: result.suspicious_words?.length ? 20 : 0}}>
              <div style={{background:'#060d18',borderRadius:12,padding:16}}>
                <div style={{color:'#7ba4c0',fontSize:11,textTransform:'uppercase',letterSpacing:1,marginBottom:4}}>Spam probability</div>
                <div style={{color:'#f87171',fontSize:22,fontWeight:700}}>{Math.round(result.spam_probability*100)}%</div>
              </div>
              <div style={{background:'#060d18',borderRadius:12,padding:16}}>
                <div style={{color:'#7ba4c0',fontSize:11,textTransform:'uppercase',letterSpacing:1,marginBottom:4}}>Safe probability</div>
                <div style={{color:'#4ade80',fontSize:22,fontWeight:700}}>{Math.round(result.safe_probability*100)}%</div>
              </div>
            </div>

            {/* Suspicious Words */}
            {result.suspicious_words?.length > 0 && (
              <div style={{borderTop:'1px solid rgba(56,189,248,0.1)',paddingTop:16}}>
                <div style={{color:'#fbbf24',fontSize:13,fontWeight:600,marginBottom:10}}>🚨 {result.suspicious_words.length} suspicious word(s) detected:</div>
                <div style={{display:'flex',flexWrap:'wrap',gap:8}}>
                  {result.suspicious_words.map(w => (
                    <span key={w} style={{background:'rgba(245,158,11,0.1)',border:'1px solid rgba(245,158,11,0.3)',borderRadius:6,padding:'4px 10px',color:'#fbbf24',fontSize:12,fontFamily:'monospace'}}>
                      {w}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
