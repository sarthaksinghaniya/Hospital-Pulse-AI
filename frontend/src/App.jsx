import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Tabs,
  Tab,
  Paper
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  MonitorHeart as VitalsIcon,
  NotificationsActive as AdherenceIcon,
  Analytics as NoShowIcon,
  Assessment as RiskIcon,
  Warning as EscalationIcon
} from '@mui/icons-material';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

// Import all components
import VitalsMonitoring from './components/VitalsMonitoring';
import AdherenceNudging from './components/AdherenceNudging';
import NoShowPrediction from './components/NoShowPrediction';
import DeteriorationRisk from './components/DeteriorationRisk';
import EscalationWorkflows from './components/EscalationWorkflows';
import OriginalDashboard from './OriginalDashboard';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 0 }}>{children}</Box>}
    </div>
  );
}

export default function App() {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const tabs = [
    { label: 'Dashboard', icon: <DashboardIcon />, component: <OriginalDashboard /> },
    { label: 'Vitals Monitoring', icon: <VitalsIcon />, component: <VitalsMonitoring /> },
    { label: 'Adherence Nudging', icon: <AdherenceIcon />, component: <AdherenceNudging /> },
    { label: 'No-Show Prediction', icon: <NoShowIcon />, component: <NoShowPrediction /> },
    { label: 'Risk Assessment', icon: <RiskIcon />, component: <DeteriorationRisk /> },
    { label: 'Escalations', icon: <EscalationIcon />, component: <EscalationWorkflows /> }
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ backgroundColor: '#0b5aa2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Hospital Pulse AI - Extended Patient Monitoring System
          </Typography>
        </Toolbar>
      </AppBar>

      <Paper sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={currentTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          aria-label="navigation tabs"
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              icon={tab.icon}
              label={tab.label}
              id={`tab-${index}`}
              aria-controls={`tabpanel-${index}`}
            />
          ))}
        </Tabs>
      </Paper>

      {tabs.map((tab, index) => (
        <TabPanel key={index} value={currentTab} index={index}>
          {tab.component}
        </TabPanel>
      ))}
    </Box>
  );
}
