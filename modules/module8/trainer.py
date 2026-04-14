import pandas as pd
import os
import joblib
from state import IndustryState
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

import state

# =========================
# 1. LOAD DATA
# =========================
def load_dataset(path="./modules/module8/resources/hydraulic_final_dataset.csv"):
    df = pd.read_csv(path)
    print("📂 Dataset loaded:", df.shape)
    return df


# =========================
# 2. FEATURE GROUPS
# =========================
FEATURE_GROUPS = {
    "temperature": [
        "temp_mean", "temp_max", "temp_min", "temp_std", "temp_gradient"
    ],
    "pressure": [
        "ps_mean", "ps_std", "ps_max", "ps_min", "ps_range", "ps_trend"
    ],
    "flow": [
        "flow_mean", "flow_std", "flow_max", "flow_min", "flow_imbalance"
    ],
    "vibration": [
        "vibration_mean", "vibration_std", "vibration_max", "vibration_spikes"
    ],
    "global": [
        "system_health_score", "anomaly_indicator"
    ]
}


# =========================
# 3. FEATURE BUILDER
# =========================
def build_features(df, selected_groups):
    features = []

    for group in selected_groups:
        if group in FEATURE_GROUPS:
            features.extend(FEATURE_GROUPS[group])

    features = list(set(features))
    features = [f for f in features if f in df.columns]

    return features


# =========================
# 4. PREPARE DATA
# =========================
def prepare_data(df, selected_features, target="pump_leak"):
    X = df[selected_features]
    y = df[target]

    return train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )


# =========================
# 5. TRAIN MODEL
# =========================
def train_model(X_train, y_train):
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)
    print("\n✅ Model trained")

    return model


# =========================
# 6. EVALUATE MODEL
# =========================
def evaluate_model(model, X_test, y_test,state: IndustryState):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    state["ml_features"]["accuracy"] = accuracy
    print("\n📊 Accuracy:", accuracy)
    print("\n📊 Report:\n", classification_report(y_test, y_pred))


# =========================
# 7. SAVE MODEL
# =========================
def save_model(model, features, path="./modules/module8/models/random_forest.pkl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    joblib.dump({
        "model": model,
        "features": features
    }, path)

    print(f"\n💾 Model saved at: {path}")


# =========================
# 8. MAIN PIPELINE
# =========================
def train_pipeline(state: IndustryState):
    # Load
    df = load_dataset()
    selected_groups = state["extracted_data"]["tensors"]  
    # Feature selection
    selected_features = build_features(df, selected_groups)

    print("\n📌 Selected groups:", selected_groups)
    print("📌 Features:", selected_features)

    #update the state with the selected features and model type
    if "ml_features" not in state or state["ml_features"] is None:
        state["ml_features"] = {}
    state["ml_features"]["sensors_used"] = selected_groups
    state["ml_features"]["feature_vector_size"] = len(selected_features)
    state["ml_features"]["model_type"] = "random_forest"


    # Prepare
    X_train, X_test, y_train, y_test = prepare_data(
        df, selected_features
    )

    # Train
    model = train_model(X_train, y_train)

    # Evaluate
    evaluate_model(model, X_test, y_test, state)

    # Save
    save_model(model, selected_features)

    print("\nyou can use the model from the endpoint /predict to make predictions")
    return model

