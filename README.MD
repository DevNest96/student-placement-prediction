# 🎓 Student Placement Prediction using Machine Learning

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-150458.svg?style=flat&logo=pandas&logoColor=white)
![Supported](https://img.shields.io/badge/Status-Completed-success.svg)

## 📌 Project Overview
This project focuses on predicting student placement status using **supervised machine learning algorithms**. The primary objective is to analyze academic performance, aptitude test scores, and training-related attributes to determine the likelihood of a student securing a placement. 

A comprehensive comparison of multiple classification models was conducted to identify the most effective and accurate predictive approach. A **research paper** based on this rigorous analysis is also included in this repository.

---

## 🎯 Problem Statement
Educational institutions constantly strive to improve placement outcomes by identifying key factors that influence student success. This project aims to build predictive models that address these challenges by:
- **Classifying students** as either *Placed* (1) or *Not Placed* (0).
- **Analyzing the impact** of various academic and training features on employability.
- **Empirically comparing** multiple Machine Learning algorithms to determine the best-performing model.

---

## 📊 Dataset Description
The dataset (`placementdata.csv`) is rich in contextual student-related attributes. Key features include:

- **CGPA**: Cumulative Grade Point Average of the student.
- **Aptitude Test Score**: Score achieved in technical/logical reasoning assessments.
- **Extracurricular Activities**: Involvement in activities outside of academics.
- **Placement Training**: Whether the student underwent specialized placement training.
- **Placement Status (Target Variable)**: The final outcome we aim to predict.
  - `1` → Placed
  - `0` → Not Placed

---

## ⚙️ Project Workflow
The end-to-end pipeline of this machine learning project is carefully designed for optimal accuracy:

1. **Data Loading & Cleaning**: Importing data and handling inconsistencies.
2. **Missing Value Handling**: Imputing or removing missing records.
3. **Duplicate Removal**: Ensuring pristine data quality.
4. **Categorical Encoding**: Applying *Label Encoding* to non-numeric attributes.
5. **Exploratory Data Analysis (EDA)**: Data visualization and correlation analysis to uncover hidden patterns.
6. **Train-Test Split**: Dividing the data to validate model generalization.
7. **Feature Scaling**: Standardizing variance using `StandardScaler`.
8. **Model Training & Evaluation**: Training classifiers and evaluating outputs.
9. **Model Comparison**: Selecting the champion model based on benchmark metrics.

---

## 🤖 Machine Learning Models Implemented
This project rigorously tests and compares the following sophisticated classification algorithms:

- **Logistic Regression**
- **K-Nearest Neighbors (KNN)**
- **Decision Tree Classifier**
- **Random Forest Classifier**
- **Naive Bayes**

*Each model is evaluated on multiple criteria to gauge reliability and effectiveness.*

---

## 📈 Evaluation Metrics
Robust evaluation metrics were leveraged to ensure the models are practically viable:
- **Accuracy**: Overall correctness of the model.
- **Precision**: Capability to avoid false positives.
- **Recall (Sensitivity)**: Capability to find all positive instances.
- **F1 Score**: Harmonic mean of precision and recall.
- **Confusion Matrix**: A tabular summary of successful predictions vs. errors.
- **Classification Report**: Detailed statistical breakdown per class.

---

## 📁 Repository Structure
```plaintext
📂 Student Placement Prediction using Machine Learning
├── 📓 Placement_analysis.ipynb   # Complete ML implementation & EDA notebook
├── 📄 placementdata.csv          # Raw evaluation dataset
├── 📜 Research_Paper.pdf         # Detail-oriented research paper based on the project
├── 📦 requirements.txt           # Python library dependencies
└── 📖 README.MD                  # Project documentation (You are here)
```

---

## 🚀 How to Run Locally

Follow these instructions to set up and run the machine learning analysis on your local system:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Tanishkraj2005/Student-Placement-Prediction-using-Machine-Learning.git
   cd Student-Placement-Prediction-using-Machine-Learning
   ```

2. **Install dependencies:**
   It's recommended to use a virtual environment. Install required packages using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Jupyter Notebook:**
   Launch Jupyter Notebook to view the code, visualizations, and model evaluations interactively.
   ```bash
   jupyter notebook Placement_analysis.ipynb
   ```
   *(Alternatively, you can open the notebook via VS Code or JupyterLab).*

---

## 📜 Research Contribution
This project serves as the foundation for a formal **research study**. It structurally analyzes predictive modeling techniques for student placement classification, offering a deep-dive comparison into algorithmic performance within modern academic contexts. The findings and comprehensive detailed study can be found in `Research_Paper.pdf`.

---

## 👤 Author
Developed and Researched by Alok Kumar Gupta

<p align="center">
  <i>If you found this project helpful, please consider leaving a ⭐ on the repository!</i>
</p>