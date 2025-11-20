# mcc_map.py
# FULL MCC → category mapping (Python dict only)

MCC_CATEGORY_MAP = {
    # --- Groceries / Supermarkets ---
    "5411": "groceries",
    "5422": "groceries",
    "5441": "groceries",
    "5451": "groceries",
    "5499": "groceries",

    # --- Dining / Restaurants / Fast Food ---
    "5812": "dining",
    "5813": "dining",
    "5814": "fast_food",

    # --- Shopping / Retail / Online marketplaces ---
    "5310": "shopping",
    "5311": "shopping",
    "5331": "shopping",
    "5399": "shopping",
    "5611": "shopping",
    "5621": "shopping",
    "5631": "shopping",
    "5651": "shopping",
    "5661": "shopping",
    "5691": "shopping",
    "5732": "shopping",
    "5734": "shopping",
    "5941": "shopping",
    "5944": "shopping",
    "5947": "shopping",
    "5999": "shopping",
    "5262": "online_shopping",

    # --- Travel: airlines, hotels, agencies ---
    "3000": "travel_air",
    "3001": "travel_air",
    "3002": "travel_air",
    "3020": "travel_air",
    "3058": "travel_air",
    "3066": "travel_air",
    "3075": "travel_air",
    "3299": "travel_air",
    "4511": "travel_air",

    "7011": "travel_hotel",
    "7012": "travel_hotel",
    "5811": "travel_hotel",

    "4722": "travel_agency",
    "5962": "travel_agency",

    "4112": "transport",
    "4111": "transport",
    "4121": "ride_hailing",
    "4131": "transport",
    "4789": "transport",

    "7512": "travel_hotel",
    "7513": "travel_hotel",
    "7523": "transport",

    # --- Entertainment ---
    "7832": "entertainment",
    "7922": "entertainment",
    "7929": "entertainment",
    "7932": "entertainment",
    "7991": "entertainment",
    "7996": "entertainment",
    "7997": "entertainment",
    "7998": "entertainment",
    "7999": "entertainment",

    # --- Utilities / Telecom ---
    "4900": "utilities",
    "4812": "telecom",
    "4814": "telecom",
    "4899": "telecom",

    # --- Education ---
    "8211": "education",
    "8220": "education",
    "8241": "education",
    "8249": "education",
    "8299": "education",

    # --- Healthcare ---
    "8011": "healthcare",
    "8021": "healthcare",
    "8043": "healthcare",
    "8050": "healthcare",
    "8062": "healthcare",
    "8099": "healthcare",
    "5912": "healthcare",

    # --- Govt / Charity / Religious ---
    "8398": "charity",
    "8661": "religious",
    "9211": "govt",
    "9222": "govt",
    "9223": "govt",
    "9311": "govt",
    "9399": "govt",

    # --- Insurance / Financial / Quasi-cash ---
    "5960": "quasi_cash",
    "6010": "quasi_cash",
    "6011": "quasi_cash",
    "6012": "quasi_cash",
    "6050": "quasi_cash",
    "6051": "quasi_cash",
    "6211": "quasi_cash",
    "6300": "insurance",
    "6513": "quasi_cash"
}
