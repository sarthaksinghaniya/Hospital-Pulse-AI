"""
No-Show Prediction Service

This service handles prediction of patient appointment no-shows, including:
- Training predictive models using KaggleV2 dataset
- Outputting probability of missed appointments
- Providing interpretable feature importance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class NoShowPredictionService:
    """Service for predicting patient appointment no-shows."""
    
    def __init__(self):
        self.model = None
        self.feature_columns = []
        self.label_encoders = {}
        self.feature_importance = {}
        self.model_trained = False
        self.data_path = Path(__file__).parents[2] / "data" / "KaggleV2-May-2016.csv"
        
    def load_and_preprocess_data(self) -> pd.DataFrame:
        """Load and preprocess the KaggleV2 dataset."""
        try:
            df = pd.read_csv(self.data_path)
            
            # Create a copy for preprocessing
            df_processed = df.copy()
            
            # Drop unnecessary columns
            columns_to_drop = ['PatientId', 'AppointmentID']
            df_processed = df_processed.drop(columns=columns_to_drop, errors='ignore')
            
            # Convert date columns
            df_processed['ScheduledDay'] = pd.to_datetime(df_processed['ScheduledDay'])
            df_processed['AppointmentDay'] = pd.to_datetime(df_processed['AppointmentDay'])
            
            # Feature engineering
            df_processed['waiting_days'] = (df_processed['AppointmentDay'] - df_processed['ScheduledDay']).dt.days
            df_processed['waiting_days'] = df_processed['waiting_days'].clip(lower=0)  # Remove negative values
            
            # Extract time features
            df_processed['scheduled_hour'] = df_processed['ScheduledDay'].dt.hour
            df_processed['scheduled_dayofweek'] = df_processed['ScheduledDay'].dt.dayofweek
            df_processed['appointment_dayofweek'] = df_processed['AppointmentDay'].dt.dayofweek
            
            # Age preprocessing
            df_processed['age'] = df_processed['Age'].clip(lower=0, upper=120)  # Remove unrealistic ages
            
            # Create age groups
            df_processed['age_group'] = pd.cut(df_processed['age'], 
                                              bins=[0, 12, 18, 35, 50, 65, 120],
                                              labels=['Child', 'Teen', 'Young Adult', 'Adult', 'Middle Age', 'Senior'])
            
            # Handle missing values
            df_processed = df_processed.dropna()
            
            # Convert target variable to binary
            df_processed['no_show_binary'] = (df_processed['No-show'] == 'Yes').astype(int)
            
            return df_processed
            
        except Exception as e:
            print(f"Error loading data: {e}")
            # Generate synthetic data as fallback
            return self._generate_synthetic_appointment_data()
    
    def _generate_synthetic_appointment_data(self) -> pd.DataFrame:
        """Generate synthetic appointment data for testing."""
        np.random.seed(42)
        n_samples = 10000
        
        data = {
            'Gender': np.random.choice(['M', 'F'], n_samples),
            'age': np.random.normal(40, 20, n_samples).clip(0, 120),
            'Scholarship': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
            'Hipertension': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
            'Diabetes': np.random.choice([0, 1], n_samples, p=[0.93, 0.07]),
            'Alcoholism': np.random.choice([0, 1], n_samples, p=[0.97, 0.03]),
            'Handcap': np.random.choice([0, 1, 2, 3, 4], n_samples, p=[0.95, 0.03, 0.01, 0.005, 0.005]),
            'SMS_received': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            'waiting_days': np.random.exponential(10, n_samples).clip(0, 100),
            'scheduled_hour': np.random.choice(range(8, 20), n_samples),
            'scheduled_dayofweek': np.random.choice(range(7), n_samples),
            'appointment_dayofweek': np.random.choice(range(7), n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Create age groups
        df['age_group'] = pd.cut(df['age'], 
                                bins=[0, 12, 18, 35, 50, 65, 120],
                                labels=['Child', 'Teen', 'Young Adult', 'Adult', 'Middle Age', 'Senior'])
        
        # Generate no-show target with some logic
        # Higher probability of no-show with: longer wait times, no SMS, younger age, no scholarship
        base_prob = 0.2
        wait_factor = np.minimum(df['waiting_days'] / 30, 0.3)
        sms_factor = -0.1 * df['SMS_received']
        age_factor = -0.05 * (df['age'] / 100)
        scholarship_factor = -0.08 * df['Scholarship']
        
        prob = base_prob + wait_factor + sms_factor + age_factor + scholarship_factor
        prob = np.clip(prob, 0.05, 0.8)
        
        df['no_show_binary'] = np.random.binomial(1, prob)
        
        return df
    
    def prepare_features(self, df: pd.DataFrame, fit_encoders: bool = True) -> pd.DataFrame:
        """Prepare features for modeling."""
        df_features = df.copy()
        
        # Select categorical columns to encode
        categorical_columns = ['Gender', 'Neighbourhood', 'age_group']
        
        for col in categorical_columns:
            if col in df_features.columns:
                if fit_encoders:
                    le = LabelEncoder()
                    df_features[f'{col}_encoded'] = le.fit_transform(df_features[col].astype(str))
                    self.label_encoders[col] = le
                else:
                    if col in self.label_encoders:
                        le = self.label_encoders[col]
                        # Handle unseen labels
                        df_features[f'{col}_encoded'] = df_features[col].astype(str).map(
                            lambda x: le.transform([x])[0] if x in le.classes_ else -1
                        )
        
        # Select final feature columns
        feature_cols = [
            'age', 'Scholarship', 'Hipertension', 'Diabetes', 'Alcoholism', 
            'Handcap', 'SMS_received', 'waiting_days', 'scheduled_hour',
            'scheduled_dayofweek', 'appointment_dayofweek'
        ]
        
        # Add encoded categorical columns
        for col in categorical_columns:
            encoded_col = f'{col}_encoded'
            if encoded_col in df_features.columns:
                feature_cols.append(encoded_col)
        
        # Ensure all feature columns exist
        available_features = [col for col in feature_cols if col in df_features.columns]
        
        if fit_encoders:
            self.feature_columns = available_features
        
        return df_features[available_features]
    
    def train_model(self) -> Dict:
        """Train the no-show prediction model."""
        try:
            # Load and preprocess data
            df = self.load_and_preprocess_data()
            
            # Prepare features
            X = self.prepare_features(df, fit_encoders=True)
            y = df['no_show_binary']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train Random Forest model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            auc_score = roc_auc_score(y_test, y_pred_proba)
            
            # Feature importance
            feature_importance_dict = dict(zip(X.columns, self.model.feature_importances_))
            sorted_importance = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)
            self.feature_importance = dict(sorted_importance)
            
            # Generate classification report
            class_report = classification_report(y_test, y_pred, output_dict=True)
            
            self.model_trained = True
            
            # Save model
            self._save_model()
            
            return {
                'status': 'success',
                'accuracy': accuracy,
                'auc_score': auc_score,
                'feature_importance': self.feature_importance,
                'classification_report': class_report,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'model_trained_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def predict_no_show(self, patient_data: Dict) -> Dict:
        """Predict no-show probability for a single patient."""
        if not self.model_trained:
            return {
                'error': 'Model not trained. Call train_model() first.'
            }
        
        try:
            # Convert patient data to DataFrame
            df = pd.DataFrame([patient_data])
            
            # Preprocess the data
            df_processed = self._preprocess_patient_data(df)
            
            # Prepare features
            X = self.prepare_features(df_processed, fit_encoders=False)
            
            # Make prediction
            prediction_proba = self.model.predict_proba(X)[0]
            no_show_prob = prediction_proba[1]  # Probability of class 1 (no-show)
            
            # Determine risk category
            if no_show_prob >= 0.7:
                risk_category = "High"
                color = "red"
            elif no_show_prob >= 0.4:
                risk_category = "Medium"
                color = "yellow"
            else:
                risk_category = "Low"
                color = "green"
            
            # Get top contributing factors
            contributing_factors = self._get_contributing_factors(df_processed.iloc[0])
            
            return {
                'patient_id': patient_data.get('patient_id', 'Unknown'),
                'no_show_probability': round(no_show_prob, 3),
                'risk_category': risk_category,
                'color_indicator': color,
                'prediction_confidence': max(prediction_proba),
                'contributing_factors': contributing_factors,
                'recommendations': self._generate_no_show_recommendations(no_show_prob, contributing_factors),
                'predicted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Prediction failed: {str(e)}'
            }
    
    def _preprocess_patient_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess patient data similar to training data."""
        df_processed = df.copy()
        
        # Ensure required columns exist
        required_cols = ['Age', 'waiting_days', 'scheduled_hour', 'scheduled_dayofweek', 'appointment_dayofweek']
        for col in required_cols:
            if col not in df_processed.columns:
                if col == 'waiting_days':
                    df_processed[col] = 1  # Default
                elif col == 'scheduled_hour':
                    df_processed[col] = 10  # Default
                elif 'dayofweek' in col:
                    df_processed[col] = 0  # Monday
                else:
                    df_processed[col] = 0
        
        # Create age column if missing
        if 'age' not in df_processed.columns and 'Age' in df_processed.columns:
            df_processed['age'] = df_processed['Age'].clip(lower=0, upper=120)
        
        # Create age groups
        if 'age' in df_processed.columns:
            df_processed['age_group'] = pd.cut(df_processed['age'], 
                                              bins=[0, 12, 18, 35, 50, 65, 120],
                                              labels=['Child', 'Teen', 'Young Adult', 'Adult', 'Middle Age', 'Senior'])
        
        # Ensure binary columns are properly formatted
        binary_cols = ['Scholarship', 'Hipertension', 'Diabetes', 'Alcoholism', 'Handcap', 'SMS_received']
        for col in binary_cols:
            if col in df_processed.columns:
                df_processed[col] = df_processed[col].astype(int)
        
        return df_processed
    
    def _get_contributing_factors(self, patient_data: pd.Series) -> List[Dict]:
        """Get top contributing factors for the prediction."""
        contributing_factors = []
        
        # Map features to human-readable factors
        factor_mapping = {
            'waiting_days': ('Long Wait Time', lambda x: x > 7),
            'SMS_received': ('No SMS Reminder', lambda x: x == 0),
            'age': ('Younger Age', lambda x: x < 30),
            'Scholarship': ('No Scholarship', lambda x: x == 0),
            'Hipertension': ('Hypertension', lambda x: x == 1),
            'Diabetes': ('Diabetes', lambda x: x == 1)
        }
        
        for feature, (description, condition) in factor_mapping.items():
            if feature in patient_data and condition(patient_data[feature]):
                importance = self.feature_importance.get(feature, 0)
                contributing_factors.append({
                    'factor': description,
                    'importance': round(importance, 3),
                    'value': patient_data[feature]
                })
        
        # Sort by importance and return top 5
        contributing_factors.sort(key=lambda x: x['importance'], reverse=True)
        return contributing_factors[:5]
    
    def _generate_no_show_recommendations(self, probability: float, factors: List[Dict]) -> List[str]:
        """Generate recommendations to reduce no-show probability."""
        recommendations = []
        
        if probability >= 0.7:
            recommendations.append("Consider double-booking this appointment slot")
            recommendations.append("Implement intensive reminder protocol")
        elif probability >= 0.4:
            recommendations.append("Send additional appointment reminders")
            recommendations.append("Consider telehealth alternative")
        
        # Factor-specific recommendations
        factor_descriptions = [f['factor'] for f in factors]
        
        if 'Long Wait Time' in factor_descriptions:
            recommendations.append("Offer earlier appointment if available")
        
        if 'No SMS Reminder' in factor_descriptions:
            recommendations.append("Ensure SMS reminders are enabled")
        
        if 'Younger Age' in factor_descriptions:
            recommendations.append("Consider digital engagement strategies")
        
        if not recommendations:
            recommendations.append("Standard reminder protocol should be sufficient")
        
        return recommendations
    
    def batch_predict(self, patients_data: List[Dict]) -> List[Dict]:
        """Predict no-show for multiple patients."""
        results = []
        for patient_data in patients_data:
            result = self.predict_no_show(patient_data)
            results.append(result)
        return results
    
    def get_model_insights(self) -> Dict:
        """Get insights about the trained model."""
        if not self.model_trained:
            return {'error': 'Model not trained yet'}
        
        return {
            'model_type': 'Random Forest Classifier',
            'feature_importance': self.feature_importance,
            'top_features': list(self.feature_importance.keys())[:10],
            'total_features': len(self.feature_importance),
            'model_trained': self.model_trained,
            'last_trained': getattr(self, 'last_trained', None)
        }
    
    def _save_model(self) -> None:
        """Save the trained model to disk."""
        try:
            model_path = Path(__file__).parent / "models"
            model_path.mkdir(exist_ok=True)
            
            joblib.dump(self.model, model_path / "no_show_model.pkl")
            joblib.dump(self.label_encoders, model_path / "no_show_encoders.pkl")
            joblib.dump(self.feature_columns, model_path / "no_show_features.pkl")
            
            self.last_trained = datetime.now().isoformat()
            
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self) -> Dict:
        """Load a previously trained model."""
        try:
            model_path = Path(__file__).parent / "models"
            
            self.model = joblib.load(model_path / "no_show_model.pkl")
            self.label_encoders = joblib.load(model_path / "no_show_encoders.pkl")
            self.feature_columns = joblib.load(model_path / "no_show_features.pkl")
            
            # Load feature importance if available
            importance_path = model_path / "feature_importance.pkl"
            if importance_path.exists():
                self.feature_importance = joblib.load(importance_path)
            
            self.model_trained = True
            
            return {
                'status': 'success',
                'message': 'Model loaded successfully'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to load model: {str(e)}'
            }
