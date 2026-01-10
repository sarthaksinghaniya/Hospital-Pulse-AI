import React, { useEffect, useMemo, useState } from 'react'
import {
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
  Typography,
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

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001'

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
  // Normalize items to ensure it's always an array
  const normalizedItems = React.useMemo(() => {
    // Handle different API response structures
    if (Array.isArray(items)) {
      return items;
    }
    
    // Handle wrapped structure like { recommendations: [...] }
    if (items && typeof items === 'object' && items.recommendations && Array.isArray(items.recommendations)) {
      return items.recommendations;
    }
    
    // Handle null/undefined or other invalid types
    return [];
  }, [items]);

  // Show empty state when no recommendations
  if (normalizedItems.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No recommendations available at the moment.
        </Typography>
      </Box>
    );
  }

  return (
    <List dense>
      {normalizedItems.map((item, idx) => {
        // Handle both string and object recommendation formats
        const recommendationText = typeof item === 'string' ? item : item?.action || 'Unknown recommendation';
        return (
          <ListItem key={idx}>
            <ListItemIcon>
              <ShieldIcon color="info" />
            </ListItemIcon>
            <ListItemText 
              primary={recommendationText}
              secondary={item?.rationale && typeof item === 'object' ? item.rationale : undefined}
            />
          </ListItem>
        );
      })}
    </List>
  );
}

function LineSection({ data, dataKey, color }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" tick={{ fontSize: 11 }} angle={-20} height={50} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

function HeatBar({ data, color }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} layout="horizontal">
        <XAxis type="number" domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} />
        <YAxis dataKey="label" type="category" width={80} />
        <Tooltip formatter={(v) => `${Math.round(v * 100)}%`} />
        <Bar dataKey="risk" fill={color} radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default function OriginalDashboard() {
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

  const fetchAll = async () => {
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
      setAlerts(alertsRes.data)
      setAlertsSummary(alertsRes.data.summary)
      setRecs(recsRes.data?.recommendations || []) // Extract recommendations array from response
      setRecsSummary(recsRes.data.summary)
      setSewi(sewiRes.data)
    } catch (e) {
      setError('Failed to load dashboard data. Please try again.')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!chatInput.trim()) return
    const userMsg = { from: 'User', text: chatInput }
    setChatMessages((prev) => [...prev, userMsg])
    setChatInput('')
    try {
      const res = await axios.post(`${API_BASE}/feature/chat`, { query: chatInput, context: 'dashboard' })
      setChatMessages((prev) => [...prev, { from: 'HOPX', text: res.data.response }])
    } catch {
      setChatMessages((prev) => [
        ...prev,
        { from: 'HOPX', text: "Sorry, I couldn't process that. Try asking about SEWI, forecasts, or recommendations." },
      ])
    }
  }

  useEffect(() => {
    fetchAll()
  }, [])

  const peakEr = useMemo(() => Math.max(...emergency.map((d) => d.value), 0), [emergency])
  const peakIcu = useMemo(() => Math.max(...icu.map((d) => d.value), 0), [icu])

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={700}>
          Hospital Pulse AI
        </Typography>
        <Stack direction="row" spacing={2}>
          {sewi && (
            <Chip
              icon={<ShieldIcon />}
              label={`SEWI: ${sewi.sewi_score?.toFixed(2)}`}
              color={sewi.risk_level === 'high' ? 'error' : sewi.risk_level === 'medium' ? 'warning' : 'success'}
              variant="outlined"
            />
          )}
          <Button variant="outlined" onClick={fetchAll} disabled={loading}>
            Refresh
          </Button>
        </Stack>
      </Stack>

      {error && (
        <MuiAlert severity="error" sx={{ mb: 3 }}>
          {error}
        </MuiAlert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <SectionCard title="ER Admissions Forecast" subtitle="Next 7 days">
            {loading ? <Skeleton variant="rectangular" height={260} sx={{ borderRadius: 2 }} /> : <LineSection data={emergency} dataKey="value" color="#1976d2" />}
            <Divider sx={{ my: 2 }} />
            <CapacityMeter label="Projected peak vs capacity (100 pts)" value={peakEr} max={100} />
            {emergencySummary && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                AI note: {emergencySummary}
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

        <Grid item xs={12}>
          <SectionCard title="Active Alerts" subtitle="System-generated notifications">
            {loading ? (
              <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
            ) : (
              <>
                {alertsSummary && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    AI note: {alertsSummary}
                  </Typography>
                )}
                <AlertList alerts={alerts} />
              </>
            )}
          </SectionCard>
        </Grid>
      </Grid>

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
                      bgcolor: m.from === 'HOPX' ? '#f0f7ff' : '#e3f2fd',
                      maxWidth: '85%',
                      wordBreak: 'break-word',
                    }}
                  >
                    <Typography variant="body2">{m.text}</Typography>
                  </Paper>
                </Stack>
              ))}
            </Stack>
            <Stack direction="row" sx={{ p: 1, borderTop: '1px solid #e6ecf2' }}>
              <input
                type="text"
                placeholder="Ask about SEWI, forecasts..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                style={{
                  flex: 1,
                  border: 'none',
                  outline: 'none',
                  padding: '8px',
                  fontSize: '14px',
                }}
              />
              <Button size="small" onClick={handleSend} disabled={!chatInput.trim()}>
                Send
              </Button>
            </Stack>
          </>
        )}
      </Paper>
    </Container>
  )
}
