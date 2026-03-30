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

---

* **data prediction**
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
- `GET /` - Root endpoint with available endpoints list
- `POST /predict/emergency` - Emergency department forecast
- `POST /predict/icu` - ICU capacity prediction  
- `POST /predict/staff` - Staff workload prediction
- `GET /alerts` - System alerts
- `GET /recommendations` - AI recommendations

### Patient Monitoring & Care Management
- `GET /vitals/overview` - Patient vitals overview
- `POST /vitals/patient-summary` - Individual patient vitals summary
- `GET /adherence/population-overview` - Population adherence metrics
- `POST /adherence/score` - Individual adherence scoring
- `POST /noshow/train` - Train no-show prediction model
- `POST /noshow/predict` - Predict patient no-show probability
- `POST /noshow/batch-predict` - Batch predict no-show for multiple patients
- `POST /risk/assess` - Comprehensive patient risk assessment
- `GET /escalation/dashboard` - Active escalations dashboard
- `POST /escalation/check-triggers` - Check and create escalations

### Analytics & Insights
- `GET /feature/surge-early-warning` - Surge Early-Warning Index (SEWI)

---

## Recent Updates & Improvements

### ✅ Latest Features (v2.0)
- **Enhanced No-Show Prediction**: Improved ML model with feature importance analysis
- **Real-time Feature Importance**: Visual chart showing key predictors (waiting_days, age, SMS)
- **Better Error Handling**: Comprehensive frontend error management and connection status
- **Fixed Backend Connection**: Resolved port conflicts and CORS issues
- **Streamlined Interface**: Removed HopX Assistant chatbot for focused healthcare monitoring

### 🔧 Technical Improvements
- **Backend Port**: Standardized on port 8000 for consistency
- **Model Service Auto-Initialization**: Fixed startup issues and test failures
- **Enhanced API Responses**: Better data formatting and error messages
- **Improved Frontend UX**: Connection status indicators and user-friendly error messages

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
# Clone the repository
git clone <repository-url>
cd Hospital-Pulse-AI

# Set up Python environment (recommended)
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
# OR use uvicorn for development:
python -m uvicorn main:app --reload --port 8000
```

**Backend will be available at:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs` (Swagger UI)

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

**Frontend will be available at:** `http://localhost:5173`

### Docker Setup
```bash
# From the root directory
docker-compose up
```

This will start both backend and frontend services simultaneously.

---

## Usage

1. **Start the backend server** on `http://localhost:8000`
2. **Start the frontend** on `http://localhost:5173`
3. **Navigate between features** using the tab navigation:
   - **Dashboard**: Original hospital operations view
   - **Vitals Monitoring**: Patient vitals analysis
   - **Adherence Nudging**: Patient engagement tools
   - **No-Show Prediction**: Appointment risk assessment
   - **Risk Assessment**: Patient deterioration scoring
   - **Escalations**: Clinical workflow management

## Testing

Run the backend test suite:
```bash
cd backend
python -m pytest
```

All tests should pass successfully. The test suite covers:
- API endpoint functionality
- Model service initialization
- Data processing workflows

---

## Troubleshooting

### Common Issues

**1. Backend fails to start with import errors**
```bash
# Ensure you're in the backend directory
cd backend
# Try running from parent directory instead
cd ..
python -m backend.main
```

**2. ModuleNotFoundError: No module named 'backend'**
- This occurs when running from the wrong directory
- Always run backend from either the `backend/` directory or the project root
- The Python path is automatically configured in `main.py`

**3. Tests fail with "ModelService not initialized yet"**
- This was fixed in the latest update
- Ensure you have the latest version of the test configuration
- Run tests with: `python -m pytest --tb=short`

**4. Frontend cannot connect to backend**
- Verify backend is running on port 8000
- Check CORS configuration in `main.py`
- Ensure no firewall is blocking the connection

**5. Port conflicts**
- Backend default port: 8000
- Frontend default port: 5173
- Change ports if needed by modifying startup commands

### Getting Help

1. Check the [API Documentation](http://localhost:8000/docs) when backend is running
2. Review the test files for usage examples
3. Check the `doc/` directory for detailed feature documentation
4. Ensure all dependencies are installed correctly

---

## Ethical Considerations

* No patient-level or identifiable data
* Decision support only, not medical advice
* Transparent and interpretable models
* Clinical oversight required for all patient care decisions
- Privacy-preserving data handling
- Fair and unbiased algorithm design

---
