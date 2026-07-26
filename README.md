# Problem Statement

Healthcare systems often face sudden Emergency Department surges, ICU bed shortages, and staff overload without adequate early warning. This leads to reactive decision-making, ER crowding, delayed care, and staff burnout. There is a need for an interpretable, proactive decision-support system that can forecast operational stress and recommend preventive actions before overload occurs.

---

# Project Name

**Hospital Pulse AI**

---


**TNX Sparks**

## 👥 Team Work Division

|-----------------------------------------------------------|
| TEAM MEMBERS   |   ROLE                                   |
|----------------|------------------------------------------|   
| Sneha Yadav    | project Lead & Fronted Developer         |
|----------------|------------------------------------------|
| Soham Srivastav| Backend,testing & debugging              |
|----------------|------------------------------------------|
| Shweta Devi    |PPT Presentation & Github Version         |
|----------------|------------------------------------------|
| Jahnvi Katiyar |UI/UX Improvements & Readme Documentation |
|----------------|------------------------------------------|

---

# 📂 Project Resources (Google Drive)

All supporting materials related to this project—including PPT, demo video, screenshots, and additional documentation—are available at the link below:

**🔗 Google Drive Folder:**  

https://drive.google.com/drive/folders/11GgfuIbG_-fXJ0N8HJHEx1o7tdpqXqP3?usp=sharing

------

## About the Project

Hospital Pulse AI is an intelligent healthcare decision-support system that provides real-time monitoring, predictive analytics, and actionable insights for hospital operations and patient care management. The system leverages machine learning models to forecast operational stress, predict patient behaviors, and optimize resource allocation.

---

## 🚀 Key Features

### Hospital Operations Management
* **Emergency Department Surge Forecasting** - 7-day advance predictions
* **ICU Capacity Monitoring** - Real-time bed utilization tracking
* **Staff Workload Analysis** - Heatmap with stress scoring
* **Surge Early-Warning Index (SEWI)** - Proactive overload detection
* **Actionable Alerts** - Real-time notifications and recommendations
* **Interactive Dashboard** - Hospital-grade visualization interface

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

* **No-Show Prediction** ✨ **NEW & IMPROVED**
  - **67.86% accuracy** with Random Forest model
  - **Feature importance analysis**: waiting_days (59.8%), age (9.24%), SMS_received (6.4%)
  - **Risk categorization**: Low/Medium/High with probability percentages
  - **Contributing factors**: Top 3 factors with importance scores
  - **Actionable recommendations**: 4-5 personalized interventions
  - **Auto-training**: Model automatically trains if not available

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

## 🛠️ Tech Stack

### Backend
- **Python 3.9+** - Core programming language
- **FastAPI** - Modern, fast web framework for APIs
- **Pandas & NumPy** - Data manipulation and analysis
- **Scikit-learn** - Machine learning models and preprocessing
- **Python-dotenv** - Environment variable management
- **Uvicorn** - ASGI server for FastAPI

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and development server
- **Material-UI (MUI)** - React component library
- **Recharts** - Data visualization library
- **Axios** - HTTP client for API calls

### Data Sources
- **KaggleV2-May-2016.csv** - Medical appointment no-show data (110,527 records)
- **diabetic_data.csv** - Chronic condition and readmission data
- **diabetes_prediction_dataset.csv** - Baseline medical risk indicators
- **synthetic_data.csv** - Time-series remote vitals monitoring data
- **IDS_mapping.csv** - Patient ID unification

---

## 📊 API Endpoints

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

### No-Show Prediction ✨ **ENHANCED**
- `POST /noshow/train` - Train no-show prediction model
- `POST /noshow/predict` - Predict patient no-show probability
- `POST /noshow/batch-predict` - Batch predict no-show for multiple patients
- `GET /noshow/model-insights` - Model performance and feature importance

### Risk Assessment & Escalations
- `POST /risk/assess` - Comprehensive patient risk assessment
- `GET /escalation/dashboard` - Active escalations dashboard
- `POST /escalation/check-triggers` - Check and create escalations

### Analytics & Insights
- `GET /feature/surge-early-warning` - Surge Early-Warning Index (SEWI)

---

## 🆕 Recent Updates & Improvements

### ✅ Latest Features (v2.1)
- **Enhanced No-Show Prediction**: Fixed end-to-end prediction system
  - **67.86% accuracy** with proper probability calculations
  - **Feature importance visualization**: waiting_days (59.8%), age (9.24%), SMS_received (6.4%)
  - **Contributing factors**: Top 3 factors with importance percentages
  - **Actionable recommendations**: 4-5 personalized interventions
  - **Auto-training**: Model automatically trains if not available

### 🔧 Technical Improvements
- **Startup Script Added**: Included a smart proxy `main.py` and `start_backend.bat` script to fix local environment run paths and reliably launch the backend on port 8000.
- **Frontend Bug Fixes**: Fixed JSON parsing issues with nested data objects in React components, allowing predictions and feature importance charts to render flawlessly.
- **Backend Serialization Fixes**: Prevented crashes related to FastAPI JSON encoding by properly casting `numpy.float32` outputs from the ML models to standard Python floats.
- **Production Deployment**: Ready for Render (backend) + Vercel (frontend)
- **CORS Configuration**: Environment-based CORS with debug logging
- **Error Handling**: Comprehensive frontend error management
- **Model Persistence**: Automatic model saving and loading
- **Feature Alignment**: Consistent features between training and prediction

### 📚 Documentation
- **Complete Feature Documentation**: NOSHOW.md with technical details
- **Deployment Guide**: DEPLOYMENT-NO-DOCKER.md for production setup
- **API Reference**: Comprehensive endpoint documentation
- **Architecture Overview**: System design and data flow

### 🚀 Production Ready
- **Backend**: FastAPI with environment-based configuration
- **Frontend**: React with Material-UI and responsive design
- **No Docker**: Clean deployment without containerization
- **CI/CD Ready**: Automatic deployment on git push

---

## 🏗️ Architecture

### Backend Services
- **Vitals Monitoring Service**: Time-series analysis and abnormality detection
- **Adherence Nudging Service**: Scoring algorithms and personalized intervention generation
- **No-Show Prediction Service**: ML model training and inference with feature importance
- **Deterioration Risk Service**: Multi-factor risk assessment and scoring
- **Escalation Workflows Service**: Automated triggering and routing of clinical escalations

### Frontend Components
- **Dashboard**: Original hospital operations overview
- **Vitals Monitoring**: Real-time patient vitals tracking and analysis
- **Adherence Nudging**: Patient engagement and intervention management
- **No-Show Prediction**: Model insights and patient risk assessment with visualizations
- **Risk Assessment**: Comprehensive patient deterioration risk scoring
- **Escalation Management**: Clinical workflow and alert management

---

## 💻 Installation & Setup

### Prerequisites
- **Python 3.8+** - Backend development
- **Node.js 16+** - Frontend development
- **Git** - Version control

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/Hospital-Pulse-AI.git
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
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be available at:** `http://localhost:5173`

---

## 🚀 Production Deployment

### Quick Start (No Docker)
**Backend**: Render.com | **Frontend**: Vercel.com

```bash
# 1. Deploy Backend to Render
# Connect repo to Render.com
# Build: pip install -r requirements.txt
# Start: uvicorn main:app --host 0.0.0.0 --port $PORT

# 2. Deploy Frontend to Vercel
# Connect repo to Vercel.com
# Build: npm run build
# Set VITE_API_BASE=https://your-backend.onrender.com

# 3. Configure CORS
# In Render: CORS_ORIGINS=https://your-app.vercel.app
```

### Deployment Platforms

#### 🖥️ Backend: Render.com
- **Runtime**: Python 3.9+
- **Build**: `pip install -r requirements.txt`
- **Start**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health**: `/health` endpoint included
- **CORS**: Configured for your domain

#### 🌐 Frontend: Vercel.com
- **Framework**: Vite (React)
- **Build**: `npm run build`
- **Output**: `dist/` directory
- **Environment**: `VITE_API_BASE` variable
- **Global CDN**: Automatic

### Environment Configuration

```bash
# Backend (Render)
CORS_ORIGINS=https://your-domain.vercel.app
OPENAI_API_KEY=your-key (optional)
PORT=10000

# Frontend (Vercel)
VITE_API_BASE=https://your-backend.onrender.com
```

### 📋 Production Checklist

- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] CORS origins configured
- [ ] Environment variables set
- [ ] Health checks passing
- [ ] API endpoints tested

**📖 Full Guide**: See [DEPLOYMENT-NO-DOCKER.md](./DEPLOYMENT-NO-DOCKER.md)

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest
```

All tests should pass successfully. The test suite covers:
- API endpoint functionality
- Model service initialization
- Data processing workflows
- No-Show prediction accuracy

### Frontend Tests
```bash
cd frontend
npm run build
```

The build process validates:
- Component compilation
- Environment variable usage
- API endpoint connectivity

---

## 🔍 Troubleshooting

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

**3. No-Show prediction returns 0% probability**
- Model automatically trains if not available
- Check backend logs for training status
- Verify patient data format matches expected schema

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
3. Check the [NOSHOW.md](./NOSHOW.md) for detailed feature documentation
4. Ensure all dependencies are installed correctly

---

## � Documentation

- **[NOSHOW.md](./NOSHOW.md)** - Complete No-Show Prediction feature documentation
- **[DEPLOYMENT-NO-DOCKER.md](./DEPLOYMENT-NO-DOCKER.md)** - Production deployment guide
- **API Documentation** - Interactive API docs at `/docs` endpoint

---

## 🎯 Project Status

### ✅ Completed Features
- **Hospital Operations Management**: Emergency, ICU, and staff forecasting
- **Patient Monitoring**: Vitals, adherence, and risk assessment
- **No-Show Prediction**: ML-powered appointment risk analysis
- **Escalation Workflows**: Automated clinical escalation management
- **Production Deployment**: Render + Vercel deployment ready

### 🚧 Current Version
- **Version**: 2.1
- **Status**: Production Ready
- **Last Updated**: July 26, 2026

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Ethical Considerations

* **No patient-level or identifiable data** - All data is anonymized and synthetic
* **Decision support only, not medical advice** - System provides insights, not diagnoses
* **Transparent and interpretable models** - Feature importance and explanations provided
* **Clinical oversight required** - All patient care decisions require clinical review
* **Privacy-preserving data handling** - No personal health information stored or processed
* **Fair and unbiased algorithm design** - Models trained on diverse datasets

---

**🏥 Hospital Pulse AI - Intelligent Healthcare Decision Support System**

*Empowering healthcare providers with data-driven insights for better patient care and operational efficiency.*
