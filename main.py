"""
main.py — CLIP Clothes Recommender for Cloud Run
------------------------------------------------
Collection: clothes
Each document:
{
    name: str,
    image_url: str,
    type: "top" | "bottom",
    embedding: [...],
    embedding_version: "ViT-B/32_v1"
}

Functions:
- /warmup/     -> loads CLIP + builds index
- /rebuild_cache/ -> regenerates embeddings for all clothes
- /upload_item/ -> called when user uploads new clothing item
- /recommend/  -> returns 1 top + 1 bottom recommendation
"""

import os
import io
from datetime import datetime
from typing import List, Dict, Any

import torch
import requests
from PIL import Image
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import firebase_admin
from firebase_admin import credentials, firestore


# -------------------- CONFIG --------------------
FIREBASE_CREDENTIALS_PATH = "firebase_service_account.json"
CLOTHES_COLLECTION = "clothes"

CLIP_MODEL_NAME = "ViT-B/32"
EMBEDDING_VERSION = f"{CLIP_MODEL_NAME}_v1"

device = "cuda" if torch.cuda.is_available() else "cpu"


# -------------------- INIT FIREBASE --------------------
if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
    raise RuntimeError(f"Missing Firebase credentials at {FIREBASE_CREDENTIALS_PATH}")

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()


# -------------------- FASTAPI --------------------
app = FastAPI(title="CLIP Clothes Recommender")


# -------------------- GLOBAL RUNTIME --------------------
model = None
preprocess = None
MODEL_LOADED = False

INDEX_TOP: List[Dict[str, Any]] = []
INDEX_BOTTOM: List[Dict[str, Any]] = []


# -------------------- CLIP HELPERS --------------------
def load_clip_model():
    """Lazy-load CLIP model."""
    global model, preprocess, MODEL_LOADED
    if MODEL_LOADED:
        return True

    import clip
    model_loaded, preprocess_loaded = clip.load(CLIP_MODEL_NAME, device=device)
    model_loaded.eval()

    model = model_loaded
    preprocess = preprocess_loaded
    MODEL_LOADED = True

    print("CLIP model loaded.")
    return True


def download_image(url: str) -> Image.Image:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def encode_image(img: Image.Image) -> List[float]:
    load_clip_model()
    x = preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        feat = model.encode_image(x)
        feat = feat / feat.norm(dim=-1, keepdim=True)
    return feat.squeeze(0).cpu().tolist()


def encode_text(text: str) -> torch.Tensor:
    import clip
    load_clip_model()

    toks = clip.tokenize([text]).to(device)
    with torch.no_grad():
        feat = model.encode_text(toks)
        feat = feat / feat.norm(dim=-1, keepdim=True)
    return feat.cpu().squeeze(0)


def cosine_similarity(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(torch.dot(a, b))


# -------------------- FIRESTORE HELPERS --------------------
def fetch_clothes():
    docs = []
    for doc in db.collection(CLOTHES_COLLECTION).stream():
        d = doc.to_dict()
        d["_id"] = doc.id
        docs.append(d)
    return docs


def build_index():
    """Build top and bottom index from existing Firestore embeddings."""
    global INDEX_TOP, INDEX_BOTTOM
    INDEX_TOP = []
    INDEX_BOTTOM = []

    docs = fetch_clothes()

    for d in docs:
        if not d.get("embedding"):
            continue

        emb = torch.tensor(d["embedding"], dtype=torch.float32)
        emb = emb / (emb.norm() + 1e-10)

        entry = {
            "id": d["_id"],
            "name": d.get("name", ""),
            "image_url": d.get("image_url", ""),
            "embedding": emb
        }

        if d.get("type") == "top":
            INDEX_TOP.append(entry)
        elif d.get("type") == "bottom":
            INDEX_BOTTOM.append(entry)

    print(f"Index built: {len(INDEX_TOP)} tops, {len(INDEX_BOTTOM)} bottoms")
    return True


# -------------------- API MODELS --------------------
class UploadItem(BaseModel):
    name: str
    size: str
    image_url: str
    type: str  # "top" or "bottom"


class RecommendRequest(BaseModel):
    season: str = ""
    weather: str = ""
    event: str = ""


class RecommendationResult(BaseModel):
    top: Dict[str, Any]
    bottom: Dict[str, Any]


# -------------------- API ROUTES --------------------
@app.get("/")
def root():
    return {"status": "running", "model_loaded": MODEL_LOADED}


@app.post("/warmup/")
def warmup():
    load_clip_model()
    build_index()
    return {
        "status": "ready",
        "tops": len(INDEX_TOP),
        "bottoms": len(INDEX_BOTTOM)
    }


@app.post("/upload_item/")
def upload_item(req: UploadItem):
    """Called when the user uploads a clothing item."""
    if req.type not in ("top", "bottom"):
        raise HTTPException(400, "type must be 'top' or 'bottom'")

    load_clip_model()

    try:
        img = download_image(req.image_url)
        emb = encode_image(img)
    except Exception as e:
        raise HTTPException(500, f"Failed to process image: {e}")

    doc_ref = db.collection(CLOTHES_COLLECTION).document()
    doc_ref.set({
        "name": req.name,
        "size": req.size,
        "image_url": req.image_url,
        "type": req.type,
        "embedding": emb,
        "embedding_version": EMBEDDING_VERSION,
        "created_at": datetime.utcnow().isoformat()
    })

    # Update in-memory index
    build_index()

    return {"status": "saved", "id": doc_ref.id}


@app.post("/rebuild_cache/")
def rebuild_cache():
    """Re-encode images for all clothes in the database."""
    load_clip_model()

    docs = fetch_clothes()
    updated = 0

    for d in docs:
        img_url = d.get("image_url")
        if not img_url:
            continue

        already = d.get("embedding_version") == EMBEDDING_VERSION
        if already:
            continue

        try:
            img = download_image(img_url)
            emb = encode_image(img)
            db.collection(CLOTHES_COLLECTION).document(d["_id"]).update({
                "embedding": emb,
                "embedding_version": EMBEDDING_VERSION,
                "updated_at": datetime.utcnow().isoformat()
            })
            updated += 1
        except Exception as e:
            print("Error processing", d["_id"], e)

    build_index()
    return {"updated": updated}

@app.post("/recommend/", response_model=RecommendationResult)
def recommend(req: RecommendRequest):
    if not MODEL_LOADED:
        raise HTTPException(500, "Model not loaded. Run /warmup first.")
    if not INDEX_TOP or not INDEX_BOTTOM:
        raise HTTPException(500, "Index empty. Upload clothes or run /rebuild_cache.")

    query = f"{req.season} {req.weather} {req.event} outfit".strip()
    if not query:
        raise HTTPException(400, "Empty query")

    text_vec = encode_text(query)

    # Rank tops
    top_scores = [
        (cosine_similarity(text_vec, item["embedding"]), item)
        for item in INDEX_TOP
    ]
    best_top = max(top_scores, key=lambda x: x[0])[1]

    # Rank bottoms
    bottom_scores = [
        (cosine_similarity(text_vec, item["embedding"]), item)
        for item in INDEX_BOTTOM
    ]
    best_bottom = max(bottom_scores, key=lambda x: x[0])[1]

    # Only return serializable fields
    return {
        "top": {
            "name": best_top.get("name", ""),
            "image_url": best_top.get("image_url", ""),
            "id": best_top.get("id", "")
        },
        "bottom": {
            "name": best_bottom.get("name", ""),
            "image_url": best_bottom.get("image_url", ""),
            "id": best_bottom.get("id", "")
        }
    }

