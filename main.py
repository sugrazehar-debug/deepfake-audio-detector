import os, shutil, uuid, sqlite3
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from datetime import datetime

# FastAPI & Security
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer
from jose import jwt
from passlib.context import CryptContext

# TensorFlow & Keras
import tensorflow as tf
import keras

# ReportLab Professional Imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIG ---
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Forensic Audio Analysis System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
SECRET_KEY = "your_deepfake_secret_key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

for folder in ["uploads", "outputs", "reports", "model"]:
    os.makedirs(folder, exist_ok=True)

# --- KERAS PATCH ---
def fix_layer_config(layer_class):
    original_init = layer_class.__init__
    def new_init(self, *args, **kwargs):
        if 'quantization_config' in kwargs: kwargs.pop('quantization_config')
        return original_init(self, *args, **kwargs)
    layer_class.__init__ = new_init
    return layer_class

custom_objects = {
    "Dense": fix_layer_config(keras.layers.Dense),
    "Flatten": fix_layer_config(keras.layers.Flatten),
    "Conv2D": fix_layer_config(keras.layers.Conv2D),
    "LSTM": fix_layer_config(keras.layers.LSTM),
    "Bidirectional": fix_layer_config(keras.layers.Bidirectional)
}

# --- MODEL LOAD ---
model = None
model_path = os.path.join("model", "deepfake_model.h5")
try:
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path, custom_objects=custom_objects, compile=False)
        print(" Forensic Model Loaded Successfully.")
except Exception as e: print(f" Model Error: {e}")

# --- DB SETUP ---
def get_db(): return sqlite3.connect("project.db", check_same_thread=False)
conn = get_db(); cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, audio_name TEXT, result TEXT, confidence REAL, mfcc_path TEXT, spectrogram_path TEXT, report_path TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
conn.commit(); conn.close()

# --- AUTH ---
def verify_token(token=Depends(security)):
    try: return jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except: raise HTTPException(401, "Invalid Token")

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register(user: UserCreate):
    conn = get_db()
    cur = conn.cursor()
    try:
        hashed = pwd_context.hash(user.password)
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, hashed))
        conn.commit()
        user_id = cur.lastrowid
        token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)
        return {"token": token, "msg": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Username already exists")
    finally:
        conn.close()

@app.post("/login")
async def login(user: UserCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE username=?", (user.username,))
    db_user = cur.fetchone()
    conn.close()
    if not db_user or not pwd_context.verify(user.password, db_user[1]):
        raise HTTPException(401, "Invalid username or password")
    token = jwt.encode({"user_id": db_user[0]}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "username": user.username}

# --- CORE PREDICT ROUTE ---
@app.post("/predict")
async def predict(file: UploadFile = File(...), user=Depends(verify_token)):
    if model is None: raise HTTPException(500, "Model Error")
    uid = str(uuid.uuid4())[:8]
    path = os.path.join("uploads", f"{uid}_{file.filename}")
    with open(path, "wb") as f: shutil.copyfileobj(file.file, f)

    try:
        # Audio Load
        y, sr = librosa.load(path, sr=22050)
        
        # 1. MFCC for Prediction 
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        target = 500
        mfcc_fixed = np.pad(mfcc, ((0,0), (0, max(0, target-mfcc.shape[1]))), mode='constant')[:, :target]

        # 2. Mel Spectrogram for Visualization
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        # AI Prediction
        x = mfcc_fixed.reshape(1, 40, 500, 1).astype('float32')
        p_val = float(model.predict(x)[0][0])
        result = "MANIPULATED (FAKE)" if p_val > 0.5 else "AUTHENTIC (REAL)"
        conf = p_val if p_val > 0.5 else 1 - p_val

        #  VISUALS ---
        mfcc_img = f"outputs/{uid}_mfcc.png"
        plt.figure(figsize=(12, 5))
        librosa.display.specshow(mfcc, sr=sr, x_axis='time', cmap='coolwarm')
        plt.colorbar(); plt.title('Mel-Frequency Cepstral Coefficients (MFCCs)')
        plt.tight_layout(); plt.savefig(mfcc_img, dpi=300); plt.close()

        mel_img = f"outputs/{uid}_mel.png"
        plt.figure(figsize=(12, 5))
        librosa.display.specshow(mel_spec_db, sr=sr, x_axis='time', y_axis='mel', cmap='magma')
        plt.colorbar(format='%+2.0f dB'); plt.title('Mel-Frequency Spectrogram')
        plt.tight_layout(); plt.savefig(mel_img, dpi=300); plt.close()

        # --- PDF GENERATION ---
        report_path = f"reports/{uid}_report.pdf"
        doc = SimpleDocTemplate(report_path, pagesize=letter)
        styles = getSampleStyleSheet()
        blue_theme = colors.toColor("#1A237E")
        v_color = colors.red if "FAKE" in result else colors.green

        elements = []
        elements.append(Paragraph("FORENSIC AUDIO ANALYSIS REPORT", ParagraphStyle('T', fontSize=22, textColor=blue_theme, alignment=1, spaceAfter=20)))
        
        data = [["CASE ATTRIBUTE", "VALUE"], 
                ["Evidence ID", f"EVD-{uid.upper()}"], 
                ["Verdict", Paragraph(f"<b>{result}</b>", ParagraphStyle('V', textColor=v_color))],
                ["Confidence", f"{round(conf*100, 2)}%"]]
        
        tbl = Table(data, colWidths=[150, 300])
        tbl.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), blue_theme), ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('PADDING', (0,0), (-1,-1), 8)]))
        elements.append(tbl); elements.append(Spacer(1, 20))

        elements.append(Paragraph("1. Mel-Frequency Cepstral Coefficients (MFCCs)", styles['Heading3']))
        elements.append(Image(mfcc_img, 520, 180))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("2. Mel-Frequency Spectrogram Analysis", styles['Heading3']))
        elements.append(Image(mel_img, 520, 180))
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("CONCLUSION", styles['Heading2']))
        elements.append(Paragraph(f"deepfake detection  analysis & identifies this sample as {result.lower()} with {round(conf*100,2)}% certainty.", styles['Normal']))
        
        doc.build(elements)

        # Database Logging
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO history (user_id, audio_name, result, confidence, mfcc_path, spectrogram_path, report_path) VALUES (?,?,?,?,?,?,?)",
                    (user["user_id"], file.filename, result, conf, mfcc_img, mel_img, report_path))
        conn.commit(); conn.close()

        return {
            "verdict": result,
            "confidence": f"{round(conf*100, 2)}%",
            "report": f"/download-report/{os.path.basename(report_path)}",
            "mfcc_path": mfcc_img,
            "spectrogram_path": mel_img
        }

    except Exception as e: raise HTTPException(500, str(e))

@app.get("/download-report/{report_name}")
def download(report_name: str):
    path = os.path.join("reports", report_name)
    if os.path.exists(path): return FileResponse(path, media_type='application/pdf', filename=report_name)
    raise HTTPException(404, "Report not found")

@app.get("/dashboard")
async def dashboard(user=Depends(verify_token)):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT audio_name, result, confidence, mfcc_path, spectrogram_path, report_path, created_at FROM history WHERE user_id=? ORDER BY created_at DESC LIMIT 10", (user["user_id"],))
    rows = cur.fetchall(); conn.close()
    history = []
    for row in rows:
        history.append({
            "audio_name": row[0],
            "result": row[1],
            "confidence": float(row[2]),
            "mfcc_path": row[3],
            "spectrogram_path": row[4],
            "report_path": row[5],
            "created_at": row[6]
        })
    return history

@app.get("/history")
async def history(user=Depends(verify_token)):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT audio_name, result, confidence, mfcc_path, spectrogram_path, report_path, created_at FROM history WHERE user_id=? ORDER BY created_at DESC", (user["user_id"],))
    rows = cur.fetchall(); conn.close()
    history = []
    for row in rows:
        history.append({
            "audio_name": row[0],
            "result": row[1],
            "confidence": float(row[2]),
            "mfcc_path": row[3],
            "spectrogram_path": row[4],
            "report_path": row[5],
            "created_at": row[6]
        })
    return history

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

@app.get("/")
def root():
    return RedirectResponse(url="/template/login.html")

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")
app.mount("/template", StaticFiles(directory="template"), name="templates")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
