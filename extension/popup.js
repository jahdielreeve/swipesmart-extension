const BACKEND_URL = "http://127.0.0.1:8000/recommend-card";

function setUrlDisplay(url) {
  const el = document.getElementById("urlDisplay");
  el.textContent = url ? `Current site: ${url}` : "Could not detect URL";
}

// basic card meta: issuer, group (miles/cashback), short note
const CARD_META = {
  "DBS Altitude Visa": {
    issuer: "DBS",
    logoClass: "logo-dbs",
    group: "miles",
    note: "General miles card. 1.3 mpd local, ~2.0 mpd FCY. Good for uncapped general spend."
  },
  "DBS Woman's World Mastercard": {
    issuer: "DBS",
    logoClass: "logo-dbs",
    group: "miles",
    note: "4 mpd on online SGD spend up to S$1k/month. FCY online earns base miles only."
  },
  "Citi Rewards": {
    issuer: "Citi",
    logoClass: "logo-citi",
    group: "miles",
    note: "4 mpd on online shopping and fashion up to S$1k/month. No bonus on travel / mobile wallet."
  },
  "Citi PremierMiles": {
    issuer: "Citi",
    logoClass: "logo-citi",
    group: "miles",
    note: "General travel miles card. 1.2 mpd local, ~2.0 mpd FCY, higher for airlines/hotels promos."
  },
  "UOB PRVI Miles Visa": {
    issuer: "UOB",
    logoClass: "logo-uob",
    group: "miles",
    note: "1.4 mpd local, ~2.4 mpd FCY, ~3 mpd for selected online travel (Agoda/Expedia)."
  },
  "OCBC 90N Visa": {
    issuer: "OCBC",
    logoClass: "logo-ocbc",
    group: "miles",
    note: "1.3 mpd local, ~2.1 mpd FCY. Simple uncapped miles card."
  },
  "HSBC Revolution": {
    issuer: "HSBC",
    logoClass: "logo-hsbc",
    group: "cashback", // treat as points/cashback-ish in UI
    note: "Up to 10x points (~4 mpd) on online and contactless dining/shopping/travel. No FCY bonus."
  },
  "UOB EVOL": {
    issuer: "UOB",
    logoClass: "logo-uob",
    group: "cashback",
    note: "Cashback card for online + contactless. Needs min spend and 3 txns to unlock boost."
  },
  "OCBC 365": {
    issuer: "OCBC",
    logoClass: "logo-ocbc",
    group: "cashback",
    note: "Cashback across dining, groceries, fuel, etc. Tiered caps and min spend."
  },
  "Maybank Family & Friends": {
    issuer: "Maybank",
    logoClass: "logo-maybank",
    group: "cashback",
    note: "High cashback on chosen categories (e.g. groceries, dining, transport) with caps."
  }
};

const AVAILABLE_CARDS = Object.keys(CARD_META);

document.addEventListener("DOMContentLoaded", () => {
  const cardListEl = document.getElementById("cardList");
  const cardSectionEl = document.getElementById("cardSection");
  const cardToggle = document.getElementById("cardToggle");
  const cardToggleIcon = document.getElementById("cardToggleIcon");
  const selectAllBtn = document.getElementById("selectAllBtn");
  const selectNoneBtn = document.getElementById("selectNoneBtn");

  const amountInput = document.getElementById("amount");
  const modeSelect = document.getElementById("mode");
  const checkBtn = document.getElementById("checkBtn");
  const resultEl = document.getElementById("result");
  const errorEl = document.getElementById("error");
  const loadingEl = document.getElementById("loading");
  const currencySelect = document.getElementById("currency");

  let cardsCollapsed = false;

  // ---------- helpers ----------

  function renderCardCheckboxes(selectedSet) {
    if (!cardListEl) return;
    cardListEl.innerHTML = "";

    // group into miles vs cashback
    const milesCards = AVAILABLE_CARDS.filter(
      (name) => CARD_META[name].group === "miles"
    );
    const cashbackCards = AVAILABLE_CARDS.filter(
      (name) => CARD_META[name].group === "cashback"
    );

    function renderGroup(title, list) {
      if (list.length === 0) return;
      const titleDiv = document.createElement("div");
      titleDiv.className = "card-group-title";
      titleDiv.textContent = title;
      cardListEl.appendChild(titleDiv);

      list.forEach((name) => {
        const meta = CARD_META[name] || {};
        const id = "card_" + name.replace(/\s+/g, "_");

        const line = document.createElement("div");
        line.className = "card-line";

        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.id = id;
        cb.value = name;
        cb.checked = selectedSet.has(name);

        const label = document.createElement("label");
        label.htmlFor = id;
        label.textContent = " " + name;

        const logoSpan = document.createElement("span");
        logoSpan.className = "card-logo " + (meta.logoClass || "");
        logoSpan.textContent = meta.issuer || "";

        const infoBtn = document.createElement("button");
        infoBtn.type = "button";
        infoBtn.className = "card-info-btn";
        infoBtn.textContent = "i";
        infoBtn.title = "Show card rules";
        infoBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          alert(meta.note || name);
        });

        line.appendChild(cb);
        line.appendChild(logoSpan);
        line.appendChild(label);
        line.appendChild(infoBtn);

        cardListEl.appendChild(line);
      });
    }

    renderGroup("Miles cards", milesCards);
    renderGroup("Cashback / points cards", cashbackCards);
  }

  function collectSelectedCards() {
    const selected = [];
    if (!cardListEl) return selected;
    cardListEl.querySelectorAll("input[type=checkbox]").forEach((cb) => {
      if (cb.checked) selected.push(cb.value);
    });
    return selected;
  }

  function setAllCards(checked) {
    if (!cardListEl) return;
    cardListEl.querySelectorAll("input[type=checkbox]").forEach((cb) => {
      cb.checked = checked;
    });
  }

  // ---------- load saved card selection ----------
  if (chrome.storage && chrome.storage.sync) {
	  chrome.storage.sync.get(["enabled_cards"], (res) => {
		const enabled = new Set(res.enabled_cards || []);
		if (enabled.size === 0) {
		  AVAILABLE_CARDS.forEach((c) => enabled.add(c));
		}
		renderCardCheckboxes(enabled);
	  });
	} else {
		 // fallback: everything enabled, no persistence
	  const enabled = new Set(AVAILABLE_CARDS);
	  renderCardCheckboxes(enabled);
	}
  // ---------- collapse / expand cards ----------
  if (cardToggle && cardSectionEl && cardToggleIcon) {
    cardToggle.addEventListener("click", () => {
      cardsCollapsed = !cardsCollapsed;
      cardSectionEl.style.display = cardsCollapsed ? "none" : "block";
      cardToggleIcon.textContent = cardsCollapsed ? "▸" : "▾";
    });
  }

  // select all / none
  if (selectAllBtn) {
    selectAllBtn.addEventListener("click", () => {
      setAllCards(true);
      const selected = collectSelectedCards();
      chrome.storage.sync.set({ enabled_cards: selected });
    });
  }

  if (selectNoneBtn) {
    selectNoneBtn.addEventListener("click", () => {
      setAllCards(false);
      chrome.storage.sync.set({ enabled_cards: [] });
    });
  }

  // ---------- get current tab URL ----------
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const url = tabs && tabs[0] ? tabs[0].url : "";
    setUrlDisplay(url);
    resultEl.dataset.currentUrl = url || "";
  });

  // ---------- click handler ----------
  checkBtn.addEventListener("click", () => {
    errorEl.textContent = "";
    resultEl.innerHTML = "";

    const selected = collectSelectedCards();
    chrome.storage.sync.set({ enabled_cards: selected });

    const amount = parseFloat(amountInput.value || "0");
    const mode = modeSelect.value;
    const currency = currencySelect ? currencySelect.value : "SGD";
    const url = resultEl.dataset.currentUrl || "";

    if (!url) {
      errorEl.textContent = "Could not detect current tab URL.";
      return;
    }
    if (!amount || amount <= 0) {
      errorEl.textContent = "Please enter a valid amount.";
      return;
    }

    const payload = {
      url,
      amount,
      currency,
      mode,
      enabled_cards: selected
    };

    if (loadingEl) loadingEl.style.display = "block";
    checkBtn.disabled = true;
    resultEl.innerHTML = "";
    errorEl.textContent = "";

    fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then((res) => res.json())
      .then((data) => {
        renderResult(data);
      })
      .catch((err) => {
        console.error(err);
        errorEl.textContent = "Failed to reach backend. Is it running?";
      })
      .finally(() => {
        if (loadingEl) loadingEl.style.display = "none";
        checkBtn.disabled = false;
      });
  });
});

// -------------------------
// RENDER RESULT
// -------------------------
function renderResult(data) {
  const resultEl = document.getElementById("result");
  const errorEl = document.getElementById("error");

  errorEl.textContent = "";

  if (!data || !data.best_card) {
    resultEl.innerHTML =
      '<div class="card"><div class="why">No suitable card found.</div></div>';
    return;
  }

  const bestCard = data.best_card;
  const miles = data.estimated_miles || 0;
  const cashback = data.estimated_cashback || 0;
  const category = data.category || "-";
  const isOnline = data.is_online ? "Online" : "Offline";
  const mcc = data.mcc || "-";
  const mode = data.mode || "miles";
  const reason = data.reason || "";
  const annualFeeWarning = data.annual_fee_warning || null;
  const breakdown = Array.isArray(data.breakdown) ? data.breakdown : [];

  let html = `
    <div class="card">
      <div class="card-title">🥇 <strong>${bestCard}</strong></div>

      <div class="value-line">
        <span class="value-label">Estimated Miles:</span>
        <span class="value-strong">${miles}</span>
      </div>

      <div class="value-line">
        <span class="value-label">Estimated Cashback:</span>
        <span class="value-strong">S$${cashback.toFixed(2)}</span>
      </div>

      <div style="margin-top:4px;">
        <span class="badge">Mode: ${mode}</span>
        <span class="badge">Category: ${category}</span>
        <span class="badge">${isOnline}</span>
        <span class="badge">MCC ${mcc}</span>
      </div>

      <div class="why"><strong>Why:</strong> ${reason}</div>
  `;

  if (annualFeeWarning) {
    html += `<div class="warning">${annualFeeWarning}</div>`;
  }

  html += `</div>`;

  if (breakdown.length > 0) {
    const sortKey = mode === "cashback" ? "cashback" : "miles";
    const sorted = [...breakdown].sort(
      (a, b) => (b[sortKey] || 0) - (a[sortKey] || 0)
    );
    const top = sorted.slice(0, 3);
    const icons = ["🥇", "🥈", "🥉"];

    html += `<div class="leaderboard"><div class="small-text">Top cards:</div>`;

    top.forEach((card, idx) => {
      const icon = icons[idx] || "🎖️";
      const value =
        sortKey === "cashback"
          ? "S$" + (card.cashback || 0).toFixed(2)
          : (card.miles || 0) + " miles";

      html += `
        <div class="leader-row">
          <div class="leader-left">
            <span>${icon}</span>
            <span>${card.card_name}</span>
          </div>
          <div>${value}</div>
        </div>
      `;
    });

    html += `</div>`;
  }

  resultEl.innerHTML = html;
}
