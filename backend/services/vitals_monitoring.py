"""
Remote Vitals Monitoring Service

This service handles time-series vitals monitoring for patients, including:
- Ingestion of vitals data from synthetic sources
- Detection of abnormal trends and missing readings
- Generation of vitals stability indicators
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class VitalsMonitoringService:
    """Service for monitoring patient vitals and detecting abnormalities."""
    
    def __init__(self):
        self.vitals_data = {}
        self.normal_ranges = {
            'heart_rate': (60, 100),
            'blood_pressure_systolic': (90, 140),
            'blood_pressure_diastolic': (60, 90),
            'temperature': (36.1, 37.2),
            'oxygen_saturation': (95, 100),
            'respiratory_rate': (12, 20),
            'blood_glucose': (70, 140)
        }
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to Python native types for JSON serialization."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj
        
    def generate_synthetic_vitals(self, num_patients: int = 50, days: int = 7) -> None:
        """Generate synthetic patient vitals data for testing."""
        np.random.seed(42)
        
        vitals_records = []
        base_time = datetime.now() - timedelta(days=days)
        
        for patient_id in range(1, num_patients + 1):
            # Generate baseline vitals for each patient
            baseline_hr = np.random.normal(75, 8)
            baseline_sbp = np.random.normal(120, 10)
            baseline_dbp = np.random.normal(80, 6)
            baseline_temp = np.random.normal(36.8, 0.3)
            baseline_spo2 = np.random.normal(98, 1)
            baseline_rr = np.random.normal(16, 2)
            baseline_glucose = np.random.normal(100, 15)
            
            for day in range(days):
                for hour in range(0, 24, 4):  # Every 4 hours
                    timestamp = base_time + timedelta(days=day, hours=hour)
                    
                    # Add some variation and potential abnormalities
                    hr = max(40, min(180, baseline_hr + np.random.normal(0, 5)))
                    sbp = max(80, min(200, baseline_sbp + np.random.normal(0, 8)))
                    dbp = max(40, min(120, baseline_dbp + np.random.normal(0, 5)))
                    temp = max(35, min(40, baseline_temp + np.random.normal(0, 0.2)))
                    spo2 = max(85, min(100, baseline_spo2 + np.random.normal(0, 1)))
                    rr = max(8, min(30, baseline_rr + np.random.normal(0, 1)))
                    glucose = max(50, min(300, baseline_glucose + np.random.normal(0, 10)))
                    
                    # Simulate occasional missing readings (10% chance)
                    if np.random.random() < 0.1:
                        hr = np.nan
                    
                    vitals_records.append({
                        'patient_id': f'P{patient_id:04d}',
                        'timestamp': timestamp,
                        'heart_rate': hr,
                        'blood_pressure_systolic': sbp,
                        'blood_pressure_diastolic': dbp,
                        'temperature': temp,
                        'oxygen_saturation': spo2,
                        'respiratory_rate': rr,
                        'blood_glucose': glucose
                    })
        
        df = pd.DataFrame(vitals_records)
        self.vitals_data = df
        
    def load_vitals_data(self, file_path: str) -> None:
        """Load vitals data from CSV file."""
        try:
            df = pd.read_csv(file_path)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            self.vitals_data = df
        except Exception as e:
            print(f"Error loading vitals data: {e}")
            self.generate_synthetic_vitals()
    
    def detect_abnormal_trends(self, patient_id: str, hours_back: int = 24) -> Dict:
        """Detect abnormal trends in patient vitals over specified time period."""
        if self.vitals_data.empty:
            return {"error": "No vitals data available"}
        
        patient_data = self.vitals_data[self.vitals_data['patient_id'] == patient_id].copy()
        if patient_data.empty:
            return {"error": f"No data found for patient {patient_id}"}
        
        # Filter data for specified time period
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        patient_data = patient_data[patient_data['timestamp'] >= cutoff_time]
        
        if patient_data.empty:
            return {"error": f"No recent data found for patient {patient_id}"}
        
        abnormalities = {}
        trends = {}
        
        for vital in ['heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                     'temperature', 'oxygen_saturation', 'respiratory_rate', 'blood_glucose']:
            if vital not in patient_data.columns:
                continue
                
            vital_data = patient_data[vital].dropna()
            if len(vital_data) < 3:
                continue
                
            # Check for values outside normal range
            normal_min, normal_max = self.normal_ranges.get(vital, (0, 1000))
            out_of_range = vital_data[(vital_data < normal_min) | (vital_data > normal_max)]
            
            # Calculate trend (slope of last few readings)
            if len(vital_data) >= 3:
                recent_values = vital_data.tail(5).values
                x = np.arange(len(recent_values))
                slope = np.polyfit(x, recent_values, 1)[0]
                
                # Detect concerning trends
                if vital in ['heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'respiratory_rate']:
                    trend_concern = abs(slope) > 2  # Rapid change
                elif vital == 'temperature':
                    trend_concern = slope > 0.1  # Rising temperature
                elif vital == 'oxygen_saturation':
                    trend_concern = slope < -0.5  # Dropping oxygen
                else:
                    trend_concern = abs(slope) > 5
                
                trends[vital] = {
                    'slope': slope,
                    'trend_concern': trend_concern,
                    'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
                }
            
            if len(out_of_range) > 0:
                abnormalities[vital] = {
                    'count_out_of_range': len(out_of_range),
                    'percentage_out_of_range': len(out_of_range) / len(vital_data) * 100,
                    'latest_value': vital_data.iloc[-1],
                    'normal_range': self.normal_ranges.get(vital),
                    'is_abnormal': len(out_of_range) > len(vital_data) * 0.3  # >30% abnormal
                }
        
        return self._convert_numpy_types({
            'patient_id': patient_id,
            'analysis_period_hours': hours_back,
            'total_readings': len(patient_data),
            'abnormalities': abnormalities,
            'trends': trends,
            'last_reading_time': patient_data['timestamp'].max().isoformat() if not patient_data.empty else None
        })
    
    def check_missing_readings(self, patient_id: str, hours_back: int = 24) -> Dict:
        """Check for missing or infrequent readings."""
        if self.vitals_data.empty:
            return {"error": "No vitals data available"}
        
        patient_data = self.vitals_data[self.vitals_data['patient_id'] == patient_id].copy()
        if patient_data.empty:
            return {"error": f"No data found for patient {patient_id}"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        patient_data = patient_data[patient_data['timestamp'] >= cutoff_time].sort_values('timestamp')
        
        if patient_data.empty:
            return {"error": f"No recent data found for patient {patient_id}"}
        
        # Calculate expected vs actual readings
        expected_readings = hours_back // 4  # Assuming readings every 4 hours
        actual_readings = len(patient_data)
        
        # Check for gaps
        if len(patient_data) > 1:
            time_gaps = patient_data['timestamp'].diff().dt.total_seconds() / 3600  # hours
            large_gaps = time_gaps[time_gaps > 6]  # Gaps > 6 hours
        else:
            large_gaps = pd.Series()
        
        missing_data = {}
        for vital in ['heart_rate', 'blood_pressure_systolic', 'temperature', 'oxygen_saturation']:
            if vital in patient_data.columns:
                missing_count = patient_data[vital].isna().sum()
                missing_data[vital] = {
                    'missing_count': missing_count,
                    'missing_percentage': missing_count / len(patient_data) * 100
                }
        
        return self._convert_numpy_types({
            'patient_id': patient_id,
            'analysis_period_hours': hours_back,
            'expected_readings': expected_readings,
            'actual_readings': actual_readings,
            'coverage_percentage': (actual_readings / expected_readings) * 100,
            'large_gaps_count': len(large_gaps),
            'max_gap_hours': large_gaps.max() if len(large_gaps) > 0 else 0,
            'missing_data_by_vital': missing_data,
            'is_concerning': actual_readings < expected_readings * 0.7  # <70% coverage
        })
    
    def generate_stability_indicators(self, patient_id: str, hours_back: int = 24) -> Dict:
        """Generate overall stability indicators for patient vitals."""
        trends = self.detect_abnormal_trends(patient_id, hours_back)
        missing = self.check_missing_readings(patient_id, hours_back)
        
        if "error" in trends or "error" in missing:
            return {"error": "Unable to generate stability indicators"}
        
        # Calculate stability score (0-100, higher is better)
        stability_score = 100
        
        # Deduct points for abnormalities
        abnormal_vitals = len([v for v in trends['abnormalities'].values() if v['is_abnormal']])
        stability_score -= abnormal_vitals * 15
        
        # Deduct points for concerning trends
        concerning_trends = len([v for v in trends['trends'].values() if v['trend_concern']])
        stability_score -= concerning_trends * 10
        
        # Deduct points for missing data
        if missing['is_concerning']:
            stability_score -= 20
        
        stability_score = max(0, min(100, stability_score))
        
        # Determine stability level
        if stability_score >= 80:
            stability_level = "Stable"
            color = "green"
        elif stability_score >= 60:
            stability_level = "Moderately Stable"
            color = "yellow"
        elif stability_score >= 40:
            stability_level = "Unstable"
            color = "orange"
        else:
            stability_level = "Critically Unstable"
            color = "red"
        
        return self._convert_numpy_types({
            'patient_id': patient_id,
            'stability_score': stability_score,
            'stability_level': stability_level,
            'color_indicator': color,
            'abnormal_vitals_count': abnormal_vitals,
            'concerning_trends_count': concerning_trends,
            'data_coverage_percentage': missing['coverage_percentage'],
            'recommendations': self._generate_recommendations(trends, missing, stability_score),
            'last_updated': datetime.now().isoformat()
        })
    
    def _generate_recommendations(self, trends: Dict, missing: Dict, score: int) -> List[str]:
        """Generate clinical recommendations based on vitals analysis."""
        recommendations = []
        
        if score < 40:
            recommendations.append("Immediate clinical review recommended")
        
        if missing['is_concerning']:
            recommendations.append("Address missing vitals readings - check monitoring equipment")
        
        for vital, abnormality in trends['abnormalities'].items():
            if abnormality['is_abnormal']:
                recommendations.append(f"Review {vital.replace('_', ' ')} - consistently out of normal range")
        
        for vital, trend in trends['trends'].items():
            if trend['trend_concern']:
                recommendations.append(f"Monitor {vital.replace('_', ' ')} trend - {trend['direction']} pattern detected")
        
        if not recommendations:
            recommendations.append("Continue routine monitoring")
        
        return recommendations
    
    def get_patient_summary(self, patient_id: str) -> Dict:
        """Get comprehensive summary of patient vitals status."""
        summary = {
            'patient_id': patient_id,
            'trend_analysis': self.detect_abnormal_trends(patient_id),
            'missing_readings': self.check_missing_readings(patient_id),
            'stability_indicators': self.generate_stability_indicators(patient_id)
        }
        return self._convert_numpy_types(summary)
    
    def get_all_patients_overview(self) -> List[Dict]:
        """Get overview of all patients' vitals status."""
        if self.vitals_data.empty:
            return []
        
        patient_ids = self.vitals_data['patient_id'].unique()
        overview = []
        
        for patient_id in patient_ids:
            stability = self.generate_stability_indicators(patient_id)
            if "error" not in stability:
                overview.append({
                    'patient_id': patient_id,
                    'stability_score': stability['stability_score'],
                    'stability_level': stability['stability_level'],
                    'color_indicator': stability['color_indicator'],
                    'last_updated': stability['last_updated']
                })
        
        return self._convert_numpy_types(sorted(overview, key=lambda x: x['stability_score']))
