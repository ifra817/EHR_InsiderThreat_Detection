import os
import random
from datetime import datetime, timedelta

import pandas as pd
import joblib #for models/encoders/scalers
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC #support vector classifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report #evaluate model performance

def simulate_data():
    num_rows = 500
    start_date = datetime(2025, 5, 5, 8, 0)
    routines = ['clinical_orders', 'assessments', 'pharmacy_orders', 'lab_results', 'visit_history']
    data = []

    #for data_frame
    for i in range(num_rows):
        timestamp = start_date + timedelta(minutes=i)
        device_id = random.randint(100, 110)
        user_id = random.randint(1, 50)
        routine = random.choice(routines)
        patient_id = random.randint(1000, 1050)
        duration = random.randint(10, 150)
        data.append((timestamp, device_id, user_id, routine, patient_id, duration)) #passed as tuple

    df = pd.DataFrame(data, columns=['timestamp', 'device_id', 'user_id', 'routine', 'patient_id', 'duration'])

    # Extract time-based features
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['dayofweek'] = df['timestamp'].dt.dayofweek

    # Encode categorical feature
    le = LabelEncoder()
    df['routine_encoded'] = le.fit_transform(df['routine'])
    os.makedirs('models', exist_ok=True)
    joblib.dump(le, 'models/label_encoder.pkl') #saving encoder

    # Prepare features for LOF
    features_for_lof = df[['device_id', 'user_id', 'routine_encoded', 'patient_id', 'duration']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features_for_lof)

    # Apply Local Outlier Factor for labeling
    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
    lof_labels = lof.fit_predict(features_scaled) #-1 for suspicious and 0 for normal
    df['label'] = [1 if label == 1 else 0 for label in lof_labels]  # 1=Normal, 0=Suspicious

    # Save processed dataset
    os.makedirs('data', exist_ok=True)  
    df.to_csv('data/processed_dataset.csv', index=False)
    print("Dataset simulation and preprocessing completed.")

def train_svm_model():
    df = pd.read_csv("data/processed_dataset.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['dayofweek'] = df['timestamp'].dt.dayofweek
    df.drop(columns=['timestamp'], inplace=True)

    features = ['device_id', 'user_id', 'routine_encoded', 'patient_id', 'duration', 'hour', 'dayofweek']

    X = df[features]
    y = df['label']

    print("Label distribution in dataset:\n", y.value_counts())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, 'models/scaler.pkl')

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

    svm_model = SVC(class_weight='balanced', probability=True)
    svm_model.fit(X_train, y_train)

    preds = svm_model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print("Model Accuracy:", acc)
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, preds))
    print("\nClassification Report:")
    print(classification_report(y_test, preds, target_names=['Anomalous (0)', 'Normal (1)']))

    joblib.dump(svm_model, 'models/svm_model.pkl')
    joblib.dump(features, 'models/features.pkl')
    print("Model, encoder, scaler, and feature list saved to 'models/'")

def predict_file(input_csv_path):
    try:
        model = joblib.load('models/svm_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        le = joblib.load('models/label_encoder.pkl')
        print("Loaded model, scaler, and label encoder.")
    except:
        print("One or more model components (model, scaler, encoder) not found.")
        return

    try:
        new_data = pd.read_csv(input_csv_path)
        print(f"\nLoaded input data:\n{new_data.head()}")
        new_data.columns = new_data.columns.str.lower()
        new_data['timestamp'] = pd.to_datetime(new_data['timestamp'])
        new_data['hour'] = new_data['timestamp'].dt.hour
        new_data['dayofweek'] = new_data['timestamp'].dt.dayofweek
        new_data['routine_encoded'] = le.transform(new_data['routine'])

        features = ['device_id', 'user_id', 'routine_encoded', 'patient_id', 'duration', 'hour', 'dayofweek']
        new_data[features] = scaler.transform(new_data[features])
    except Exception as e:
        print(f"Error preprocessing data: {e}")
        return

    try:
        predictions = model.predict(new_data[features])
        print("\nPredictions Summary:")
        print(pd.Series(predictions).value_counts().rename({0: "Anomalous", 1: "Normal"}))
        for i, pred in enumerate(predictions):
            result = "Normal" if pred == 1 else "Suspicious"
            #print(f"Row {i + 1}: {result}")
        return predictions.tolist()
    except Exception as e:
        print(f"Error during prediction: {e}")

def predict_single_record(record_dict):
    try:
        model = joblib.load('models/svm_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        le = joblib.load('models/label_encoder.pkl')
        features = joblib.load('models/features.pkl')
    except Exception as e:
        print(f"Error loading model components: {e}")
        return False

    # Add time-based features
    try:
        timestamp = pd.to_datetime(record_dict['timestamp'])
        record_dict['hour'] = timestamp.hour
        record_dict['dayofweek'] = timestamp.dayofweek
    except Exception as e:
        print(f"Invalid timestamp: {e}")
        return False

    # Validate routine
    if record_dict['routine'] not in le.classes_:
        raise ValueError(f"Routine '{record_dict['routine']}' is not recognized. Valid routines: {list(le.classes_)}")

    # Prepare DataFrame
    df = pd.DataFrame([record_dict])
    df['routine_encoded'] = le.transform(df['routine'])
    
    # Ensure all required features exist
    try:
        X = df[features]
        X_scaled = scaler.transform(X)
    except Exception as e:
        print(f"Feature preprocessing error: {e}")
        return False

    try:
        prediction = model.predict(X_scaled)[0]
        result = "Suspicious" if prediction == 0 else "Normal"
        print(f"Prediction Result: {result}")
        return prediction == 0  #0 if suspicious
    except Exception as e:
        print(f"Prediction failed: {e}")
        return False



if __name__ == "__main__":
    simulate_data()
    train_svm_model()
    input_csv_path = "data/processed_dataset.csv"
    predict_file(input_csv_path)
    
