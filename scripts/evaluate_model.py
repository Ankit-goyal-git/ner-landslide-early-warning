import os
import sys
import json
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

def evaluate(model_path, metadata_path, features_csv):
    print("--- Evaluating Trained Landslide Model ---")
    if not os.path.exists(model_path):
        print(f"Error: Model file {model_path} does not exist. Run train_model.py first.")
        sys.exit(1)
        
    model = joblib.load(model_path)
    with open(metadata_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
        
    df = pd.read_csv(features_csv)
    feature_cols = meta['feature_columns']
    
    # Evaluate on test set (>= 2016)
    test_df = df[df['year'] >= 2016]
    X_test = test_df[feature_cols]
    y_test = test_df['label']
    
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    print("\nClassification Report (Hold-Out Test Set 2016):")
    print(classification_report(y_test, preds, target_names=['Pseudo-Absence (0)', 'Landslide Event (1)']))
    
    cm = confusion_matrix(y_test, preds)
    print("Confusion Matrix:")
    print(cm)
    
    auc = roc_auc_score(y_test, probs)
    print(f"ROC-AUC Score: {auc:.4f}")
    print("\nModel evaluation completed successfully.")

if __name__ == '__main__':
    model_file = os.path.join('models', 'landslide_model.pkl')
    metadata_file = os.path.join('models', 'metadata.json')
    features_file = os.path.join('data', 'processed', 'ner_features.csv')
    evaluate(model_file, metadata_file, features_file)
