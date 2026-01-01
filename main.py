import os
import io
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
import random

import torch
import requests
from PIL import Image
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from difflib import get_close_matches
from urllib.parse import quote
from contextlib import asynccontextmanager
from event_rules import event_rules
from colors_rules import COLOR_FAMILIES, COLOR_COMPATIBILITY, COLOR_NORMALIZATION

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


WEATHER_RULES = {
    "hot": ["light", "short-sleeve"],
    "rainy": ["long-sleeve"],
    "cold": ["long-sleeve"],
    "normal": []     
}

FREEZING_FORCE_CATEGORIES = {
    "top": ["thermal_top", "sweater", "coat"],
    "bottom": ["thermal_bottom", "long_pants"],
    "one_piece": ["winter_coat"]
}

EVENT_TO_UPLOAD_CATEGORY = {
    # ---------- ONE PIECE ----------
    "dress": "dress",
    "gown": "gown",
    "maxi dress": "maxi dress",
    "jumpsuit": "jumpsuit",
    "baju kurung": "baju kurung",
    "baju kebaya": "baju kebaya",
    "baju melayu": "baju melayu",
    "cheongsam": "cheongsam",
    "qipao": "qipao",
    "saree": "saree",
    "salwar kameez": "salwar kameez",
    "pavadai": "pavadai",
    "evening gown": "gown",
    "evening dress": "dress",

    # ---------- TOP ----------
    "t-shirt": "t-shirt",
    "blouse": "blouse",
    "shirt": "shirt",
    "long-sleeve t-shirt": "t-shirt",
    "long-sleeve shirt": "shirt",
    "long-sleeve blouse": "blouse",
    "tunic": "tunic",
    "kurta": "kurta",
    "dress shirt": "shirt",
    "tang suit": "tang suit",
    "collared shirt": "shirt",

    # ---------- BOTTOM ----------
    "pants": "pants",
    "trousers": "trousers",
    "skirt": "skirt",
    "jeans": "jeans",
    "palazzo pants": "palazzo pants",
    "long skirt": "long skirt",
    "dhoti": "dhoti",
    "veshti": "veshti"
}

CLIP_CANONICAL = {
    # Malay
    "baju kurung": "long-sleeve loose dress",
    "baju kebaya": "fitted traditional blouse and long skirt",
    "baju melayu": "long-sleeve traditional tunic and trousers",

    # Chinese
    "qipao": "fitted high-collar dress",
    "cheongsam": "fitted high-collar dress",
    "tang suit": "traditional jacket with mandarin collar",

    # Indian
    "saree": "draped long fabric dress",
    "salwar kameez": "long tunic with loose trousers",
    "kurta": "long tunic",
    "veshti": "wrapped long skirt",
    "dhoti": "wrapped long garment",
    "pavadai": "traditional long skirt",

    # others
    "evening gown": "evening gown",
    "evening dress": "evening dress",
    "dress": "dress",
    "gown": "gown",
    "maxi dress": "maxi dress",
    "blouse": "blouse",
    "shirt": "shirt",
    "t-shirt": "t-shirt",
    "tunic": "tunic",
    "pants": "pants",
    "trousers": "trousers",
    "skirt": "skirt",
    "jeans": "jeans",
    "collared shirt": "collared shirt",
    "long-sleeve shirt": "long-sleeve shirt",
    "long-sleeve blouse": "long-sleeve blouse",
    "long-sleeve t-shirt": "long-sleeve t-shirt",
    "dress shirt": "dress shirt",
    "jumpsuit": "jumpsuit",
    "palazzo pants": "palazzo pants",
    "long skirt": "long skirt",
}   

# -------------------- FASTAPI --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    print("Server starting: Loading CLIP model...")
    load_clip_model()
        
    yield  # The application runs while this yield is active

# Initialize app with the new lifespan handler
app = FastAPI(title="CLIP Clothes Recommender", lifespan=lifespan)

# -------------------- GLOBAL RUNTIME --------------------
model = None
preprocess = None
MODEL_LOADED = False
CACHE_REBUILT = False

USER_INDEX: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
USER_INDEX_BUILT = {}

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
def fetch_clothes(user_id: str):
    docs = []
    query = db.collection(CLOTHES_COLLECTION).where("user_id", "==", user_id)
    for doc in query.stream():
        d = doc.to_dict()
        d["_id"] = doc.id
        docs.append(d)
    return docs

def fetch_all_clothes():
    docs = []
    for doc in db.collection(CLOTHES_COLLECTION).stream():
        d = doc.to_dict()
        d["_id"] = doc.id
        docs.append(d)
    return docs

def fetch_all_user_ids() -> List[str]:
    user_ids = set()
    docs = db.collection(CLOTHES_COLLECTION).stream()
    for doc in docs:
        d = doc.to_dict()
        if "user_id" in d:
            user_ids.add(d["user_id"])
    return list(user_ids)

def build_index(user_id: str):
    """Build top and bottom index from existing Firestore embeddings."""

    if USER_INDEX_BUILT.get(user_id):
        return True # Already built, skip

    docs = fetch_clothes(user_id)

    USER_INDEX[user_id] = {"tops": [], "bottoms": [], "one_piece": []}
    for d in docs:
        if not d.get("embedding"):
            continue

        emb = torch.tensor(d["embedding"], dtype=torch.float32)
        emb = emb / (emb.norm() + 1e-10)

        entry = {
            "id": d["_id"],
            "name": d.get("name", ""),
            "image_url": d.get("image_url", ""),
            "category": d.get("category", "").lower(),
            "piece_type": d.get("piece_type"),
            "color": d.get("color"),
            "embedding": emb
        }

        if d.get("piece_type") == "top":
            USER_INDEX[user_id]["tops"].append(entry)
        elif d.get("piece_type") == "bottom":
            USER_INDEX[user_id]["bottoms"].append(entry)
        elif d.get("piece_type") == "one_piece":
            USER_INDEX[user_id]["one_piece"].append(entry)

    USER_INDEX_BUILT[user_id] = True

    print(
        f"Index built for {user_id}: "
        f"{len(USER_INDEX[user_id]['tops'])} tops, "
        f"{len(USER_INDEX[user_id]['bottoms'])} bottoms, "
        f"{len(USER_INDEX[user_id]['one_piece'])} one-piece"
    )

    return True
    
def normalize_color(c):
    return COLOR_NORMALIZATION.get(c, c)

def normalize_ui_color(family: str | None, attributes: List[str]) -> dict:
    fam = normalize_color(family) if family else None

    attrs = []
    for a in attributes:
        if not a:
            continue
        a_norm = normalize_color(a)
        if a_norm and a_norm not in attrs:
            attrs.append(a_norm)

    return {
        "family": fam,
        "attributes": attrs
    }

def normalize_weather(weather_main: str, temp_c: int) -> str:
    weather_main = weather_main.lower()

    if "rain" in weather_main or "drizzle" in weather_main or "thunderstorm" in weather_main:
        return "rainy"
    
    if temp_c <= 0:
        return "freezing"

    if temp_c <= 18:
        return "cold"

    if temp_c >= 30:
        return "hot"

    return "normal"

def normalize_event(event: str) -> str:
    if not event:
        return ""
    return event.lower().strip()

def match_event(user_event: str) -> str:
    """Directly validate event against EVENT_RULES keys."""
    if not user_event:
        return ""

    event_key = user_event.lower().strip()

    if event_key in event_rules:
        return event_key

    return ""

def normalize_event_category(cat: str) -> str:
    c = cat.lower().strip()
    return EVENT_TO_UPLOAD_CATEGORY.get(c, c)

def get_allowed_categories(event_info, style, gender):
    style_map = event_info.get("style_categories", {})
    style_info = style_map.get(style, {})
    gender_info = style_info.get(gender, {})

    return {
        "one_piece": gender_info.get("one_piece", []),
        "top": gender_info.get("top", []),
        "bottom": gender_info.get("bottom", [])
    }

def serialize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Remove non-JSON fields before API response"""
    return {
        "id": item["id"],
        "name": item["name"],
        "image_url": item["image_url"],
        "category": item["category"],
        "piece_type": item["piece_type"],
        "color": item["color"]
    }


# --------------Prepare Purchase LINKS --------------------
def generate_online_links(query: str) -> Dict[str, Any]:
    """
    Generates online shopping links for Shopee, Lazada, Taobao
    using the query string.
    """
    # Simple URL encoding
    import urllib.parse
    q_encoded = urllib.parse.quote(query)

    links = {
        "shopee": f"https://shopee.com.my/search?keyword={q_encoded}",
        "lazada": f"https://www.lazada.com.my/catalog/?q={q_encoded}",
        "taobao": f"https://world.taobao.com/search/search.htm?q={q_encoded}"
    }

    return links

def format_links(links, name):
    return [
        {"platform": p.capitalize(), "name": name, "price": "Check online", "url": u}
                for p, u in links.items()
    ]

# -------------------- API MODELS --------------------
class UploadItem(BaseModel):
    name: str
    size: str
    image_url: str
    category: str
    piece_type: str # top || bottom || one-piece
    user_id: str
    color_family: str | None = None
    color_attributes: List[str] = []

class UpdateItem(BaseModel):
    user_id: str
    name: str
    size: str
    category: str
    piece_type: str
    image_url: str
    color_family: Optional[str] = None
    color_attributes: List[str] = []

class RecommendRequest(BaseModel):
    user_id: str = ""
    season: str = ""
    weather: str = ""
    temp: int | None = None
    event: str = ""
    style_preference: str = ""
    gender: str = ""
    exclude_item_ids: List[str] = []

class RecommendationResult(BaseModel):
    piece_type: str
    top: Dict[str, Any] | None = None
    bottom: Dict[str, Any] | None = None
    alternative_tops: List[Dict[str, Any]] = []
    alternative_bottoms: List[Dict[str, Any]] = []
    shoppingSuggestions: Dict[str, List[Dict[str, Any]]] | None

# -------------------- API ROUTES --------------------
@app.get("/")
def root():
    return {"status": "running", "model_loaded": MODEL_LOADED}


@app.post("/warmup/")
def warmup(user_id: str):
    load_clip_model()
    build_index(user_id = user_id)
    user_index = USER_INDEX.get(user_id, {"tops": [], "bottoms": [], "one_piece": []})
    return {
        "status": "ready",
        "tops": len(user_index["tops"]),
        "bottoms": len(user_index["bottoms"]),
        "one_piece": len(user_index["one_piece"])
    }


@app.post("/upload_item/")
def upload_item(req: UploadItem):
    """Called when the user uploads a clothing item."""
    if req.piece_type not in ("top", "bottom", "one_piece"):
        raise HTTPException(400, "Invalid piece_type")
    
    if not req.user_id:
        raise HTTPException(400, "user_id is required")

    if not req.color_family and not req.color_attributes:
        raise HTTPException(
            status_code=400,
            detail="Color information (family or attribute) is required"
        )

    load_clip_model()

    try:
        img = download_image(req.image_url)
        emb = encode_image(img)
        color = normalize_ui_color(req.color_family, req.color_attributes)
    except Exception as e:
        raise HTTPException(500, f"Failed to process image: {e}")

    doc_ref = db.collection(CLOTHES_COLLECTION).document()
    doc_ref.set({
        "user_id": req.user_id,
        "name": req.name,
        "size": req.size,
        "image_url": req.image_url,
        "category": req.category.lower(),
        "piece_type": req.piece_type,
        "color": color,
        "embedding": emb,
        "embedding_version": EMBEDDING_VERSION,
        "created_at": firestore.SERVER_TIMESTAMP
    })

    USER_INDEX_BUILT[req.user_id] = False
    # Update in-memory index
    build_index(req.user_id)

    return {"status": "saved", "id": doc_ref.id, "user_id": req.user_id}

@app.put("/items/{item_id}")
def update_item(item_id: str, req: UpdateItem):
    """Updates an existing item, re-calculates embedding if needed, and rebuilds index."""
    
    doc_ref = db.collection(CLOTHES_COLLECTION).document(item_id)
    doc_snap = doc_ref.get()

    if not doc_snap.exists:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_data = doc_snap.to_dict()
    color_data = normalize_ui_color(req.color_family, req.color_attributes)

    if req.image_url != existing_data.get("image_url"):
        try:
            load_clip_model()
            img = download_image(req.image_url)
            emb = encode_image(img)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process new image: {e}")
    else:
        emb = existing_data.get("embedding")

    update_data = {
        "name": req.name,
        "size": req.size,
        "category": req.category.lower(),
        "piece_type": req.piece_type,
        "image_url": req.image_url,
        "color": color_data,
        "embedding": emb,
    }
    
    doc_ref.update(update_data)

    USER_INDEX_BUILT[req.user_id] = False
    try:
        build_index(req.user_id)
    except Exception as e:
        print(f"Warning: Index rebuild failed: {e}")

    return {"status": "updated", "id": item_id}

@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    """Deletes an item from Firestore and rebuilds the user's index."""
    
    doc_ref = db.collection(CLOTHES_COLLECTION).document(item_id)
    doc_snap = doc_ref.get()

    if not doc_snap.exists:
        raise HTTPException(status_code=404, detail="Item not found")

    item_data = doc_snap.to_dict()
    user_id = item_data.get("user_id")

    doc_ref.delete()

    if user_id:
        USER_INDEX_BUILT[user_id] = False
        try:
            build_index(user_id)
        except Exception as e:
            print(f"Warning: Failed to rebuild index for user {user_id}: {e}")
            
    return {"status": "deleted", "id": item_id}

@app.post("/rebuild_cache/")
def rebuild_cache():
    """Re-encode images for all clothes in the database."""
    load_clip_model()

    docs = fetch_all_clothes()
    updated = 0

    for d in docs:
        img_url = d.get("image_url")
        if not img_url:
            continue

        if d.get("embedding_version") == EMBEDDING_VERSION:
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

    # rebuild per-user cache
    all_user_ids = fetch_all_user_ids()
    for user_id in all_user_ids:
        build_index(user_id)

    return {
        "updated_embeddings": updated,
        "users_reindexed": len(all_user_ids)
    }

@app.get("/event-rules")
def get_event_rules():
    return event_rules

@app.post("/recommend/", response_model=RecommendationResult)
def recommend(req: RecommendRequest):
    # Ensure the CLIP model and index are loaded
    if not MODEL_LOADED:
        print("Model not loaded. Loading now...")
        load_clip_model()

    user_id = req.user_id
    if not user_id:
        raise HTTPException(400, "user_id is required")
    
    if not USER_INDEX_BUILT.get(user_id):
        build_index(user_id)

    # ------------------ EVENT, STYLE & OTHER LOGIC ------------------
    event_key = match_event(req.event)
    event_info = event_rules.get(event_key, {})
    weather_state = normalize_weather(req.weather, req.temp or 32)
    user_style = (req.style_preference or "").lower().strip()
    gender = (req.gender or "female").lower()

    is_freezing = weather_state == "freezing"

    # ------------------ TYPE DETECTION ------------------
    if is_freezing:
        allowed = FREEZING_FORCE_CATEGORIES
    else:
        allowed = get_allowed_categories(event_info, user_style, gender)

    for k in ("top", "bottom", "one_piece"):
        allowed[k] = [
            normalize_event_category(c)
            for c in allowed.get(k, [])
            if normalize_event_category(c) in EVENT_TO_UPLOAD_CATEGORY.values()
        ]

    if allowed["one_piece"]:
        detected_type = "one_piece"
    elif allowed["top"] and allowed["bottom"]:
        detected_type = "top_bottom"
    else:
        detected_type = "fallback"
    
    # ------------------ Choose a category ------------------
    if detected_type == "one_piece":
        category = allowed["one_piece"]
    elif detected_type == "top_bottom":
        top_cat = allowed["top"]
        bottom_cat = allowed["bottom"]
    else:
        top_cat = bottom_cat = category = None

    # ------------------ Select color & style ------------------
    colors = event_info.get("colors", [])
    forbidden_colors = event_info.get("forbidden_colors", [])
    chosen_color = random.choice(colors) if colors and colors != ["neutral"] else ""
    allowed_styles = event_info.get("allowed_styles", [])

    # ------------------ Prepare Shopping Links ------------------
    shopping_suggestions = {
        "one_piece": [],
        "top": [],
        "bottom": [],
    }

    def add_links(cat_list, part_name, color_override=None):
        if part_name not in shopping_suggestions:
            return
        
        c_name = cat_list[0] if isinstance(cat_list, list) and cat_list else "clothes"
        
        search_color = color_override if color_override else chosen_color
        
        if weather_state == "freezing":
            query = f"thermal winter {c_name}"
        else:
            query = f"{search_color} {user_style} {c_name}".strip()

        links = generate_online_links(query)
        
        shopping_suggestions[part_name] = format_links(links, query)
    
    # ------------------ Color filter helper ------------------
    def color_matches(item_color, allowed_colors, forbidden_colors=None):
        if not item_color or not item_color.get("family"):
            return not allowed_colors

        family = normalize_color(item_color.get("family"))
        attributes = item_color.get("attributes", [])

        # ---- Forbidden colors ----
        if forbidden_colors:
            for f in forbidden_colors:
                f = normalize_color(f)
                if f == family or f in attributes:
                    return False

        # ---- Allowed colors ----
        if not allowed_colors:
            return True

        for c in allowed_colors:
            c = normalize_color(c)
            if family in COLOR_FAMILIES.get(c, [c]):
                return True

        return False
    
    def colors_compatible(top, bottom):
        top_family = normalize_color(top["color"]["family"])
        bottom_family = normalize_color(bottom["color"]["family"])

        return bottom_family in COLOR_COMPATIBILITY.get(top_family, [])

    # ------------------ CLIP query builder ------------------
    def build_clip_prompt(category: str):
        """
        CLIP-safe, visual-only prompt.
        """

        base = CLIP_CANONICAL.get(category, category)
        
        if weather_state == "freezing":
            return f"a photo of thermal winter clothing, {base}"

        if user_style == "traditional":
            return f"a photo of {base}"
        
        SLEEVE_KEYWORDS = ["short-sleeve","long-sleeve"]
        adjectives = []
        
        has_intrinsic_sleeve = any(s in base for s in SLEEVE_KEYWORDS)

        for adj in WEATHER_RULES.get(weather_state, []):
            if adj in SLEEVE_KEYWORDS and has_intrinsic_sleeve:
                continue    
            if adj in base:
                continue

            adjectives.append(adj)

        prefix = " ".join(adjectives).strip()

        if prefix:
            return f"a photo of {prefix} {base}"

        return f"a photo of {base}"

    SIM_THRESHOLD = 0.12 

    def rank_by_clip(items, prompt):
        text_vec = encode_text(prompt)
        scored = [
            (cosine_similarity(text_vec, i["embedding"]), i)
            for i in items
        ]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [i for s, i in scored if s >= SIM_THRESHOLD]

    # ------------------ Safe find_items helper ------------------
    def find_items(user_items, allowed_categories, allowed_colors, forbidden_colors=None, exclude_ids=None):
        if not user_items or not allowed_categories:
            return None, []
        
        forbidden_colors = forbidden_colors or []
        exclude_ids = exclude_ids or []

        available_items = [i for i in user_items if i["id"] not in exclude_ids]

        if not available_items:
            return None, []

        # ---- Try strict match: category + color ----
        for cat in allowed_categories:
            prompt = build_clip_prompt(cat)
            candidates = [
                i for i in available_items if i["category"] == cat
            ]
            ranked = rank_by_clip(candidates, prompt)
            for item in ranked:
                if color_matches(item.get("color"), allowed_colors, forbidden_colors):
                    return item, ranked[1:4]

        # ---- Relax color constraint: category only ----            
        for cat in allowed_categories:
            prompt = build_clip_prompt(cat)
            candidates = [
                i for i in available_items if i["category"] == cat
            ]
            ranked = rank_by_clip(candidates, prompt)
            for item in ranked:
                if color_matches(item.get("color"), allowed_colors=[], forbidden_colors=forbidden_colors):
                    return item, ranked[1:4]

        # Failed
        return None, []

    excluded = req.exclude_item_ids
    # ------------------ Generate recommendations ------------------
    if detected_type == "one_piece":
        top, alt_tops = find_items(USER_INDEX[user_id]["one_piece"], allowed["one_piece"], colors, forbidden_colors, exclude_ids=excluded)

        if not top:
            add_links(allowed["one_piece"], "one_piece")

            return RecommendationResult(
                piece_type=detected_type,
                top=None, 
                bottom=None, 
                alternative_tops=[], 
                alternative_bottoms=[], 
                shoppingSuggestions=shopping_suggestions 
            )
            
        return RecommendationResult(
            piece_type=detected_type,
            top=serialize_item(top),
            bottom=None,
            alternative_tops=[serialize_item(i) for i in alt_tops],
            alternative_bottoms=[],
            shoppingSuggestions=shopping_suggestions
        )
           
    if detected_type == "top_bottom":
        # FIND TOP FIRST
        top, alt_tops = find_items(USER_INDEX[user_id]["tops"], allowed["top"], colors, forbidden_colors, exclude_ids=excluded)

        if not top:
            add_links(allowed["top"], "top")
            
            bottom_search_color = chosen_color

            if chosen_color:
                top_fam = normalize_color(chosen_color)
                
                compatible_list = COLOR_COMPATIBILITY.get(top_fam, [])
                
                valid_options = [c for c in compatible_list if c not in forbidden_colors]
                
                if valid_options:
                     bottom_search_color = valid_options[0]

            # Generate links for BOTTOM using the compatible color
            add_links(allowed["bottom"], "bottom", color_override=bottom_search_color) 

            return RecommendationResult(
                piece_type=detected_type,
                top=None,
                bottom=None,
                alternative_tops=[],
                alternative_bottoms=[],
                shoppingSuggestions=shopping_suggestions
            )

        # FIND MATCHING BOTTOM
        bottom_search_color = chosen_color 
        
        if top and top.get("color") and top["color"].get("family"):
            top_fam = normalize_color(top["color"]["family"])
            compatible_list = COLOR_COMPATIBILITY.get(top_fam, [])
            valid_options = [c for c in compatible_list if c not in forbidden_colors]
            
            if valid_options:
                bottom_search_color = valid_options[0]

        if user_style == "traditional":
            if top["category"] == "kurta":
                bottom, alt_bottoms = find_items(USER_INDEX[user_id]["bottoms"], ["dhoti", "veshti"], ["white"], forbidden_colors, exclude_ids=excluded)
            else:
                bottom, alt_bottoms = find_items(USER_INDEX[user_id]["bottoms"], allowed["bottom"], colors, forbidden_colors, exclude_ids=excluded)
        else:
             bottoms = USER_INDEX[user_id]["bottoms"]
             bottoms = [b for b in bottoms if b["category"] in allowed["bottom"] and b["id"] not in excluded]

             ranked_bottoms = []
             for cat in allowed["bottom"]:
                 prompt = build_clip_prompt(cat)
                 candidates = [b for b in bottoms if b["category"] == cat]
                 ranked_bottoms.extend(rank_by_clip(candidates, prompt))
             
             compatible = [
                 b for b in ranked_bottoms 
                 if color_matches(b.get("color"), colors, forbidden_colors) 
                 and colors_compatible(top, b)
             ]
             
             if not compatible:
                 compatible = [b for b in ranked_bottoms if colors_compatible(top, b)]
             
             if not compatible:
                 compatible = ranked_bottoms

             bottom = compatible[0] if compatible else None
             alt_bottoms = compatible[1:4] if compatible else []

        if not bottom:
            add_links(allowed["bottom"], "bottom", color_override=bottom_search_color)

        return RecommendationResult(
            piece_type=detected_type,
            top=serialize_item(top),
            bottom=serialize_item(bottom) if bottom else None,
            alternative_tops=[serialize_item(i) for i in alt_tops],
            alternative_bottoms=[serialize_item(i) for i in alt_bottoms],
            shoppingSuggestions=shopping_suggestions
        )
    
    return RecommendationResult(
        piece_type="fallback",
        top=None,
        bottom=None,
        alternative_tops=[],
        alternative_bottoms=[],
        shoppingSuggestions=shopping_suggestions
    )
