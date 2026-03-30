# Hospital Pulse AI - API Documentation

## Overview
Hospital Pulse AI provides a comprehensive REST API for hospital operations management and patient monitoring. All endpoints return JSON responses and include proper error handling.

## Base URL
```
http://localhost:8001
```

## Authentication
Currently no authentication is required (development mode).

## Response Format
All responses follow this structure:
```json
{
  "status": "success|error",
  "data": {...},  // for successful responses
  "message": "error description"  // for errors
}
```

## Hospital Operations Endpoints

### Health Check
```http
GET /health
```
Returns server health status.

**Response:**
```json
{
  "status": "ok"
}
```

### Emergency Department Forecast
```http
POST /predict/emergency
```
Forecast Emergency Department demand for the next 7 days.

**Request Body:**
```json
{
  "horizon_hours": 24
}
```

**Response:**
```json
{
  "forecast": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "predicted_admissions": 15,
      "ambulance_arrivals": 3
    }
  ],
  "surge_probability": 0.25,
  "summary": "Low surge risk expected in next 24 hours"
}
```

### ICU Capacity Prediction
```http
POST /predict/icu
```
Predict ICU occupancy and capacity pressure.

**Request Body:**
```json
{
  "horizon_hours": 24
}
```

**Response:**
```json
{
  "required_beds": 35,
  "peak_risk": 0.6,
  "summary": "ICU capacity within safe limits"
}
```

### Staff Workload Prediction
```http
POST /predict/staff
```
Predict staff workload and stress levels.

**Request Body:**
```json
{
  "horizon_hours": 24
}
```

**Response:**
```json
{
  "workload": [
    {
      "shift": "morning",
      "nurse_to_patient_ratio": 1:4,
      "stress_score": 0.3
    }
  ]
}
```

### System Alerts
```http
GET /alerts
```
Get current system alerts and warnings.

**Response:**
```json
{
  "alerts": [
    {
      "severity": "caution",
      "message": "Moderate ER surge expected",
      "time_window": "24-48 hours",
      "recommendation": "Consider additional staffing"
    }
  ]
}
```

### AI Recommendations
```http
GET /recommendations
```
Get AI-generated operational recommendations.

**Response:**
```json
{
  "recommendations": [
    {
      "priority": "high",
      "action": "Pre-position additional staff",
      "reason": "High ER surge probability detected",
      "timeframe": "next 24 hours"
    }
  ]
}
```

## Patient Monitoring Endpoints

### Vitals Overview
```http
GET /vitals/overview
```
Get population-level vitals statistics.

**Response:**
```json
{
  "total_patients": 150,
  "critical_readings": 3,
  "missing_readings": 12,
  "average_stability": 0.85
}
```

### Patient Vitals Summary
```http
POST /vitals/patient-summary
```
Get detailed vitals summary for a specific patient.

**Request Body:**
```json
{
  "patient_id": "P12345",
  "time_range_hours": 24
}
```

**Response:**
```json
{
  "patient_id": "P12345",
  "vitals": {
    "heart_rate": {"avg": 72, "trend": "stable"},
    "blood_pressure": {"avg": "120/80", "trend": "stable"},
    "temperature": {"avg": 98.6, "trend": "stable"}
  },
  "stability_score": 0.9,
  "alerts": []
}
```

### Population Adherence Overview
```http
GET /adherence/population-overview
```
Get adherence metrics across all patients.

**Response:**
```json
{
  "overall_adherence": 0.78,
  "vitals_adherence": 0.85,
  "medication_adherence": 0.72,
  "appointment_adherence": 0.80,
  "high_risk_patients": 15
}
```

### Individual Adherence Score
```http
POST /adherence/score
```
Calculate adherence score for a specific patient.

**Request Body:**
```json
{
  "patient_id": "P12345",
  "include_vitals": true,
  "include_medications": true,
  "include_appointments": true
}
```

**Response:**
```json
{
  "patient_id": "P12345",
  "overall_score": 0.82,
  "components": {
    "vitals": 0.90,
    "medications": 0.75,
    "appointments": 0.85
  },
  "risk_level": "low",
  "recommendations": [
    "Continue current medication schedule",
    "Maintain vitals monitoring routine"
  ]
}
```

## No-Show Prediction Endpoints

### Train No-Show Model
```http
POST /noshow/train
```
Train the no-show prediction model.

**Response:**
```json
{
  "status": "success",
  "model_accuracy": 0.82,
  "feature_importance": {
    "age": 0.25,
    "previous_no_shows": 0.30,
    "appointment_type": 0.15
  }
}
```

### Predict No-Show Probability
```http
POST /noshow/predict
```
Predict no-show probability for a single patient.

**Request Body:**
```json
{
  "patient_id": "P12345",
  "age": 45,
  "gender": "F",
  "appointment_type": "follow_up",
  "days_until_appointment": 3,
  "previous_no_shows": 1
}
```

**Response:**
```json
{
  "patient_id": "P12345",
  "no_show_probability": 0.25,
  "risk_level": "low",
  "key_factors": ["low previous no-show history", "short wait time"],
  "recommendations": [
    "Send reminder 24 hours before appointment",
    "Offer flexible scheduling options"
  ]
}
```

### Batch No-Show Prediction
```http
POST /noshow/batch-predict
```
Predict no-show for multiple patients.

**Request Body:**
```json
{
  "patients": [
    {
      "patient_id": "P12345",
      "age": 45,
      "gender": "F",
      "appointment_type": "follow_up",
      "days_until_appointment": 3,
      "previous_no_shows": 1
    }
  ]
}
```

## Risk Assessment Endpoints

### Patient Deterioration Risk
```http
POST /risk/assess
```
Comprehensive patient deterioration risk assessment.

**Request Body:**
```json
{
  "patient_id": "P12345",
  "age": 65,
  "chronic_conditions": ["diabetes", "hypertension"],
  "vitals": {
    "heart_rate": 85,
    "blood_pressure_systolic": 140,
    "blood_pressure_diastolic": 90,
    "temperature": 98.6,
    "oxygen_saturation": 96
  },
  "adherence_score": 0.75
}
```

**Response:**
```json
{
  "patient_id": "P12345",
  "overall_risk_score": 0.42,
  "risk_level": "medium",
  "components": {
    "vitals_risk": 0.3,
    "chronic_conditions_risk": 0.6,
    "adherence_risk": 0.4
  },
  "key_drivers": ["hypertension", "moderate adherence"],
  "recommendations": [
    "Increase vitals monitoring frequency",
    "Medication adherence intervention",
    "Consider specialist consultation"
  ],
  "escalation_required": false
}
```

## Escalation Management Endpoints

### Escalation Dashboard
```http
GET /escalation/dashboard
```
Get active escalations and their status.

**Response:**
```json
{
  "active_escalations": [
    {
      "escalation_id": "E12345",
      "patient_id": "P12345",
      "severity": "medium",
      "type": "vital_abnormality",
      "status": "pending_review",
      "created_at": "2024-01-01T10:00:00Z",
      "assigned_to": "nurse_team"
    }
  ],
  "total_count": 5,
  "by_severity": {
    "high": 1,
    "medium": 3,
    "low": 1
  }
}
```

### Check Escalation Triggers
```http
POST /escalation/check-triggers
```
Check if escalation conditions are met and create escalations.

**Request Body:**
```json
{
  "patient_id": "P12345",
  "vitals": {
    "heart_rate": 110,
    "blood_pressure_systolic": 160,
    "blood_pressure_diastolic": 100
  },
  "risk_threshold": 0.7
}
```

**Response:**
```json
{
  "escalation_triggered": true,
  "escalation_id": "E12346",
  "severity": "high",
  "reason": "Blood pressure exceeds critical threshold",
  "recommended_action": "Immediate physician review",
  "assigned_to": "physician_team"
}
```

## AI Assistant Endpoints

### HOPX Chat Assistant
```http
POST /feature/hopx-chat
```
Chat with the HOPX AI assistant for operational guidance.

**Request Body:**
```json
{
  "message": "What is our current ICU capacity risk?",
  "context": "dashboard_view"
}
```

**Response:**
```json
{
  "response": "Based on current predictions, your ICU capacity risk is moderate at 0.6. Peak demand is expected in 48 hours with 35 beds required out of 40 available.",
  "sources": ["icu_prediction_model"],
  "confidence": 0.85,
  "follow_up_questions": [
    "What staffing adjustments do you recommend?",
    "What are the key drivers of this risk?"
  ]
}
```

### Surge Early-Warning Index (SEWI)
```http
GET /feature/surge-early-warning
```
Get the composite Surge Early-Warning Index score.

**Response:**
```json
{
  "score": 0.62,
  "risk_level": "medium",
  "surge_probability": 0.55,
  "icu_peak_risk": 0.60,
  "staff_max_risk": 0.50,
  "explanation": "ER surge probability 55%, ICU peak risk 60%, max staff stress 50%. Composite SEWI score 0.62.",
  "actions": [
    "Pre-position one extra staff for evening/night shifts.",
    "Audit ICU bed turnover and prepare rapid discharge protocols."
  ],
  "updated_at": "2024-01-01T12:00:00Z"
}
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "status": "error",
  "message": "Invalid request format: missing required field 'patient_id'"
}
```

**404 Not Found:**
```json
{
  "status": "error", 
  "message": "Patient not found"
}
```

**500 Internal Server Error:**
```json
{
  "status": "error",
  "message": "Model service temporarily unavailable"
}
```

## Rate Limiting
Currently no rate limiting is enforced (development mode).

## Data Models
Detailed data models and schemas are available in the Swagger UI at `/docs`.

## Testing
Use the provided test suite to verify API functionality:
```bash
cd backend
python -m pytest
```

## Support
For API issues, check the troubleshooting section in the main README.md file.
