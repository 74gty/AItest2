const api = {
  async get(url) {
    const response = await fetch(url);
    return response.json();
  },
  async post(url, payload) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return response.json();
  },
};

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
}

function renderJson(id, value) {
  setText(id, JSON.stringify(value, null, 2));
}

async function refreshDashboard() {
  if (!document.querySelector(".dashboard")) {
    return;
  }

  const [health, watchlist, portfolio, risks] = await Promise.all([
    api.get("/api/health"),
    api.get("/api/watchlist"),
    api.get("/api/portfolio/summary"),
    api.get("/api/risk/alerts"),
  ]);

  setText("health-status", health.data.status);
  setText("watchlist-count", watchlist.data.length);
  setText("market-value", portfolio.data.total_market_value);
  setText("risk-count", risks.data.length);

  const watchlistItems = document.getElementById("watchlist-items");
  watchlistItems.innerHTML = watchlist.data.map((item) => (
    `<li><span>${item.item_type} ${item.symbol} ${item.name}</span><span>${item.item_id.slice(0, 8)}</span></li>`
  )).join("") || "<li><span>暂无自选关注</span></li>";

  const summary = portfolio.data.holdings.map((item) => (
    `${item.item_type} ${item.symbol} 市值 ${item.market_value} 盈亏 ${item.profit}`
  ));
  setText("portfolio-summary", summary.join("\n") || "暂无模拟持仓");

  const riskAlerts = document.getElementById("risk-alerts");
  riskAlerts.innerHTML = risks.data.map((item) => (
    `<li><span>${item.symbol} ${item.risk_type}</span><span>${item.level}</span></li>`
  )).join("") || "<li><span>暂无风险提醒</span></li>";

  await refreshDbWatchlist();
}

async function refreshDbWatchlist() {
  const dbWatchlistItems = document.getElementById("db-watchlist-items");
  if (!dbWatchlistItems) {
    return;
  }

  const result = await api.get("/api/db/watchlist?created_by=tester");
  dbWatchlistItems.innerHTML = result.data.map((item) => (
    `<li><span>${item.item_type} ${item.symbol} ${item.name}</span><span>#${item.item_id}</span></li>`
  )).join("") || "<li><span>暂无数据库自选</span></li>";
}

function bindLogin() {
  const form = document.getElementById("login-form");
  if (!form) {
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const result = await api.post("/api/auth/login", {
      username: document.getElementById("username").value,
      password: document.getElementById("password").value,
    });

    if (result.success) {
      window.location.href = "/dashboard";
      return;
    }
    setText("login-message", result.error.message);
  });
}

function bindDashboardActions() {
  const quoteForm = document.getElementById("quote-form");
  if (!quoteForm) {
    return;
  }

  quoteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const symbol = document.getElementById("quote-symbol").value;
    renderJson("quote-result", await api.get(`/api/stock/realtime?symbol=${encodeURIComponent(symbol)}`));
  });

  document.getElementById("watchlist-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    await api.post("/api/watchlist", {
      item_type: document.getElementById("watchlist-type").value,
      symbol: document.getElementById("watchlist-symbol").value,
      name: document.getElementById("watchlist-name").value,
    });
    await refreshDashboard();
  });

  document.getElementById("holding-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    await api.post("/api/portfolio/holding", {
      item_type: document.getElementById("holding-type").value,
      symbol: document.getElementById("holding-symbol").value,
      quantity: Number(document.getElementById("holding-quantity").value),
      cost_price: Number(document.getElementById("holding-cost").value),
    });
    await refreshDashboard();
  });

  document.getElementById("db-watchlist-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    await api.post("/api/db/watchlist", {
      item_type: document.getElementById("db-watchlist-type").value,
      symbol: document.getElementById("db-watchlist-symbol").value,
      name: document.getElementById("db-watchlist-name").value,
      created_by: "tester",
    });
    await refreshDbWatchlist();
  });

  document.getElementById("logout-button").addEventListener("click", async () => {
    await api.post("/api/auth/logout", {});
    window.location.href = "/login";
  });
}

bindLogin();
bindDashboardActions();
refreshDashboard();
