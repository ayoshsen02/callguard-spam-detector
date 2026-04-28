import { useState }         from 'react'
import { useNavigate }      from 'react-router-dom'
import { analyzeCall }      from '../utils/api'
import { useAuth }          from '../App'
import toast                from 'react-hot-toast'
import Navbar               from '../components/Navbar'
import ResultCard           from '../components/ResultCard'
import HighlightedText      from '../components/HighlightedText'
import { Scan, Eraser, AlertTriangle } from 'lucide-react'

const SAMPLE_SPAM = `Hello, this is the IRS calling. We have detected fraudulent activity on your account and a warrant has been issued in your name. You owe $3,200 in back taxes. To avoid immediate arrest, press 1 now or call us back within 24 hours. Failure to respond will result in legal action.`

const SAMPLE_SAFE = `Hi, this is Sarah from Dr. Johnson's office calling for Alex. We wanted to remind you that your annual check-up is scheduled for tomorrow, Thursday, at 2:30 PM. Please call us back at 555-0100 if you need to reschedule. Have a great day!`

export default function Dashboard() {
  const { logout, theme } = useAuth()
  const navigate          = useNavigate()

  const [text,    setText]    = useState('')
  const [result,  setResult]  = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleAnalyze() {
    if (text.trim().length < 10) {
      return toast.error('Please enter at least 10 characters of call text.')
    }
    setLoading(true)
    setResult(null)
    try {
      const res = await analyzeCall(text)
      setResult(res.data)
      if (res.data.label === 'spam') {
        toast.error('⚠️ Spam / Fraud call detected!')
      } else {
        toast.success('✅ Call appears safe.')
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Analysis failed. Is the backend running?'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      <Navbar />

      {/* Hero strip */}
      <div className="relative overflow-hidden border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-40"
               style={{ background: 'radial-gradient(ellipse 60% 100% at 50% 0%, rgba(14,165,233,0.12), transparent)' }} />
        </div>
        <div className="max-w-4xl mx-auto px-6 py-10 relative">
          <h1 className="font-display text-3xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
            Analyse a Call
          </h1>
          <p style={{ color: 'var(--text-muted)' }} className="text-sm">
            Paste or type a call transcript below. Our AI will detect spam and fraud signals instantly.
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">

        {/* Input card */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold text-base" style={{ color: 'var(--text-primary)' }}>
              Call Transcript
            </h2>
            <div className="flex gap-2">
              <button className="text-xs px-3 py-1.5 rounded-lg border font-mono transition-colors"
                      style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}
                      onClick={() => setText(SAMPLE_SPAM)}>
                Sample Spam
              </button>
              <button className="text-xs px-3 py-1.5 rounded-lg border font-mono transition-colors"
                      style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}
                      onClick={() => setText(SAMPLE_SAFE)}>
                Sample Safe
              </button>
            </div>
          </div>

          <textarea
            className="input-field font-body text-sm resize-none leading-relaxed"
            rows={8}
            placeholder="Paste or type the call conversation here…

Example: 'Hello, this is the IRS calling about unpaid taxes…'"
            value={text}
            onChange={e => setText(e.target.value)}
          />

          <div className="flex items-center justify-between mt-4">
            <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
              {text.length} / 5000 characters
            </span>
            <div className="flex gap-3">
              <button className="btn-outline text-sm py-2.5 flex items-center gap-2"
                      onClick={() => { setText(''); setResult(null) }}>
                <Eraser size={14} /> Clear
              </button>
              <button className="btn-primary text-sm py-2.5 flex items-center gap-2"
                      onClick={handleAnalyze}
                      disabled={loading || !text.trim()}>
                {loading ? (
                  <span className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full" />
                ) : (
                  <Scan size={15} />
                )}
                {loading ? 'Analysing…' : 'Analyse Call'}
              </button>
            </div>
          </div>
        </div>

        {/* Result */}
        {result && (
          <div className="animate-slide-up space-y-4">
            <ResultCard result={result} />
            {result.suspicious_words?.length > 0 && (
              <div className="card p-6">
                <h3 className="font-display font-semibold text-sm mb-4 flex items-center gap-2"
                    style={{ color: 'var(--text-primary)' }}>
                  <AlertTriangle size={16} className="text-amber-400" />
                  Highlighted Transcript
                </h3>
                <HighlightedText text={text} keywords={result.suspicious_words} />
              </div>
            )}
          </div>
        )}

        {/* History CTA */}
        <div className="text-center py-4">
          <button className="text-sm" style={{ color: 'var(--text-muted)' }}
                  onClick={() => navigate('/history')}>
            View analysis history →
          </button>
        </div>
      </div>
    </div>
  )
}
