"""
Hospital Pulse AI - Chatbot Feed Service

Real-time information feed for HopX Assistant providing:
- System status updates
- Feature availability
- Patient alerts
- Operational insights
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
from enum import Enum

class MessageType(Enum):
    SYSTEM_INFO = "system_info"
    PATIENT_ALERT = "patient_alert"
    FEATURE_UPDATE = "feature_update"
    OPERATIONAL_INSIGHT = "operational_insight"
    ERROR_ALERT = "error_alert"
    SUCCESS_MESSAGE = "success_message"

class ChatMessage:
    """Chat message structure for HopX Assistant feed."""
    
    def __init__(self, message_type: MessageType, content: Dict, priority: str = "normal"):
        self.id = str(uuid.uuid4())
        self.type = message_type.value
        self.content = content
        self.priority = priority  # low, normal, high, critical
        self.timestamp = datetime.now().isoformat()
        self.read = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "read": self.read
        }

class ChatbotFeedService:
    """Service for managing HopX Assistant chatbot feed."""
    
    def __init__(self):
        self.messages: List[ChatMessage] = []
        self.active_connections = []
        self.system_status = {
            "backend": "online",
            "database": "connected",
            "ml_models": "active",
            "api_endpoints": "operational"
        }
        self.feature_status = {
            "vitals_monitoring": True,
            "adherence_nudging": True,
            "no_show_prediction": True,
            "deterioration_risk": True,
            "escalation_workflows": True
        }
        
    def add_system_message(self, content: Dict, priority: str = "normal"):
        """Add system information message."""
        message = ChatMessage(MessageType.SYSTEM_INFO, content, priority)
        self.messages.append(message)
        return message
    
    def add_patient_alert(self, patient_id: str, alert_type: str, details: Dict):
        """Add patient alert message."""
        content = {
            "patient_id": patient_id,
            "alert_type": alert_type,
            "details": details,
            "action_required": self._get_action_required(alert_type)
        }
        message = ChatMessage(MessageType.PATIENT_ALERT, content, "high")
        self.messages.append(message)
        return message
    
    def add_feature_update(self, feature_name: str, status: str, details: Dict = None):
        """Add feature status update."""
        content = {
            "feature": feature_name,
            "status": status,
            "details": details or {},
            "description": self._get_feature_description(feature_name)
        }
        message = ChatMessage(MessageType.FEATURE_UPDATE, content, "normal")
        self.messages.append(message)
        return message
    
    def add_operational_insight(self, insight_type: str, data: Dict):
        """Add operational insight message."""
        content = {
            "insight_type": insight_type,
            "data": data,
            "recommendation": self._get_recommendation(insight_type, data)
        }
        message = ChatMessage(MessageType.OPERATIONAL_INSIGHT, content, "normal")
        self.messages.append(message)
        return message
    
    def add_error_alert(self, error_type: str, details: Dict, severity: str = "high"):
        """Add error alert message."""
        content = {
            "error_type": error_type,
            "details": details,
            "troubleshooting": self._get_troubleshooting_steps(error_type),
            "impact": self._get_error_impact(error_type)
        }
        message = ChatMessage(MessageType.ERROR_ALERT, content, severity)
        self.messages.append(message)
        return message
    
    def add_success_message(self, operation: str, details: Dict):
        """Add success message."""
        content = {
            "operation": operation,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        message = ChatMessage(MessageType.SUCCESS_MESSAGE, content, "low")
        self.messages.append(message)
        return message
    
    def get_recent_messages(self, limit: int = 50, message_type: str = None) -> List[Dict]:
        """Get recent messages with optional filtering."""
        filtered_messages = self.messages
        
        if message_type:
            filtered_messages = [msg for msg in filtered_messages if msg.type == message_type]
        
        # Sort by timestamp (most recent first)
        filtered_messages.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Return limited number
        recent_messages = filtered_messages[:limit]
        
        return [msg.to_dict() for msg in recent_messages]
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health status."""
        return {
            "overall_status": "healthy" if all(status == "online" or status == "connected" or status == "active" or status == "operational" for status in self.system_status.values()) else "degraded",
            "components": self.system_status,
            "features": self.feature_status,
            "uptime": self._calculate_uptime(),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_active_features(self) -> List[Dict]:
        """Get list of active features with descriptions."""
        features = []
        for feature, active in self.feature_status.items():
            if active:
                features.append({
                    "name": feature,
                    "status": "active",
                    "description": self._get_feature_description(feature),
                    "last_check": datetime.now().isoformat()
                })
        return features
    
    def get_patient_alerts_summary(self) -> Dict:
        """Get summary of recent patient alerts."""
        alert_messages = [msg for msg in self.messages if msg.type == MessageType.PATIENT_ALERT.value]
        recent_alerts = alert_messages[:10]  # Last 10 alerts
        
        return {
            "total_alerts": len(alert_messages),
            "recent_alerts": [msg.to_dict() for msg in recent_alerts],
            "alert_types": self._count_alert_types(alert_messages),
            "critical_alerts": len([msg for msg in recent_alerts if msg.priority == "critical"])
        }
    
    def _get_action_required(self, alert_type: str) -> str:
        """Get required action for alert type."""
        actions = {
            "critical_vitals": "Immediate clinical assessment required",
            "high_risk_score": "Physician review within 2 hours",
            "adherence_crisis": "Case manager intervention needed",
            "no_show_risk": "Patient outreach recommended",
            "rapid_deterioration": "Urgent evaluation required"
        }
        return actions.get(alert_type, "Review patient status")
    
    def _get_feature_description(self, feature_name: str) -> str:
        """Get feature description."""
        descriptions = {
            "vitals_monitoring": "Real-time patient vital signs monitoring and trend analysis",
            "adherence_nudging": "Personalized patient compliance and adherence interventions",
            "no_show_prediction": "AI-powered appointment attendance forecasting",
            "deterioration_risk": "Multi-factor patient risk assessment and early warning",
            "escalation_workflows": "Human-in-the-loop clinical intervention system"
        }
        return descriptions.get(feature_name, "Hospital Pulse AI feature")
    
    def _get_recommendation(self, insight_type: str, data: Dict) -> str:
        """Get recommendation for operational insight."""
        recommendations = {
            "high_alert_volume": "Consider additional staffing during peak hours",
            "system_performance": "Monitor server resources and optimize queries",
            "patient_flow": "Review appointment scheduling and resource allocation",
            "escalation_response": "Review escalation protocols and response times"
        }
        return recommendations.get(insight_type, "Review operational metrics")
    
    def _get_troubleshooting_steps(self, error_type: str) -> List[str]:
        """Get troubleshooting steps for error type."""
        steps = {
            "database_connection": ["Check database server status", "Verify connection strings", "Restart database service"],
            "api_timeout": ["Check network connectivity", "Verify API endpoints", "Review timeout configurations"],
            "model_prediction_error": ["Check input data format", "Verify model loading", "Review feature engineering"],
            "escalation_failure": ["Check notification settings", "Verify user permissions", "Review escalation rules"]
        }
        return steps.get(error_type, ["Check system logs", "Verify configuration", "Contact support"])
    
    def _get_error_impact(self, error_type: str) -> str:
        """Get impact description for error type."""
        impacts = {
            "database_connection": "Patient data access may be unavailable",
            "api_timeout": "Real-time updates may be delayed",
            "model_prediction_error": "AI predictions may be unavailable",
            "escalation_failure": "Critical alerts may not be delivered"
        }
        return impacts.get(error_type, "System functionality may be affected")
    
    def _count_alert_types(self, alert_messages: List[ChatMessage]) -> Dict:
        """Count different types of alerts."""
        alert_types = {}
        for msg in alert_messages:
            alert_type = msg.content.get("alert_type", "unknown")
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        return alert_types
    
    def _calculate_uptime(self) -> str:
        """Calculate system uptime (placeholder)."""
        return "99.9%"  # In production, calculate from actual start time

# Global chatbot feed service instance
chatbot_service = ChatbotFeedService()

# Initialize with welcome message
def initialize_chatbot_feed():
    """Initialize chatbot feed with welcome message."""
    welcome_content = {
        "message": "🏥 Welcome to Hospital Pulse AI - HopX Assistant Feed",
        "system_status": chatbot_service.get_system_health(),
        "active_features": chatbot_service.get_active_features(),
        "available_commands": [
            "/status - Check system status",
            "/features - View active features",
            "/alerts - See patient alerts",
            "/help - Get assistance"
        ]
    }
    chatbot_service.add_system_message(welcome_content, "normal")
    
    # Add feature status messages
    for feature, active in chatbot_service.feature_status.items():
        if active:
            chatbot_service.add_feature_update(feature, "active")

# Initialize the service
initialize_chatbot_feed()
