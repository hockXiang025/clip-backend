import os
import io
import re
from datetime import datetime
from typing import List, Dict, Any
import random

import torch
import requests
from PIL import Image
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from difflib import get_close_matches
from urllib.parse import quote

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

# -------------------- EVENT RULES --------------------
# This dictionary combines Malay, Chinese, and general events
event_rules = {

    # ---------------- MALAY CULTURAL EVENTS ----------------
    "malay_wedding": {
        "type": "traditional",
        "allowed_styles": ["traditional", "semi-formal", "formal"],
        "colors": ["gold", "green", "blue", "purple"],
        "traditional": {
            "female": ["baju kurung", "kebaya"],
            "male": ["baju melayu"]
        },
        "style_categories": {
            "semi-formal": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["long skirt", "palazzo pants"]
                },
                "male": {
                    "top": ["long-sleeve shirt"],
                    "bottom": ["trousers"]
                }
            },
            "formal": {
                "female": {
                    "one_piece": ["evening gown"]
                },
                "male": {
                    "top": ["dress shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "aqiqah": {
        "type": "traditional",
        "allowed_styles": ["traditional", "modest"],
        "colors": ["soft", "neutral", "pastel"],
        "traditional": {
            "female": ["baju kurung", "kebaya"],
            "male": ["baju melayu"]
        },
        "style_categories": {
            "modest": {
                "female": {
                    "top": ["long-sleeve blouse"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["long-sleeve shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "hari_raya_aidilfitri": {
        "type": "traditional",
        "allowed_styles": ["traditional", "modest"],
        "colors": ["bright", "green", "yellow", "blue", "pink", "purple"],
        "traditional": {
            "female": ["baju kurung", "kebaya"],
            "male": ["baju melayu"]
        },
        "style_categories": {
            "modest": {
                "female": {
                    "top": ["long-sleeve blouse"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["collared shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "circumcision_ceremony": {
        "type": "general",
        "allowed_styles": ["casual", "modest"],
        "colors": ["neutral", "blue", "white"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            },
            "modest": {
                "female": {
                    "top": ["tunic"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["long-sleeve top"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "malay_engagement_ceremony": {
        "type": "traditional",
        "allowed_styles": ["traditional", "semi-formal"],
        "colors": ["jewel tone", "gold", "soft"],
        "traditional": {
            "female": ["baju kurung", "kebaya"],
            "male": ["baju melayu"]
        },
        "style_categories": {
            "semi-formal": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["dress shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "majlis_rasmi_awards_ceremony": {
        "type": "general",
        "allowed_styles": ["formal"],
        "colors": ["dark", "neutral", "navy", "black"],
        "style_categories": {
            "formal": {
                "female": {"one_piece": ["evening gown"]},
                "male": {
                    "top": ["dress shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    # ---------------- CHINESE CULTURAL EVENTS ----------------
    "chinese_engagement_ceremony": {
        "type": "traditional",
        "allowed_styles": ["traditional", "semi-formal"],
        "colors": ["red", "soft", "gold"],
        "traditional": {
            "female": ["cheongsam", "qipao"],
            "male": ["tang suit"]
        },
        "style_categories": {
            "semi-formal": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["collared shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "chinese_wedding": {
        "type": "traditional",
        "allowed_styles": ["traditional", "formal"],
        "colors": ["red", "gold"],
        "traditional": {
            "female": ["cheongsam", "qipao"],
            "male": ["tang suit"]
        },
        "style_categories": {
            "formal": {
                "female": {"one_piece": ["evening dress"]},
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "baby_shower": {
        "type": "traditional",
        "allowed_styles": ["traditional", "festive"],
        "colors": ["red", "pink", "soft", "gold"],
        "traditional": {
            "female": ["cheongsam", "qipao"],
            "male": ["tang suit"]
        },
        "style_categories": {
            "festive": {
                "female": {"one_piece": ["dress"]},
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "chinese_new_year": {
        "type": "traditional",
        "allowed_styles": ["traditional", "casual"],
        "colors": ["red", "gold", "orange", "bright"],
        "traditional": {
            "female": ["cheongsam", "qipao"],
            "male": ["tang suit"]
        },
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["skirt"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "mid_autumn_festival": {
        "type": "general",
        "allowed_styles": ["semi-formal", "casual"],
        "colors": ["red", "gold", "green", "pastel"],
        "style_categories": {
            "semi-formal": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            },
            "casual": {
                "female": {
                    "top": ["blouse", "t-shirt"],
                    "bottom": ["skirt", "jeans"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["jeans"]
                }
            }
        }
    },

    "dragon_boat_festival": {
        "type": "traditional",
        "allowed_styles": ["traditional", "casual", "festive"],
        "colors": ["green", "white", "red", "gold"],
        "traditional": {
            "female": ["cheongsam", "qipao"],
            "male": ["tang suit"]
        },
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["t-shirt", "blouse"],
                    "bottom": ["jeans", "skirt"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["jeans"]
                }
            },
            "festive": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "chinese_birthday": {
        "type": "general",
        "allowed_styles": ["casual", "semi-formal", "festive"],
        "colors": ["bright", "red", "yellow", "pastel"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["t-shirt", "blouse"],
                    "bottom": ["jeans", "skirt"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["jeans"]
                }
            },
            "semi-formal": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            },
            "festive": {
                "female": {
                    "one_piece": ["dress", "jumpsuit"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "temple_prayer_ceremony": {
        "type": "general",
        "allowed_styles": ["casual", "modest"],
        "colors": ["soft", "white", "neutral"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            },
            "modest": {
                "female": {
                    "top": ["tunic"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["long-sleeve top"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "chinese_funeral": {
        "type": "general",
        "allowed_styles": ["formal"],
        "colors": ["white", "black", "neutral"],
        "style_categories": {
            "formal": {
                "female": {
                    "top": ["blouse", "long-sleeve top"],
                    "bottom": ["long skirt", "trousers"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    # ---------------- INDIAN CULTURAL EVENTS (Malaysia) ----------------
    "deepavali": {
        "type": "traditional",
        "allowed_styles": ["traditional", "festive"],
        "colors": ["bright", "gold", "red", "orange"],
        "traditional": {
            "female": ["saree","salwar kameez"],
            "male": ["kurta", "dhoti"]
        },
        "style_categories": {
            "festive": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "thaipusam": {
        "type": "traditional",
        "allowed_styles": ["traditional", "modest"],
        "colors": ["white", "yellow", "red"],
        "traditional": {
            "female": ["saree", "salwar kameez"],
            "male": ["veshti", "kurta"]
        },
        "style_categories": {
            "modest": {
                "female": {
                    "top": ["tunic"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["long-sleeve top"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "pongal": {
        "type": "traditional",
        "allowed_styles": ["traditional", "casual"],
        "colors": ["white", "yellow", "orange"],
        "traditional": {
            "female": ["pavadai", "saree"],
            "male": ["veshti", "kurta"]
        },
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    # ---------------- GENERAL EVENTS ----------------
    "work_at_workplace": {
        "type": "general",
        "allowed_styles": ["formal", "semi-formal", "smart-casual"],
        "colors": ["neutral", "dark", "black", "navy", "grey"],
        "style_categories": {
            "formal": {
                "female": {
                    "top": ["blouse", "long-sleeve top"],
                    "bottom": ["trousers", "long skirt"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            },
            "semi-formal": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["trousers", "skirt"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            },
            "smart-casual": {
                "female": {
                    "top": ["blouse", "tunic"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },
    
    "corporate_event": {
        "type": "general",
        "allowed_styles": ["formal", "semi-formal"],
        "colors": ["neutral", "dark", "black", "navy"],
        "style_categories": {
            "formal": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["trousers", "long skirt"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            },
            "semi-formal": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "government_office": {
        "type": "general",
        "allowed_styles": ["formal"],
        "colors": ["neutral", "navy", "black"],
        "style_categories": {
            "formal": {
                "female": {
                    "top": ["blouse", "long-sleeve top"],
                    "bottom": ["long skirt", "trousers"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "hospital_visit": {
        "type": "general",
        "allowed_styles": ["comfortable"],
        "colors": ["soft", "neutral"],
        "style_categories": {
            "comfortable": {
                "female": {
                    "top": ["t-shirt", "tunic"],
                    "bottom": ["pants", "long skirt"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "western_birthday_party": {
        "type": "general",
        "allowed_styles": ["casual", "semi-formal", "festive"],
        "colors": ["bright", "soft", "pastel", "pink", "blue"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["t-shirt", "blouse"],
                    "bottom": ["jeans", "skirt"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["jeans"]
                }
            },
            "semi-formal": {
                "female": {
                    "one_piece": ["dress"],
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            },
            "festive": {
                "female": {
                    "one_piece": ["dress", "jumpsuit"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "exercising": {
        "type": "general",
        "allowed_styles": ["sporty", "casual"],
        "colors": ["bright", "dark", "black", "blue"],
        "style_categories": {
            "sporty": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            },
            "casual": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "climbing": {
        "type": "general",
        "allowed_styles": ["sporty"],
        "colors": ["neutral", "dark"],
        "style_categories": {
            "sporty": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["pants", "jeans"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "casual_outing": {
        "type": "general",
        "allowed_styles": ["casual"],
        "colors": ["bright", "soft", "pastel"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["t-shirt", "blouse"],
                    "bottom": ["jeans", "skirt"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["jeans"]
                }
            }
        }
    },

    "dating": {
        "type": "general",
        "allowed_styles": ["casual", "semi-formal", "elegant"],
        "colors": ["soft", "neutral", "pastel", "black", "maroon"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["jeans"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["jeans"]
                }
            },
            "semi-formal": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            },
            "elegant": {
                "female": {
                    "one_piece": ["maxi dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "formal_dinner": {
        "type": "general",
        "allowed_styles": ["formal", "casual"],
        "colors": ["dark", "neutral", "black", "navy", "maroon"],
        "style_categories": {
            "formal": {
                "female": {
                    "one_piece": ["gown"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            },
            "casual": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "stay_at_home": {
        "type": "general",
        "allowed_styles": ["casual", "comfortable"],
        "colors": ["soft", "neutral", "pastel"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            },
            "comfortable": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "work_from_home": {
        "type": "general",
        "allowed_styles": ["casual", "smart-casual"],
        "colors": ["neutral", "soft", "blue", "grey"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            },
            "smart-casual": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "travelling": {
        "type": "general",
        "allowed_styles": ["casual", "comfortable", "sporty"],
        "colors": ["neutral", "dark", "soft"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["jeans"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["jeans"]
                }
            },
            "comfortable": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            },
            "sporty": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "public_holiday_gathering": {
        "type": "general",
        "allowed_styles": ["festive", "semi-formal"],
        "colors": ["bright", "red", "yellow", "green", "blue"],
        "style_categories": {
            "festive": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            },
            "semi-formal": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    },

    "university": {
        "type": "general",
        "allowed_styles": ["casual", "smart-casual", "modest"],
        "colors": ["neutral", "soft", "dark", "blue"],
        "style_categories": {
            "casual": {
                "female": {
                    "top": ["t-shirt"],
                    "bottom": ["jeans"]
                },
                "male": {
                    "top": ["t-shirt"],
                    "bottom": ["jeans"]
                }
            },
            "smart-casual": {
                "female": {
                    "top": ["blouse"],
                    "bottom": ["pants"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            },
            "modest": {
                "female": {
                    "top": ["tunic"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "western_wedding": {
        "type": "general",
        "allowed_styles": ["formal", "semi-formal", "elegant"],
        "colors": ["pastel", "soft", "neutral", "dark"],
        "style_categories": {
            "formal": {
                "female": {
                    "one_piece": ["gown"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            },
            "semi-formal": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            },
            "elegant": {
                "female": {
                    "one_piece": ["maxi dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "open_house": {
        "type": "general",
        "allowed_styles": ["festive", "semi-formal"],
        "colors": ["bright", "soft"],
        "style_categories": {
            "festive": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["trousers"]
                }
            },
            "semi-formal": {
                "female": {
                    "one_piece": ["dress"]
                },
                "male": {
                    "top": ["shirt"],
                    "bottom": ["pants"]
                }
            }
        }
    }
}


# -------------------- FASTAPI --------------------
app = FastAPI(title="CLIP Clothes Recommender")

# -------------------- GLOBAL RUNTIME --------------------
model = None
preprocess = None
MODEL_LOADED = False
CACHE_REBUILT = False

INDEX_TOP: List[Dict[str, Any]] = []
INDEX_BOTTOM: List[Dict[str, Any]] = []
USER_INDEX: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
USER_INDEX_BUILT = {}

# Pre-process event rule keys so matching is easier
CANONICAL_KEYS = list(event_rules.keys())

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
    global INDEX_TOP, INDEX_BOTTOM, INDEX_ONE_PIECE, USER_INDEX_BUILT

    first_time = not USER_INDEX_BUILT.get(user_id)

    if USER_INDEX_BUILT.get(user_id):
        return True # Already built, skip
    
    INDEX_TOP = []
    INDEX_BOTTOM = []
    INDEX_ONE_PIECE = []

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
            "embedding": emb
        }

        if d.get("piece_type") == "top":
            USER_INDEX[user_id]["tops"].append(entry)
        elif d.get("piece_type") == "bottom":
            USER_INDEX[user_id]["bottoms"].append(entry)
        elif d.get("piece_type") == "one_piece":
            USER_INDEX[user_id]["one_piece"].append(entry)

    if first_time:
        print(f"Index built (first time): {len(INDEX_TOP)} tops, {len(INDEX_BOTTOM)} bottoms")

    USER_INDEX_BUILT[user_id] = True
    return True

def normalize_event(event: str) -> str:
    """
    Since UI restricts event selection,
    this only ensures consistent formatting.
    """
    if not event:
        return ""
    return event.lower().strip()

def match_event(user_event: str) -> str:
    """
    Directly validate event against EVENT_RULES keys.
    """
    if not user_event:
        return ""

    event_key = user_event.lower().strip()

    # Direct match only
    if event_key in event_rules:
        return event_key

    # Safety fallback (should not happen)
    return ""

def get_allowed_categories(event_info, style, gender):
    style_map = event_info.get("style_categories", {})
    style_info = style_map.get(style, {})
    gender_info = style_info.get(gender, {})

    return {
        "one_piece": gender_info.get("one_piece", []),
        "top": gender_info.get("top", []),
        "bottom": gender_info.get("bottom", [])
    }

# -------------------- EXTERNAL STORE LINKS --------------------
def generate_online_links(query: str) -> Dict[str, Any]:
    """
    Generates online shopping links for Shopee, Lazada, Taobao
    using the query string (e.g., "red dress long baju kurung").
    """
    # Simple URL encoding
    import urllib.parse
    q_encoded = urllib.parse.quote(query)

    links = {
        "shopee": f"https://shopee.com.my/search?keyword={q_encoded}",
        "lazada": f"https://www.lazada.com.my/catalog/?q={q_encoded}",
        "taobao": f"https://world.taobao.com/search/search.htm?q={q_encoded}"
    }

    # Prices/images could be added if you scrape APIs or use official feeds
    return links

# -------------------- API MODELS --------------------
class UploadItem(BaseModel):
    name: str
    size: str
    image_url: str
    category: str
    piece_type: str # top || bottom || one-piece
    user_id: str

class RecommendRequest(BaseModel):
    user_id: str = ""
    season: str = ""
    weather: str = ""
    event: str = ""
    style_preference: str = ""
    gender: str = ""

class RecommendationResult(BaseModel):
    top: Dict[str, Any] | None = None
    bottom: Dict[str, Any] | None = None
    alternative_tops: List[Dict[str, Any]] = []
    alternative_bottoms: List[Dict[str, Any]] = []
    shoppingSuggestions: List[Dict[str, Any]] = []

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

    load_clip_model()

    try:
        img = download_image(req.image_url)
        emb = encode_image(img)
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
        "embedding": emb,
        "embedding_version": EMBEDDING_VERSION,
        "created_at": firestore.SERVER_TIMESTAMP
    })

    # Update in-memory index
    build_index(req.user_id)

    def clear_user_cache(user_id: str):
        USER_INDEX_BUILT[user_id] = False

    return {"status": "saved", "id": doc_ref.id, "user_id": req.user_id}


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
        return RecommendationResult(
            top=None,
            bottom=None,
            alternative_tops=[],
            alternative_bottoms=[],
            shoppingSuggestions=[]
        )
    user_id = req.user_id
    if not user_id:
        raise HTTPException(400, "user_id is required")
    
    if not USER_INDEX_BUILT.get(user_id):
        build_index(user_id)

    # ------------------ EVENT & STYLE LOGIC ------------------
    event_key = match_event(req.event)  # match input to event_rules keys
    event_info = event_rules.get(event_key, {})

    user_style = (req.style_preference or "").lower().strip()
    gender = (req.gender or "female").lower()

    # ------------------ TYPE DETECTION ------------------
    allowed = get_allowed_categories(event_info, user_style, gender)

    if allowed["one_piece"]:
        detected_type = "one_piece"
    elif allowed["top"] and allowed["bottom"]:
        detected_type = "top_bottom"
    else:
        detected_type = "fallback"
    
    # ------------------ Randomly choose a category if needed ------------------
    if detected_type == "one_piece":
        category = random.choice(allowed["one_piece"])
    elif detected_type == "top_bottom":
        top_cat = random.choice(allowed["top"])
        bottom_cat = random.choice(allowed["bottom"])
    else:
        top_cat = bottom_cat = category = None

    # ------------------ Select color & style ------------------
    colors = event_info.get("colors", [])
    chosen_color = random.choice(colors) if colors else ""
    allowed_styles = event_info.get("allowed_styles", [])
    chosen_styles = [user_style] if user_style in allowed_styles else ([allowed_styles[0]] if allowed_styles else [])

    # Traditional items for event
    traditional_map = event_info.get("traditional", {})
    traditional_items = traditional_map.get(gender, []) if "traditional" in chosen_styles else []
    trad_item = random.choice(traditional_items) if traditional_items else ""

    # ------------------ Prepare Shopping Links ------------------
    purchase_query = " ".join(filter(None, [chosen_color] + chosen_styles + ([trad_item] if trad_item else []) + 
                    ([category] if detected_type == "one_piece" else [top_cat, bottom_cat] if detected_type=="top_bottom" else []))) 
    
    links_dict = generate_online_links(purchase_query)

    shopping_suggestions = [ 
        {"platform": p.capitalize(), "name": purchase_query or "Clothing", 
         "price": "Check online", "url": u} for p, u in links_dict.items() 
    ]

    # ------------------ Handle error ------------------
    user_index = USER_INDEX.get(user_id, {"tops": [], "bottoms": [], "one_piece": []}) 
    
    if not user_index["tops"]:
        return RecommendationResult(
            top=None, bottom=None,
            alternative_tops=[], 
            alternative_bottoms=[], 
            shoppingSuggestions=shopping_suggestions 
        ) 
    
    if not user_index["bottoms"]:
        return RecommendationResult(
            top=None, 
            bottom=None, 
            alternative_tops=[], 
            alternative_bottoms=[], 
            shoppingSuggestions=shopping_suggestions 
        )
        
    if detected_type == "one_piece" and not user_index["one_piece"]:
        return RecommendationResult(
            top=None, 
            bottom=None, 
            alternative_tops=[], 
            alternative_bottoms=[], 
            shoppingSuggestions=shopping_suggestions 
        )
    
    if user_style == "traditional" and detected_type != "one_piece":
        raise HTTPException(400, "Traditional style must use one_piece clothing")

    # ------------------ CLIP query builder ------------------
    def build_clip_query(item_type, item_category=None):
        parts = []
        if req.weather:
            parts.append(req.weather)
        if chosen_color:
            parts.append(chosen_color)
        parts += chosen_styles
        if trad_item:
            parts.append(trad_item)
        if item_category:
            parts.append(item_category)
        return " ".join(parts).strip() or item_type

    SIM_THRESHOLD = 0.22 if traditional_items else 0.30

    # ------------------ Safe find_items helper ------------------
    def find_items(index_list, allowed_categories, colors, strict=True):
        if not index_list or not allowed_categories: 
            return None, [] 
        
        # Same category + color 
        for cat in allowed_categories: 
            for color in colors: 
                query = build_clip_query("", cat) 
                if color: 
                    query = f"{color} {query}"

                text_vec = encode_text(query) 
                scored = [
                    {"score": cosine_similarity(text_vec, item["embedding"]), "item": item} 
                    for item in index_list 
                    if item.get("category") == cat 
                ]

                matched = [x for x in scored if x["score"] >= SIM_THRESHOLD] 
                if matched: 
                    matched.sort(key=lambda x: x["score"], reverse=True) 
                    return matched[0]["item"], [x["item"] for x in matched[1:4]] 
        
        # Same category, different color 
        for cat in allowed_categories: 
            query = build_clip_query("", cat) 
            text_vec = encode_text(query) 
            scored = [ 
                {"score": cosine_similarity(text_vec, item["embedding"]), "item": item} 
                for item in index_list 
                if item.get("category") == cat 
            ]

            if scored: 
                scored.sort(key=lambda x: x["score"], reverse=True) 
                return scored[0]["item"], [x["item"] for x in scored[1:4]] 
            
            # Strict stop (traditional) 
            if strict: 
                return None, [] 
            
            # Non-strict fallback (casual/general only) 
            query = build_clip_query("", "") 
            text_vec = encode_text(query) 
            scored = [ 
                {"score": cosine_similarity(text_vec, item["embedding"]), "item": item} 
                for item in index_list 
            ]

            scored.sort(key=lambda x: x["score"], reverse=True) 
            return scored[0]["item"], [x["item"] for x in scored[1:4]]


    # ------------------ Generate recommendations ------------------
    is_traditional = user_style == "traditional"

    if detected_type == "one_piece":
        top, alt_tops = find_items(USER_INDEX[user_id]["one_piece"], allowed["one_piece"], colors, strict=is_traditional)
        return RecommendationResult(
            top=top,
            bottom=None,
            alternative_tops=alt_tops,
            alternative_bottoms=[],
            shoppingSuggestions=shopping_suggestions
        )

    top, alt_tops = find_items(USER_INDEX[user_id]["tops"], allowed["top"], colors, strict=False)
    bottom, alt_bottoms = find_items(USER_INDEX[user_id]["bottoms"], allowed["bottom"], colors, strict=False)

    return RecommendationResult(
        top=top,
        bottom=bottom,
        alternative_tops=alt_tops,
        alternative_bottoms=alt_bottoms,
        shoppingSuggestions=shopping_suggestions
    )
