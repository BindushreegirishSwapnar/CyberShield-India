import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import joblib

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from train_model import TRAINING_DATA, CATEGORIES

def run_ml_pipeline():
    print(f"Executing Enterprise ML Pipeline across {len(TRAINING_DATA)} complaints...")
    texts = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.20, random_state=42, stratify=labels
    )

    # Feature Engineering: N-gram TF-IDF Vectorizer with Sublinear Scaling
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=3500,
        sublinear_tf=True,
        stop_words='english'
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Model Candidates for Formal Comparative Evaluation
    candidates = {
        "Calibrated Linear SVM": CalibratedClassifierCV(
            estimator=LinearSVC(C=1.2, random_state=42, max_iter=2000),
            cv=3
        ),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.2),
        "Logistic Regression (Balanced)": LogisticRegression(
            C=3.0, max_iter=1000, class_weight='balanced', random_state=42
        ),
        "Random Forest (100 Trees)": RandomForestClassifier(
            n_estimators=100, max_depth=20, random_state=42
        )
    }

    results = {}
    best_f1 = -1.0
    best_model_name = None
    best_model_obj = None

    skf = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)

    print("\n--- MODEL COMPARISON MATRIX ---")
    for name, clf in candidates.items():
        # Cross validation on training set
        cv_scores = cross_val_score(clf, X_train_vec, y_train, cv=skf, scoring='f1_macro')
        cv_mean = float(np.mean(cv_scores))

        # Train and test evaluation
        clf.fit(X_train_vec, y_train)
        y_pred = clf.predict(X_test_vec)

        acc = float(accuracy_score(y_test, y_pred))
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
            y_test, y_pred, average='macro', zero_division=0
        )
        p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
            y_test, y_pred, average='weighted', zero_division=0
        )

        results[name] = {
            "accuracy": round(acc * 100, 2),
            "precision_macro": round(float(p_macro) * 100, 2),
            "recall_macro": round(float(r_macro) * 100, 2),
            "f1_macro": round(float(f1_macro) * 100, 2),
            "f1_weighted": round(float(f1_weighted) * 100, 2),
            "cv_f1_mean": round(cv_mean * 100, 2),
            "cv_scores": [round(float(s) * 100, 2) for s in cv_scores]
        }

        print(f"[{name}] Acc: {acc*100:.1f}%, F1-Macro: {f1_macro*100:.1f}%, 4-Fold CV F1: {cv_mean*100:.1f}%")

        if f1_macro > best_f1:
            best_f1 = f1_macro
            best_model_name = name
            best_model_obj = clf

    print(f"\nChampion Model Selected: '{best_model_name}' (F1: {best_f1*100:.2f}%)")

    # Serialize Artifacts
    vec_path = os.path.join(MODELS_DIR, 'tfidf_vectorizer_v2.joblib')
    clf_path = os.path.join(MODELS_DIR, 'cybercrime_classifier_v2.joblib')
    joblib.dump(vectorizer, vec_path)
    joblib.dump(best_model_obj, clf_path)

    # Save detailed metadata
    metadata = {
        "model_version": "v2.0-Production",
        "champion_algorithm": best_model_name,
        "training_samples": len(TRAINING_DATA),
        "train_set_size": len(X_train),
        "test_set_size": len(X_test),
        "categories_count": len(CATEGORIES),
        "categories": CATEGORIES,
        "performance": results[best_model_name],
        "comparison_matrix": results,
        "feature_count": X_train_vec.shape[1],
        "vectorizer_params": {
            "ngram_range": [1, 2],
            "max_features": 3500,
            "sublinear_tf": True
        }
    }

    comp_path = os.path.join(MODELS_DIR, 'model_comparison.json')
    meta_path = os.path.join(MODELS_DIR, 'model_metrics.json')

    with open(comp_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"Artifacts successfully serialized to {MODELS_DIR}")
    return metadata

if __name__ == '__main__':
    run_ml_pipeline()
