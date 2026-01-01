COLOR_NORMALIZATION = {
    # ---- Core hues ----
    "red": "red","maroon": "red","burgundy": "red",
    "blue": "blue","navy": "blue","cyan": "blue",
    "green": "green","olive": "green",
    "yellow": "yellow","gold": "yellow","orange": "orange",
    "purple": "purple",
    "pink": "pink",
    "black": "black",
    "white": "white",
    "grey": "neutral","gray": "neutral","beige": "neutral","brown": "neutral",

    # ---- Semantic groups ----
    "soft": "pastel","pastel": "pastel",
    "bright": "bright","jewel tone": "bright",
    "dark": "dark",
    "neutral": "neutral"
}

COLOR_FAMILIES = {
    "red": ["red", "maroon", "burgundy"],
    "blue": ["blue", "navy", "cyan"],
    "green": ["green", "olive"],
    "yellow": ["yellow", "gold"],
    "orange": ["orange"],
    "purple": ["purple"],
    "pink": ["pink"],
    "white": ["white", "ivory", "cream"],
    "black": ["black"],
    "neutral": ["beige", "brown", "grey", "gray", "white"],

    # semantic families
    "pastel": ["pastel", "soft", "cream", "light"],
    "bright": ["bright", "jewel tone"],
    "dark": ["dark", "black", "navy"]
}

COLOR_COMPATIBILITY = {
    # ---- Safe bases ----
    "neutral": ["neutral", "pastel", "bright", "dark", "red", "blue", "green"],
    "white": ["neutral", "pastel", "bright", "dark"],
    "black": ["neutral", "bright", "red"],

    # ---- Tones ----
    "pastel": ["neutral", "pastel"],
    "bright": ["neutral", "dark"],
    "dark": ["neutral", "bright"],

    # ---- Hues ----
    "red": ["neutral", "black", "white", "gold"],
    "blue": ["neutral", "white", "grey"],
    "green": ["neutral", "beige", "gold"],
    "yellow": ["neutral", "white"],
    "purple": ["neutral", "silver", "white"],
    "orange": ["neutral", "white"]
}