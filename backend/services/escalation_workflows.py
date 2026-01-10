"""
Human Escalation Workflows Service

This service handles escalation workflows for high-risk patients, including:
- Triggering escalations when risk increases sharply
- Routing to clinician/admin dashboards
- Logging escalation events with timestamps and reasons
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import uuid
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class EscalationLevel(Enum):
    """Escalation levels for patient care."""
    NURSE = "nurse"
    PHYSICIAN = "physician"
    SPECIALIST = "specialist"
    EMERGENCY = "emergency"

class EscalationStatus(Enum):
    """Status of escalation events."""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"

class HumanEscalationService:
    """Service for managing human escalation workflows."""
    
    def __init__(self):
        self.escalation_events = {}
        self.escalation_rules = self._initialize_default_rules()
        self.care_team_assignments = {}
        self.escalation_templates = self._initialize_escalation_templates()
        
    def _initialize_default_rules(self) -> Dict:
        """Initialize default escalation rules."""
        return {
            'risk_score_threshold': {
                'high': 70,
                'critical': 85
            },
            'rapid_increase_threshold': 15,  # Points increase in short time
            'vitals_critical_values': {
                'heart_rate': {'min': 40, 'max': 150},
                'blood_pressure_systolic': {'min': 80, 'max': 200},
                'blood_pressure_diastolic': {'min': 40, 'max': 120},
                'temperature': {'min': 35.0, 'max': 40.0},
                'oxygen_saturation': {'min': 85, 'max': 100},
                'respiratory_rate': {'min': 8, 'max': 30}
            },
            'adherence_critical_threshold': 30,  # Below this triggers escalation
            'no_show_critical_threshold': 0.7,  # 70% probability
            'time_windows': {
                'immediate': 0,  # minutes
                'urgent': 15,    # minutes
                'routine': 60    # minutes
            }
        }
    
    def _initialize_escalation_templates(self) -> Dict:
        """Initialize escalation message templates."""
        return {
            'high_risk': {
                'title': 'High Risk Patient Alert',
                'message': 'Patient {patient_id} has been identified as high risk (score: {risk_score}). Immediate review required.',
                'recommended_action': 'Clinical assessment within 2 hours',
                'priority': 'high'
            },
            'critical_vitals': {
                'title': 'Critical Vitals Alert',
                'message': 'Patient {patient_id} has critical vitals readings: {vitals_details}. Immediate intervention required.',
                'recommended_action': 'Emergency assessment',
                'priority': 'critical'
            },
            'rapid_deterioration': {
                'title': 'Rapid Deterioration Alert',
                'message': 'Patient {patient_id} shows rapid deterioration (risk increase: {risk_increase} points).',
                'recommended_action': 'Urgent clinical evaluation',
                'priority': 'high'
            },
            'adherence_crisis': {
                'title': 'Adherence Crisis Alert',
                'message': 'Patient {patient_id} has critical adherence issues (score: {adherence_score}). Care coordination needed.',
                'recommended_action': 'Case manager intervention',
                'priority': 'medium'
            },
            'missed_appointment_risk': {
                'title': 'High No-Show Risk',
                'message': 'Patient {patient_id} at high risk of missing appointment (probability: {no_show_prob}). Outreach recommended.',
                'recommended_action': 'Patient contact and reminder',
                'priority': 'medium'
            }
        }
    
    def check_escalation_triggers(self, patient_id: str, current_risk_assessment: Dict, 
                                 previous_risk_assessment: Dict = None) -> List[Dict]:
        """Check if escalation should be triggered based on risk assessment."""
        escalations = []
        
        current_risk_score = current_risk_assessment.get('overall_risk_score', 0)
        risk_category = current_risk_assessment.get('risk_category', 'Low')
        
        # Check for high/critical risk scores
        if current_risk_score >= self.escalation_rules['risk_score_threshold']['critical']:
            escalations.append({
                'trigger_type': 'critical_risk_score',
                'escalation_level': EscalationLevel.PHYSICIAN.value,
                'urgency': 'immediate',
                'reason': f'Critical risk score: {current_risk_score}',
                'template': 'high_risk'
            })
        elif current_risk_score >= self.escalation_rules['risk_score_threshold']['high']:
            escalations.append({
                'trigger_type': 'high_risk_score',
                'escalation_level': EscalationLevel.NURSE.value,
                'urgency': 'urgent',
                'reason': f'High risk score: {current_risk_score}',
                'template': 'high_risk'
            })
        
        # Check for rapid increase in risk
        if previous_risk_assessment:
            previous_score = previous_risk_assessment.get('overall_risk_score', 0)
            risk_increase = current_risk_score - previous_score
            
            if risk_increase >= self.escalation_rules['rapid_increase_threshold']:
                escalations.append({
                    'trigger_type': 'rapid_risk_increase',
                    'escalation_level': EscalationLevel.PHYSICIAN.value,
                    'urgency': 'urgent',
                    'reason': f'Rapid risk increase: {risk_increase} points',
                    'template': 'rapid_deterioration',
                    'risk_increase': risk_increase
                })
        
        # Check for critical vitals
        component_risks = current_risk_assessment.get('component_risks', {})
        vitals_risk = component_risks.get('vitals_stability', {})
        
        if vitals_risk.get('risk_score', 0) > 50:
            escalations.append({
                'trigger_type': 'critical_vitals',
                'escalation_level': EscalationLevel.EMERGENCY.value,
                'urgency': 'immediate',
                'reason': 'Critical vital signs detected',
                'template': 'critical_vitals',
                'vitals_details': self._get_critical_vitals_details(current_risk_assessment)
            })
        
        # Check adherence crisis
        adherence_risk = component_risks.get('adherence', {})
        adherence_score = adherence_risk.get('adherence_score', 100)
        
        if adherence_score < self.escalation_rules['adherence_critical_threshold']:
            escalations.append({
                'trigger_type': 'adherence_crisis',
                'escalation_level': EscalationLevel.NURSE.value,
                'urgency': 'routine',
                'reason': f'Critical adherence score: {adherence_score}',
                'template': 'adherence_crisis',
                'adherence_score': adherence_score
            })
        
        # Check high no-show risk
        no_show_risk = component_risks.get('no_show_prediction', {})
        no_show_prob = no_show_risk.get('no_show_probability', 0)
        
        if no_show_prob >= self.escalation_rules['no_show_critical_threshold']:
            escalations.append({
                'trigger_type': 'high_no_show_risk',
                'escalation_level': EscalationLevel.NURSE.value,
                'urgency': 'routine',
                'reason': f'High no-show probability: {no_show_prob}',
                'template': 'missed_appointment_risk',
                'no_show_prob': no_show_prob
            })
        
        return escalations
    
    def _get_critical_vitals_details(self, risk_assessment: Dict) -> str:
        """Extract details about critical vitals."""
        component_risks = risk_assessment.get('component_risks', {})
        vitals_risk = component_risks.get('vitals_stability', {})
        
        details = []
        if 'contributing_factors' in vitals_risk:
            details.extend(vitals_risk['contributing_factors'][:3])
        
        return '; '.join(details) if details else 'Multiple vital sign abnormalities'
    
    def create_escalation_event(self, patient_id: str, escalation_trigger: Dict, 
                              current_risk_assessment: Dict) -> Dict:
        """Create and log an escalation event."""
        
        escalation_id = str(uuid.uuid4())
        template_key = escalation_trigger.get('template', 'high_risk')
        template = self.escalation_templates.get(template_key, self.escalation_templates['high_risk'])
        
        # Create escalation event
        escalation_event = {
            'escalation_id': escalation_id,
            'patient_id': patient_id,
            'created_at': datetime.now().isoformat(),
            'trigger_type': escalation_trigger['trigger_type'],
            'escalation_level': escalation_trigger['escalation_level'],
            'urgency': escalation_trigger['urgency'],
            'status': EscalationStatus.PENDING.value,
            'title': template['title'].format(
                patient_id=patient_id,
                risk_score=current_risk_assessment.get('overall_risk_score', 0)
            ),
            'message': template['message'].format(
                patient_id=patient_id,
                risk_score=current_risk_assessment.get('overall_risk_score', 0),
                risk_increase=escalation_trigger.get('risk_increase', 0),
                adherence_score=escalation_trigger.get('adherence_score', 0),
                no_show_prob=escalation_trigger.get('no_show_prob', 0),
                vitals_details=escalation_trigger.get('vitals_details', 'N/A')
            ),
            'recommended_action': template['recommended_action'],
            'priority': template['priority'],
            'reason': escalation_trigger['reason'],
            'risk_assessment': current_risk_assessment,
            'assigned_to': None,
            'acknowledged_at': None,
            'resolved_at': None,
            'resolution_notes': None,
            'follow_up_required': True,
            'follow_up_date': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        # Store escalation event
        if patient_id not in self.escalation_events:
            self.escalation_events[patient_id] = []
        self.escalation_events[patient_id].append(escalation_event)
        
        # Route to appropriate dashboard/personnel
        self._route_escalation(escalation_event)
        
        return escalation_event
    
    def _route_escalation(self, escalation_event: Dict) -> Dict:
        """Route escalation to appropriate personnel/dashboard."""
        escalation_level = escalation_event['escalation_level']
        urgency = escalation_event['urgency']
        
        routing_info = {
            'escalation_id': escalation_event['escalation_id'],
            'routed_to': [],
            'delivery_methods': [],
            'estimated_response_time': None
        }
        
        # Determine routing based on escalation level and urgency
        if escalation_level == EscalationLevel.EMERGENCY.value:
            routing_info['routed_to'] = ['emergency_department', 'on_call_physician', 'charge_nurse']
            routing_info['delivery_methods'] = ['sms_alert', 'phone_call', 'dashboard_notification']
            routing_info['estimated_response_time'] = '5 minutes'
            
        elif escalation_level == EscalationLevel.PHYSICIAN.value:
            routing_info['routed_to'] = ['primary_care_physician', 'charge_nurse']
            if urgency == 'immediate':
                routing_info['delivery_methods'] = ['phone_call', 'dashboard_notification', 'sms_alert']
                routing_info['estimated_response_time'] = '15 minutes'
            else:
                routing_info['delivery_methods'] = ['dashboard_notification', 'email']
                routing_info['estimated_response_time'] = '1 hour'
                
        elif escalation_level == EscalationLevel.SPECIALIST.value:
            routing_info['routed_to'] = ['specialist', 'primary_care_physician']
            routing_info['delivery_methods'] = ['dashboard_notification', 'email']
            routing_info['estimated_response_time'] = '4 hours'
            
        else:  # NURSE
            routing_info['routed_to'] = ['charge_nurse', 'case_manager']
            routing_info['delivery_methods'] = ['dashboard_notification']
            routing_info['estimated_response_time'] = '2 hours'
        
        # Store routing information
        escalation_event['routing_info'] = routing_info
        
        return routing_info
    
    def acknowledge_escalation(self, escalation_id: str, acknowledged_by: str, 
                             notes: str = None) -> Dict:
        """Acknowledge an escalation event."""
        
        # Find the escalation event
        escalation_event = self._find_escalation_by_id(escalation_id)
        
        if not escalation_event:
            return {'error': f'Escalation {escalation_id} not found'}
        
        # Update status
        escalation_event['status'] = EscalationStatus.ACKNOWLEDGED.value
        escalation_event['acknowledged_at'] = datetime.now().isoformat()
        escalation_event['acknowledged_by'] = acknowledged_by
        escalation_event['acknowledgment_notes'] = notes
        
        return {
            'escalation_id': escalation_id,
            'status': 'acknowledged',
            'acknowledged_by': acknowledged_by,
            'acknowledged_at': escalation_event['acknowledged_at'],
            'message': 'Escalation acknowledged successfully'
        }
    
    def resolve_escalation(self, escalation_id: str, resolved_by: str, 
                          resolution_notes: str, follow_up_required: bool = False) -> Dict:
        """Resolve an escalation event."""
        
        escalation_event = self._find_escalation_by_id(escalation_id)
        
        if not escalation_event:
            return {'error': f'Escalation {escalation_id} not found'}
        
        # Update status
        escalation_event['status'] = EscalationStatus.RESOLVED.value
        escalation_event['resolved_at'] = datetime.now().isoformat()
        escalation_event['resolved_by'] = resolved_by
        escalation_event['resolution_notes'] = resolution_notes
        escalation_event['follow_up_required'] = follow_up_required
        
        if follow_up_required:
            escalation_event['follow_up_date'] = (datetime.now() + timedelta(days=7)).isoformat()
        
        return {
            'escalation_id': escalation_id,
            'status': 'resolved',
            'resolved_by': resolved_by,
            'resolved_at': escalation_event['resolved_at'],
            'follow_up_required': follow_up_required,
            'message': 'Escalation resolved successfully'
        }
    
    def _find_escalation_by_id(self, escalation_id: str) -> Optional[Dict]:
        """Find escalation event by ID."""
        for patient_escalations in self.escalation_events.values():
            for escalation in patient_escalations:
                if escalation['escalation_id'] == escalation_id:
                    return escalation
        return None
    
    def get_patient_escalations(self, patient_id: str, status: str = None) -> List[Dict]:
        """Get all escalations for a patient, optionally filtered by status."""
        if patient_id not in self.escalation_events:
            return []
        
        escalations = self.escalation_events[patient_id]
        
        if status:
            escalations = [e for e in escalations if e['status'] == status]
        
        # Sort by creation date (most recent first)
        escalations.sort(key=lambda x: x['created_at'], reverse=True)
        
        return escalations
    
    def get_active_escalations(self, escalation_level: str = None) -> List[Dict]:
        """Get all active (pending/acknowledged/in_progress) escalations."""
        active_escalations = []
        
        for patient_escalations in self.escalation_events.values():
            for escalation in patient_escalations:
                if escalation['status'] in [EscalationStatus.PENDING.value, 
                                           EscalationStatus.ACKNOWLEDGED.value,
                                           EscalationStatus.IN_PROGRESS.value]:
                    
                    if escalation_level is None or escalation['escalation_level'] == escalation_level:
                        active_escalations.append(escalation)
        
        # Sort by urgency and creation time
        urgency_order = {'immediate': 0, 'urgent': 1, 'routine': 2}
        active_escalations.sort(key=lambda x: (urgency_order.get(x['urgency'], 3), x['created_at']))
        
        return active_escalations
    
    def get_escalation_dashboard_data(self) -> Dict:
        """Get comprehensive data for escalation dashboard."""
        
        active_escalations = self.get_active_escalations()
        
        # Summary statistics
        total_active = len(active_escalations)
        by_status = {}
        by_level = {}
        by_urgency = {}
        
        for escalation in active_escalations:
            # Count by status
            status = escalation['status']
            by_status[status] = by_status.get(status, 0) + 1
            
            # Count by level
            level = escalation['escalation_level']
            by_level[level] = by_level.get(level, 0) + 1
            
            # Count by urgency
            urgency = escalation['urgency']
            by_urgency[urgency] = by_urgency.get(urgency, 0) + 1
        
        # Recent escalations (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_escalations = []
        
        for patient_escalations in self.escalation_events.values():
            for escalation in patient_escalations:
                created_time = datetime.fromisoformat(escalation['created_at'])
                if created_time >= recent_cutoff:
                    recent_escalations.append(escalation)
        
        # Overdue escalations (older than 24 hours and not resolved)
        overdue_cutoff = datetime.now() - timedelta(hours=24)
        overdue_escalations = []
        
        for escalation in active_escalations:
            created_time = datetime.fromisoformat(escalation['created_at'])
            if created_time <= overdue_cutoff:
                overdue_escalations.append(escalation)
        
        return {
            'summary': {
                'total_active': total_active,
                'by_status': by_status,
                'by_level': by_level,
                'by_urgency': by_urgency,
                'overdue_count': len(overdue_escalations),
                'last_updated': datetime.now().isoformat()
            },
            'active_escalations': active_escalations[:20],  # Limit to 20 most recent
            'recent_escalations': sorted(recent_escalations, 
                                       key=lambda x: x['created_at'], reverse=True)[:10],
            'overdue_escalations': overdue_escalations,
            'escalation_trends': self._get_escalation_trends()
        }
    
    def _get_escalation_trends(self) -> Dict:
        """Get escalation trends over time."""
        # Calculate trends for last 7 days
        trends = {}
        current_date = datetime.now()
        
        for i in range(7):
            date = current_date - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            daily_count = 0
            for patient_escalations in self.escalation_events.values():
                for escalation in patient_escalations:
                    created_time = datetime.fromisoformat(escalation['created_at'])
                    if created_time.date() == date.date():
                        daily_count += 1
            
            trends[date_str] = daily_count
        
        return {
            'daily_counts': trends,
            'total_last_7_days': sum(trends.values()),
            'average_per_day': sum(trends.values()) / 7
        }
    
    def generate_escalation_report(self, patient_id: str = None, 
                                 start_date: str = None, end_date: str = None) -> Dict:
        """Generate comprehensive escalation report."""
        
        # Filter escalations based on criteria
        filtered_escalations = []
        
        if patient_id:
            filtered_escalations.extend(self.get_patient_escalations(patient_id))
        else:
            for patient_escalations in self.escalation_events.values():
                filtered_escalations.extend(patient_escalations)
        
        # Filter by date range if provided
        if start_date or end_date:
            start = datetime.fromisoformat(start_date) if start_date else datetime.min
            end = datetime.fromisoformat(end_date) if end_date else datetime.max
            
            filtered_escalations = [
                e for e in filtered_escalations 
                if start <= datetime.fromisoformat(e['created_at']) <= end
            ]
        
        # Generate statistics
        total_escalations = len(filtered_escalations)
        resolved_count = len([e for e in filtered_escalations if e['status'] == EscalationStatus.RESOLVED.value])
        
        # Average resolution time
        resolution_times = []
        for escalation in filtered_escalations:
            if escalation.get('resolved_at') and escalation.get('created_at'):
                created = datetime.fromisoformat(escalation['created_at'])
                resolved = datetime.fromisoformat(escalation['resolved_at'])
                resolution_times.append((resolved - created).total_seconds() / 3600)  # hours
        
        avg_resolution_time = np.mean(resolution_times) if resolution_times else 0
        
        # Escalations by trigger type
        trigger_counts = {}
        for escalation in filtered_escalations:
            trigger = escalation['trigger_type']
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        return {
            'report_parameters': {
                'patient_id': patient_id,
                'start_date': start_date,
                'end_date': end_date,
                'generated_at': datetime.now().isoformat()
            },
            'summary': {
                'total_escalations': total_escalations,
                'resolved_count': resolved_count,
                'resolution_rate': (resolved_count / total_escalations * 100) if total_escalations > 0 else 0,
                'average_resolution_time_hours': round(avg_resolution_time, 2),
                'active_escalations': len([e for e in filtered_escalations if e['status'] != EscalationStatus.RESOLVED.value])
            },
            'escalations_by_trigger_type': trigger_counts,
            'detailed_escalations': sorted(filtered_escalations, 
                                         key=lambda x: x['created_at'], reverse=True)
        }
