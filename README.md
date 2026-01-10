# Problem Statement

Healthcare systems often face sudden Emergency Department surges, ICU bed shortages, and staff overload without adequate early warning. This leads to reactive decision-making, ER crowding, delayed care, and staff burnout. There is a need for an interpretable, proactive decision-support system that can forecast operational stress and recommend preventive actions before overload occurs.

---

# Project Name

**Hospital Pulse AI**

---


**TechNeekX**

**Developer:** Sarthak Singhaniya  
**Portfolio:** https://sarthaksinghaniya.netlify.app

---

# 📂 Project Resources (Google Drive)

All supporting materials related to this project—including PPT, demo video, screenshots, and additional documentation—are available at the link below:

**🔗 Google Drive Folder:**  

https://drive.google.com/drive/folders/11GgfuIbG_-fXJ0N8HJHEx1o7tdpqXqP3?usp=sharing

------

## About the Project

Hospital Pulse AI 

## Key Features

### Hospital Operations Management
* Emergency Department surge forecasting (next 7 days)
* ICU capacity monitoring and peak risk prediction
* Staff workload heatmap with stress scores
* Surge Early-Warning Index (SEWI)
* Actionable alerts and recommendations
* Interpretable, privacy-safe AI
* Hospital-grade interactive dashboard

### Patient Monitoring & Care Management
* **Remote Vitals Monitoring**
  - Time-series vitals ingestion and analysis
  - Abnormal trend detection and missing reading alerts
  - Vitals stability indicators with color-coded risk levels
  - Patient-specific vitals summaries and recommendations

* **Adherence Nudging**
  - Comprehensive adherence scoring (vitals, appointments, medication)
  - Personalized, non-clinical nudge generation
  - Adherence trend tracking and population insights
  - Multi-channel delivery recommendations

* **No-Show Predis an AI-powered hospital operations decision-support platform that forecasts Emergency Department load, ICU demand, and staff workload. It provides early warnings, interpretable risk scores, and actionable recommendations to help hospital administrators prepare in advance and prevent overload situations.

---iction**
  - Machine learning model trained on KaggleV2 dataset
  - Probability-based no-show risk assessment
  - Interpretable feature importance analysis
  - Patient-specific intervention recommendations

* **Patient Deterioration Risk Score**
  - Multi-factor risk assessment (vitals, chronic conditions, adherence)
  - Low/Medium/High risk categorization with explanations
  - Component-wise risk breakdown and driver analysis
  - Trend tracking and early warning capabilities

* **Human Escalation Workflows**
  - Automated escalation triggering based on risk thresholds
  - Multi-level routing (nurse, physician, specialist, emergency)
  - Real-time dashboard with active escalation management
  - Comprehensive logging and reporting capabilities

---

## Tech Stack

* **Backend:** Python, FastAPI, Pandas, NumPy, Scikit-learn
* **Frontend:** React, Vite, Material-UI, Recharts
* **Data:** Synthetic, anonymized operational data + Real healthcare datasets
  - KaggleV2-May-2016.csv (Medical appointment no-show data)
  - diabetic_data.csv (Chronic condition & readmission data)
  - diabetes_prediction_dataset.csv (Baseline medical risk indicators)
  - synthetic_data.csv (Time-series remote vitals monitoring)
  - IDS_mapping.csv (Patient ID unification)

---

## API Endpoints

### Hospital Operations
- `GET /health` - Health check
- `POST /predict/emergency` - Emergency department forecast
- `POST /predict/icu` - ICU capacity prediction
- `POST /predict/staff` - Staff workload prediction
- `GET /alerts` - System alerts
- `GET /recommendations` - AI recommendations

### Patient Monitoring
- `GET /vitals/overview` - Patient vitals overview
- `POST /vitals/patient-summary` - Individual patient vitals summary
- `POST /vitals/trends` - Vitals trend analysis
- `POST /vitals/stability` - Stability indicators
- `GET /adherence/population-overview` - Population adherence metrics
- `POST /adherence/score` - Individual adherence scoring
- `POST /adherence/nudge` - Generate personalized nudges
- `POST /noshow/train` - Train no-show prediction model
- `POST /noshow/predict` - Predict patient no-show probability
- `POST /risk/assess` - Comprehensive patient risk assessment
- `GET /escalation/dashboard` - Active escalations dashboard
- `POST /escalation/check-triggers` - Check and create escalations

---

## Architecture

### Backend Services
- **Vitals Monitoring Service**: Time-series analysis and abnormality detection
- **Adherence Nudging Service**: Scoring algorithms and personalized intervention generation
- **No-Show Prediction Service**: ML model training and inference
- **Deterioration Risk Service**: Multi-factor risk assessment and scoring
- **Escalation Workflows Service**: Automated triggering and routing of clinical escalations

### Frontend Components
- **Dashboard**: Original hospital operations overview
- **Vitals Monitoring**: Real-time patient vitals tracking and analysis
- **Adherence Nudging**: Patient engagement and intervention management
- **No-Show Prediction**: Model insights and patient risk assessment
- **Risk Assessment**: Comprehensive patient deterioration risk scoring
- **Escalation Management**: Clinical workflow and alert management

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker (optional)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker Setup
```bash
docker-compose up
```

---

## Usage

1. **Start the backend server** on `http://localhost:8000`
2. **Start the frontend** on `http://localhost:5173`
3. **Navigate between features** using the tab navigation:
   - Dashboard: Original hospital operations view
   - Vitals Monitoring: Patient vitals analysis
   - Adherence Nudging: Patient engagement tools
   - No-Show Prediction: Appointment risk assessment
   - Risk Assessment: Patient deterioration scoring
   - Escalations: Clinical workflow management

---

## Ethical Considerations

* No patient-level or identifiable data
* Decision support only, not medical advice
* Transparent and interpretable models
* Clinical oversight required for all patient care decisions
- Privacy-preserving data handling
- Fair and unbiased algorithm design

---
