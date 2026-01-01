# -------------------- EVENT RULES --------------------
# This dictionary combines Malay, Chinese, and general events
event_rules = {

    # ---------------- MALAY CULTURAL EVENTS ----------------
    "malay_wedding": {
        "type": "traditional",
        "allowed_styles": ["traditional", "semi-formal", "formal"],
        "colors": ["gold", "green", "blue", "purple"],
        "forbidden_colors": ["black", "neon"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["baju kurung", "baju kebaya"]
                },
                "male": {
                    "one_piece": ["baju melayu"]
                }
            },
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
        "forbidden_colors": ["neon", "black", "red"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["baju kurung", "baju kebaya"]
                },
                "male": {
                    "one_piece": ["baju melayu"]
                }
            },
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
        "forbidden_colors": ["black", "dark"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["baju kurung", "baju kebaya"]
                },
                "male": {
                    "one_piece": ["baju melayu"]
                }
            },
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
        "forbidden_colors": ["neon", "black"],
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
                    "top": ["long-sleeve t-shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "malay_engagement_ceremony": {
        "type": "traditional",
        "allowed_styles": ["traditional", "semi-formal"],
        "colors": ["jewel tone", "gold", "soft"],
        "forbidden_colors": ["neon", "black"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["baju kurung", "baju kebaya"]
                },
                "male": {
                    "one_piece": ["baju melayu"]
                }
            },
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
        "forbidden_colors": ["neon", "bright"],
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
        "forbidden_colors": ["black", "white", "dark"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["qipao", "cheongsam"]
                },
                "male": {
                    "top": ["tang suit"],
                    "bottom": ["trousers"]
                }
            },
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
        "forbidden_colors": ["black", "white", "dark"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["qipao", "cheongsam"]
                },
                "male": {
                    "one_piece": ["tang suit"]
                }
            },
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
        "forbidden_colors": ["black", "dark"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["qipao", "cheongsam"]
                },
                "male": {
                    "one_piece": ["tang suit"]
                }
            },
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
        "forbidden_colors": ["black", "white", "dark"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["qipao", "cheongsam"]
                },
                "male": {
                    "one_piece": ["tang suit"]
                }
            },
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
        "forbidden_colors": ["black"],
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
        "forbidden_colors": ["black", "dark"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["qipao", "cheongsam"]
                },
                "male": {
                    "one_piece": ["tang suit"]
                }
            },
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
        "forbidden_colors": ["black"],
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
        "forbidden_colors": ["neon", "bright"],
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
                    "top": ["t-shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "chinese_funeral": {
        "type": "general",
        "allowed_styles": ["formal"],
        "colors": ["white", "black", "neutral"],
        "forbidden_colors": ["red", "bright", "neon"],
        "style_categories": {
            "formal": {
                "female": {
                    "top": ["blouse", "long-sleeve shirt"],
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
        "forbidden_colors": ["black", "dark"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["saree","salwar kameez"]
                },
                "male": {
                    "top": ["kurta"],
                    "bottom": ["dhoti"]
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

    "thaipusam": {
        "type": "traditional",
        "allowed_styles": ["traditional", "modest"],
        "colors": ["white", "yellow", "red"],
        "forbidden_colors": ["black", "dark", "neon"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["saree", "salwar kameez"]
                },
                "male": {
                    "top": ["kurta"],
                    "bottom": ["veshti"]
                }
            },
            "modest": {
                "female": {
                    "top": ["tunic"],
                    "bottom": ["long skirt"]
                },
                "male": {
                    "top": ["long-sleeve t-shirt"],
                    "bottom": ["trousers"]
                }
            }
        }
    },

    "pongal": {
        "type": "traditional",
        "allowed_styles": ["traditional", "casual"],
        "colors": ["white", "yellow", "orange"],
        "forbidden_colors": ["black", "dark"],
        "style_categories": {
            "traditional": {
                "female": {
                    "one_piece": ["saree", "pavadai"]
                },
                "male": {
                    "top": ["kurta"],
                    "bottom": ["veshti"]
                }
            },
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
        "forbidden_colors": ["neon", "bright"],
        "style_categories": {
            "formal": {
                "female": {
                    "top": ["blouse", "long-sleeve shirt"],
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
        "forbidden_colors": ["neon", "bright"],
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
        "forbidden_colors": ["neon", "bright"],
        "style_categories": {
            "formal": {
                "female": {
                    "top": ["blouse", "long-sleeve shirt"],
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
        "forbidden_colors": ["neon", "bright"],
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
        "forbidden_colors": ["black"],
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
        "forbidden_colors": [],
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
        "forbidden_colors": [],
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
        "forbidden_colors": [],
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
        "forbidden_colors": ["neon"],
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
        "forbidden_colors": ["neon", "bright"],
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
        "forbidden_colors": [],
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
        "forbidden_colors": [],
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
        "forbidden_colors": [],
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
        "forbidden_colors": [],
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
        "forbidden_colors": ["neon"],
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
        "forbidden_colors": ["white", "neon"],
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
        "forbidden_colors": ["black"],
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