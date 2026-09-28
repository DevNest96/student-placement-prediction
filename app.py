import os
import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# Load models and metadata
def load_artifacts():
    if not os.path.exists(os.path.join(MODELS_DIR, "scaler.joblib")):
        # Auto-train if models not found
        from model_trainer import train_and_save_models
        train_and_save_models()

    scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.joblib"))
    
    with open(os.path.join(MODELS_DIR, "metadata.json"), "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    models = {
        'Logistic Regression': joblib.load(os.path.join(MODELS_DIR, "logistic_regression.joblib")),
        'Random Forest': joblib.load(os.path.join(MODELS_DIR, "random_forest.joblib")),
        'KNN': joblib.load(os.path.join(MODELS_DIR, "knn.joblib")),
        'Decision Tree': joblib.load(os.path.join(MODELS_DIR, "decision_tree.joblib")),
        'Naive Bayes': joblib.load(os.path.join(MODELS_DIR, "naive_bayes.joblib"))
    }
    
    best_model_name = metadata.get("best_model", "Logistic Regression")
    best_model = models.get(best_model_name, models['Logistic Regression'])
    
    return scaler, models, best_model_name, metadata

scaler, models, best_model_name, metadata = load_artifacts()

def parse_student_input(data):
    """Safely parse and validate input student attributes."""
    cgpa = float(data.get("cgpa", 7.5))
    internships = int(data.get("internships", 1))
    projects = int(data.get("projects", 2))
    workshops = int(data.get("workshops", 1))
    aptitude = float(data.get("aptitude", 75))
    soft_skills = float(data.get("soft_skills", 4.0))
    
    # Categoricals (accepts boolean, int 0/1, or 'yes'/'no')
    extra = data.get("extracurricular", 0)
    if isinstance(extra, str):
        extra = 1 if extra.strip().lower() in ['yes', '1', 'true'] else 0
    else:
        extra = 1 if extra else 0
        
    training = data.get("placement_training", 0)
    if isinstance(training, str):
        training = 1 if training.strip().lower() in ['yes', '1', 'true'] else 0
    else:
        training = 1 if training else 0
        
    ssc = float(data.get("ssc_marks", 70))
    hsc = float(data.get("hsc_marks", 70))
    
    feature_vector = pd.DataFrame([[
        cgpa, internships, projects, workshops, aptitude,
        soft_skills, extra, training, ssc, hsc
    ]], columns=metadata['feature_columns'])
    
    return feature_vector, {
        'CGPA': cgpa,
        'Internships': internships,
        'Projects': projects,
        'Workshops/Certifications': workshops,
        'AptitudeTestScore': aptitude,
        'SoftSkillsRating': soft_skills,
        'ExtracurricularActivities': 'Yes' if extra == 1 else 'No',
        'PlacementTraining': 'Yes' if training == 1 else 'No',
        'SSC_Marks': ssc,
        'HSC_Marks': hsc
    }

@app.route("/")
def index():
    return render_template("index.html", metadata=metadata)

@app.route("/api/metadata", methods=["GET"])
def get_metadata():
    return jsonify(metadata)

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True) if request.is_json else request.form.to_dict()
        feature_vector, clean_input = parse_student_input(data)
        
        # Scale features
        scaled_features = scaler.transform(feature_vector)
        
        # Predictions across all models
        model_results = {}
        placed_votes = 0
        total_models = len(models)
        
        for name, model in models.items():
            pred = int(model.predict(scaled_features)[0])
            if pred == 1:
                placed_votes += 1
                
            prob = None
            if hasattr(model, "predict_proba"):
                prob = round(float(model.predict_proba(scaled_features)[0][1]) * 100, 1)
            else:
                prob = 100.0 if pred == 1 else 0.0
                
            model_results[name] = {
                'prediction': pred,
                'status': 'Placed' if pred == 1 else 'Not Placed',
                'probability': prob,
                'accuracy': metadata['metrics'].get(name, {}).get('accuracy', 0)
            }
            
        champion_result = model_results[best_model_name]
        consensus_rate = round((placed_votes / total_models) * 100, 1)
        
        # Generate actionable advice
        recommendations = []
        if clean_input['CGPA'] < 7.5:
            recommendations.append("Strengthen academic score: aiming for CGPA ≥ 7.5 significantly elevates placement probability.")
        if clean_input['AptitudeTestScore'] < 75:
            recommendations.append("Practice technical aptitude and quantitative problem solving (target score ≥ 80).")
        if clean_input['Projects'] < 2:
            recommendations.append("Build at least 2 hands-on, end-to-end portfolio projects to demonstrate practical domain skills.")
        if clean_input['PlacementTraining'] == 'No':
            recommendations.append("Enroll in formal Placement Training sessions—historical data shows trained candidates have a 3.3x higher placement rate.")
        if clean_input['ExtracurricularActivities'] == 'No':
            recommendations.append("Participate in club leadership, hackathons, or student committees to strengthen soft-skill credentials.")
        if not recommendations:
            recommendations.append("Outstanding profile! Continue sharpening mock interview preparation and company-specific coding rounds.")

        return jsonify({
            'success': True,
            'prediction': champion_result['prediction'],
            'status': champion_result['status'],
            'probability': champion_result['probability'],
            'champion_model': best_model_name,
            'champion_accuracy': metadata['metrics'][best_model_name]['accuracy'],
            'consensus_rate': consensus_rate,
            'all_models': model_results,
            'inputs': clean_input,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
