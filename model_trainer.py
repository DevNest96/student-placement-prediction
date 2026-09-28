import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)

def train_and_save_models(data_path="placementdata.csv", output_dir="models"):
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"[*] Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"    Raw records: {len(df)}")
    
    # Preprocessing
    df = df.fillna(df.mean(numeric_only=True))
    df = df.fillna(df.mode().iloc[0])
    df = df.drop_duplicates()
    
    # Feature columns (excluding StudentID and PlacementStatus)
    feature_columns = [
        'CGPA',
        'Internships',
        'Projects',
        'Workshops/Certifications',
        'AptitudeTestScore',
        'SoftSkillsRating',
        'ExtracurricularActivities',
        'PlacementTraining',
        'SSC_Marks',
        'HSC_Marks'
    ]
    
    # Encode categorical features
    # 'Yes' -> 1, 'No' -> 0
    df['ExtracurricularActivities_Enc'] = df['ExtracurricularActivities'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)
    df['PlacementTraining_Enc'] = df['PlacementTraining'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)
    df['PlacementStatus_Enc'] = df['PlacementStatus'].apply(lambda x: 1 if str(x).strip().lower() == 'placed' else 0)
    
    encoded_feature_cols = [
        'CGPA',
        'Internships',
        'Projects',
        'Workshops/Certifications',
        'AptitudeTestScore',
        'SoftSkillsRating',
        'ExtracurricularActivities_Enc',
        'PlacementTraining_Enc',
        'SSC_Marks',
        'HSC_Marks'
    ]
    
    X = df[encoded_feature_cols]
    Y = df['PlacementStatus_Enc']
    
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, random_state=42, stratify=Y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save scaler and feature names
    joblib.dump(scaler, os.path.join(output_dir, "scaler.joblib"))
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'KNN': KNeighborsClassifier(n_neighbors=5),
        'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
        'Naive Bayes': GaussianNB()
    }
    
    metrics_summary = {}
    saved_models = {}
    
    print("\n[*] Training and evaluating models...")
    for name, model in models.items():
        model.fit(X_train_scaled, Y_train)
        preds = model.predict(X_test_scaled)
        
        # Probabilities
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_test_scaled)[:, 1]
            auc_val = float(roc_auc_score(Y_test, probs))
        else:
            auc_val = 0.0
            
        acc = float(accuracy_score(Y_test, preds))
        prec = float(precision_score(Y_test, preds, zero_division=0))
        rec = float(recall_score(Y_test, preds, zero_division=0))
        f1 = float(f1_score(Y_test, preds, zero_division=0))
        cm = confusion_matrix(Y_test, preds).tolist()
        
        metrics_summary[name] = {
            'accuracy': round(acc * 100, 2),
            'precision': round(prec * 100, 2),
            'recall': round(rec * 100, 2),
            'f1_score': round(f1 * 100, 2),
            'roc_auc': round(auc_val * 100, 2),
            'confusion_matrix': cm
        }
        
        print(f"    - {name:20s} | Acc: {acc*100:6.2f}% | F1: {f1*100:6.2f}% | AUC: {auc_val*100:6.2f}%")
        
        # Save individual model
        filename = f"{name.lower().replace(' ', '_')}.joblib"
        joblib.dump(model, os.path.join(output_dir, filename))
        saved_models[name] = filename
        
    # Best model selection by accuracy then F1
    best_model_name = max(metrics_summary, key=lambda m: (metrics_summary[m]['accuracy'], metrics_summary[m]['f1_score']))
    print(f"\n[+] Champion Model: {best_model_name} ({metrics_summary[best_model_name]['accuracy']}%)")
    
    # Save best model reference
    joblib.dump(models[best_model_name], os.path.join(output_dir, "best_model.joblib"))
    
    # Feature importances / coefficients for best model
    feature_importance = {}
    if hasattr(models[best_model_name], 'coef_'):
        coefs = models[best_model_name].coef_[0]
        for feat, val in zip(encoded_feature_cols, coefs):
            feature_importance[feat] = round(float(val), 4)
    elif hasattr(models[best_model_name], 'feature_importances_'):
        importances = models[best_model_name].feature_importances_
        for feat, val in zip(encoded_feature_cols, importances):
            feature_importance[feat] = round(float(val), 4)
            
    # Dataset statistics
    stats = {
        'total_records': len(df),
        'features': encoded_feature_cols,
        'placed_count': int((df['PlacementStatus_Enc'] == 1).sum()),
        'not_placed_count': int((df['PlacementStatus_Enc'] == 0).sum()),
        'placement_rate': round(float((df['PlacementStatus_Enc'] == 1).mean() * 100), 2),
        'averages': {
            'cgpa': round(float(df['CGPA'].mean()), 2),
            'aptitude': round(float(df['AptitudeTestScore'].mean()), 2),
            'projects': round(float(df['Projects'].mean()), 1),
            'ssc': round(float(df['SSC_Marks'].mean()), 1),
            'hsc': round(float(df['HSC_Marks'].mean()), 1),
            'soft_skills': round(float(df['SoftSkillsRating'].mean()), 2)
        }
    }
    
    metadata = {
        'best_model': best_model_name,
        'metrics': metrics_summary,
        'feature_importance': feature_importance,
        'stats': stats,
        'feature_columns': encoded_feature_cols
    }
    
    with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"[+] All models and metadata saved to '{output_dir}/'")
    return metadata

if __name__ == "__main__":
    train_and_save_models()
