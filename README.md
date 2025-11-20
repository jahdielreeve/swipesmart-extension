# SpendSmart

A lightweight credit-card recommendation engine for Singapore, powered by FastAPI, Streamlit, and a Chrome Extension.

This app helps users instantly find the **best credit card** for miles or cashback based on:

* Merchant URL (e.g. shopee.sg, agoda.com)
* MCC category mapping
* Online vs offline spend
* SGD vs Foreign Currency (FCY)
* Per‑card rewards rules & bonus caps

---

## 🚀 Features

### ✅ Backend (FastAPI)

* `/recommend-card` endpoint
* Card rules loaded from `cards_data.json`
* FCY detection (`fcy_mpd` support)
* Bonus cap warnings
* Blocked MCC / blocked category logic
* Returns:

  * best card
  * miles + cashback
  * MCC detected
  * reasoning
  * leaderboard breakdown

### ✅ Frontend Tester (Streamlit)

* Dark-mode UI
* Pretty recommendation card
* Leaderboard (🥇 🥈 🥉)
* History log
* Debug JSON viewer

### ✅ Chrome Extension

* Detects current tab URL automatically
* Sends request to backend
* Beautiful popup UI
* Amount + mode selector (Miles/Cashback)
* Loading spinner
* Bank logos (optional)

---

## 🗂 Folder Structure

```
project/
├── backend/
│   ├── main.py
│   ├── rules.py
│   ├── cards_data.json
│   ├── mcc_map.py
│   └── ...
├── frontend/
│   └── tester_app.py
└── extension/
    ├── manifest.json
    ├── popup.html
    ├── popup.js
```

---

## ⚙️ Setup Instructions

### 1. Install backend dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install fastapi uvicorn
```

### 2. Run the backend

```bash
uvicorn main:app --reload
```

Now open:

```
http://127.0.0.1:8000/
```

### 3. Run the Streamlit tester

```bash
cd frontend
streamlit run tester_app.py
```

### 4. Load the Chrome Extension

* Go to `chrome://extensions`
* Enable **Developer mode**
* Click **Load unpacked**
* Select the `extension/` folder
* Reload after each change

---

## 🔄 Updating Card Rules

All card logic lives in:

```
backend/cards_data.json
```

Supports:

* `base_mpd`
* `fcy_mpd`
* `online_mpd`
* `category_mpd`
* `cashback_rate`
* `bonus_cap_amount`
* `blocked_categories`
* `blocked_mccs`

---

## 🛠 Future Upgrades

* Auto‑pull T&Cs from PDFs
* Train an ML model to categorize unknown merchants
* Automatically parse MCC from receipt/email
* Deploy backend to Render/Fly.io for 24/7 availability

---

## ❤️ Credits

Built for personal finance who want to maximise miles and cashback with minimal effort.

Swipe smart, earn smart.
