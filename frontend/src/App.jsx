import React, { useState } from 'react';
import { designSystem, navigationStructure } from './styles/designSystem';

// Import redesigned components
import VitalsMonitoringRedesigned from './components/VitalsMonitoring-Redesigned';
import NoShowPredictionRedesigned from './components/NoShowPrediction-Redesigned';

// Import original components for now (will be redesigned later)
import AdherenceNudging from './components/AdherenceNudging';
import DeteriorationRisk from './components/DeteriorationRisk';
import EscalationWorkflows from './components/EscalationWorkflows';
import OriginalDashboard from './components/OriginalDashboard';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export default function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleNavigation = (item) => {
    if (item.items) {
      return; // Don't navigate to parent items
    }
    setCurrentView(item.key);
  };

  const getCurrentComponent = () => {
    const componentMap = {
      'dashboard': <OriginalDashboard />,
      'noShow': <NoShowPredictionRedesigned />,
      'risk': <DeteriorationRisk />,
      'vitals': <VitalsMonitoringRedesigned />,
      'adherence': <AdherenceNudging />,
      'escalations': <EscalationWorkflows />
    };
    return componentMap[currentView] || <OriginalDashboard />;
  };

  const getCurrentTitle = () => {
    const titleMap = {
      'dashboard': 'Dashboard',
      'noShow': 'No-Show Prediction',
      'risk': 'Risk Assessment',
      'vitals': 'Vitals Monitoring',
      'adherence': 'Adherence Tracking',
      'escalations': 'Alerts & Escalations'
    };
    return titleMap[currentView] || 'Dashboard';
  };

  const getCurrentDescription = () => {
    const descriptionMap = {
      'dashboard': 'Hospital operations overview and key metrics',
      'noShow': 'Predict patient appointment attendance and identify risk factors',
      'risk': 'Assess patient deterioration risk with AI-powered insights',
      'vitals': 'Monitor patient vitals in real-time and detect abnormalities',
      'adherence': 'Track patient compliance with treatment and appointments',
      'escalations': 'Manage clinical alerts and escalation workflows'
    };
    return descriptionMap[currentView] || 'Hospital operations overview';
  };

  const getIcon = (iconName) => {
    const iconMap = {
      dashboard: '📊',
      analytics: '📈',
      assessment: '🔍',
      monitor_heart: '❤️',
      notifications_active: '🔔',
      local_hospital: '🏥',
      emergency: '🚨',
      people: '👥',
      warning: '⚠️'
    };
    return iconMap[iconName] || '📊';
  };

  const SidebarItem = ({ item, onClick, isActive }) => {
    const [expanded, setExpanded] = useState(false);
    
    if (item.items) {
      return (
        <Box>
          <Box
            onClick={() => setExpanded(!expanded)}
            sx={{
              p: 2,
              borderRadius: designSystem.borderRadius.lg,
              mb: 1,
              backgroundColor: isActive ? designSystem.colors.accent.primary + '15' : 'transparent',
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: designSystem.colors.accent.primary + '10'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <span style={{ fontSize: '20px', marginRight: '12px' }}>
                  {getIcon(item.icon)}
                </span>
                <span style={{ 
                  fontSize: '16px', 
                  fontWeight: 600,
                  color: designSystem.colors.text.primary 
                }}>
                  {item.title}
                </span>
              </Box>
              <span style={{ fontSize: '12px', color: designSystem.colors.text.secondary }}>
                {expanded ? '▼' : '▶'}
              </span>
            </Box>
            {expanded && (
              <span style={{ 
                fontSize: '12px', 
                color: designSystem.colors.text.secondary,
                display: 'block',
                marginTop: '4px'
              }}>
                {item.description}
              </span>
            )}
          </Box>
          {expanded && (
            <Box sx={{ pl: 3, mt: 1 }}>
              {Object.entries(item.items).map(([key, subItem]) => (
                <Box
                  key={key}
                  onClick={() => onClick(subItem)}
                  sx={{
                    p: 1.5,
                    borderRadius: designSystem.borderRadius.md,
                    mb: 0.5,
                    backgroundColor: isActive ? designSystem.colors.accent.primary + '10' : 'transparent',
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: designSystem.colors.accent.primary + '08'
                    }
                  }}
                >
                  <span style={{ fontSize: '16px', marginRight: '8px' }}>
                    {getIcon(subItem.icon)}
                  </span>
                  <span style={{ 
                    fontSize: '14px', 
                    fontWeight: 500,
                    color: designSystem.colors.text.primary 
                  }}>
                    {subItem.title}
                  </span>
                </Box>
              ))}
            </Box>
          )}
        </Box>
      );
    }
    
    return (
      <Box
        onClick={() => onClick(item)}
        sx={{
          p: 2,
          borderRadius: designSystem.borderRadius.lg,
          mb: 1,
          backgroundColor: isActive ? designSystem.colors.accent.primary + '15' : 'transparent',
          cursor: 'pointer',
          '&:hover': {
            backgroundColor: designSystem.colors.accent.primary + '10'
          }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ fontSize: '20px', marginRight: '12px' }}>
            {getIcon(item.icon)}
          </span>
          <span style={{ 
            fontSize: '16px', 
            fontWeight: 600,
            color: designSystem.colors.text.primary 
          }}>
            {item.title}
          </span>
        </Box>
      </Box>
    );
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      minHeight: '100vh',
      backgroundColor: designSystem.colors.background
    }}>
      {/* Sidebar */}
      <Box
        sx={{
          width: sidebarOpen ? 320 : 80,
          minHeight: '100vh',
          backgroundColor: designSystem.colors.card,
          borderRight: `1px solid ${designSystem.colors.border}`,
          boxShadow: designSystem.shadows.soft,
          transition: 'width 0.3s ease',
          overflow: 'hidden'
        }}
      >
        <Box sx={{ p: designSystem.spacing.lg }}>
          {/* Header */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            mb: designSystem.spacing.xl 
          }}>
            <span style={{ 
              fontSize: sidebarOpen ? '18px' : '14px',
              fontWeight: 700,
              color: designSystem.colors.accent.primary 
            }}>
              {sidebarOpen ? '🏥 HopX' : '🏥'}
            </span>
            <span
              onClick={() => setSidebarOpen(!sidebarOpen)}
              style={{ 
                cursor: 'pointer',
                fontSize: '16px',
                color: designSystem.colors.text.secondary 
              }}
            >
              {sidebarOpen ? '◀' : '▶'}
            </span>
          </Box>

          {/* Navigation */}
          {sidebarOpen && (
            <Box>
              <SidebarItem 
                item={navigationStructure.dashboard}
                onClick={handleNavigation}
                isActive={currentView === 'dashboard'}
              />
              <SidebarItem 
                item={navigationStructure.patientIntelligence}
                onClick={handleNavigation}
                isActive={['noShow', 'risk'].includes(currentView)}
              />
              <SidebarItem 
                item={navigationStructure.monitoring}
                onClick={handleNavigation}
                isActive={['vitals', 'adherence'].includes(currentView)}
              />
              <SidebarItem 
                item={navigationStructure.operations}
                onClick={handleNavigation}
                isActive={['icu', 'emergency', 'staff'].includes(currentView)}
              />
              <SidebarItem 
                item={navigationStructure.alerts}
                onClick={() => setCurrentView('escalations')}
                isActive={currentView === 'escalations'}
              />
            </Box>
          )}
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ 
        flexGrow: 1, 
        display: 'flex', 
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Top Bar */}
        <Box
          sx={{
            p: designSystem.spacing.lg,
            backgroundColor: designSystem.colors.card,
            borderBottom: `1px solid ${designSystem.colors.border}`,
            boxShadow: designSystem.shadows.soft
          }}
        >
          <Box>
            <span style={{ 
              fontSize: '24px',
              fontWeight: 700,
              color: designSystem.colors.text.primary,
              display: 'block',
              marginBottom: '8px'
            }}>
              {getCurrentTitle()}
            </span>
            <span style={{ 
              fontSize: '16px',
              color: designSystem.colors.text.secondary,
              display: 'block'
            }}>
              {getCurrentDescription()}
            </span>
          </Box>
        </Box>

        {/* Content Area */}
        <Box sx={{ 
          flexGrow: 1, 
          overflow: 'auto',
          backgroundColor: designSystem.colors.background
        }}>
          {getCurrentComponent()}
        </Box>
      </Box>
    </Box>
  );
}
