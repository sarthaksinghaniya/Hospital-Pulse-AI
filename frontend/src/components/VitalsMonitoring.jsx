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
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  MonitorHeart,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Refresh,
  Person,
  Timeline
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

const VitalsMonitoring = () => {
  const [overview, setOverview] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientSummary, setPatientSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchOverview = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE}/vitals/overview`);
      console.log('Vitals overview response:', response.data);
      if (response.data && response.data.data) {
        setOverview(response.data.data);
      } else {
        setOverview([]);
        setError('No patient data available');
      }
    } catch (err) {
      console.error('Error fetching vitals overview:', err);
      setError('Failed to fetch vitals overview');
      setOverview([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchPatientSummary = async (patientId) => {
    try {
      const response = await axios.post(`${API_BASE}/vitals/patient-summary`, {
        patient_id: patientId
      });
      setPatientSummary(response.data.data);
    } catch (err) {
      setError('Failed to fetch patient summary');
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const getStabilityColor = (level) => {
    switch (level) {
      case 'Stable': return 'success';
      case 'Moderately Stable': return 'info';
      case 'Unstable': return 'warning';
      case 'Critically Unstable': return 'error';
      default: return 'default';
    }
  };

  const renderOverviewCard = () => (
    <Card>
      <CardHeader
        title="Patient Vitals Overview"
        action={
          <Button onClick={fetchOverview} startIcon={<Refresh />}>
            Refresh
          </Button>
        }
      />
      <CardContent>
        {loading ? (
          <LinearProgress />
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Patient ID</TableCell>
                  <TableCell>Stability Score</TableCell>
                  <TableCell>Stability Level</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {overview && Array.isArray(overview) && overview.map((patient) => (
                  <TableRow key={patient.patient_id}>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Person sx={{ mr: 1 }} />
                        {patient.patient_id}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Typography variant="body2" sx={{ mr: 1 }}>
                          {patient.stability_score}
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={patient.stability_score}
                          sx={{ width: 100 }}
                          color={getStabilityColor(patient.stability_level)}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={patient.stability_level}
                        color={getStabilityColor(patient.stability_level)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: patient.color_indicator === 'green' ? '#4caf50' :
                                          patient.color_indicator === 'yellow' ? '#ff9800' :
                                          patient.color_indicator === 'orange' ? '#ff5722' : '#f44336'
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        onClick={() => {
                          setSelectedPatient(patient.patient_id);
                          fetchPatientSummary(patient.patient_id);
                        }}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );

  const renderPatientDetails = () => {
    if (!patientSummary) return null;

    const { trend_analysis, missing_readings, stability_indicators } = patientSummary;

    return (
      <Grid container spacing={3}>
        {/* Stability Indicators */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Stability Indicators" />
            <CardContent>
              <Box textAlign="center" mb={2}>
                <Typography variant="h4" color={getStabilityColor(stability_indicators.stability_level)}>
                  {stability_indicators.stability_score}
                </Typography>
                <Chip
                  label={stability_indicators.stability_level}
                  color={getStabilityColor(stability_indicators.stability_level)}
                  sx={{ mt: 1 }}
                />
              </Box>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6">Recommendations:</Typography>
              <List dense>
                {stability_indicators.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Trend Analysis */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Trend Analysis" />
            <CardContent>
              {trend_analysis.abnormalities && Object.keys(trend_analysis.abnormalities).length > 0 ? (
                <List>
                  {Object.entries(trend_analysis.abnormalities).map(([vital, data]) => (
                    <ListItem key={vital}>
                      <ListItemText
                        primary={vital.replace(/_/g, ' ').toUpperCase()}
                        secondary={`${data.latest_value?.toFixed(1)} (Normal: ${data.normal_range?.[0]}-${data.normal_range?.[1]})`}
                      />
                      <Chip
                        label="Abnormal"
                        color="error"
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Alert severity="success">No abnormalities detected</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Missing Readings */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Data Coverage" />
            <CardContent>
              <Box mb={2}>
                <Typography variant="body2" gutterBottom>
                  Coverage: {missing_readings.coverage_percentage?.toFixed(1)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={missing_readings.coverage_percentage || 0}
                  color={missing_readings.is_concerning ? 'error' : 'success'}
                />
              </Box>
              <Typography variant="body2">
                Expected: {missing_readings.expected_readings} readings
              </Typography>
              <Typography variant="body2">
                Actual: {missing_readings.actual_readings} readings
              </Typography>
              {missing_readings.is_concerning && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Low data coverage detected
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <MonitorHeart sx={{ mr: 2, verticalAlign: 'middle' }} />
        Remote Vitals Monitoring
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderOverviewCard()}
        </Grid>

        {selectedPatient && (
          <Grid item xs={12}>
            <Card>
              <CardHeader
                title={`Patient Details: ${selectedPatient}`}
                action={
                  <Button onClick={() => setSelectedPatient(null)}>
                    Close
                  </Button>
                }
              />
              <CardContent>
                {renderPatientDetails()}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default VitalsMonitoring;
