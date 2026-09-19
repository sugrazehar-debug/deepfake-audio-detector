# 🎙️ DeepGuard | AI Audio Forensics

### Deepfake Audio Detection & Forensic System

DeepGuard is an AI-powered audio forensics system designed to detect whether an uploaded audio file is **Real or Deepfake**. The system combines **MFCC-based audio feature extraction** with a **CNN-BiLSTM deep learning model** to analyze audio patterns and identify potential synthetic or manipulated speech.

It also provides visual audio analysis through **MFCC and Mel-Spectrograms**, along with confidence scores and downloadable forensic reports.

---

## 🎥 Demo

**[▶️ Watch DeepGuard Demo](./project demo/demo.mp4)

## 🚀 Key Features

- 🎧 Real vs Deepfake audio classification
- 🤖 CNN-BiLSTM based deep learning model
- 📊 Confidence score for predictions
- 🎵 MFCC feature visualization
- 🌈 Mel-Spectrogram visualization
- 📄 Automatic forensic PDF report generation
- 🕒 Prediction history with date and time
- 🔐 User authentication with JWT
- 🔑 Password hashing for secure authentication
- 🗃️ SQLite database for user and prediction records
- 📥 Downloadable prediction reports
- 🗑️ Prediction history management
- ⚡ FastAPI backend for API-based inference

## 🧠 How It Works

          Upload Audio
                ↓
       Audio Preprocessing
                ↓
       MFCC Feature Extraction
                ↓
          CNN Layers
                ↓
         BiLSTM Layer
                ↓
       Real / Deepfake
                ↓
      Confidence Score
          ↙         ↘
       MFCC      Mel-Spectrogram
                ↓
        Forensic PDF Report

## 🏗️ Model Architecture

DeepGuard uses a hybrid **CNN-BiLSTM architecture**.

### Audio Processing

- Sample Rate: `16,000 Hz`
- MFCC Features: `40`
- Maximum Sequence Length: `500`
- Input Shape: `(40, 500)`

### CNN Layers

The CNN component extracts local patterns from the MFCC representation.

- Conv2D: 32 filters
- Conv2D: 64 filters
- Conv2D: 128 filters
- Batch Normalization
- Max Pooling

### BiLSTM

The extracted sequential features are passed to a **Bidirectional LSTM** to capture temporal patterns from both directions.

- BiLSTM Units: `128`
- Dropout: `0.3`
- Recurrent Dropout: `0.2`

### Training

- Epochs: Up to `100`
- Batch Size: `32`
- Early Stopping based on validation accuracy
- Class balancing using balanced class weights



## 🛠️ Technology Stack

### Machine Learning

- Python
- TensorFlow / Keras
- Librosa
- NumPy
- Scikit-learn

### Backend

- FastAPI
- Python
- JWT Authentication
- Passlib / bcrypt

### Database

- SQLite

### Visualization & Reports

- Matplotlib
- Librosa
- ReportLab

### Development

- Google Colab
- VS Code
- Git & GitHub



## 📂 Project Structure

deepfake-audio-detector/
│
├── model/
│   └── deepfake_model.h5
│
├── training/
│   ├── model_training.ipynb
│   └── test.ipynb
│
├── template/
│
├── output/
│
├── reports/
│
├── project demo/
│   └── demo-video.mp4
│
├── uploads/
│
├── main.py
├── .gitignore
└── README.md
```

> User-generated uploads, virtual environments, and local database files are excluded from version control through `.gitignore`.


## 📊 Model Evaluation

The trained model was evaluated on **3,179 audio files**.

| Metric | Result |
|---|---:|
| Accuracy | 99.34% |
| Precision | 99.49% |
| Recall | 98.73% |
| Test Loss | 0.0278 |

### Confusion Matrix

| | Predicted Real | Predicted Fake |
|---|---:|---:|
| Actual Real | 1991 | 6 |
| Actual Fake | 15 | 1167 |

These results represent the evaluation performed during the project development and testing phase.

---

## 🔐 Security

DeepGuard includes basic application-level security mechanisms:

- JWT-based authentication
- Password hashing
- Authenticated prediction history
- User-specific records
- Protected API operations

---

## 📄 Forensic Report

After analyzing an audio file, DeepGuard can generate a PDF report containing information such as:

- Audio filename
- Prediction
- Confidence score
- MFCC visualization
- Mel-Spectrogram
- Analysis timestamp
- Prediction details

---

## 💻 Running the Project

### 1. Clone the Repository

```bash
git clone https://github.com/sugrazehar-debug/deepfake-audio-detector.git
cd deepfake-audio-detector
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start FastAPI Server

```bash
uvicorn main:app --reload
```

The API will be available locally through the FastAPI development server.

---

## 🎯 Project Objectives

- Detect AI-generated and manipulated speech
- Assist in audio authenticity analysis
- Provide interpretable audio visualizations
- Generate forensic-style reports
- Maintain prediction history
- Provide a practical AI audio forensics workflow

---

## 🔮 Future Scope

- Support for additional audio formats
- Real-time audio deepfake detection
- Advanced transformer-based audio models
- Speaker-level forensic analysis
- Explainable AI for prediction decisions
- Improved robustness against unseen deepfake generation techniques
- Cloud deployment and scalable inference

---

## 👩‍💻 Project

**DeepGuard | AI Audio Forensics**

**Domain:** Artificial Intelligence & Data Science  
**Project Type:** Deep Learning / Audio Forensics  
**Backend:** FastAPI  
**Model:** CNN-BiLSTM  
**Database:** SQLite

---

## ⭐ Acknowledgement

This project was developed as an academic AI & Data Science project to explore deepfake detection, audio feature analysis, and AI-based digital forensics.
