"""
Hospital Pulse AI - Chatbot Feed API Routes

Real-time chatbot feed for HopX Assistant providing:
- System status updates
- Patient alerts
- Feature information
- Operational insights
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict, Optional
import json
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
from pathlib import Path
env_path = Path(__file__).parents[2] / "env" / ".env"
load_dotenv(env_path)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

print(f"DEBUG: OpenAI API Key loaded: {'Yes' if OPENAI_API_KEY else 'No'}")
print(f"DEBUG: OpenAI Model: {OPENAI_MODEL}")

from backend.services.chatbot_feed import chatbot_service, ChatMessage, MessageType

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection."""
        try:
            await websocket.send_text(message)
        except:
            # Connection might be closed
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all active connections."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

async def get_openai_response(message: str) -> str:
    """Get response from OpenAI API."""
    if not openai_client:
        return "I'm HopX Assistant, your healthcare AI companion. I can help you with system status, patient alerts, and feature information. The OpenAI integration is not configured."
    
    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are HopX Assistant, a helpful healthcare AI assistant for Hospital Pulse AI. You provide information about hospital operations, patient monitoring, system status, and medical insights. Be concise and helpful."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "I apologize, but I'm having trouble connecting to my AI services right now. Please try again later."

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time chatbot WebSocket endpoint with OpenAI integration."""
    await manager.connect(websocket)
    
    try:
        # Send initial welcome message
        welcome_msg = {
            "type": "welcome",
            "data": {
                "message": "🤖 HopX Assistant connected successfully!",
                "timestamp": datetime.now().isoformat(),
                "features": chatbot_service.get_active_features(),
                "system_status": chatbot_service.get_system_health()
            }
        }
        await manager.send_personal_message(json.dumps(welcome_msg), websocket)
        
        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "chat_message":
                    user_message = message_data.get("content", "")
                    if user_message.strip():
                        # Get AI response
                        ai_response = await get_openai_response(user_message)
                        
                        # Send response back
                        response_msg = {
                            "type": "chat_response",
                            "data": {
                                "content": ai_response,
                                "timestamp": datetime.now().isoformat(),
                                "role": "assistant"
                            }
                        }
                        await manager.send_personal_message(json.dumps(response_msg), websocket)
                        
                elif message_data.get("type") == "ping":
                    # Handle ping/pong for connection health
                    pong_msg = {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.send_personal_message(json.dumps(pong_msg), websocket)
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error processing message: {e}")
                error_msg = {
                    "type": "error",
                    "data": {
                        "message": "Sorry, I encountered an error processing your message.",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                await manager.send_personal_message(json.dumps(error_msg), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def start_broadcast_updates(websocket: WebSocket):
    """Start broadcasting real-time updates."""
    while True:
        try:
            # Get latest messages
            recent_messages = chatbot_service.get_recent_messages(limit=10)
            
            update_msg = {
                "type": "update",
                "data": {
                    "messages": recent_messages,
                    "system_health": chatbot_service.get_system_health(),
                    "alerts_summary": chatbot_service.get_patient_alerts_summary(),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            await manager.send_personal_message(json.dumps(update_msg), websocket)
            
            # Wait before next update
            await asyncio.sleep(30)  # Update every 30 seconds
            
        except:
            break  # Connection closed

@router.get("/feed")
async def get_chatbot_feed(limit: int = 50, message_type: Optional[str] = None):
    """Get chatbot feed messages."""
    try:
        messages = chatbot_service.get_recent_messages(limit=limit, message_type=message_type)
        
        return {
            "status": "success",
            "data": {
                "messages": messages,
                "total_count": len(messages),
                "system_health": chatbot_service.get_system_health(),
                "active_features": chatbot_service.get_active_features(),
                "alerts_summary": chatbot_service.get_patient_alerts_summary()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ping")
async def ping():
    """Simple health check endpoint for programmatic checks."""
    try:
        return {"status": "ok", "message": "chatbot route is reachable"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status():
    """Get comprehensive system status."""
    try:
        return {
            "status": "success",
            "data": {
                "system_health": chatbot_service.get_system_health(),
                "active_features": chatbot_service.get_active_features(),
                "uptime": chatbot_service._calculate_uptime(),
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/features")
async def get_features_status():
    """Get all features status and descriptions."""
    try:
        return {
            "status": "success",
            "data": {
                "active_features": chatbot_service.get_active_features(),
                "feature_details": {
                    "vitals_monitoring": {
                        "description": "Real-time patient vital signs monitoring and trend analysis",
                        "capabilities": [
                            "7 vital signs tracking",
                            "Trend analysis with statistical significance",
                            "Abnormality detection",
                            "Stability scoring (0-100 scale)",
                            "Missing reading alerts"
                        ],
                        "status": "active",
                        "last_check": datetime.now().isoformat()
                    },
                    "adherence_nudging": {
                        "description": "Personalized patient compliance and adherence interventions",
                        "capabilities": [
                            "Multi-dimensional adherence scoring",
                            "Personalized messaging",
                            "Predictive non-compliance identification",
                            "Social determinants integration",
                            "Behavioral nudging"
                        ],
                        "status": "active",
                        "last_check": datetime.now().isoformat()
                    },
                    "no_show_prediction": {
                        "description": "AI-powered appointment attendance forecasting",
                        "capabilities": [
                            "Ensemble ML models",
                            "47 predictive factors",
                            "Explainable AI with SHAP values",
                            "Dynamic learning",
                            "Capacity planning insights"
                        ],
                        "status": "active",
                        "last_check": datetime.now().isoformat()
                    },
                    "deterioration_risk": {
                        "description": "Multi-factor patient risk assessment and early warning",
                        "capabilities": [
                            "Physiological trend analysis",
                            "Laboratory integration",
                            "Medication adherence factors",
                            "Social determinants",
                            "Temporal dynamics"
                        ],
                        "status": "active",
                        "last_check": datetime.now().isoformat()
                    },
                    "escalation_workflows": {
                        "description": "Human-in-the-loop clinical intervention system",
                        "capabilities": [
                            "Smart trigger system",
                            "Role-based routing",
                            "SLA management",
                            "Complete audit trail",
                            "Real-time dashboard"
                        ],
                        "status": "active",
                        "last_check": datetime.now().isoformat()
                    }
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_patient_alerts(limit: int = 20):
    """Get patient alerts summary."""
    try:
        alerts_summary = chatbot_service.get_patient_alerts_summary()
        recent_alerts = chatbot_service.get_recent_messages(limit=limit, message_type="patient_alert")
        
        return {
            "status": "success",
            "data": {
                "summary": alerts_summary,
                "recent_alerts": recent_alerts,
                "alert_types": alerts_summary["alert_types"],
                "critical_count": alerts_summary["critical_alerts"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message")
async def add_chat_message(message_type: str, content: Dict, priority: str = "normal"):
    """Add new message to chatbot feed."""
    try:
        # Convert string to MessageType enum
        message_type_enum = MessageType(message_type)
        
        if message_type_enum == MessageType.SYSTEM_INFO:
            message = chatbot_service.add_system_message(content, priority)
        elif message_type_enum == MessageType.PATIENT_ALERT:
            message = chatbot_service.add_patient_alert(
                content.get("patient_id", ""),
                content.get("alert_type", ""),
                content.get("details", {})
            )
        elif message_type_enum == MessageType.FEATURE_UPDATE:
            message = chatbot_service.add_feature_update(
                content.get("feature_name", ""),
                content.get("status", ""),
                content.get("details", {})
            )
        elif message_type_enum == MessageType.OPERATIONAL_INSIGHT:
            message = chatbot_service.add_operational_insight(
                content.get("insight_type", ""),
                content.get("data", {})
            )
        elif message_type_enum == MessageType.ERROR_ALERT:
            message = chatbot_service.add_error_alert(
                content.get("error_type", ""),
                content.get("details", {}),
                content.get("severity", "high")
            )
        elif message_type_enum == MessageType.SUCCESS_MESSAGE:
            message = chatbot_service.add_success_message(
                content.get("operation", ""),
                content.get("details", {})
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid message type")
        
        # Broadcast to all connected clients
        broadcast_msg = {
            "type": "new_message",
            "data": message.to_dict()
        }
        await manager.broadcast(json.dumps(broadcast_msg))
        
        return {
            "status": "success",
            "data": message.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/help")
async def get_help_information():
    """Get help information and available commands."""
    try:
        help_info = {
            "commands": [
                {
                    "command": "/status",
                    "description": "Check system health and status",
                    "example": "GET /chatbot/status"
                },
                {
                    "command": "/features",
                    "description": "View active features and capabilities",
                    "example": "GET /chatbot/features"
                },
                {
                    "command": "/alerts",
                    "description": "See patient alerts and notifications",
                    "example": "GET /chatbot/alerts"
                },
                {
                    "command": "/feed",
                    "description": "Get chatbot feed messages",
                    "example": "GET /chatbot/feed?limit=50"
                },
                {
                    "command": "/help",
                    "description": "Get help information",
                    "example": "GET /chatbot/help"
                }
            ],
            "websocket_info": {
                "endpoint": "/chatbot/ws",
                "description": "Real-time chatbot feed via WebSocket",
                "connection": "WebSocket connection for live updates"
            },
            "message_types": [
                {
                    "type": "system_info",
                    "description": "System status and health information"
                },
                {
                    "type": "patient_alert",
                    "description": "Patient-related alerts and notifications"
                },
                {
                    "type": "feature_update",
                    "description": "Feature status updates and changes"
                },
                {
                    "type": "operational_insight",
                    "description": "Operational insights and recommendations"
                },
                {
                    "type": "error_alert",
                    "description": "Error notifications and troubleshooting"
                },
                {
                    "type": "success_message",
                    "description": "Success confirmations and completions"
                }
            ],
            "priority_levels": [
                {"level": "low", "description": "Informational messages"},
                {"level": "normal", "description": "Standard updates"},
                {"level": "high", "description": "Important notifications"},
                {"level": "critical", "description": "Urgent alerts requiring attention"}
            ]
        }
        
        return {
            "status": "success",
            "data": help_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
async def get_operational_insights():
    """Get operational insights and recommendations."""
    try:
        # Generate sample operational insights
        insights = {
            "system_performance": {
                "title": "System Performance",
                "insight": "All systems operating within normal parameters",
                "recommendation": "Continue monitoring",
                "data": {
                    "cpu_usage": "45%",
                    "memory_usage": "62%",
                    "response_time": "120ms"
                }
            },
            "patient_flow": {
                "title": "Patient Flow Analysis",
                "insight": "Patient volume within expected range",
                "recommendation": "Current staffing levels appropriate",
                "data": {
                    "active_patients": 50,
                    "new_admissions": 5,
                    "discharges": 3
                }
            },
            "alert_volume": {
                "title": "Alert Volume",
                "insight": "Alert volume moderate and manageable",
                "recommendation": "Monitor for escalation patterns",
                "data": {
                    "total_alerts": 12,
                    "critical_alerts": 2,
                    "resolution_rate": "85%"
                }
            }
        }
        
        return {
            "status": "success",
            "data": {
                "insights": insights,
                "timestamp": datetime.now().isoformat(),
                "next_update": "30 seconds"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
