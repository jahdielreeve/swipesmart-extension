import streamlit as st
import requests
import pandas as pd
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000/recommend-card"

# ---------- Page config ----------
st.set_page_config(
    page_title="SpendSmartSG",
    page_icon="💳",
    layout="centered",
)

# ---------- Dark mode CSS ----------
dark_css = """
<style>
    body {
        background-color: #0f172a;
        color: #e5e7eb;
    }
    .main {
        background-color: #020617;
    }
    .css-18e3th9, .css-1d391kg {
        background-color: #020617;
    }
    .swipe-card {
        background: #020617;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 16px 18px;
        margin-top: 10px;
        box-shadow: 0 0 18px rgba(15, 23, 42, 0.8);
    }
    .swipe-card h3 {
        margin: 0 0 6px 0;
        color: #e5e7eb;
        font-size: 1.1rem;
    }
    .swipe-card p {
        margin: 2px 0;
        color: #cbd5f5;
        font-size: 0.95rem;
    }
    .swipe-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 999px;
        border: 1px solid #1e293b;
        font-size: 0.75rem;
        margin-right: 4px;
        background: #020617;
        color: #cbd5f5;
    }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# ---------- Session state for history ----------
if "history" not in st.session_state:
    st.session_state["history"] = []  # list of dicts


# ---------- Header ----------
st.title("SpendSmart💳")
st.caption("Help! Which credit card should i use for this purchase?")


# ---------- Input area ----------
st.subheader("1. Enter purchase details")

merchant_options = ["Shopee", "Agoda", "NTUC", "Custom URL"]
merchant_choice = st.selectbox("Merchant", merchant_options, index=0)

default_url_map = {
    "Shopee": "https://shopee.sg",
    "Agoda": "https://www.agoda.com",
    "NTUC": "https://www.fairprice.com.sg",
}

if merchant_choice == "Custom URL":
    url = st.text_input("Merchant URL", "https://example.com")
else:
    url = st.text_input(
        "Merchant URL",
        default_url_map.get(merchant_choice, "https://example.com"),
    )

amount = st.number_input("Amount (SGD)", min_value=0.0, value=50.0, step=1.0)

mode_choice = st.selectbox("Reward focus", ["Miles", "Cashback"], index=0)
mode_value = "miles" if mode_choice == "Miles" else "cashback"

check_btn = st.button("🔍 Check Best Card", type="primary")


# ---------- Call backend ----------
data = None
if check_btn:
    payload = {
        "url": url,
        "amount": amount,
        "currency": "SGD",
        "mode": mode_value,
    }

    try:
        res = requests.post(BACKEND_URL, json=payload)
        res.raise_for_status()
        data = res.json()

        # Save to history
        best_card = data.get("best_card")
        estimated_miles = data.get("estimated_miles", 0.0)
        estimated_cashback = data.get("estimated_cashback", 0.0)
        category = data.get("category")
        is_online = data.get("is_online")
        mcc = data.get("mcc", "")

        st.session_state["history"].append(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "merchant": merchant_choice if merchant_choice != "Custom URL" else url,
                "amount": amount,
                "best_card": best_card,
                "miles": estimated_miles,
                "cashback": estimated_cashback,
                "category": category,
                "online": is_online,
                "mcc": mcc,
                "mode": data.get("mode", mode_value),
            }
        )

    except Exception as e:
        st.error(f"⚠️ Could not reach backend: {e}")


# ---------- Result card ----------
if data:
    st.write("---")
    st.subheader("2. Recommendation")

    best_card = data.get("best_card")
    estimated_miles = data.get("estimated_miles", 0.0)
    estimated_cashback = data.get("estimated_cashback", 0.0)
    category = data.get("category")
    is_online = data.get("is_online")
    mcc = data.get("mcc", "")
    mode_used = data.get("mode", mode_value)
    reason = data.get("reason", "")
    annual_fee_warning = data.get("annual_fee_warning")

    if best_card:
        # Styled card with 🥇 + big miles/cashback
        card_html = f"""
        <div class="swipe-card" style="
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 20px;
        background: linear-gradient(145deg, #0f172a, #1e293b20);
        box-shadow: 0 0 25px rgba(30, 41, 59, 0.45);
        ">
        <p style="font-size: 1.6rem; margin: 0 0 6px 0;">
            🥇 <strong>{best_card}</strong>
        </p>

        <p style="font-size: 1.1rem; margin: 0 0 8px 0;">
            <span style="color:#a5b4fc;">Estimated Miles:</span>
            <strong style="font-size: 1.4rem; color:#fcd34d;">{estimated_miles}</strong>
        </p>

        <p style="font-size: 1.0rem; margin: 0 0 12px 0;">
            <span style="color:#a5b4fc;">Estimated Cashback:</span>
            <strong style="font-size: 1.2rem; color:#bbf7d0;">S${estimated_cashback:.2f}</strong>
        </p>

        <p style="margin: 0 0 10px 0;">
            <span class="swipe-badge">Mode: {mode_used}</span>
            <span class="swipe-badge">Category: {category}</span>
            <span class="swipe-badge">Online: {is_online}</span>
            <span class="swipe-badge">MCC: {mcc}</span>
        </p>

        <p style="color:#cbd5e1; font-size:0.95rem; margin: 12px 0 0 0;">
            <strong>Why:</strong> {reason}
        </p>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

        if annual_fee_warning:
            st.warning(annual_fee_warning)

    else:
        st.warning("No suitable card found with current rules.")


    # ---------- Compare all cards breakdown ----------
    st.subheader("3. Compare all cards (breakdown)")

    breakdown = data.get("breakdown")

    if breakdown:
        df_breakdown = pd.DataFrame(breakdown)

        # Determine sorting metric based on mode
        sort_mode = data.get("mode", mode_value)
        sort_col = "miles" if sort_mode == "miles" else "cashback"

        df_breakdown = df_breakdown.sort_values(
            by=sort_col, ascending=False
        ).reset_index(drop=True)

        # Add ranking emojis
        rank_emojis = ["🥇", "🥈", "🥉"]
        df_breakdown["Rank"] = ""

        for i in range(len(df_breakdown)):
            if i < 3:
                df_breakdown.at[i, "Rank"] = rank_emojis[i]
            else:
                df_breakdown.at[i, "Rank"] = "🎖️"

        # Show nicely
        df_breakdown.index += 1  # start row numbering at 1

        st.dataframe(
            df_breakdown[
                [
                    "Rank",
                    "card_name",
                    "card_type",
                    "miles",
                    "cashback",
                    "blocked",
                    "capped",
                ]
            ],
            use_container_width=True,
            column_config={
                "Rank": "Rank",
                "card_name": "Card",
                "card_type": "Type",
                "miles": "Miles",
                "cashback": "Cashback (S$)",
                "blocked": "Blocked?",
                "capped": "Cap Note?",
            },
        )
    else:
        st.info(
            "No breakdown data from backend yet. "
            "Once you add a `breakdown` list to the API response, "
            "it will show all cards here."
        )


# ---------- History table ----------
st.write("---")
st.subheader("4. Recent queries (session history)")

if st.session_state["history"]:
    hist_df = pd.DataFrame(st.session_state["history"])
    # Latest first
    hist_df = hist_df.iloc[::-1].reset_index(drop=True)

    st.dataframe(
        hist_df,
        use_container_width=True,
        column_config={
            "time": "Time",
            "merchant": "Merchant",
            "amount": "Amount (SGD)",
            "best_card": "Best Card",
            "miles": "Miles",
            "cashback": "Cashback (S$)",
            "category": "Category",
            "online": "Online?",
            "mcc": "MCC",
            "mode": "Mode",
        },
    )
else:
    st.caption("No history yet. Run a check to see your first entry.")


# ---------- Debug raw JSON ----------
with st.expander("🔧 Raw API Response (debug)"):
    if data:
        st.json(data)
    else:
        st.caption("No response yet. Run a query first.")
