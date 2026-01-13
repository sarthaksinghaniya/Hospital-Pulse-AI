import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  IconButton,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  Tooltip,
  Collapse,
  Fade,
  Slide
} from '@mui/material';
import {
  Send,
  SmartToy,
  Notifications,
  HealthAndSafety,
  TrendingUp,
  Warning,
  CheckCircle,
  Error,
  Info,
  Settings,
  Refresh,
  Close,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE = 'http://localhost:8001';

const HopXChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [systemStatus, setSystemStatus] = useState({});
  const [activeFeatures, setActiveFeatures] = useState([]);
  const [alertsSummary, setAlertsSummary] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [expandedSection, setExpandedSection] = useState(null);
  const ws = useRef(null);
  const messagesEndRef = useRef(null);
  const reconnectTimeout = useRef(null);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    fetchInitialData();
    
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      ws.current = new WebSocket(`${API_BASE}/chatbot/ws`);
      
      ws.current.onopen = () => {
        setIsConnected(true);
        console.log('HopX Assistant connected');
      };
      
      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      ws.current.onclose = () => {
        setIsConnected(false);
        console.log('HopX Assistant disconnected');
        // Attempt to reconnect after 5 seconds
        reconnectTimeout.current = setTimeout(connectWebSocket, 5000);
      };
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setIsConnected(false);
    }
  };

  const handleWebSocketMessage = (data) => {
    if (data.type === 'welcome') {
      setSystemStatus(data.data.system_status);
      setActiveFeatures(data.data.active_features);
      addMessage({
        type: 'system',
        content: data.data.message,
        timestamp: new Date().toISOString(),
        isBot: true
      });
    } else if (data.type === 'update') {
      setMessages(prevMessages => [...data.data.messages, ...prevMessages].slice(0, 50));
      setSystemStatus(data.data.system_health);
      setAlertsSummary(data.data.alerts_summary);
    } else if (data.type === 'new_message') {
      addMessage({
        type: data.data.type,
        content: data.data.content,
        timestamp: data.data.timestamp,
        priority: data.data.priority,
        isBot: true
      });
    }
  };

  const fetchInitialData = async () => {
    try {
      const [feedResponse, statusResponse, featuresResponse] = await Promise.all([
        axios.get(`${API_BASE}/chatbot/feed?limit=20`),
        axios.get(`${API_BASE}/chatbot/status`),
        axios.get(`${API_BASE}/chatbot/features`)
      ]);
      
      setMessages(feedResponse.data.data.messages);
      setSystemStatus(statusResponse.data.data.system_health);
      setActiveFeatures(featuresResponse.data.data.active_features);
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
    }
  };

  const addMessage = (message) => {
    setMessages(prev => [message, ...prev].slice(0, 100));
    scrollToBottom();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
      isBot: false
    };
    
    addMessage(userMessage);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      // Handle commands
      if (inputMessage.startsWith('/')) {
        await handleCommand(inputMessage);
      } else {
        // Regular chat message
        await handleChatMessage(inputMessage);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage({
        type: 'error',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isBot: true
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommand = async (command) => {
    const commandMap = {
      '/status': () => axios.get(`${API_BASE}/chatbot/status`),
      '/features': () => axios.get(`${API_BASE}/chatbot/features`),
      '/alerts': () => axios.get(`${API_BASE}/chatbot/alerts`),
      '/help': () => axios.get(`${API_BASE}/chatbot/help`),
      '/insights': () => axios.get(`${API_BASE}/chatbot/insights`)
    };
    
    const commandFunction = commandMap[command];
    if (commandFunction) {
      const response = await commandFunction();
      addMessage({
        type: 'command_response',
        content: response.data.data,
        timestamp: new Date().toISOString(),
        isBot: true
      });
    } else {
      addMessage({
        type: 'error',
        content: 'Unknown command. Type /help for available commands.',
        timestamp: new Date().toISOString(),
        isBot: true
      });
    }
  };

  const handleChatMessage = async (message) => {
    // Simple chat response logic
    const responses = {
      'hello': 'Hello! I am HopX Assistant, your healthcare AI companion. How can I help you today?',
      'help': 'I can help you with system status, patient alerts, and feature information. Try typing /help for commands.',
      'status': 'You can check system status by typing /status command.',
      'alerts': 'For patient alerts, use the /alerts command.',
      'features': 'To see all active features, type /features command.'
    };
    
    const lowerMessage = message.toLowerCase();
    const response = responses[lowerMessage] || 
      'I understand you\'re asking about: "' + message + '". Try using commands like /status, /features, or /alerts for specific information.';
    
    addMessage({
      type: 'chat_response',
      content: response,
      timestamp: new Date().toISOString(),
      isBot: true
    });
  };

  const getMessageIcon = (type) => {
    const iconMap = {
      'system_info': <Info color="primary" />,
      'patient_alert': <Warning color="error" />,
      'feature_update': <Settings color="secondary" />,
      'operational_insight': <TrendingUp color="success" />,
      'error_alert': <Error color="error" />,
      'success_message': <CheckCircle color="success" />,
      'user': <Avatar sx={{ width: 24, height: 24 }}>U</Avatar>,
      'chat_response': <SmartToy color="primary" />,
      'command_response': <SmartToy color="secondary" />
    };
    return iconMap[type] || <SmartToy color="primary" />;
  };

  const getPriorityColor = (priority) => {
    const colorMap = {
      'low': 'default',
      'normal': 'primary',
      'high': 'warning',
      'critical': 'error'
    };
    return colorMap[priority] || 'default';
  };

  const formatMessageContent = (content) => {
    if (typeof content === 'string') {
      return content;
    } else if (typeof content === 'object') {
      return JSON.stringify(content, null, 2);
    }
    return String(content);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', p: 2 }}>
      {/* Header */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ py: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Badge color={isConnected ? 'success' : 'error'} variant="dot">
                <SmartToy sx={{ fontSize: 32, color: 'primary.main' }} />
              </Badge>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  HopX Assistant
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Hospital Pulse AI Chatbot
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={isConnected ? <CheckCircle /> : <Error />}
                label={isConnected ? 'Connected' : 'Disconnected'}
                color={isConnected ? 'success' : 'error'}
                size="small"
              />
              <IconButton onClick={() => setShowHelp(!showHelp)} size="small">
                <Info />
              </IconButton>
              <IconButton onClick={fetchInitialData} size="small">
                <Refresh />
              </IconButton>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* System Status Bar */}
      {systemStatus.overall_status && (
        <Alert 
          severity={systemStatus.overall_status === 'healthy' ? 'success' : 'warning'}
          sx={{ mb: 2 }}
        >
          <Typography variant="body2">
            System Status: {systemStatus.overall_status?.toUpperCase()} | 
            Active Features: {activeFeatures.length} | 
            Total Alerts: {alertsSummary.total_alerts || 0}
          </Typography>
        </Alert>
      )}

      {/* Help Panel */}
      <Collapse in={showHelp}>
        <Card sx={{ mb: 2, bgcolor: 'info.main', color: 'white' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Available Commands
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText primary="/status - Check system health" />
              </ListItem>
              <ListItem>
                <ListItemText primary="/features - View active features" />
              </ListItem>
              <ListItem>
                <ListItemText primary="/alerts - See patient alerts" />
              </ListItem>
              <ListItem>
                <ListItemText primary="/insights - Get operational insights" />
              </ListItem>
              <ListItem>
                <ListItemText primary="/help - Show this help message" />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Collapse>

      {/* Messages Area */}
      <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <CardContent sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          <List sx={{ width: '100%' }}>
            {messages.map((message, index) => (
              <Fade in={true} timeout={300} key={`${message.timestamp}-${index}`}>
                <ListItem
                  sx={{
                    flexDirection: message.isBot ? 'row' : 'row-reverse',
                    alignItems: 'flex-start',
                    mb: 1
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 'auto', mr: 1, ml: 1 }}>
                    {getMessageIcon(message.type)}
                  </ListItemIcon>
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      bgcolor: message.isBot ? 'grey.100' : 'primary.main',
                      color: message.isBot ? 'text.primary' : 'white',
                      borderRadius: 2
                    }}
                  >
                      {message.priority && (
                        <Chip
                          label={message.priority}
                          size="small"
                          color={getPriorityColor(message.priority)}
                          sx={{ mb: 1 }}
                        />
                      )}
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {formatMessageContent(message.content)}
                      </Typography>
                      <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                        {formatTimestamp(message.timestamp)}
                      </Typography>
                    </Paper>
                  </ListItem>
              </Fade>
            ))}
          </List>
          <div ref={messagesEndRef} />
        </CardContent>
      </Card>

      {/* Input Area */}
      <Card sx={{ mt: 2 }}>
        <CardContent sx={{ py: 2 }}>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type a message or command (e.g., /status)..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={!isConnected}
              size="small"
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!isConnected || !inputMessage.trim() || isLoading}
              startIcon={isLoading ? <CircularProgress size={16} /> : <Send />}
            >
              Send
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default HopXChatbot;
