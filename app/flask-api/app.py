from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

app = Flask(__name__)

# Train and save model if it doesn't exist
def train_model():
    np.random.seed(42)
    n = 500
    attendance = np.random.randint(50, 100, n)
    study_hours = np.random.randint(1, 10, n)
    assignment_scores = np.random.randint(40, 100, n)
    midterm_scores = np.random.randint(40, 100, n)
    performance = ((attendance > 75) & (study_hours > 5) & 
                   (assignment_scores > 60) & (midterm_scores > 60)).astype(int)
    
    X = pd.DataFrame({
        'attendance': attendance,
        'study_hours': study_hours,
        'assignment_scores': assignment_scores,
        'midterm_scores': midterm_scores
    })
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, performance)
    
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    return model

# Load or train model
if os.path.exists('model.pkl'):
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
else:
    model = train_model()

@app.route('/health', methods=['GET'])
def health():
return jsonify({'status': 'healthy', 'service': 'edupredictops', 'version': 'v2'}), 200

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required = ['attendance', 'study_hours', 'assignment_scores', 'midterm_scores']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    X = pd.DataFrame([{
        'attendance': data['attendance'],
        'study_hours': data['study_hours'],
        'assignment_scores': data['assignment_scores'],
        'midterm_scores': data['midterm_scores']
    }])
    
    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0][1]
    
    result = 'Pass' if prediction == 1 else 'Fail'
    return jsonify({
        'prediction': result,
        'confidence': round(float(probability) * 100, 2),
        'inputs': data
    }), 200

@app.route('/students', methods=['GET'])
def get_info():
    return jsonify({
        'service': 'EduPredictOps',
        'version': '1.0',
        'endpoints': ['/health', '/predict', '/students']
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
