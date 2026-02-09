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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Assessment,
  Warning,
  TrendingUp,
  TrendingDown,
  Person,
  MonitorHeart,
  Schedule,
  ExpandMore,
  LocalHospital,
  HealthAndSafety,
  PriorityHigh
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const DeteriorationRisk = () => {
  const [patientData, setPatientData] = useState({
    patient_id: '',
    age: 50,
    gender: 'F',
    chronic_conditions: {},
    waiting_days: 3,
    sms_received: 1,
    scholarship: 0,
    hypertension: 0,
    diabetes: 0,
    alcoholism: 0,
    handcap: 0
  });
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const assessRisk = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/risk/assess`, patientData);
      setRiskAssessment(response.data.data);
    } catch (err) {
      setError('Failed to assess risk');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (category) => {
    switch (category) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  const getRiskIcon = (category) => {
    switch (category) {
      case 'High': return <PriorityHigh color="error" />;
      case 'Medium': return <Warning color="warning" />;
      case 'Low': return <HealthAndSafety color="success" />;
      default: return <Assessment />;
    }
  };

  const COLORS = ['#f44336', '#ff9800', '#4caf50'];

  const renderRiskAssessmentForm = () => (
    <Card>
      <CardHeader title="Patient Risk Assessment" />
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Patient ID"
              value={patientData.patient_id}
              onChange={(e) => setPatientData({...patientData, patient_id: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Age"
              type="number"
              value={patientData.age}
              onChange={(e) => setPatientData({...patientData, age: parseInt(e.target.value)})}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Gender</InputLabel>
              <Select
                value={patientData.gender}
                onChange={(e) => setPatientData({...patientData, gender: e.target.value})}
              >
                <MenuItem value="M">Male</MenuItem>
                <MenuItem value="F">Female</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Waiting Days"
              type="number"
              value={patientData.waiting_days}
              onChange={(e) => setPatientData({...patientData, waiting_days: parseInt(e.target.value)})}
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Hypertension</InputLabel>
              <Select
                value={patientData.hypertension}
                onChange={(e) => setPatientData({...patientData, hypertension: parseInt(e.target.value)})}
              >
                <MenuItem value={0}>No</MenuItem>
                <MenuItem value={1}>Yes</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Diabetes</InputLabel>
              <Select
                value={patientData.diabetes}
                onChange={(e) => setPatientData({...patientData, diabetes: parseInt(e.target.value)})}
              >
                <MenuItem value={0}>No</MenuItem>
                <MenuItem value={1}>Yes</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Alcoholism</InputLabel>
              <Select
                value={patientData.alcoholism}
                onChange={(e) => setPatientData({...patientData, alcoholism: parseInt(e.target.value)})}
              >
                <MenuItem value={0}>No</MenuItem>
                <MenuItem value={1}>Yes</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Handicap</InputLabel>
              <Select
                value={patientData.handcap}
                onChange={(e) => setPatientData({...patientData, handcap: parseInt(e.target.value)})}
              >
                <MenuItem value={0}>None</MenuItem>
                <MenuItem value={1}>Level 1</MenuItem>
                <MenuItem value={2}>Level 2</MenuItem>
                <MenuItem value={3}>Level 3</MenuItem>
                <MenuItem value={4}>Level 4</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <Button
              variant="contained"
              onClick={assessRisk}
              disabled={loading || !patientData.patient_id}
              startIcon={<Assessment />}
              fullWidth
            >
              Assess Deterioration Risk
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderRiskResults = () => {
    if (!riskAssessment) return null;

    const { overall_risk_score, risk_category, color_indicator, component_risks, risk_drivers, recommendations } = riskAssessment;

    const pieData = [
      { name: 'Low Risk', value: 30, color: '#4caf50' },
      { name: 'Medium Risk', value: 40, color: '#ff9800' },
      { name: 'High Risk', value: overall_risk_score, color: '#f44336' }
    ];

    const componentData = Object.entries(component_risks).map(([key, value]) => ({
      name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      score: value.risk_score
    }));

    return (
      <Grid container spacing={3}>
        {/* Overall Risk Score */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Overall Risk Assessment" />
            <CardContent>
              <Box textAlign="center" mb={2}>
                {getRiskIcon(risk_category)}
                <Typography variant="h3" color={getRiskColor(risk_category)} sx={{ mt: 1 }}>
                  {overall_risk_score}
                </Typography>
                <Chip
                  label={risk_category}
                  color={getRiskColor(risk_category)}
                  sx={{ mt: 1 }}
                />
              </Box>
              <Box sx={{ height: 200 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Component Risk Breakdown */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Risk Component Breakdown" />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={componentData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="score" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Drivers */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Primary Risk Drivers" />
            <CardContent>
              <List>
                {risk_drivers.slice(0, 5).map((driver, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {driver.category === 'Vitals Stability' ? <MonitorHeart /> :
                       driver.category === 'Chronic Conditions' ? <LocalHospital /> :
                       driver.category === 'Adherence' ? <Schedule /> :
                       <Warning />}
                    </ListItemIcon>
                    <ListItemText
                      primary={driver.category}
                      secondary={`${driver.contribution.toFixed(1)} points`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Detailed Component Analysis */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Detailed Component Analysis" />
            <CardContent>
              {Object.entries(component_risks).map(([component, data]) => (
                <Accordion key={component}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">
                      {component.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} - {data.risk_score.toFixed(1)} points
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom>Details:</Typography>
                        {component === 'vitals_stability' && (
                          <List dense>
                            <ListItem>
                              <ListItemText 
                                primary="Base Stability Risk" 
                                secondary={`${data.base_stability_risk?.toFixed(1)} points`} 
                              />
                            </ListItem>
                            <ListItem>
                              <ListItemText 
                                primary="Trend Risk" 
                                secondary={`${data.trend_risk?.toFixed(1)} points`} 
                              />
                            </ListItem>
                            <ListItem>
                              <ListItemText 
                                primary="Abnormality Risk" 
                                secondary={`${data.abnormality_risk?.toFixed(1)} points`} 
                              />
                            </ListItem>
                          </List>
                        )}
                        {component === 'chronic_conditions' && (
                          <List dense>
                            <ListItem>
                              <ListItemText 
                                primary="Condition Risk" 
                                secondary={`${data.condition_risk?.toFixed(1)} points`} 
                              />
                            </ListItem>
                            <ListItem>
                              <ListItemText 
                                primary="Age Risk" 
                                secondary={`${data.age_risk?.toFixed(1)} points`} 
                              />
                            </ListItem>
                            <ListItem>
                              <ListItemText 
                                primary="Age" 
                                secondary={`${data.age} years`} 
                              />
                            </ListItem>
                          </List>
                        )}
                        {component === 'adherence' && (
                          <List dense>
                            <ListItem>
                              <ListItemText 
                                primary="Adherence Score" 
                                secondary={`${data.adherence_score}%`} 
                              />
                            </ListItem>
                            <ListItem>
                              <ListItemText 
                                primary="Adherence Level" 
                                secondary={data.adherence_level} 
                              />
                            </ListItem>
                          </List>
                        )}
                        {component === 'no_show_prediction' && (
                          <List dense>
                            <ListItem>
                              <ListItemText 
                                primary="No-Show Probability" 
                                secondary={`${(data.no_show_probability * 100).toFixed(1)}%`} 
                              />
                            </ListItem>
                            <ListItem>
                              <ListItemText 
                                primary="Risk Category" 
                                secondary={data.risk_category} 
                              />
                            </ListItem>
                          </List>
                        )}
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom>Contributing Factors:</Typography>
                        <List dense>
                          {data.contributing_factors?.map((factor, index) => (
                            <ListItem key={index}>
                              <ListItemText primary={factor} />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Recommendations" />
            <CardContent>
              <List>
                {recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Schedule />
                    </ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <Assessment sx={{ mr: 2, verticalAlign: 'middle' }} />
        Patient Deterioration Risk Assessment
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderRiskAssessmentForm()}
        </Grid>
        {riskAssessment && (
          <Grid item xs={12}>
            {renderRiskResults()}
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default DeteriorationRisk;
