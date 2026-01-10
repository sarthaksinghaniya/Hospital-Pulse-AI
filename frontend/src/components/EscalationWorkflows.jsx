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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Badge,
  Tooltip
} from '@mui/material';
import {
  NotificationsActive,
  Warning,
  CheckCircle,
  Schedule,
  Person,
  LocalHospital,
  PriorityHigh,
  Refresh,
  Visibility,
  Done,
  Close,
  Timeline,
  Assessment,
  Report
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const EscalationWorkflows = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [activeEscalations, setActiveEscalations] = useState([]);
  const [selectedEscalation, setSelectedEscalation] = useState(null);
  const [escalationDetails, setEscalationDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [acknowledgeDialogOpen, setAcknowledgeDialogOpen] = useState(false);
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false);
  const [acknowledgmentNotes, setAcknowledgmentNotes] = useState('');
  const [resolutionNotes, setResolutionNotes] = useState('');

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/escalation/dashboard`);
      setDashboardData(response.data.data);
      setActiveEscalations(response.data.data.active_escalations || []);
    } catch (err) {
      setError('Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeEscalation = async (escalationId) => {
    try {
      await axios.post(`${API_BASE}/escalation/acknowledge`, {
        escalation_id: escalationId,
        acknowledged_by: 'Clinical Staff',
        notes: acknowledgmentNotes
      });
      setAcknowledgeDialogOpen(false);
      setAcknowledgmentNotes('');
      fetchDashboardData();
    } catch (err) {
      setError('Failed to acknowledge escalation');
    }
  };

  const resolveEscalation = async (escalationId) => {
    try {
      await axios.post(`${API_BASE}/escalation/resolve`, {
        escalation_id: escalationId,
        resolved_by: 'Clinical Staff',
        resolution_notes: resolutionNotes,
        follow_up_required: false
      });
      setResolveDialogOpen(false);
      setResolutionNotes('');
      fetchDashboardData();
    } catch (err) {
      setError('Failed to resolve escalation');
    }
  };

  const fetchEscalationDetails = async (escalationId) => {
    try {
      const response = await axios.get(`${API_BASE}/escalation/${escalationId}`);
      setEscalationDetails(response.data.data);
    } catch (err) {
      setError('Failed to fetch escalation details');
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'immediate': return 'error';
      case 'urgent': return 'warning';
      case 'routine': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'error';
      case 'acknowledged': return 'warning';
      case 'in_progress': return 'info';
      case 'resolved': return 'success';
      default: return 'default';
    }
  };

  const getLevelIcon = (level) => {
    switch (level) {
      case 'emergency': return <PriorityHigh color="error" />;
      case 'physician': return <LocalHospital color="warning" />;
      case 'specialist': return <Assessment color="info" />;
      case 'nurse': return <Person color="success" />;
      default: return <Schedule />;
    }
  };

  const renderDashboardSummary = () => {
    if (!dashboardData) return null;

    const { summary } = dashboardData;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6">Active</Typography>
            <Typography variant="h4" color="primary">
              {summary.total_active}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6">Pending</Typography>
            <Typography variant="h4" color="error">
              {summary.by_status?.pending || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6">Acknowledged</Typography>
            <Typography variant="h4" color="warning">
              {summary.by_status?.acknowledged || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6">In Progress</Typography>
            <Typography variant="h4" color="info">
              {summary.by_status?.in_progress || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6">Overdue</Typography>
            <Typography variant="h4" color="error">
              {summary.overdue_count}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6">7-Day Avg</Typography>
            <Typography variant="h4">
              {summary.escalation_trends?.average_per_day?.toFixed(1) || 0}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    );
  };

  const renderActiveEscalations = () => (
    <Card>
      <CardHeader
        title="Active Escalations"
        action={
          <Button onClick={fetchDashboardData} startIcon={<Refresh />}>
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
                  <TableCell>Title</TableCell>
                  <TableCell>Level</TableCell>
                  <TableCell>Urgency</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {activeEscalations.map((escalation) => (
                  <TableRow key={escalation.escalation_id}>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Person sx={{ mr: 1 }} />
                        {escalation.patient_id}
                      </Box>
                    </TableCell>
                    <TableCell>{escalation.title}</TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        {getLevelIcon(escalation.escalation_level)}
                        <Typography variant="body2" sx={{ ml: 1 }}>
                          {escalation.escalation_level}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={escalation.urgency}
                        color={getUrgencyColor(escalation.urgency)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={escalation.status}
                        color={getStatusColor(escalation.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(escalation.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedEscalation(escalation);
                              fetchEscalationDetails(escalation.escalation_id);
                            }}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        {escalation.status === 'pending' && (
                          <Tooltip title="Acknowledge">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedEscalation(escalation);
                                setAcknowledgeDialogOpen(true);
                              }}
                            >
                              <CheckCircle />
                            </IconButton>
                          </Tooltip>
                        )}
                        {escalation.status !== 'resolved' && (
                          <Tooltip title="Resolve">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedEscalation(escalation);
                                setResolveDialogOpen(true);
                              }}
                            >
                              <Done />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
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

  const renderEscalationTrends = () => {
    if (!dashboardData?.escalation_trends) return null;

    const data = Object.entries(dashboardData.escalation_trends.daily_counts || {})
      .map(([date, count]) => ({
        date: new Date(date).toLocaleDateString(),
        count
      }))
      .slice(-7); // Last 7 days

    return (
      <Card>
        <CardHeader title="Escalation Trends (Last 7 Days)" />
        <CardContent>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <RechartsTooltip />
                <Line type="monotone" dataKey="count" stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </CardContent>
      </Card>
    );
  };

  const renderEscalationDetails = () => {
    if (!escalationDetails) return null;

    return (
      <Dialog open={!!selectedEscalation} onClose={() => setSelectedEscalation(null)} maxWidth="md" fullWidth>
        <DialogTitle>
          <NotificationsActive sx={{ mr: 1, verticalAlign: 'middle' }} />
          Escalation Details
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6">Basic Information</Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="Escalation ID" secondary={escalationDetails.escalation_id} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Patient ID" secondary={escalationDetails.patient_id} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Title" secondary={escalationDetails.title} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Level" secondary={escalationDetails.escalation_level} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Urgency" secondary={escalationDetails.urgency} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Status" secondary={escalationDetails.status} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Created" secondary={new Date(escalationDetails.created_at).toLocaleString()} />
                </ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6">Message & Actions</Typography>
              <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
                <Typography>{escalationDetails.message}</Typography>
              </Paper>
              <Typography variant="subtitle2">Recommended Action:</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {escalationDetails.recommended_action}
              </Typography>
              <Typography variant="subtitle2">Reason:</Typography>
              <Typography variant="body2">
                {escalationDetails.reason}
              </Typography>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedEscalation(null)}>Close</Button>
          {escalationDetails.status === 'pending' && (
            <Button
              variant="contained"
              onClick={() => {
                setAcknowledgeDialogOpen(true);
                setSelectedEscalation(escalationDetails);
              }}
            >
              Acknowledge
            </Button>
          )}
          {escalationDetails.status !== 'resolved' && (
            <Button
              variant="contained"
              color="success"
              onClick={() => {
                setResolveDialogOpen(true);
                setSelectedEscalation(escalationDetails);
              }}
            >
              Resolve
            </Button>
          )}
        </DialogActions>
      </Dialog>
    );
  };

  const renderAcknowledgeDialog = () => (
    <Dialog open={acknowledgeDialogOpen} onClose={() => setAcknowledgeDialogOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Acknowledge Escalation</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Acknowledgment Notes"
          multiline
          rows={4}
          value={acknowledgmentNotes}
          onChange={(e) => setAcknowledgmentNotes(e.target.value)}
          placeholder="Enter any notes about this acknowledgment..."
          sx={{ mt: 2 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setAcknowledgeDialogOpen(false)}>Cancel</Button>
        <Button
          variant="contained"
          onClick={() => acknowledgeEscalation(selectedEscalation?.escalation_id)}
        >
          Acknowledge
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderResolveDialog = () => (
    <Dialog open={resolveDialogOpen} onClose={() => setResolveDialogOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Resolve Escalation</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Resolution Notes"
          multiline
          rows={4}
          value={resolutionNotes}
          onChange={(e) => setResolutionNotes(e.target.value)}
          placeholder="Describe how this escalation was resolved..."
          sx={{ mt: 2 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setResolveDialogOpen(false)}>Cancel</Button>
        <Button
          variant="contained"
          color="success"
          onClick={() => resolveEscalation(selectedEscalation?.escalation_id)}
        >
          Resolve
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <NotificationsActive sx={{ mr: 2, verticalAlign: 'middle' }} />
        Human Escalation Workflows
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderDashboardSummary()}
        </Grid>
        <Grid item xs={12} md={8}>
          {renderActiveEscalations()}
        </Grid>
        <Grid item xs={12} md={4}>
          {renderEscalationTrends()}
        </Grid>
      </Grid>

      {renderEscalationDetails()}
      {renderAcknowledgeDialog()}
      {renderResolveDialog()}
    </Box>
  );
};

export default EscalationWorkflows;
