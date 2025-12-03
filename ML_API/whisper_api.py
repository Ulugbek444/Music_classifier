import whisper
import torch
import tempfile
import os
from pathlib import Path

from typing import Optional
from transformers import PreTrainedTokenizer, PreTrainedModel

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel


app = FastAPI(title="ML API")

# === Whisper ===
whisper_model = None

# === Emotion model ===
tokenizer: Optional[PreTrainedTokenizer] = None
emotion_model: Optional[PreTrainedModel] = None


@app.on_event("startup")
def load_model():
    global whisper_model, tokenizer, emotion_model

    # ===== Whisper =====
    whisper_model = whisper.load_model("small")
    print("✅ Whisper model loaded")

    # ===== Emotion =====
    BASE_DIR = Path(__file__).resolve().parent
    MODEL_PATH = BASE_DIR / "models" / "lyrics_emotion_bert"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    emotion_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    emotion_model.eval()

    print("✅ Emotion model loaded")
    print("Tokenizer type:", type(tokenizer))
    print("Emotion model type:", type(emotion_model))


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if whisper_model is None:
        raise HTTPException(status_code=503, detail="Whisper model not loaded")

    suffix = os.path.splitext(file.filename)[1] or ".ogg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = whisper_model.transcribe(tmp_path, language="en", fp16=False)
        return {"text": result["text"].strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(tmp_path)


class TextInput(BaseModel):
    text: str


@app.post("/predict-emotion")
def predict_emotion(data: TextInput):

    if tokenizer is None or emotion_model is None:
        raise HTTPException(status_code=503, detail="Emotion model not loaded")

    inputs = tokenizer(
        data.text,
        return_tensors="pt",
        truncation=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = emotion_model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)

    pred_id = probs.argmax(dim=1).item()
    confidence = probs.max().item()

    return {
        "emotion": emotion_model.config.id2label[pred_id],
        "confidence": confidence
    }


@app.get("/health")
def health():
    return {"status": "ok"}
