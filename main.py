import os
import cv2
import numpy as np
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet import preprocess_input
from typing import List

from app.database import supabase
from app.models import (
    BloodType,
    Patient, CreatePatient, UpdatePatient,
    Test, CreateTest, UpdateTest
)

app = FastAPI()
model = None
IMG_SIZE = (224, 224)
CLASS_NAMES = {0: "Negative", 1: "Positive"}

@app.on_event("startup")
def load_trained_model():
    global model
    model_path = os.getenv("MODEL_PATH", "SickleCell.keras")
    if not os.path.exists(model_path):
        raise RuntimeError(f"Model file not found at {model_path}")
    model = load_model(model_path)

# ——— Patient endpoints ———
@app.get("/patients", response_model=List[Patient])
def read_patients():
    res = supabase.table("patients").select("*").execute()
    return res.data

@app.get("/patients/{patient_id}", response_model=Patient)
def read_patient(patient_id: int):
    res = supabase.table("patients").select("*").eq("patient_id", patient_id).execute()
    if not res.data:
        raise HTTPException(404, "Patient not found")
    return res.data[0]

@app.post("/patients", response_model=Patient)
def create_patient(patient: CreatePatient):
    payload = {
        "patient_name":    patient.patient_name,
        "patient_age":     patient.patient_age,
        "patient_bloodtype": patient.patient_bloodtype.value
    }
    res = supabase.table("patients").insert(payload).execute()
    return res.data[0]

@app.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patient: UpdatePatient):
    data = patient.dict(exclude_unset=True)
    if "patient_bloodtype" in data:
        data["patient_bloodtype"] = data["patient_bloodtype"].value
    res = supabase.table("patients").update(data).eq("patient_id", patient_id).execute()
    if not res.data:
        raise HTTPException(404, "Patient not found")
    return res.data[0]

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    res = supabase.table("patients").delete().eq("patient_id", patient_id).execute()
    if not res.data:
        raise HTTPException(404, "Patient not found")
    return {"deleted": True}

# ——— Test endpoints ———
@app.get("/tests", response_model=List[Test])
def read_tests():
    res = supabase.table("tests").select("*").execute()
    return res.data

@app.get("/tests/{patient_id}", response_model=Test)
def read_test(patient_id: int):
    res = supabase.table("tests").select("*").eq("patient_id", patient_id).execute()
    if not res.data:
        raise HTTPException(404, "Test not found")
    return res.data[0]

@app.post("/tests", response_model=Test)
def create_test(test: CreateTest):
    payload = test.dict()
    res = supabase.table("tests").insert(payload).execute()
    return res.data[0]

@app.put("/tests/{patient_id}", response_model=Test)
def update_test(patient_id: int, test: UpdateTest):
    data = test.dict(exclude_unset=True)
    res = supabase.table("tests").update(data).eq("patient_id", patient_id).execute()
    if not res.data:
        raise HTTPException(404, "Test not found")
    return res.data[0]

@app.delete("/tests/{patient_id}")
def delete_test(patient_id: int):
    res = supabase.table("tests").delete().eq("patient_id", patient_id).execute()
    if not res.data:
        raise HTTPException(404, "Test not found")
    return {"deleted": True}

# ——— Prediction endpoint ———
@app.post("/predict")
async def predict_sickle(
    patient_id:    int        = Form(...),
    hemoglobin:    float      = Form(...),
    rbc_count:     float      = Form(...),
    image_file:    UploadFile = File(...)
):
    if model is None:
        raise HTTPException(503, "Model not loaded")
    data = await image_file.read()
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Invalid image file")
    img = cv2.resize(img, IMG_SIZE)
    x = preprocess_input(np.expand_dims(img, axis=0))
    preds = model.predict(x)[0]
    idx = int(np.argmax(preds))
    label = CLASS_NAMES[idx]
    confidence = float(preds[idx])
    record = {
        "patient_id":       patient_id,
        "hemoglobin_level": hemoglobin,
        "rbc_count":        rbc_count,
        "image_url":        image_file.filename,
        "prediction":       label,
        "confidence":       confidence
    }
    supabase.table("tests").insert(record).execute()
    return {"prediction": label, "confidence": confidence}

# ——— Run with Uvicorn ———
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)