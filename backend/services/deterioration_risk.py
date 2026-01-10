"""
Patient Deterioration Risk Score Service

This service handles comprehensive patient risk assessment, including:
- Combining vitals trends, chronic indicators, and adherence scores
- Outputting Low / Medium / High risk categories
- Including explanations of risk drivers
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class PatientDeteriorationRiskService:
    """Service for assessing patient deterioration risk."""
    
    def __init__(self):
        self.risk_thresholds = {
            'low': (0, 30),
            'medium': (30, 70),
            'high': (70, 100)
        }
        
        # Risk factor weights
        self.risk_weights = {
            'vitals_stability': 0.35,
            'chronic_conditions': 0.25,
            'adherence_score': 0.20,
            'age_risk': 0.10,
            'no_show_risk': 0.10
        }
        
        # Chronic condition severity mapping
        self.chronic_condition_severity = {
            'diabetes': 0.7,
            'hypertension': 0.5,
            'heart_disease': 0.8,
            'kidney_disease': 0.9,
            'respiratory_disease': 0.6,
            'obesity': 0.4
        }
    
    def calculate_vitals_risk(self, vitals_stability_score: float, vitals_trends: Dict) -> Dict:
        """Calculate risk component based on vitals stability and trends."""
        if vitals_stability_score is None:
            vitals_stability_score = 50  # Default if no data
        
        # Base risk from stability score (inverted - lower stability = higher risk)
        base_risk = (100 - vitals_stability_score) * self.risk_weights['vitals_stability']
        
        # Additional risk from concerning trends
        trend_risk = 0
        if vitals_trends and 'trends' in vitals_trends:
            concerning_trends = [t for t in vitals_trends['trends'].values() if t.get('trend_concern', False)]
            trend_risk = len(concerning_trends) * 5  # 5 points per concerning trend
        
        # Additional risk from abnormalities
        abnormality_risk = 0
        if vitals_trends and 'abnormalities' in vitals_trends:
            abnormal_vitals = [v for v in vitals_trends['abnormalities'].values() if v.get('is_abnormal', False)]
            abnormality_risk = len(abnormal_vitals) * 8  # 8 points per abnormal vital
        
        total_vitals_risk = base_risk + trend_risk + abnormality_risk
        total_vitals_risk = min(100, total_vitals_risk)  # Cap at 100
        
        return {
            'risk_score': round(total_vitals_risk, 1),
            'base_stability_risk': round(base_risk, 1),
            'trend_risk': round(trend_risk, 1),
            'abnormality_risk': round(abnormality_risk, 1),
            'weight_used': self.risk_weights['vitals_stability'],
            'contributing_factors': self._get_vitals_risk_factors(vitals_trends)
        }
    
    def calculate_chronic_conditions_risk(self, patient_data: Dict) -> Dict:
        """Calculate risk component based on chronic conditions."""
        chronic_conditions = patient_data.get('chronic_conditions', {})
        age = patient_data.get('age', 50)
        
        # Base risk from chronic conditions
        condition_risk = 0
        condition_details = []
        
        for condition, severity in chronic_conditions.items():
            if isinstance(severity, bool):
                severity = 1 if severity else 0
            
            condition_severity = self.chronic_condition_severity.get(condition.lower(), 0.3)
            condition_risk += condition_severity * severity * 20  # Scale to 0-20 per condition
            
            condition_details.append({
                'condition': condition,
                'severity': severity,
                'risk_contribution': round(condition_severity * severity * 20, 1)
            })
        
        # Age-related risk
        age_risk = 0
        if age >= 80:
            age_risk = 15
        elif age >= 70:
            age_risk = 10
        elif age >= 60:
            age_risk = 5
        elif age < 18:
            age_risk = 8
        
        total_chronic_risk = (condition_risk * self.risk_weights['chronic_conditions'] + 
                             age_risk * self.risk_weights['age_risk'])
        
        return {
            'risk_score': round(total_chronic_risk, 1),
            'condition_risk': round(condition_risk * self.risk_weights['chronic_conditions'], 1),
            'age_risk': round(age_risk * self.risk_weights['age_risk'], 1),
            'conditions': condition_details,
            'age': age,
            'weight_used': self.risk_weights['chronic_conditions'] + self.risk_weights['age_risk']
        }
    
    def calculate_adherence_risk(self, adherence_score: Dict) -> Dict:
        """Calculate risk component based on adherence score."""
        if not adherence_score or 'overall_score' not in adherence_score:
            # Default risk if no adherence data
            return {
                'risk_score': 35.0,  # Medium risk
                'adherence_score': 50,
                'weight_used': self.risk_weights['adherence_score'],
                'risk_level': 'medium'
            }
        
        overall_score = adherence_score['overall_score']
        adherence_level = adherence_score.get('adherence_level', 'Fair')
        
        # Risk is inverse of adherence (lower adherence = higher risk)
        adherence_risk = (100 - overall_score) * self.risk_weights['adherence_score']
        
        # Additional risk for critical adherence levels
        if adherence_level == 'Critical':
            adherence_risk += 10
        elif adherence_level == 'Poor':
            adherence_risk += 5
        
        adherence_risk = min(100, adherence_risk)
        
        return {
            'risk_score': round(adherence_risk, 1),
            'adherence_score': overall_score,
            'adherence_level': adherence_level,
            'weight_used': self.risk_weights['adherence_score'],
            'component_scores': adherence_score.get('component_scores', {})
        }
    
    def calculate_no_show_risk(self, no_show_prediction: Dict) -> Dict:
        """Calculate risk component based on no-show probability."""
        if not no_show_prediction or 'no_show_probability' not in no_show_prediction:
            # Default risk if no prediction data
            return {
                'risk_score': 20.0,  # Low-medium risk
                'no_show_probability': 0.2,
                'weight_used': self.risk_weights['no_show_risk'],
                'risk_category': 'Low'
            }
        
        no_show_prob = no_show_prediction['no_show_probability']
        risk_category = no_show_prediction.get('risk_category', 'Low')
        
        # Direct mapping of no-show probability to risk
        no_show_risk = no_show_prob * 100 * self.risk_weights['no_show_risk']
        
        return {
            'risk_score': round(no_show_risk, 1),
            'no_show_probability': no_show_prob,
            'risk_category': risk_category,
            'weight_used': self.risk_weights['no_show_risk'],
            'contributing_factors': no_show_prediction.get('contributing_factors', [])
        }
    
    def calculate_overall_risk_score(self, patient_id: str, patient_data: Dict, 
                                   vitals_service=None, adherence_service=None, 
                                   no_show_service=None) -> Dict:
        """Calculate comprehensive deterioration risk score."""
        
        # Get component data
        vitals_stability = None
        vitals_trends = None
        if vitals_service:
            try:
                vitals_stability = vitals_service.generate_stability_indicators(patient_id)
                vitals_trends = vitals_service.detect_abnormal_trends(patient_id)
            except:
                pass
        
        adherence_score = None
        if adherence_service:
            try:
                adherence_score = adherence_service.compute_adherence_score(patient_id)
            except:
                pass
        
        no_show_prediction = None
        if no_show_service:
            try:
                # Create basic patient data for no-show prediction
                basic_patient_data = {
                    'patient_id': patient_id,
                    'Age': patient_data.get('age', 50),
                    'Gender': patient_data.get('gender', 'F'),
                    'waiting_days': patient_data.get('waiting_days', 3),
                    'SMS_received': patient_data.get('sms_received', 1),
                    'Scholarship': patient_data.get('scholarship', 0),
                    'Hipertension': patient_data.get('hypertension', 0),
                    'Diabetes': patient_data.get('diabetes', 0),
                    'Alcoholism': patient_data.get('alcoholism', 0),
                    'Handcap': patient_data.get('handcap', 0)
                }
                no_show_prediction = no_show_service.predict_no_show(basic_patient_data)
            except:
                pass
        
        # Calculate component risks
        vitals_risk = self.calculate_vitals_risk(
            vitals_stability.get('stability_score') if vitals_stability else None,
            vitals_trends
        )
        
        chronic_risk = self.calculate_chronic_conditions_risk(patient_data)
        
        adherence_risk = self.calculate_adherence_risk(adherence_score)
        
        no_show_risk = self.calculate_no_show_risk(no_show_prediction)
        
        # Calculate overall risk score
        overall_risk = (
            vitals_risk['risk_score'] +
            chronic_risk['risk_score'] +
            adherence_risk['risk_score'] +
            no_show_risk['risk_score']
        )
        
        # Determine risk category
        if overall_risk >= self.risk_thresholds['high'][0]:
            risk_category = "High"
            color = "red"
            urgency = "immediate"
        elif overall_risk >= self.risk_thresholds['medium'][0]:
            risk_category = "Medium"
            color = "yellow"
            urgency = "soon"
        else:
            risk_category = "Low"
            color = "green"
            urgency = "routine"
        
        # Generate risk drivers explanation
        risk_drivers = self._generate_risk_drivers(
            vitals_risk, chronic_risk, adherence_risk, no_show_risk
        )
        
        # Generate recommendations
        recommendations = self._generate_risk_recommendations(
            risk_category, vitals_risk, chronic_risk, adherence_risk, no_show_risk
        )
        
        return {
            'patient_id': patient_id,
            'overall_risk_score': round(overall_risk, 1),
            'risk_category': risk_category,
            'color_indicator': color,
            'urgency_level': urgency,
            'component_risks': {
                'vitals_stability': vitals_risk,
                'chronic_conditions': chronic_risk,
                'adherence': adherence_risk,
                'no_show_prediction': no_show_risk
            },
            'risk_drivers': risk_drivers,
            'recommendations': recommendations,
            'assessment_timestamp': datetime.now().isoformat(),
            'next_assessment_recommended': self._get_next_assessment_timing(risk_category)
        }
    
    def _get_vitals_risk_factors(self, vitals_trends: Dict) -> List[str]:
        """Extract specific vitals risk factors."""
        factors = []
        
        if not vitals_trends:
            return ["No vitals data available"]
        
        if 'trends' in vitals_trends:
            for vital, trend in vitals_trends['trends'].items():
                if trend.get('trend_concern', False):
                    direction = trend.get('direction', 'changing')
                    factors.append(f"Concerning {vital.replace('_', ' ')} trend ({direction})")
        
        if 'abnormalities' in vitals_trends:
            for vital, abnormality in vitals_trends['abnormalities'].items():
                if abnormality.get('is_abnormal', False):
                    factors.append(f"Consistently abnormal {vital.replace('_', ' ')}")
        
        return factors[:5]  # Return top 5 factors
    
    def _generate_risk_drivers(self, vitals_risk: Dict, chronic_risk: Dict, 
                              adherence_risk: Dict, no_show_risk: Dict) -> List[Dict]:
        """Generate ordered list of risk drivers with their contributions."""
        drivers = []
        
        # Add vitals drivers
        if vitals_risk['risk_score'] > 20:
            drivers.append({
                'category': 'Vitals Stability',
                'contribution': vitals_risk['risk_score'],
                'description': f"Vital signs instability (score: {vitals_risk['risk_score']})",
                'factors': vitals_risk.get('contributing_factors', [])
            })
        
        # Add chronic conditions drivers
        if chronic_risk['risk_score'] > 15:
            drivers.append({
                'category': 'Chronic Conditions',
                'contribution': chronic_risk['risk_score'],
                'description': f"Chronic health conditions (score: {chronic_risk['risk_score']})",
                'factors': [f"{cond['condition']}: {cond['risk_contribution']}" 
                           for cond in chronic_risk.get('conditions', [])]
            })
        
        # Add adherence drivers
        if adherence_risk['risk_score'] > 15:
            drivers.append({
                'category': 'Adherence',
                'contribution': adherence_risk['risk_score'],
                'description': f"Poor treatment adherence (score: {adherence_risk['risk_score']})",
                'factors': [f"Overall adherence: {adherence_risk.get('adherence_score', 'N/A')}%"]
            })
        
        # Add no-show drivers
        if no_show_risk['risk_score'] > 10:
            drivers.append({
                'category': 'Appointment Attendance',
                'contribution': no_show_risk['risk_score'],
                'description': f"High no-show probability (score: {no_show_risk['risk_score']})",
                'factors': [f"No-show probability: {no_show_risk.get('no_show_probability', 'N/A')}%"]
            })
        
        # Sort by contribution
        drivers.sort(key=lambda x: x['contribution'], reverse=True)
        
        return drivers
    
    def _generate_risk_recommendations(self, risk_category: str, vitals_risk: Dict, 
                                      chronic_risk: Dict, adherence_risk: Dict, 
                                      no_show_risk: Dict) -> List[str]:
        """Generate recommendations based on risk assessment."""
        recommendations = []
        
        # Risk category specific recommendations
        if risk_category == "High":
            recommendations.append("Immediate clinical review required")
            recommendations.append("Consider hospital admission for close monitoring")
            recommendations.append("Implement intensive case management")
        elif risk_category == "Medium":
            recommendations.append("Schedule follow-up within 48 hours")
            recommendations.append("Increase monitoring frequency")
            recommendations.append("Consider home health visit")
        else:
            recommendations.append("Continue routine monitoring")
            recommendations.append("Maintain current care plan")
        
        # Component-specific recommendations
        if vitals_risk['risk_score'] > 30:
            recommendations.append("Address vital signs abnormalities immediately")
            recommendations.append("Review and adjust medications")
        
        if chronic_risk['risk_score'] > 25:
            recommendations.append("Optimize chronic disease management")
            recommendations.append("Consider specialist consultation")
        
        if adherence_risk['risk_score'] > 20:
            recommendations.append("Implement adherence improvement strategies")
            recommendations.append("Address barriers to care")
        
        if no_show_risk['risk_score'] > 15:
            recommendations.append("Implement appointment reminder system")
            recommendations.append("Consider telehealth options")
        
        return recommendations[:8]  # Return top 8 recommendations
    
    def _get_next_assessment_timing(self, risk_category: str) -> str:
        """Determine when next risk assessment should be performed."""
        if risk_category == "High":
            return "Every 4 hours"
        elif risk_category == "Medium":
            return "Every 12 hours"
        else:
            return "Every 24 hours"
    
    def get_population_risk_overview(self, patient_risk_scores: List[Dict]) -> Dict:
        """Get overview of risk distribution across patient population."""
        if not patient_risk_scores:
            return {'error': 'No patient risk data available'}
        
        risk_scores = [p['overall_risk_score'] for p in patient_risk_scores]
        risk_categories = [p['risk_category'] for p in patient_risk_scores]
        
        category_counts = pd.Series(risk_categories).value_counts().to_dict()
        
        # Identify high-risk patients
        high_risk_patients = [p for p in patient_risk_scores if p['risk_category'] == 'High']
        
        return {
            'total_patients': len(patient_risk_scores),
            'average_risk_score': np.mean(risk_scores),
            'risk_distribution': category_counts,
            'high_risk_count': len(high_risk_patients),
            'high_risk_percentage': (len(high_risk_patients) / len(patient_risk_scores)) * 100,
            'highest_risk_patient': max(patient_risk_scores, key=lambda x: x['overall_risk_score']) if patient_risk_scores else None,
            'assessment_timestamp': datetime.now().isoformat()
        }
    
    def track_risk_trends(self, patient_id: str, historical_assessments: List[Dict]) -> Dict:
        """Track risk trends for a specific patient over time."""
        if len(historical_assessments) < 2:
            return {'error': 'Insufficient historical data for trend analysis'}
        
        # Sort by timestamp
        assessments = sorted(historical_assessments, key=lambda x: x.get('assessment_timestamp', ''))
        
        scores = [a['overall_risk_score'] for a in assessments]
        timestamps = [a.get('assessment_timestamp') for a in assessments]
        
        # Calculate trend
        recent_scores = scores[-3:]  # Last 3 assessments
        earlier_scores = scores[-6:-3] if len(scores) >= 6 else scores[:-3]
        
        trend_direction = "stable"
        if len(recent_scores) > 0 and len(earlier_scores) > 0:
            recent_avg = np.mean(recent_scores)
            earlier_avg = np.mean(earlier_scores)
            if recent_avg > earlier_avg + 5:
                trend_direction = "worsening"
            elif recent_avg < earlier_avg - 5:
                trend_direction = "improving"
        
        # Calculate rate of change
        if len(scores) >= 2:
            rate_of_change = (scores[-1] - scores[0]) / len(scores)
        else:
            rate_of_change = 0
        
        return {
            'patient_id': patient_id,
            'current_score': scores[-1],
            'trend_direction': trend_direction,
            'rate_of_change': round(rate_of_change, 2),
            'peak_score': max(scores),
            'lowest_score': min(scores),
            'score_volatility': round(np.std(scores), 2),
            'assessment_count': len(assessments),
            'last_assessment': timestamps[-1],
            'trend_analysis_period': f"{len(assessments)} assessments"
        }
