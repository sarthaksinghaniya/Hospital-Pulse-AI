import React, { useEffect, useMemo, useState } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Stack,
  Chip,
  Divider,
  LinearProgress,
  Skeleton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Alert as MuiAlert,
  Button,
} from '@mui/material'
import Box from '@mui/material/Box'
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import ShieldIcon from '@mui/icons-material/Shield'
import LocalHospitalIcon from '@mui/icons-material/LocalHospital'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import GroupIcon from '@mui/icons-material/Group'
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart'
import TimelineIcon from '@mui/icons-material/Timeline'
import axios from 'axios'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts'
import SectionCard from './components/SectionCard'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const formatTS = (ts) => new Date(ts).toLocaleString([], { hour: '2-digit', minute: '2-digit', weekday: 'short' })

function CapacityMeter({ value, max, label }) {
  const pct = Math.min(100, Math.round((value / max) * 100))
  const color = pct > 85 ? 'error' : pct > 65 ? 'warning' : 'success'
  return (
    <Stack spacing={0.5}>
      <Stack direction="row" justifyContent="space-between">
        <Typography variant="body2" fontWeight={600}>
          {label}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {pct}%
        </Typography>
      </Stack>
      <LinearProgress variant="determinate" value={pct} color={color} sx={{ height: 8, borderRadius: 6 }} />
    </Stack>
  )
}

function AlertList({ alerts }) {
  if (!alerts.length) return null
  return (
    <Stack spacing={1}>
      {alerts.map((a, idx) => (
        <MuiAlert
          key={idx}
          iconMapping={{
            success: <LocalHospitalIcon fontSize="inherit" />,
            warning: <WarningAmberIcon fontSize="inherit" />,
            error: <WarningAmberIcon fontSize="inherit" />,
            info: <TimelineIcon fontSize="inherit" />,
          }}
          severity={a.severity === 'high' ? 'error' : a.severity === 'medium' ? 'warning' : 'info'}
          sx={{ alignItems: 'center' }}
        >
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
            <Chip
              size="small"
              label={a.severity === 'high' ? 'Critical' : a.severity === 'medium' ? 'Caution' : 'Info'}
              color={a.severity === 'high' ? 'error' : a.severity === 'medium' ? 'warning' : 'default'}
              variant="outlined"
            />
            <Chip size="small" label={`~${a.window}`} color="default" variant="outlined" />
            <Typography fontWeight={700}>{a.message}</Typography>
          </Stack>
        </MuiAlert>
      ))}
    </Stack>
  )
}

function Recommendations({ items }) {
  return (
    <List dense>
      {items.map((r, idx) => (
        <ListItem key={idx} alignItems="flex-start">
          <ListItemIcon>
            <GroupIcon color={r.priority === 'high' ? 'error' : r.priority === 'medium' ? 'warning' : 'info'} />
          </ListItemIcon>
          <ListItemText
            primary={
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography fontWeight={700}>{r.action}</Typography>
                <Chip
                  size="small"
                  label={r.priority}
                  color={r.priority === 'high' ? 'error' : r.priority === 'medium' ? 'warning' : 'default'}
                  variant="outlined"
                />
                <Chip size="small" label="Interpretable" variant="outlined" color="success" />
              </Stack>
            }
            secondary={
              <Typography variant="body2" color="text.secondary">
                Why this matters: {r.rationale}
              </Typography>
            }
          />
        </ListItem>
      ))}
    </List>
  )
}

function LineSection({ data, dataKey, color }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ left: -20, right: 10, top: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5eaf0" />
        <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#4a5568' }} angle={-20} height={50} />
        <YAxis allowDecimals={false} tick={{ fill: '#4a5568' }} />
        <Tooltip formatter={(v) => v.toFixed ? v.toFixed(1) : v} />
        <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2.2} dot={false} animationDuration={350} />
      </LineChart>
    </ResponsiveContainer>
  )
}

function HeatBar({ data, color }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ left: -20, right: 10, top: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
        <XAxis dataKey="label" tick={{ fontSize: 11 }} angle={-20} height={50} />
        <YAxis domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} />
        <Tooltip formatter={(v) => `${Math.round(v * 100)}%`} />
        <Bar dataKey="risk" fill={color} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default function App() {
  const [emergency, setEmergency] = useState([])
  const [icu, setIcu] = useState([])
  const [staff, setStaff] = useState([])
  const [alerts, setAlerts] = useState([])
  const [recs, setRecs] = useState([])
  const [emergencySummary, setEmergencySummary] = useState('')
  const [icuSummary, setIcuSummary] = useState('')
  const [staffSummary, setStaffSummary] = useState('')
  const [alertsSummary, setAlertsSummary] = useState('')
  const [recsSummary, setRecsSummary] = useState('')
  const [sewi, setSewi] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [chatOpen, setChatOpen] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const [chatMessages, setChatMessages] = useState([
    { from: 'HOPX', text: 'Welcome to Hospital Pulse AI. I can explain SEWI, forecasts, and recommendations. How can I help?' },
  ])

  const fetchAll = async () =>
    {
      setLoading(true)
      setError('')
      try {
        const [emer, icuRes, staffRes, alertsRes, recsRes, sewiRes] = await Promise.all([
          axios.post(`${API_BASE}/predict/emergency`, { horizon_hours: 168 }),
          axios.post(`${API_BASE}/predict/icu`, { horizon_hours: 168 }),
          axios.post(`${API_BASE}/predict/staff`, { horizon_hours: 72 }),
          axios.get(`${API_BASE}/alerts`),
          axios.get(`${API_BASE}/recommendations`),
          axios.get(`${API_BASE}/feature/surge-early-warning`),
        ])
        setEmergency(
          emer.data.forecast.map((p) => ({ label: formatTS(p.timestamp), value: p.value }))
        )
        setEmergencySummary(emer.data.summary)
        setIcu(icuRes.data.required_beds.map((p) => ({ label: formatTS(p.timestamp), value: p.value })))
        setIcuSummary(icuRes.data.summary)
        setStaff(
          staffRes.data.workload.map((w, idx) => ({ label: `${w.shift} #${idx + 1}`, risk: w.risk_score, note: w.stress_note }))
        )
        setStaffSummary(staffRes.data.summary)
        setAlerts(alertsRes.data.alerts || [])
        setAlertsSummary(alertsRes.data.summary || '')
        setRecs(recsRes.data.recommendations || [])
        setRecsSummary(recsRes.data.summary || '')
        setSewi(sewiRes.data)
      } catch (err) {
        console.error(err)
        setError('Failed to load data from backend. Is FastAPI running on port 8000?')
      } finally {
        setLoading(false)
      }
    }

  useEffect(() => {
    fetchAll()
  }, [])

  const peakIcu = useMemo(() => (icu.length ? Math.max(...icu.map((d) => d.value)) : 0), [icu])
  const latestEmergency = useMemo(() => (emergency.length ? emergency[0].value : 0), [emergency])
  const readinessScore = useMemo(() => {
    const sewiScore = sewi ? (1 - sewi.score) * 0.6 : 0.3
    const alertPenalty = alerts.some((a) => a.severity === 'high') ? 0.2 : alerts.some((a) => a.severity === 'medium') ? 0.1 : 0
    const base = 0.8 - alertPenalty
    return Math.max(0, Math.min(1, base + sewiScore * 0.2))
  }, [sewi, alerts])

  const pushMessage = (from, text) => {
    setChatMessages((msgs) => [...msgs, { from, text }])
    // Auto-scroll to latest message after a short delay
    setTimeout(() => {
      const chatEl = document.getElementById('hopx-chat-scroll')
      if (chatEl) chatEl.scrollTop = chatEl.scrollHeight
    }, 100)
  }

  const handleQuickAsk = (q) => {
    setChatInput(q)
    handleChatSend(q)
  }

  const handleChatSend = (overrideText) => {
    const text = (overrideText ?? chatInput).trim()
    if (!text) return
    pushMessage('You', text)
    setChatInput('')
    // Auto-scroll to chat widget when used
    setTimeout(() => {
      const chatEl = document.getElementById('hopx-chat-container')
      if (chatEl) {
        chatEl.scrollIntoView({ behavior: 'smooth', block: 'end' })
      }
    }, 150)
    // Call backend for chat reply
    ;(async () => {
      try {
        const res = await axios.post(`${API_BASE}/feature/hopx-chat`, { message: text })
        pushMessage('HOPX', res.data.reply)
      } catch {
        // Fallback rule-based replies
        let reply = 'I can help summarize SEWI, alerts, and recommendations.'
        const t = text.toLowerCase()
        if (t.includes('sewi')) {
          reply =
            'SEWI combines ER surge, ICU peak, and staff pressure into one operational risk score. Lower is better; high levels mean activate surge plans.'
        } else if (t.includes('alert')) {
          reply = 'Alerts flag critical or caution items for the next 72h, with time windows like ~48h to act early.'
        } else if (t.includes('recommend')) {
          reply = 'Recommendations are rule-based actions tied to detected risks (e.g., add triage staff, prep ICU beds).'
        } else if (t.includes('icu')) {
          reply = 'ICU forecast tracks projected occupancy vs a 40-bed capacity; peaks nearing capacity raise operational risk.'
        } else if (t.includes('staff') || t.includes('workload')) {
          reply = 'Staff workload pressure estimates nurse-to-patient stress; high pressure suggests reallocating shifts.'
        }
        pushMessage('HOPX', reply)
      }
    })()
  }

  return (
    <Paper sx={{ minHeight: '100vh', bgcolor: '#f7f9fb' }}>
      <AppBar position="static" color="primary" sx={{ bgcolor: '#0b5aa2' }}>
        <Toolbar sx={{ gap: 2 }}>
          <Box component="img" src="/hopex4.jpg" sx={{ height: 32, width: 32, mr: 1 }} />
          <Typography variant="h6" fontWeight={700} sx={{ flexGrow: 1 }}>
            Hospital Pulse AI
          </Typography>
          <Chip label="Decision Support Tool" color="default" size="small" variant="outlined" sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.7)' }} />
          <Chip
            icon={<ShieldIcon sx={{ color: 'white !important' }} />}
            label={
              sewi
                ? `SEWI: ${sewi.risk_level.toUpperCase()} • ${Math.round(sewi.score * 100)}%`
                : 'SEWI loading'
            }
            color={sewi && sewi.risk_level === 'high' ? 'error' : sewi && sewi.risk_level === 'medium' ? 'warning' : 'success'}
            variant="outlined"
            sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }}
          />
          <Chip
            label={`Readiness: ${Math.round(readinessScore * 100)}%`}
            color={readinessScore > 0.75 ? 'success' : readinessScore > 0.55 ? 'warning' : 'error'}
            variant="outlined"
            sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }}
          />
        </Toolbar>
      </AppBar>

      <Container sx={{ py: 3 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ xs: 'flex-start', md: 'center' }} mb={2}>
          <Typography variant="h5" fontWeight={700}>
            Hospital Operations Command Dashboard
          </Typography>
          <Chip label="Aggregated Data" variant="outlined" color="primary" />
          <Chip label="Interpretable AI" variant="outlined" color="success" />
          <Chip label="Decision Support Only" variant="outlined" color="default" />
          <Button variant="contained" onClick={fetchAll} disabled={loading}>
            Refresh data
          </Button>
        </Stack>

        {error && <MuiAlert severity="error" sx={{ mb: 2 }}>{error}</MuiAlert>}
        {loading && <LinearProgress sx={{ mb: 2 }} />}

        <Grid container spacing={2}>
          <Grid item xs={12} md={12}>
            <SectionCard
              title="Surge Early-Warning Index"
              subtitle="Composite ER/ICU/staff operational risk"
              action={
                sewi ? (
                  <Chip
                    icon={<ShieldIcon />}
                    label={`${sewi.risk_level.toUpperCase()} • ${Math.round(sewi.score * 100)}%`}
                    color={sewi.risk_level === 'high' ? 'error' : sewi.risk_level === 'medium' ? 'warning' : 'success'}
                    variant="outlined"
                  />
                ) : null
              }
            >
              {sewi ? (
                <Stack spacing={1.5}>
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <CapacityMeter label="SEWI (inverse readiness)" value={sewi.score * 100} max={100} />
                    <CapacityMeter label="Readiness score" value={Math.round(readinessScore * 100)} max={100} />
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {sewi.explanation}
                  </Typography>
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <Chip icon={<TimelineIcon />} label={`ER surge: ${Math.round(sewi.surge_probability * 100)}%`} variant="outlined" />
                    <Chip icon={<MonitorHeartIcon />} label={`ICU peak: ${Math.round(sewi.icu_peak_risk * 100)}%`} variant="outlined" />
                    <Chip icon={<GroupIcon />} label={`Staff pressure: ${Math.round(sewi.staff_max_risk * 100)}%`} variant="outlined" />
                  </Stack>
                  <Typography variant="body2" fontWeight={700}>
                    Recommended actions:
                  </Typography>
                  <List dense>
                    {sewi.actions.map((a, idx) => (
                      <ListItem key={idx}>
                        <ListItemIcon><ShieldIcon color="primary" /></ListItemIcon>
                        <ListItemText primary={a} />
                      </ListItem>
                    ))}
                  </List>
                </Stack>
              ) : (
                <Skeleton variant="rectangular" height={120} />
              )}
            </SectionCard>
          </Grid>

          <Grid item xs={12} md={12}>
            <SectionCard title="Emergency Load Forecast" subtitle="Next 7 days (hourly)">
              {loading ? <Skeleton variant="rectangular" height={260} sx={{ borderRadius: 2 }} /> : <LineSection data={emergency} dataKey="value" color="#0b5aa2" />}
              <Divider sx={{ my: 2 }} />
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <CapacityMeter label="Current ER load vs baseline" value={latestEmergency} max={80} />
                <CapacityMeter label="Surge threshold (80th pct)" value={latestEmergency} max={100} />
              </Stack>
              {emergencySummary && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  AI note: {emergencySummary}
                </Typography>
              )}
            </SectionCard>
          </Grid>

          <Grid item xs={12} md={4}>
            <SectionCard title="Alerts" subtitle="Next 72h">
              {loading ? (
                <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
              ) : (
                <AlertList alerts={alerts} />
              )}
              {alertsSummary && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  AI note: {alertsSummary}
                </Typography>
              )}
            </SectionCard>
          </Grid>

          <Grid item xs={12} md={6}>
            <SectionCard title="ICU Capacity Monitor" subtitle="Projected occupancy">
              {loading ? <Skeleton variant="rectangular" height={260} sx={{ borderRadius: 2 }} /> : <LineSection data={icu} dataKey="value" color="#d32f2f" />}
              <Divider sx={{ my: 2 }} />
              <CapacityMeter label="Projected peak vs capacity (40 beds)" value={peakIcu} max={40} />
              {icuSummary && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  AI note: {icuSummary}
                </Typography>
              )}
            </SectionCard>
          </Grid>

          <Grid item xs={12} md={6}>
            <SectionCard title="Staff Workload Heatmap" subtitle="Risk by predicted shifts">
              {loading ? <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} /> : <HeatBar data={staff} color="#ed6c02" />}
              <Divider sx={{ my: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Nurse-to-patient stress score derived from ER demand and staffing levels.
              </Typography>
              {staffSummary && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  AI note: {staffSummary}
                </Typography>
              )}
            </SectionCard>
          </Grid>

          <Grid item xs={12}>
            <SectionCard
              title="AI Recommendations"
              subtitle="Actionable adjustments based on surge and ICU risk"
              action={<Chip label="Interpretable" color="success" size="small" />}
            >
              {loading ? (
                <Skeleton variant="rectangular" height={140} sx={{ borderRadius: 2 }} />
              ) : (
                <>
                  {recsSummary && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    AI note: {recsSummary}
                  </Typography>
                  )}
                  <Recommendations items={recs} />
                </>
              )}
            </SectionCard>
          </Grid>
        </Grid>
      </Container>

      {/* HOPX Mini Chat Bot */}
      <Paper
        elevation={chatOpen ? 6 : 3}
        sx={{
          position: 'fixed',
          right: 16,
          bottom: 16,
          width: chatOpen ? 320 : 64,
          height: chatOpen ? 420 : 64,
          borderRadius: chatOpen ? 3 : '50%',
          overflow: 'hidden',
          transition: 'all 200ms ease',
          bgcolor: '#fdfefe',
          border: '1px solid #e6ecf2',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 1300,
        }}
        id="hopx-chat-container"
      >
        <Button
          startIcon={chatOpen ? <SmartToyIcon /> : <ChatBubbleOutlineIcon />}
          onClick={() => setChatOpen((v) => !v)}
          sx={{
            justifyContent: 'flex-start',
            px: chatOpen ? 2 : 1.5,
            py: chatOpen ? 1.5 : 1,
            minHeight: 48,
            color: '#0b5aa2',
          }}
        >
          {chatOpen ? 'HOPX Assistant' : ''}
        </Button>
        {chatOpen && (
          <>
            <Divider />
            <Stack spacing={1} sx={{ p: 1.5, flex: 1, overflowY: 'auto' }} id="hopx-chat-scroll">
              {chatMessages.map((m, idx) => (
                <Stack
                  key={idx}
                  alignItems={m.from === 'HOPX' ? 'flex-start' : 'flex-end'}
                >
                  <Paper
                    sx={{
                      p: 1,
                      maxWidth: '95%',
                      bgcolor: m.from === 'HOPX' ? '#eef4fb' : '#dff3e3',
                      borderRadius: 2,
                    }}
                  >
                    <Typography variant="caption" color="text.secondary">
                      {m.from}
                    </Typography>
                    <Typography variant="body2">{m.text}</Typography>
                  </Paper>
                </Stack>
              ))}
            </Stack>
            <Stack direction="row" spacing={1} sx={{ px: 1.5, pb: 1 }}>
              {['What is SEWI?', 'Explain alerts', 'Show recommendations'].map((q) => (
                <Chip key={q} size="small" label={q} onClick={() => handleQuickAsk(q)} />
              ))}
            </Stack>
            <Stack direction="row" spacing={1} sx={{ p: 1.5 }}>
              <input
                style={{
                  flex: 1,
                  border: '1px solid #e6ecf2',
                  borderRadius: 8,
                  padding: '8px 10px',
                  fontSize: 14,
                }}
                value={chatInput}
                placeholder="Ask HOPX about forecasts or actions..."
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleChatSend()
                }}
              />
              <Button variant="contained" size="small" onClick={handleChatSend} disabled={!chatInput.trim()}>
                Send
              </Button>
            </Stack>
          </>
        )}
      </Paper>
    </Paper>
  )
}
