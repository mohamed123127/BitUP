from state import IndustryState
from .datasetPreprocicing import preprocess_dataset
from .trainer import train_pipeline
import os

from helper.progressTracker import send_progress
import asyncio

async def module_8_ml(state: IndustryState):
    print("⚫ Module 8: Digital Twin ML")
    await send_progress("MOD_008", "in_progress", "DIGITAL_TWIN", 10.0, "Checking ML dataset...")
    
    #check if the dataset is available in resources/hydraulic_final_dataset.csv 
    if not os.path.exists("./modules/module8/resources/hydraulic_final_dataset.csv"):
        print("start the dataset preprocessing...")
        await send_progress("MOD_008", "in_progress", "DIGITAL_TWIN", 30.0, "Preprocessing dataset...")
        preprocess_dataset()
        await asyncio.sleep(1)
    
    await send_progress("MOD_008", "in_progress", "DIGITAL_TWIN", 60.0, "Training pipeline with specified tensors...")
    train_pipeline(state)
    await asyncio.sleep(1)
   
    print("Build the model and train it with the specified tensors")
    await send_progress("MOD_008", "completed", "DIGITAL_TWIN", 100.0, "Model trained successfully.", state.get("ml_features", {}))

    return state