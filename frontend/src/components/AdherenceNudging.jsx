import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Grid,
  Box,
  Chip,
  LinearProgress,
  Alert,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import {
  ThumbUp,
  ThumbDown,
  NotificationsActive,
  TrendingUp,
  TrendingDown,
  Person,
  Message,
  Refresh,
  Send,
  Schedule,
  CheckCircle,
  Warning
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

const AdherenceNudging = () => {
  const [populationOverview, setPopulationOverview] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState('');
  const [adherenceScore, setAdherenceScore] = useState(null);
  const [nudge, setNudge] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nudgeDialogOpen, setNudgeDialogOpen] = useState(false);

  const fetchPopulationOverview = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE}/adherence/population-overview`);
      console.log('Adherence overview response:', response.data);
      if (response.data && response.data.data) {
        setPopulationOverview(response.data.data);
      } else {
        setPopulationOverview(null);
        setError('No population data available');
      }
    } catch (err) {
      console.error('Error fetching population overview:', err);
      setError('Failed to fetch population overview');
      setPopulationOverview(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchAdherenceScore = async (patientId) => {
    try {
      const response = await axios.post(`${API_BASE}/adherence/score`, {
        patient_id: patientId
      });
      setAdherenceScore(response.data.data);
    } catch (err) {
      setError('Failed to fetch adherence score');
    }
  };

  const generateNudge = async (patientId) => {
    try {
      const response = await axios.post(`${API_BASE}/adherence/nudge`, {
        patient_id: patientId,
        patient_name: `Patient ${patientId}`
      });
      setNudge(response.data.data.nudge);
      setNudgeDialogOpen(true);
    } catch (err) {
      setError('Failed to generate nudge');
    }
  };

  const fetchInsights = async (patientId) => {
    try {
      const response = await axios.post(`${API_BASE}/adherence/insights`, {
        patient_id: patientId
      });
      setInsights(response.data.data);
    } catch (err) {
      setError('Failed to fetch insights');
    }
  };

  useEffect(() => {
    fetchPopulationOverview();
  }, []);

  const getAdherenceColor = (level) => {
    switch (level) {
      case 'Excellent': return 'success';
      case 'Good': return 'info';
      case 'Fair': return 'warning';
      case 'Poor': return 'error';
      case 'Critical': return 'error';
      default: return 'default';
    }
  };

  const handlePatientAnalysis = () => {
    if (selectedPatient) {
      fetchAdherenceScore(selectedPatient);
      fetchInsights(selectedPatient);
    }
  };

  const renderPopulationOverview = () => (
    <Card>
      <CardHeader
        title="Population Adherence Overview"
        action={
          <Button onClick={fetchPopulationOverview} startIcon={<Refresh />}>
            Refresh
          </Button>
        }
      />
      <CardContent>
        {loading ? (
          <LinearProgress />
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : populationOverview && typeof populationOverview === 'object' && Object.keys(populationOverview).length > 0 ? (
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6">Total Patients</Typography>
                <Typography variant="h4">{populationOverview?.total_patients || 0}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6">Average Score</Typography>
                <Typography variant="h4">
                  {populationOverview?.average_adherence_score?.toFixed(1) || '0.0'}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6">High Risk</Typography>
                <Typography variant="h4" color="error">
                  {populationOverview?.high_risk_patients || 0}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6">Excellent</Typography>
                <Typography variant="h4" color="success">
                  {populationOverview?.excellent_adherence_patients || 0}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Adherence Distribution</Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={Object.entries(populationOverview?.adherence_distribution || {}).map(([level, count]) => ({
                    level,
                    count
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="level" />
                    <YAxis />
                    <RechartsTooltip />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </Grid>
          </Grid>
        ) : null}
      </CardContent>
    </Card>
  );

  const renderPatientAnalysis = () => (
    <Card>
      <CardHeader title="Patient Analysis" />
      <CardContent>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Patient ID"
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(e.target.value)}
              placeholder="e.g., P0001"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              variant="contained"
              onClick={handlePatientAnalysis}
              disabled={!selectedPatient}
              fullWidth
            >
              Analyze Patient
            </Button>
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              variant="outlined"
              onClick={() => generateNudge(selectedPatient)}
              disabled={!selectedPatient || !adherenceScore}
              startIcon={<Send />}
              fullWidth
            >
              Generate Nudge
            </Button>
          </Grid>
        </Grid>

        {adherenceScore && (
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardHeader title="Adherence Score" />
                <CardContent>
                  <Box textAlign="center" mb={2}>
                    <Typography variant="h3" color={getAdherenceColor(adherenceScore.adherence_level)}>
                      {adherenceScore.overall_score}
                    </Typography>
                    <Chip
                      label={adherenceScore.adherence_level}
                      color={getAdherenceColor(adherenceScore.adherence_level)}
                      sx={{ mt: 1 }}
                    />
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6">Component Scores:</Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary="Vitals Compliance"
                        secondary={`${adherenceScore.component_scores.vitals_compliance}%`}
                      />
                      <LinearProgress
                        variant="determinate"
                        value={adherenceScore.component_scores.vitals_compliance}
                        sx={{ width: 100 }}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Appointment Attendance"
                        secondary={`${adherenceScore.component_scores.appointment_attendance}%`}
                      />
                      <LinearProgress
                        variant="determinate"
                        value={adherenceScore.component_scores.appointment_attendance}
                        sx={{ width: 100 }}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Medication Adherence"
                        secondary={`${adherenceScore.component_scores.medication_adherence}%`}
                      />
                      <LinearProgress
                        variant="determinate"
                        value={adherenceScore.component_scores.medication_adherence}
                        sx={{ width: 100 }}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardHeader title="Insights & Recommendations" />
                <CardContent>
                  {insights ? (
                    <>
                      <Typography variant="h6" gutterBottom>Key Insights:</Typography>
                      <List dense>
                        {insights.insights.map((insight, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              {insight.includes('excellent') ? <ThumbUp color="success" /> :
                               insight.includes('requires') ? <Warning color="warning" /> :
                               <TrendingUp />}
                            </ListItemIcon>
                            <ListItemText primary={insight} />
                          </ListItem>
                        ))}
                      </List>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="h6" gutterBottom>Recommended Actions:</Typography>
                      <List dense>
                        {insights.recommended_actions.map((action, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              <Schedule />
                            </ListItemIcon>
                            <ListItemText primary={action} />
                          </ListItem>
                        ))}
                      </List>
                    </>
                  ) : (
                    <Alert severity="info">Select a patient and click "Analyze Patient" to see insights</Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </CardContent>
    </Card>
  );

  const renderNudgeDialog = () => (
    <Dialog open={nudgeDialogOpen} onClose={() => setNudgeDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Message sx={{ mr: 1, verticalAlign: 'middle' }} />
        Personalized Patient Nudge
      </DialogTitle>
      <DialogContent>
        {nudge && (
          <Box>
            <Typography variant="h6" gutterBottom>Message:</Typography>
            <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
              <Typography>{nudge.personalized_message}</Typography>
            </Paper>
            
            <Typography variant="h6" gutterBottom>Delivery Channels:</Typography>
            <Box sx={{ mb: 2 }}>
              {nudge.delivery_channels.map((channel, index) => (
                <Chip key={index} label={channel} sx={{ mr: 1, mb: 1 }} />
              ))}
            </Box>
            
            <Typography variant="h6" gutterBottom>Optimal Timing:</Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              {nudge.optimal_timing?.preferred_time} on {nudge.optimal_timing?.best_days?.join(', ')}
            </Typography>
            
            <Typography variant="h6" gutterBottom>Recommendations:</Typography>
            <List dense>
              {nudge.recommendations.map((rec, index) => (
                <ListItem key={index}>
                  <ListItemText primary={rec} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setNudgeDialogOpen(false)}>Close</Button>
        <Button variant="contained" startIcon={<Send />}>
          Send Nudge
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <NotificationsActive sx={{ mr: 2, verticalAlign: 'middle' }} />
        Adherence Nudging
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderPopulationOverview()}
        </Grid>
        <Grid item xs={12}>
          {renderPatientAnalysis()}
        </Grid>
      </Grid>

      {renderNudgeDialog()}
    </Box>
  );
};

export default AdherenceNudging;
