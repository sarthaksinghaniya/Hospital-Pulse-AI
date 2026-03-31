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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Assessment,
  TrendingUp,
  TrendingDown,
  Person,
  Schedule,
  Warning,
  CheckCircle,
  BarChart,
  Refresh,
  Analytics
} from '@mui/icons-material';
import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const NoShowPrediction = () => {
  const [modelInsights, setModelInsights] = useState(null);
  const [featureImportance, setFeatureImportance] = useState(null);
  const [patientData, setPatientData] = useState({
    patient_id: '',
    Age: 50,
    Gender: 'F',
    waiting_days: 3,
    scheduled_hour: 10,
    scheduled_dayofweek: 0,
    appointment_dayofweek: 0,
    SMS_received: 1,
    Scholarship: 0,
    Hipertension: 0,
    Diabetes: 0,
    Alcoholism: 0,
    Handcap: 0
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchModelInsights = async () => {
    try {
      console.log('DEBUG: Fetching model insights...');
      const response = await axios.get(`${API_BASE}/noshow/model-insights`);
      console.log('DEBUG: Model insights response:', response.data);
      setModelInsights(response.data.data);
    } catch (err) {
      console.error('DEBUG: Failed to fetch model insights:', err);
      setError('Failed to fetch model insights');
    }
  };

  const fetchFeatureImportance = async () => {
    try {
      console.log('DEBUG: Fetching feature importance...');
      const response = await axios.get(`${API_BASE}/noshow/feature-importance`);
      console.log('DEBUG: Feature importance response:', response.data);
      setFeatureImportance(response.data.data);
    } catch (err) {
      console.error('DEBUG: Failed to fetch feature importance:', err);
      setError('Failed to fetch feature importance');
    }
  };

  const trainModel = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('DEBUG: Starting model training...');
      const response = await axios.post(`${API_BASE}/noshow/train`);
      console.log('DEBUG: Train model response:', response.data);
      
      if (response.data.status === 'success') {
        console.log('DEBUG: Model training successful, fetching insights...');
        // Wait a moment for the model to be fully saved
        await new Promise(resolve => setTimeout(resolve, 500));
        await fetchModelInsights();
        await fetchFeatureImportance();
      } else {
        console.error('DEBUG: Model training failed:', response.data);
        setError('Model training failed');
      }
    } catch (err) {
      console.error('DEBUG: Train model error:', err);
      setError('Failed to train model');
    } finally {
      setLoading(false);
    }
  };

  const predictNoShow = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE}/noshow/predict`, patientData);
      console.log('DEBUG: Prediction response:', response.data);
      
      // Ensure the response has the expected structure
      const predictionData = response.data.data;
      if (predictionData) {
        // Set prediction with new format
        setPrediction(predictionData);
      } else {
        setError('Invalid prediction response from server');
      }
    } catch (err) {
      console.error('DEBUG: Prediction error:', err);
      setError('Failed to predict no-show: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModelInsights();
    fetchFeatureImportance();
  }, []);

  const getRiskColor = (category) => {
    switch (category) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const renderModelOverview = () => (
    <Card>
      <CardHeader
        title="Model Overview"
        action={
          <Box>
            <Button onClick={trainModel} startIcon={<Refresh />} sx={{ mr: 1 }}>
              Train Model
            </Button>
            <Button onClick={fetchModelInsights} startIcon={<Assessment />}>
              Refresh Insights
            </Button>
          </Box>
        }
      />
      <CardContent>
        {loading ? (
          <LinearProgress />
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : modelInsights ? (
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6">Model Type</Typography>
                <Typography variant="body1">{modelInsights.model_type}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6">Total Features</Typography>
                <Typography variant="h4">{modelInsights.total_features}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6">Status</Typography>
                <Chip
                  label={modelInsights.model_trained ? 'Trained' : 'Not Trained'}
                  color={modelInsights.model_trained ? 'success' : 'warning'}
                />
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6">Last Trained</Typography>
                <Typography variant="body2">
                  {modelInsights.last_trained ? new Date(modelInsights.last_trained).toLocaleDateString() : 'Never'}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        ) : (
          <Alert severity="info">Click "Train Model" to initialize the prediction model</Alert>
        )}
      </CardContent>
    </Card>
  );

  const renderFeatureImportance = () => {
    console.log('DEBUG: Rendering feature importance chart...');
    console.log('DEBUG: modelInsights state:', modelInsights);
    
    if (!modelInsights || !modelInsights.feature_importance) {
      console.log('DEBUG: No feature importance data available');
      return (
        <Card>
          <CardHeader title="Feature Importance" />
          <CardContent>
            <Alert severity="info">
              No feature importance data available. Please train the model first.
            </Alert>
          </CardContent>
        </Card>
      );
    }

    const data = Object.entries(modelInsights.feature_importance || {})
      .map(([feature, importance]) => ({
        feature: feature
          .replace(/_/g, ' ')
          .replace(/encoded/g, '')
          .replace(/([A-Z])/g, ' $1')
          .trim()
          .toUpperCase(),
        importance: parseFloat(importance)  // Already in percentage format
      }))
      .filter(item => item.importance > 0.01)  // Filter out very small values
      .sort((a, b) => b.importance - a.importance);  // Sort by importance descending

    console.log('DEBUG: Formatted chart data:', data);
    
    if (data.length === 0 || data.every(item => item.importance === 0)) {
      console.log('DEBUG: All importance values are zero or empty');
      return (
        <Card>
          <CardHeader title="Feature Importance" />
          <CardContent>
            <Alert severity="warning">
              Feature importance values are all zero. Please retrain the model.
            </Alert>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card>
        <CardHeader title="Feature Importance" />
        <CardContent>
          <Box sx={{ height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RechartsBarChart data={data} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 'dataMax']} />
                <YAxis dataKey="feature" type="category" width={120} />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Importance']}
                  labelFormatter={(label) => `Feature: ${label}`}
                />
                <Bar dataKey="importance" fill="#8884d8" />
              </RechartsBarChart>
            </ResponsiveContainer>
          </Box>
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Showing top {data.length} features by importance
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  };

  const renderPredictionForm = () => (
    <Card>
      <CardHeader title="Patient No-Show Prediction" />
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
              value={patientData.Age}
              onChange={(e) => setPatientData({...patientData, Age: parseInt(e.target.value)})}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Gender</InputLabel>
              <Select
                value={patientData.Gender}
                onChange={(e) => setPatientData({...patientData, Gender: e.target.value})}
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
            <TextField
              fullWidth
              label="Scheduled Hour"
              type="number"
              value={patientData.scheduled_hour}
              onChange={(e) => setPatientData({...patientData, scheduled_hour: parseInt(e.target.value)})}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>SMS Received</InputLabel>
              <Select
                value={patientData.SMS_received}
                onChange={(e) => setPatientData({...patientData, SMS_received: parseInt(e.target.value)})}
              >
                <MenuItem value={0}>No</MenuItem>
                <MenuItem value={1}>Yes</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Scholarship</InputLabel>
              <Select
                value={patientData.Scholarship}
                onChange={(e) => setPatientData({...patientData, Scholarship: parseInt(e.target.value)})}
              >
                <MenuItem value={0}>No</MenuItem>
                <MenuItem value={1}>Yes</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Hypertension</InputLabel>
              <Select
                value={patientData.Hipertension}
                onChange={(e) => setPatientData({...patientData, Hipertension: parseInt(e.target.value)})}
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
                value={patientData.Diabetes}
                onChange={(e) => setPatientData({...patientData, Diabetes: parseInt(e.target.value)})}
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
                value={patientData.Alcoholism}
                onChange={(e) => setPatientData({...patientData, Alcoholism: parseInt(e.target.value)})}
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
                value={patientData.Handcap}
                onChange={(e) => setPatientData({...patientData, Handcap: parseInt(e.target.value)})}
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
              onClick={predictNoShow}
              disabled={loading || !patientData.patient_id}
              startIcon={<Analytics />}
              fullWidth
            >
              Predict No-Show Probability
            </Button>
          </Grid>
        </Grid>

        {prediction && (
          <Box sx={{ mt: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6">No-Show Probability</Typography>
                  <Typography variant="h3" color={getRiskColor(prediction.risk_category || 'low')}>
                    {prediction.probability ? `${prediction.probability}%` : '0%'}
                  </Typography>
                  <Chip
                    label={prediction.risk_level || prediction.risk_category || 'Unknown'}
                    color={getRiskColor(prediction.risk_level || prediction.risk_category || 'low')}
                    sx={{ mt: 1 }}
                  />
                </Paper>
              </Grid>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Contributing Factors</Typography>
                  <List dense>
                    {prediction.contributing_factors && prediction.contributing_factors.length > 0 ? (
                      prediction.contributing_factors.map((factor, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={factor.factor}
                            secondary={`Importance: ${factor.importance}%`}
                          />
                        </ListItem>
                      ))
                    ) : (
                      <ListItem>
                        <ListItemText primary="No contributing factors available" />
                      </ListItem>
                    )}
                  </List>
                </Paper>
              </Grid>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Recommendations</Typography>
                  <List dense>
                    {prediction.recommendations && prediction.recommendations.length > 0 ? (
                      prediction.recommendations.map((rec, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <Schedule />
                          </ListItemIcon>
                          <ListItemText primary={rec} />
                        </ListItem>
                      ))
                    ) : (
                      <ListItem>
                        <ListItemText primary="No recommendations available" />
                      </ListItem>
                    )}
                  </List>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <Analytics sx={{ mr: 2, verticalAlign: 'middle' }} />
        No-Show Prediction
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderModelOverview()}
        </Grid>
        <Grid item xs={12} md={6}>
          {renderFeatureImportance()}
        </Grid>
        <Grid item xs={12} md={6}>
          {renderPredictionForm()}
        </Grid>
      </Grid>
    </Box>
  );
};

export default NoShowPrediction;
