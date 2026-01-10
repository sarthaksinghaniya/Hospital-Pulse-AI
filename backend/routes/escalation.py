"""
API Routes for Human Escalation Workflows
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
import sys
import os

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.escalation_workflows import HumanEscalationService
from services.deterioration_risk import PatientDeteriorationRiskService

router = APIRouter()
escalation_service = HumanEscalationService()
risk_service = PatientDeteriorationRiskService()

class EscalationTriggerRequest(BaseModel):
    patient_id: str
    current_risk_assessment: Dict
    previous_risk_assessment: Optional[Dict] = None

class EscalationAcknowledgeRequest(BaseModel):
    escalation_id: str
    acknowledged_by: str
    notes: Optional[str] = None

class EscalationResolveRequest(BaseModel):
    escalation_id: str
    resolved_by: str
    resolution_notes: str
    follow_up_required: bool = False

class EscalationReportRequest(BaseModel):
    patient_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@router.post("/check-triggers")
def check_escalation_triggers(request: EscalationTriggerRequest):
    """Check if escalation should be triggered based on risk assessment."""
    try:
        triggers = escalation_service.check_escalation_triggers(
            request.patient_id,
            request.current_risk_assessment,
            request.previous_risk_assessment
        )
        
        # Create escalation events for each trigger
        created_escalations = []
        for trigger in triggers:
            escalation = escalation_service.create_escalation_event(
                request.patient_id,
                trigger,
                request.current_risk_assessment
            )
            created_escalations.append(escalation)
        
        return {
            "status": "success",
            "data": {
                "triggers": triggers,
                "created_escalations": created_escalations,
                "total_escalations": len(created_escalations)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/acknowledge")
def acknowledge_escalation(request: EscalationAcknowledgeRequest):
    """Acknowledge an escalation event."""
    try:
        result = escalation_service.acknowledge_escalation(
            request.escalation_id,
            request.acknowledged_by,
            request.notes
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resolve")
def resolve_escalation(request: EscalationResolveRequest):
    """Resolve an escalation event."""
    try:
        result = escalation_service.resolve_escalation(
            request.escalation_id,
            request.resolved_by,
            request.resolution_notes,
            request.follow_up_required
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}")
def get_patient_escalations(patient_id: str, status: Optional[str] = Query(None)):
    """Get all escalations for a patient, optionally filtered by status."""
    try:
        escalations = escalation_service.get_patient_escalations(patient_id, status)
        return {
            "status": "success",
            "data": {
                "patient_id": patient_id,
                "escalations": escalations,
                "total_count": len(escalations)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active")
def get_active_escalations(escalation_level: Optional[str] = Query(None)):
    """Get all active (pending/acknowledged/in_progress) escalations."""
    try:
        escalations = escalation_service.get_active_escalations(escalation_level)
        return {
            "status": "success",
            "data": {
                "active_escalations": escalations,
                "total_count": len(escalations)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
def get_escalation_dashboard():
    """Get comprehensive data for escalation dashboard."""
    try:
        dashboard_data = escalation_service.get_escalation_dashboard_data()
        return {
            "status": "success",
            "data": dashboard_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
def generate_escalation_report(request: EscalationReportRequest):
    """Generate comprehensive escalation report."""
    try:
        report = escalation_service.generate_escalation_report(
            request.patient_id,
            request.start_date,
            request.end_date
        )
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules")
def get_escalation_rules():
    """Get current escalation rules and thresholds."""
    try:
        return {
            "status": "success",
            "data": {
                "escalation_rules": escalation_service.escalation_rules,
                "escalation_templates": escalation_service.escalation_templates
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{escalation_id}")
def get_escalation_details(escalation_id: str):
    """Get details of a specific escalation event."""
    try:
        escalation = escalation_service._find_escalation_by_id(escalation_id)
        if not escalation:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        return {
            "status": "success",
            "data": escalation
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
