import sys
import argparse
import json
import os
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def run_train():
    from model_trainer import train_and_save_models
    print("\n" + "="*60)
    print("[*] STUDENT PLACEMENT PREDICTION - MODEL TRAINING")
    print("="*60)
    metadata = train_and_save_models()
    print("\n" + "-"*60)
    print("BENCHMARK SUMMARY:")
    print(f"{'Model':<24} | {'Accuracy':<10} | {'F1-Score':<10} | {'ROC-AUC':<10}")
    print("-"*60)
    for model, m in metadata['metrics'].items():
        print(f"{model:<24} | {m['accuracy']:>7.2f}%   | {m['f1_score']:>7.2f}%   | {m['roc_auc']:>7.2f}%")
    print("="*60 + "\n")

def run_predict(cgpa=8.0, aptitude=82, projects=2, internships=1, workshops=1,
                soft_skills=4.5, extra=1, training=1, ssc=75, hsc=78):
    import joblib
    import numpy as np

    models_dir = os.path.join(os.path.dirname(__file__), "models")
    if not os.path.exists(os.path.join(models_dir, "best_model.joblib")):
        print("[!] Models not found. Training now...")
        run_train()

    scaler = joblib.load(os.path.join(models_dir, "scaler.joblib"))
    model = joblib.load(os.path.join(models_dir, "best_model.joblib"))
    
    with open(os.path.join(models_dir, "metadata.json"), "r") as f:
        meta = json.load(f)

    cols = meta['feature_columns']
    features_df = pd.DataFrame([[
        cgpa, internships, projects, workshops, aptitude,
        soft_skills, extra, training, ssc, hsc
    ]], columns=cols)
    scaled = scaler.transform(features_df)
    pred = model.predict(scaled)[0]
    prob = model.predict_proba(scaled)[0][1] * 100 if hasattr(model, "predict_proba") else 0

    print("\n" + "="*50)
    print("[*] PLACEMENT PREDICTION RESULT")
    print("="*50)
    print(f"Model Used        : {meta['best_model']} (Accuracy: {meta['metrics'][meta['best_model']]['accuracy']}%)")
    print(f"Input CGPA        : {cgpa}")
    print(f"Aptitude Score    : {aptitude}")
    print(f"Projects          : {projects}")
    print(f"Internships       : {internships}")
    print(f"Workshops/Certs   : {workshops}")
    print(f"Soft Skills       : {soft_skills} / 5.0")
    print(f"Extracurricular   : {'Yes' if extra else 'No'}")
    print(f"Placement Training: {'Yes' if training else 'No'}")
    print(f"SSC / HSC Marks   : {ssc}% / {hsc}%")
    print("-"*50)
    status_str = "[+] PLACED" if pred == 1 else "[-] NOT PLACED"
    print(f"Predicted Status  : {status_str}")
    print(f"Placement Prob.   : {prob:.1f}%")
    print("="*50 + "\n")

def run_web():
    from app import app
    print("\n" + "="*60)
    print("🚀 STARTING STUDENT PLACEMENT PREDICTION WEB PORTAL")
    print("📍 URL: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False)

def run_notebook():
    import nbformat
    from nbclient import NotebookClient

    nb_file = "AlokGupta_Placement_analysis.ipynb"
    print(f"[*] Executing notebook: {nb_file}...")
    with open(nb_file, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    client = NotebookClient(nb, timeout=600, kernel_name='python3')
    client.execute()

    with open(nb_file, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    print(f"[+] Successfully executed {nb_file} with all outputs preserved.")

def main():
    parser = argparse.ArgumentParser(description="Student Placement Prediction CLI & App")
    parser.add_argument("--train", action="store_true", help="Train and evaluate all machine learning models")
    parser.add_argument("--predict", action="store_true", help="Run a placement prediction on student parameters")
    parser.add_argument("--web", action="store_true", help="Launch the interactive Web Application")
    parser.add_argument("--notebook", action="store_true", help="Run the full Jupyter Notebook end-to-end")
    
    # Feature arguments for --predict
    parser.add_argument("--cgpa", type=float, default=8.0, help="CGPA (0 - 10)")
    parser.add_argument("--aptitude", type=float, default=82.0, help="Aptitude score (0 - 100)")
    parser.add_argument("--projects", type=int, default=2, help="Number of projects")
    parser.add_argument("--internships", type=int, default=1, help="Number of internships")
    parser.add_argument("--workshops", type=int, default=1, help="Workshops/Certifications")
    parser.add_argument("--soft-skills", type=float, default=4.5, help="Soft skills rating (0 - 5)")
    parser.add_argument("--extra", type=int, default=1, help="Extracurricular (1=Yes, 0=No)")
    parser.add_argument("--training", type=int, default=1, help="Placement Training (1=Yes, 0=No)")
    parser.add_argument("--ssc", type=float, default=75.0, help="SSC Marks (%)")
    parser.add_argument("--hsc", type=float, default=78.0, help="HSC Marks (%)")

    args = parser.parse_args()

    if args.train:
        run_train()
    elif args.web:
        run_web()
    elif args.notebook:
        run_notebook()
    elif args.predict:
        run_predict(
            cgpa=args.cgpa,
            aptitude=args.aptitude,
            projects=args.projects,
            internships=args.internships,
            workshops=args.workshops,
            soft_skills=args.soft_skills,
            extra=args.extra,
            training=args.training,
            ssc=args.ssc,
            hsc=args.hsc
        )
    else:
        # Default action: run train summary and show web launch command
        print("\n[*] STUDENT PLACEMENT PREDICTION")
        print("Available modes:")
        print("  python main.py --train     : Train all 5 ML models and print evaluation benchmarks")
        print("  python main.py --predict   : Run CLI placement prediction")
        print("  python main.py --web       : Launch the interactive Web Portal (http://127.0.0.1:5000)")
        print("  python main.py --notebook  : Re-run the Jupyter notebook end-to-end")
        print("\nRunning a quick prediction demonstration...")
        run_predict()

if __name__ == "__main__":
    main()
