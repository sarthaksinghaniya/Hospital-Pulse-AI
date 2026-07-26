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
from xgboost import XGBClassifier
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
            
            # Train XGBoost model
            self.model = XGBClassifier(
                n_estimators=150,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=(len(y_train) - sum(y_train)) / sum(y_train) if sum(y_train) > 0 else 1,
                random_state=42,
                eval_metric='logloss'
            )
            
            self.model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            auc_score = roc_auc_score(y_test, y_pred_proba)
            
            # Feature importance extraction and normalization
            feature_importance_dict = dict(zip(X.columns, self.model.feature_importances_))
            
            # Normalize feature importance to sum to 1
            importances = np.array(list(feature_importance_dict.values()))
            if np.sum(importances) > 0:
                normalized_importances = importances / np.sum(importances)
                feature_importance_dict = dict(zip(feature_importance_dict.keys(), normalized_importances))
            
            # Sort by importance (descending)
            sorted_importance = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)
            self.feature_importance = dict(sorted_importance)
            
            # Debug logging
            print(f"DEBUG: Feature importance extracted: {self.feature_importance}")
            print(f"DEBUG: Top 3 features: {list(self.feature_importance.keys())[:3]}")
            print(f"DEBUG: Sum of importance: {np.sum(list(self.feature_importance.values()))}")
            
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
        # Auto-train model if not trained
        if not self.model_trained:
            print("DEBUG: Model not trained, auto-training...")
            train_result = self.train_model()
            if train_result['status'] != 'success':
                return {
                    'error': f'Model training failed: {train_result.get("message", "Unknown error")}'
                }
        
        try:
            print(f"DEBUG: Making prediction for patient: {patient_data.get('patient_id', 'Unknown')}")
            
            # Convert patient data to DataFrame
            df = pd.DataFrame([patient_data])
            
            # Preprocess the data
            df_processed = self._preprocess_patient_data(df)
            print(f"DEBUG: Processed data shape: {df_processed.shape}")
            
            # Prepare features
            X = self.prepare_features(df_processed, fit_encoders=False)
            print(f"DEBUG: Feature matrix shape: {X.shape}")
            print(f"DEBUG: Feature columns: {list(X.columns)}")
            
            # Make prediction
            prediction_proba = self.model.predict_proba(X)[0]
            no_show_prob = prediction_proba[1]  # Probability of class 1 (no-show)
            
            print(f"DEBUG: Prediction probabilities: {prediction_proba}")
            print(f"DEBUG: No-show probability: {no_show_prob}")
            
            # Convert to percentage
            no_show_percentage = round(no_show_prob * 100, 2)
            
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
            print(f"DEBUG: Contributing factors: {contributing_factors}")
            
            # Generate recommendations
            recommendations = self._generate_no_show_recommendations(no_show_prob, contributing_factors)
            print(f"DEBUG: Recommendations: {recommendations}")
            
            # Prepare feature importance for display
            feature_importance_display = {}
            if self.feature_importance:
                # Convert to percentage and round
                for feature, importance in self.feature_importance.items():
                    feature_importance_display[feature] = round(importance * 100, 2)
            
            print(f"DEBUG: Feature importance for display: {feature_importance_display}")
            
            result = {
                'patient_id': patient_data.get('patient_id', 'Unknown'),
                'probability': no_show_percentage,
                'risk_level': risk_category,
                'risk_category': risk_category,
                'color_indicator': color,
                'confidence': round(max(prediction_proba) * 100, 2),
                'contributing_factors': contributing_factors,
                'recommendations': recommendations,
                'feature_importance': feature_importance_display,
                'predicted_at': datetime.now().isoformat()
            }
            
            print(f"DEBUG: Final prediction result: {result}")
            return result
            
        except Exception as e:
            print(f"DEBUG: Prediction error: {e}")
            import traceback
            traceback.print_exc()
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
        
        # Add missing Neighbourhood column with default value
        if 'Neighbourhood' not in df_processed.columns:
            df_processed['Neighbourhood'] = 'UNKNOWN'  # Default neighborhood
        
        # Ensure binary columns are properly formatted
        binary_cols = ['Scholarship', 'Hipertension', 'Diabetes', 'Alcoholism', 'Handcap', 'SMS_received']
        for col in binary_cols:
            if col in df_processed.columns:
                df_processed[col] = df_processed[col].astype(int)
        
        print(f"DEBUG: Preprocessed patient data columns: {list(df_processed.columns)}")
        return df_processed
    
    def _get_contributing_factors(self, patient_data: pd.Series) -> List[Dict]:
        """Get top contributing factors for the prediction."""
        contributing_factors = []
        
        print(f"DEBUG: Analyzing contributing factors for patient data: {patient_data.to_dict()}")
        print(f"DEBUG: Available feature importance: {self.feature_importance}")
        
        # Map features to human-readable factors
        factor_mapping = {
            'waiting_days': ('Long Wait Time', lambda x: x > 7),
            'SMS_received': ('No SMS Reminder', lambda x: x == 0),
            'age': ('Younger Age', lambda x: x < 30),
            'Scholarship': ('No Scholarship', lambda x: x == 0),
            'Hipertension': ('Hypertension', lambda x: x == 1),
            'Diabetes': ('Diabetes', lambda x: x == 1),
            'Alcoholism': ('Alcoholism', lambda x: x == 1),
            'Handcap': ('Handicap', lambda x: x > 0),
            'scheduled_hour': ('Late Hour', lambda x: x >= 16),
            'Gender_encoded': ('Gender Factor', lambda x: x in [0, 1])  # Always include gender
        }
        
        for feature, (description, condition) in factor_mapping.items():
            if feature in patient_data:
                try:
                    value = patient_data[feature]
                    if condition(value):
                        importance = self.feature_importance.get(feature, 0.05)  # Default 5% if not found
                        contributing_factors.append({
                            'factor': description,
                            'importance': round(importance * 100, 2),  # Convert to percentage
                            'value': value,
                            'feature_name': feature
                        })
                        print(f"DEBUG: Added factor: {description}, importance: {importance}, value: {value}")
                except Exception as e:
                    print(f"DEBUG: Error processing factor {feature}: {e}")
                    continue
        
        # If no factors found, add default factors based on top features
        if not contributing_factors and self.feature_importance:
            print("DEBUG: No specific factors found, using top features")
            top_features = list(self.feature_importance.keys())[:3]
            for feature in top_features:
                if feature in patient_data:
                    importance = self.feature_importance[feature]
                    value = patient_data[feature]
                    
                    # Create description based on feature name
                    description_map = {
                        'waiting_days': f'Wait Time: {value} days',
                        'age': f'Age: {value} years',
                        'SMS_received': f'SMS: {"Yes" if value else "No"}',
                        'Gender_encoded': f'Gender: {"Female" if value == 0 else "Male"}',
                        'Scholarship': f'Scholarship: {"Yes" if value else "No"}',
                        'Hipertension': f'Hypertension: {"Yes" if value else "No"}',
                        'Diabetes': f'Diabetes: {"Yes" if value else "No"}',
                        'Alcoholism': f'Alcoholism: {"Yes" if value else "No"}',
                        'Handcap': f'Handicap: {"Yes" if value > 0 else "No"}',
                        'scheduled_hour': f'Scheduled Hour: {value}:00'
                    }
                    
                    description = description_map.get(feature, f'{feature}: {value}')
                    
                    contributing_factors.append({
                        'factor': description,
                        'importance': round(importance * 100, 2),
                        'value': value,
                        'feature_name': feature
                    })
        
        # Sort by importance and return top 5
        contributing_factors.sort(key=lambda x: x['importance'], reverse=True)
        result = contributing_factors[:5]
        print(f"DEBUG: Final contributing factors: {result}")
        return result
    
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
            
            # Save feature importance separately
            joblib.dump(self.feature_importance, model_path / "feature_importance.pkl")
            
            self.last_trained = datetime.now().isoformat()
            
            print(f"DEBUG: Model and feature importance saved successfully")
            
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
                print(f"DEBUG: Feature importance loaded: {len(self.feature_importance)} features")
                print(f"DEBUG: Top 3 loaded features: {list(self.feature_importance.keys())[:3]}")
            else:
                print("DEBUG: No feature importance file found, will be empty")
                self.feature_importance = {}
            
            self.model_trained = True
            
            return {
                'status': 'success',
                'message': 'Model loaded successfully'
            }
            
        except Exception as e:
            print(f"DEBUG: Model loading failed: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to load model: {str(e)}'
            }
