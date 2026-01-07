import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

def train_model():
    # 1. Load Data from the CSV you just generated
    print("Loading dataset...")
    csv_path = "bacteria_train_data.csv"
    
    if not os.path.exists(csv_path):
         print(f"❌ Error: '{csv_path}' not found. You MUST run 'generate_dataset.py' first!")
         return

    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} rows from {csv_path}")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # 2. Prepare Features (X) and Target (y)
    # These columns MUST match what 'generate_dataset.py' created
    feature_cols = [
        'genome_length', 
        'gc_content', 
        'orf_count', 
        'resistance_gene_count', 
        'virulence_factor_count', 
        'crispr_present'
    ]
    
    # Check if all columns exist
    if not all(col in df.columns for col in feature_cols):
        print(f"❌ Error: CSV is missing columns. Expected: {feature_cols}")
        return

    X = df[feature_cols]
    y = df['label']

    # 3. Split Data (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Initialize and Train Random Forest
    print("Training Random Forest Model (this may take a few seconds)...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # 5. Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n✅ Model Trained successfully!")
    print(f"Accuracy: {acc * 100:.2f}%")
    
    # 6. Save Model to 'models' folder
    os.makedirs("models", exist_ok=True)
    model_path = "models/pathogen_risk_rf.pkl"
    joblib.dump(clf, model_path)
    print(f"💾 Model saved to: {model_path}")

if __name__ == "__main__":
    train_model()