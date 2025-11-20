import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "cards_data.json"

with open(DATA_PATH, "r") as f:
    CARDS = json.load(f)


def compute_card_rewards(
    card: dict,
    amount: float,
    category: str,
    is_online: bool,
    mcc: str,
    mode: str = "miles",
    currency: str = "SGD",
) -> dict:
    """
    Returns a dict with miles, cashback, blocked/cap info, notes, etc.
    mode = "miles" or "cashback".
    Handles FCY, SGD-only bonus cards, caps, etc.
    """

    name = card["name"]
    mode = mode.lower()
    currency = currency.upper()
    is_fcy = currency != "SGD"

    # ---------- 1) blocked logic ----------
    blocked = False
    blocked_reason = ""

    blocked_categories = card.get("blocked_categories", [])
    blocked_mccs = card.get("blocked_mccs", [])

    if category in blocked_categories:
        blocked = True
        blocked_reason = f"Category '{category}' is blocked for {name}."

    if mcc and mcc in blocked_mccs:
        blocked = True
        extra = f"MCC {mcc} is blocked for {name}."
        blocked_reason = (blocked_reason + " " + extra).strip()

    if blocked:
        return {
            "card_name": name,
            "card_type": card.get("type", "miles"),
            "miles": 0.0,
            "cashback": 0.0,
            "blocked": True,
            "blocked_reason": blocked_reason or "Blocked category/MCC.",
            "capped": False,
            "cap_note": "",
            "notes": card.get("notes", ""),
            "annual_fee": card.get("annual_fee"),
            "annual_fee_waivable": card.get("annual_fee_waivable", True),
        }

    # ---------- 2) miles logic ----------
    base_mpd = card.get("base_mpd", 0.0)
    fcy_mpd = card.get("fcy_mpd")  # optional
    category_mpd = card.get("category_mpd", {})
    online_mpd = card.get("online_mpd")
    no_fcy_bonus = card.get("no_fcy_bonus", False)

    # start from base
    mpd = base_mpd

    # online bonus
    if is_online and online_mpd:
        mpd = online_mpd

    # category-specific override (stronger than generic online)
    if category in category_mpd:
        mpd = category_mpd[category]

    # FCY adjustments
    if is_fcy:
        if no_fcy_bonus:
            # this card's bonuses are SGD-only → FCY gets base/fcy_mpd
            mpd = fcy_mpd if fcy_mpd is not None else base_mpd
        elif fcy_mpd is not None and fcy_mpd > mpd:
            # normal FCY upgrade (e.g. PRVI, PMiles, 90N)
            mpd = fcy_mpd

    miles = amount * mpd

    # ---------- 3) cashback logic ----------
    cashback_rate = card.get("cashback_rate", 0.0)  # % value
    cashback = amount * cashback_rate / 100 if cashback_rate else 0.0

    # ---------- 4) bonus cap warnings ----------
    bonus_cap_amount = card.get("bonus_cap_amount")
    capped = False
    cap_note = ""

    if bonus_cap_amount:
        if amount > bonus_cap_amount:
            capped = True
            cap_note = (
                f"Bonus rate for {name} usually capped at about "
                f"S${bonus_cap_amount:.0f}/month; this txn exceeds that."
            )
        else:
            cap_note = (
                f"Bonus earn for {name} usually capped at about "
                f"S${bonus_cap_amount:.0f}/month. "
                f"This app doesn't track monthly usage yet."
            )

    return {
        "card_name": name,
        "card_type": card.get("type", "miles"),
        "miles": round(miles, 2),
        "cashback": round(cashback, 2),
        "blocked": False,
        "blocked_reason": "",
        "capped": capped,
        "cap_note": cap_note,
        "notes": card.get("notes", ""),
        "annual_fee": card.get("annual_fee"),
        "annual_fee_waivable": card.get("annual_fee_waivable", True),
        "is_fcy": is_fcy,
        "effective_mpd": mpd,
    }
