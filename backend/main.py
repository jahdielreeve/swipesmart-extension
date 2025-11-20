from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse

from mcc_map import MCC_CATEGORY_MAP
from rules import CARDS, compute_card_rewards

app = FastAPI()

# (from chrome://extensions)
EXTENSION_ID = "aaeaknjonfeaofipbnkfenbnfndkhmco"

origins = [
    f"chrome-extension://{EXTENSION_ID}",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # or ["POST"] if you want to be strict
    allow_headers=["*"],
)


class RecommendationRequest(BaseModel):
    url: str
    amount: float
    currency: str = "SGD"
    mode: str = "miles"  # "miles" or "cashback"
    enabled_cards: list[str] | None = None 


# Hardcoded merchant+MCC map (URL-based)
MERCHANT_MAP = {
    "shopee": ("shopping", True, "5311"),
    "lazada": ("shopping", True, "5311"),
    "qoo10": ("shopping", True, "5311"),
    "amazon": ("shopping", True, "5311"),
    "agoda": ("travel", True, "4722"),
    "booking": ("travel", True, "4722"),
    "expedia": ("travel", True, "4722"),
    "ntuc": ("groceries", False, "5411"),
    "fairprice": ("groceries", False, "5411"),
    "coldstorage": ("groceries", False, "5411"),
}


def category_from_mcc(mcc: str, fallback_category: str = "general") -> str:
    """Map MCC → category, or fall back if unknown."""
    if not mcc:
        return fallback_category
    return MCC_CATEGORY_MAP.get(mcc, fallback_category)


def get_merchant_info(url: str):
    """
    Basic v1:
    - Look at hostname (e.g. shopee.sg, agoda.com)
    - Match against MERCHANT_MAP keys
    Returns: (category, is_online, mcc)
    """
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    for key, (category, is_online, mcc) in MERCHANT_MAP.items():
        if key in host:
            return category, is_online, mcc

    # default fallback
    return "general", True, "0000"


@app.get("/")
def root():
    return {"message": "SwipeSmart backend running"}


@app.post("/recommend-card")
def recommend_card(req: RecommendationRequest):
    # 1) detect from URL first
    category_from_url, is_online, mcc = get_merchant_info(req.url)

    # 2) if MCC known, override category using MCC map
    category = category_from_mcc(mcc, fallback_category=category_from_url)

    # 3) sanitize mode
    mode = req.mode.lower()
    if mode not in ("miles", "cashback"):
        mode = "miles"

    breakdown = []
    best_card_result = None
    best_score = -1.0

    # 4) compute rewards for each card
    
    # filter cards by user selection (if provided)
    enabled = set(req.enabled_cards or [])
    if enabled:
        cards_to_consider = [c for c in CARDS if c["name"] in enabled]
    else:
        cards_to_consider = CARDS

    for card in cards_to_consider:
        result = compute_card_rewards(
            card=card,
            amount=req.amount,
            category=category,
            is_online=is_online,
            mcc=mcc,
            mode=mode,
            currency=req.currency,
        )
        breakdown.append(result)

        score = result["miles"] if mode == "miles" else result["cashback"]

        if score > best_score:
            best_score = score
            best_card_result = result

    # 5) sort the full breakdown
    breakdown = sorted(
        breakdown,
        key=lambda x: x["miles"] if mode == "miles" else x["cashback"],
        reverse=True,
    )

    # 6) no suitable card
    if not best_card_result:
        return {
            "best_card": None,
            "estimated_miles": 0.0,
            "estimated_cashback": 0.0,
            "category": category,
            "is_online": is_online,
            "mcc": mcc,
            "mode": mode,
            "reason": "No suitable card found with current rules.",
            "annual_fee_warning": None,
            "breakdown": breakdown,
        }

    # 7) annual fee notes
    annual_fee_warning = None
    fee = best_card_result.get("annual_fee")
    if fee:
        if best_card_result.get("annual_fee_waivable", True):
            annual_fee_warning = (
                f"{best_card_result['card_name']} has around S${fee} annual fee. Usually waivable."
            )
        else:
            annual_fee_warning = (
                f"{best_card_result['card_name']} has around S${fee} annual fee and may NOT be waivable."
            )

    # 8) human-friendly reasoning
    reason_parts = [
        f"Picked {best_card_result['card_name']} based on category '{category}', "
        f"online={is_online}, MCC={mcc}."
    ]

    if best_card_result.get("blocked"):
        reason_parts.append("Note: this card is blocked for this category/MCC.")

    if best_card_result.get("cap_note"):
        reason_parts.append(best_card_result["cap_note"])

    if best_card_result.get("notes"):
        reason_parts.append(best_card_result["notes"])

    reason = " ".join(reason_parts).strip()

    # 9) final response
    return {
        "best_card": best_card_result["card_name"],
        "estimated_miles": best_card_result.get("miles", 0.0),
        "estimated_cashback": best_card_result.get("cashback", 0.0),
        "category": category,
        "is_online": is_online,
        "mcc": mcc,
        "mode": mode,
        "reason": reason,
        "annual_fee_warning": annual_fee_warning,
        "breakdown": breakdown,
    }
