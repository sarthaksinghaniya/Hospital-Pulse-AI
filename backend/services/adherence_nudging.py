"""
Adherence Nudging Service

This service handles patient adherence monitoring and nudging, including:
- Computing adherence scores using vitals consistency and no-show history
- Generating personalized, non-clinical nudges
- Storing and tracking adherence trends over time
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

class AdherenceNudgingService:
    """Service for monitoring patient adherence and generating personalized nudges."""
    
    def __init__(self):
        self.adherence_data = {}
        self.nudge_history = {}
        self.adherence_trends = {}
        
        # Nudge templates for different scenarios
        self.nudge_templates = {
            'low_vitals_compliance': [
                "Hi {name}! We noticed you missed some recent health check-ins. Regular monitoring helps us keep you healthy. Can we help you set up reminders?",
                "Hello {name}! Your health team wants to make sure you're feeling your best. Let's get those vitals checked today - it only takes a minute!",
                "Hey {name}! Staying on top of your health readings is important. We're here to help if you're having any trouble with the monitoring process."
            ],
            'missed_appointments': [
                "Hi {name}! We missed you at your last appointment. Your health is important to us - let's reschedule at a time that works better for you.",
                "Hello {name}! Life gets busy, but your health can't wait. We have flexible appointment times available. When would work best for you?",
                "Hey {name}! We noticed you haven't been able to make it to recent appointments. Is there anything we can do to make it easier for you?"
            ],
            'declining_trend': [
                "Hi {name}! We've noticed some changes in your recent health readings. Let's work together to get things back on track.",
                "Hello {name}! Your health team is here to support you. We'd like to check in and see how you're doing with your care plan.",
                "Hey {name}! Small changes can make a big difference. Let's talk about what might help improve your health routine."
            ],
            'positive_reinforcement': [
                "Great job, {name}! Your consistent health monitoring is really making a difference. Keep up the excellent work!",
                "Fantastic progress, {name}! Your dedication to your health is inspiring. We're proud to be part of your healthcare team!",
                "Wonderful commitment, {name}! Your regular check-ins show how much you care about your health. Keep it up!"
            ],
            'medication_reminder': [
                "Hi {name}! Quick reminder about your medication. Taking it as prescribed helps you stay healthy and feel your best.",
                "Hello {name}! It's medication time. Your health is worth that extra moment of care each day.",
                "Hey {name}! Gentle reminder about your medication. Consistency is key to managing your health effectively."
            ]
        }
    
    def compute_adherence_score(self, patient_id: str, vitals_service=None, appointments_data=None) -> Dict:
        """Compute comprehensive adherence score for a patient."""
        
        # Initialize score components
        vitals_compliance_score = 0
        appointment_attendance_score = 0
        medication_adherence_score = 0  # Placeholder for future implementation
        overall_score = 0
        
        # Calculate vitals compliance score
        if vitals_service:
            try:
                missing_analysis = vitals_service.check_missing_readings(patient_id, hours_back=168)  # 1 week
                if "error" not in missing_analysis:
                    coverage = missing_analysis['coverage_percentage'] / 100
                    vitals_compliance_score = coverage * 100
            except:
                vitals_compliance_score = 50  # Default if service unavailable
        else:
            vitals_compliance_score = 50  # Default score
        
        # Calculate appointment attendance score
        if appointments_data is not None:
            try:
                patient_appointments = appointments_data[appointments_data['patient_id'] == patient_id]
                if len(patient_appointments) > 0:
                    attended = len(patient_appointments[patient_appointments['no_show'] == 'No'])
                    total = len(patient_appointments)
                    appointment_attendance_score = (attended / total) * 100
            except:
                appointment_attendance_score = 50
        else:
            # Simulate appointment adherence based on patient ID
            np.random.seed(hash(patient_id) % 1000)
            appointment_attendance_score = np.random.normal(75, 15)
            appointment_attendance_score = max(0, min(100, appointment_attendance_score))
        
        # Calculate medication adherence (simulated for now)
        np.random.seed((hash(patient_id) + 1) % 1000)
        medication_adherence_score = np.random.normal(80, 10)
        medication_adherence_score = max(0, min(100, medication_adherence_score))
        
        # Calculate weighted overall score
        weights = {
            'vitals': 0.4,
            'appointments': 0.35,
            'medication': 0.25
        }
        
        overall_score = (
            vitals_compliance_score * weights['vitals'] +
            appointment_attendance_score * weights['appointments'] +
            medication_adherence_score * weights['medication']
        )
        
        # Determine adherence level
        if overall_score >= 85:
            adherence_level = "Excellent"
            color = "green"
        elif overall_score >= 70:
            adherence_level = "Good"
            color = "blue"
        elif overall_score >= 55:
            adherence_level = "Fair"
            color = "yellow"
        elif overall_score >= 40:
            adherence_level = "Poor"
            color = "orange"
        else:
            adherence_level = "Critical"
            color = "red"
        
        return {
            'patient_id': patient_id,
            'overall_score': round(overall_score, 1),
            'adherence_level': adherence_level,
            'color_indicator': color,
            'component_scores': {
                'vitals_compliance': round(vitals_compliance_score, 1),
                'appointment_attendance': round(appointment_attendance_score, 1),
                'medication_adherence': round(medication_adherence_score, 1)
            },
            'weights_used': weights,
            'calculated_at': datetime.now().isoformat()
        }
    
    def generate_personalized_nudge(self, patient_id: str, adherence_score: Dict, 
                                  patient_name: str = "Patient", vitals_trends: Dict = None) -> Dict:
        """Generate personalized nudge based on adherence score and trends."""
        
        overall_score = adherence_score['overall_score']
        adherence_level = adherence_score['adherence_level']
        component_scores = adherence_score['component_scores']
        
        # Determine nudge type and urgency
        nudge_type = None
        urgency = "low"
        
        if overall_score < 40:
            nudge_type = 'missed_appointments' if component_scores['appointment_attendance'] < 50 else 'low_vitals_compliance'
            urgency = "high"
        elif overall_score < 55:
            nudge_type = 'low_vitals_compliance' if component_scores['vitals_compliance'] < 60 else 'declining_trend'
            urgency = "medium"
        elif overall_score >= 85:
            nudge_type = 'positive_reinforcement'
            urgency = "low"
        elif vitals_trends and any(trend.get('trend_concern', False) for trend in vitals_trends.get('trends', {}).values()):
            nudge_type = 'declining_trend'
            urgency = "medium"
        else:
            nudge_type = 'medication_reminder'
            urgency = "low"
        
        # Select appropriate nudge template
        templates = self.nudge_templates.get(nudge_type, self.nudge_templates['medication_reminder'])
        selected_template = np.random.choice(templates)
        
        # Personalize the message
        personalized_message = selected_template.format(name=patient_name)
        
        # Generate specific recommendations
        recommendations = self._generate_adherence_recommendations(component_scores, adherence_level)
        
        # Store nudge in history
        nudge_record = {
            'patient_id': patient_id,
            'nudge_type': nudge_type,
            'urgency': urgency,
            'message': personalized_message,
            'recommendations': recommendations,
            'adherence_score_at_time': overall_score,
            'sent_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        if patient_id not in self.nudge_history:
            self.nudge_history[patient_id] = []
        self.nudge_history[patient_id].append(nudge_record)
        
        return {
            'patient_id': patient_id,
            'nudge_type': nudge_type,
            'urgency': urgency,
            'personalized_message': personalized_message,
            'recommendations': recommendations,
            'delivery_channels': self._suggest_delivery_channels(urgency),
            'optimal_timing': self._suggest_optimal_timing(patient_id),
            'nudge_id': len(self.nudge_history.get(patient_id, []))
        }
    
    def _generate_adherence_recommendations(self, component_scores: Dict, adherence_level: str) -> List[str]:
        """Generate specific recommendations based on adherence components."""
        recommendations = []
        
        if component_scores['vitals_compliance'] < 60:
            recommendations.append("Set up daily reminders for vitals monitoring")
            recommendations.append("Consider simplifying your monitoring routine")
        
        if component_scores['appointment_attendance'] < 60:
            recommendations.append("Schedule appointments at consistent times")
            recommendations.append("Set up appointment reminders 24 hours in advance")
            recommendations.append("Consider telehealth options for convenience")
        
        if component_scores['medication_adherence'] < 60:
            recommendations.append("Use pill organizers or medication apps")
            recommendations.append("Set up medication alarms")
            recommendations.append("Coordinate medication times with daily routines")
        
        if adherence_level in ["Poor", "Critical"]:
            recommendations.append("Consider involving a family member or caregiver")
            recommendations.append("Schedule a consultation with your care coordinator")
        
        if not recommendations:
            recommendations.append("Continue your current excellent adherence routine")
        
        return recommendations
    
    def _suggest_delivery_channels(self, urgency: str) -> List[str]:
        """Suggest optimal delivery channels based on urgency."""
        if urgency == "high":
            return ["phone_call", "sms", "email", "patient_portal"]
        elif urgency == "medium":
            return ["sms", "email", "patient_portal"]
        else:
            return ["patient_portal", "email"]
    
    def _suggest_optimal_timing(self, patient_id: str) -> Dict:
        """Suggest optimal timing for nudge delivery."""
        # Simulate patient preference based on ID
        np.random.seed(hash(patient_id) % 1000)
        preferred_hour = np.random.choice([9, 10, 14, 16, 18])
        
        return {
            'preferred_time': f"{preferred_hour:02d}:00",
            'timezone': 'local',
            'best_days': ['Monday', 'Wednesday', 'Friday'],
            'avoid_times': ['early_morning', 'late_night']
        }
    
    def track_adherence_trends(self, patient_id: str, days_back: int = 30) -> Dict:
        """Track adherence trends over time for a patient."""
        
        # Generate historical adherence data (simulated)
        np.random.seed(hash(patient_id) % 1000)
        dates = pd.date_range(end=datetime.now(), periods=days_back, freq='D')
        
        # Create realistic trend with some variation
        base_score = 70 + np.random.normal(0, 10)
        trend_scores = []
        
        for i, date in enumerate(dates):
            # Add some random variation and potential trend
            variation = np.random.normal(0, 5)
            trend_effect = i * 0.1  # Slight trend over time
            score = base_score + variation + trend_effect
            score = max(0, min(100, score))
            trend_scores.append(score)
        
        # Calculate trend statistics
        recent_scores = trend_scores[-7:]  # Last week
        older_scores = trend_scores[-14:-7] if len(trend_scores) >= 14 else trend_scores[:-7]
        
        trend_direction = "stable"
        if len(recent_scores) > 0 and len(older_scores) > 0:
            recent_avg = np.mean(recent_scores)
            older_avg = np.mean(older_scores)
            if recent_avg > older_avg + 5:
                trend_direction = "improving"
            elif recent_avg < older_avg - 5:
                trend_direction = "declining"
        
        return {
            'patient_id': patient_id,
            'analysis_period_days': days_back,
            'current_score': trend_scores[-1] if trend_scores else 0,
            'average_score': np.mean(trend_scores) if trend_scores else 0,
            'trend_direction': trend_direction,
            'recent_week_average': np.mean(recent_scores) if recent_scores else 0,
            'score_volatility': np.std(trend_scores) if trend_scores else 0,
            'best_score': max(trend_scores) if trend_scores else 0,
            'worst_score': min(trend_scores) if trend_scores else 0,
            'data_points': len(trend_scores),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_adherence_insights(self, patient_id: str) -> Dict:
        """Get comprehensive adherence insights for a patient."""
        
        # Get current adherence score
        adherence_score = self.compute_adherence_score(patient_id)
        
        # Get trends
        trends = self.track_adherence_trends(patient_id)
        
        # Get nudge history
        nudge_history = self.nudge_history.get(patient_id, [])
        recent_nudges = nudge_history[-5:] if nudge_history else []
        
        # Generate insights
        insights = []
        
        if adherence_score['overall_score'] < 50:
            insights.append("Patient requires immediate intervention to improve adherence")
        elif trends['trend_direction'] == "declining":
            insights.append("Adherence is declining - proactive intervention recommended")
        elif adherence_score['overall_score'] > 85:
            insights.append("Patient shows excellent adherence - maintain current support")
        
        if len(recent_nudges) > 3:
            insights.append("Multiple recent nudges sent - consider alternative intervention strategies")
        
        # Identify most challenging component
        component_scores = adherence_score['component_scores']
        lowest_component = min(component_scores, key=component_scores.get)
        insights.append(f"Focus area: {lowest_component.replace('_', ' ').title()}")
        
        return {
            'patient_id': patient_id,
            'current_adherence': adherence_score,
            'trend_analysis': trends,
            'recent_nudges': recent_nudges,
            'insights': insights,
            'recommended_actions': self._generate_recommended_actions(adherence_score, trends),
            'last_updated': datetime.now().isoformat()
        }
    
    def _generate_recommended_actions(self, adherence_score: Dict, trends: Dict) -> List[str]:
        """Generate recommended actions based on adherence analysis."""
        actions = []
        score = adherence_score['overall_score']
        component_scores = adherence_score['component_scores']
        
        if score < 40:
            actions.append("Schedule immediate case manager consultation")
            actions.append("Implement intensive monitoring protocol")
        elif score < 55:
            actions.append("Increase check-in frequency to twice weekly")
            actions.append("Consider home health visit")
        
        if component_scores['vitals_compliance'] < 60:
            actions.append("Provide additional training on monitoring equipment")
            actions.append("Set up automated vitals reminders")
        
        if component_scores['appointment_attendance'] < 60:
            actions.append("Offer flexible scheduling options")
            actions.append("Implement appointment reminder system")
        
        if trends['trend_direction'] == "declining":
            actions.append("Identify and address barriers to adherence")
            actions.append("Consider social work consultation")
        
        if not actions:
            actions.append("Continue current monitoring and support")
        
        return actions
    
    def get_population_adherence_overview(self) -> Dict:
        """Get adherence overview for all patients."""
        # Simulate population data
        np.random.seed(42)
        num_patients = 50
        
        adherence_levels = []
        scores = []
        
        for i in range(num_patients):
            patient_id = f"P{i+1:04d}"
            score = self.compute_adherence_score(patient_id)
            adherence_levels.append(score['adherence_level'])
            scores.append(score['overall_score'])
        
        level_counts = pd.Series(adherence_levels).value_counts().to_dict()
        
        return {
            'total_patients': num_patients,
            'average_adherence_score': np.mean(scores),
            'adherence_distribution': level_counts,
            'high_risk_patients': level_counts.get('Critical', 0) + level_counts.get('Poor', 0),
            'excellent_adherence_patients': level_counts.get('Excellent', 0),
            'last_updated': datetime.now().isoformat()
        }
