from fastapi import FastAPI
import joblib
import pandas as pd
from main import run_pipeline
from fastapi import UploadFile, File
import asyncio
import shutil

import os
from fastapi.middleware.cors import CORSMiddleware
import state

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start")
async def start(file: UploadFile = File(...)):
    file_path = os.path.join("inputs", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    state.latest_progress = {} # Reset progress
    asyncio.create_task(run_pipeline(file_path))
    return {"status": "started"}

@app.get("/progress")
def get_progress():
    return state.latest_progress























# =========================
# LOAD MODEL
# =========================
MODEL_PATH = "./modules/module8/models/random_forest.pkl"

data = joblib.load(MODEL_PATH)
model = data["model"]
features = data["features"]


# =========================
# BUILD SAMPLE FUNCTION
# =========================
def build_sample(values: dict):
    """
    Ensure input matches model feature order
    """
    return pd.DataFrame([[values.get(f, 0) for f in features]], columns=features)

# =========================
# 1. GOOD MACHINE STATE
# =========================
@app.get("/predict/good")
def predict_good():

    good_state = {
        "ps_mean": 45,
        "ps_std": 5,
        "ps_max": 120,
        "ps_min": 30,
        "ps_range": 90,
        "ps_trend": 0,

        "flow_mean": 10,
        "flow_std": 1,
        "flow_max": 15,
        "flow_min": 8,
        "flow_imbalance": 2,

        "temp_mean": 60,
        "temp_max": 70,
        "temp_min": 55,
        "temp_std": 3,
        "temp_gradient": 0.5,

        "vibration_mean": 0.2,
        "vibration_std": 0.05,
        "vibration_max": 0.4,
        "vibration_spikes": 0.1,

        "system_health_score": 0.9,
        "anomaly_indicator": 0.1
    }

    sample = build_sample(good_state)
    prediction = model.predict(sample)[0]

    return {
        "status": "GOOD_STATE",
        "prediction": int(prediction)
    }


# =========================
# 2. FAULTY MACHINE STATE
# =========================
@app.get("/predict/fault")
def predict_fault():

    fault_state = {
        "ps_mean": 90,
        "ps_std": 25,
        "ps_max": 200,
        "ps_min": 10,
        "ps_range": 190,
        "ps_trend": -40,

        "flow_mean": 4,
        "flow_std": 3,
        "flow_max": 12,
        "flow_min": 0,
        "flow_imbalance": 8,

        "temp_mean": 95,
        "temp_max": 120,
        "temp_min": 80,
        "temp_std": 15,
        "temp_gradient": 5,

        "vibration_mean": 1.5,
        "vibration_std": 0.8,
        "vibration_max": 3.0,
        "vibration_spikes": 2.5,

        "system_health_score": 0.3,
        "anomaly_indicator": 0.9
    }

    sample = build_sample(fault_state)
    prediction = model.predict(sample)[0]

    return {
        "status": "FAULT_STATE",
        "prediction": int(prediction)
    }