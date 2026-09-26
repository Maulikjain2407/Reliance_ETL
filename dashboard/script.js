/* =========================================================================
   CONFIG
   Each entry points at a JSON file produced by the Python ETL pipeline
   (see export/json_exporter.py). "label" is used in status and error
   messages shown to the user.
   ========================================================================= */
const DATASETS = {
  quarterly: { path: "./data/quarterly.json", label: "quarterly" },
  profit_loss: { path: "./data/profit_loss.json", label: "profit & loss" },
  balance_sheet: { path: "./data/balance_sheet.json", label: "balance sheet" },
  cash_flow: { path: "./data/cash_flow.json", label: "cash flow" },
  ratios: { path: "./data/ratios.json", label: "ratios" },
};

// Holds whatever we loaded (or failed to load) for each dataset.
const state = {
  datasets: {}, // key -> array of row objects, or null if loading failed
};

/* =========================================================================
   DATA LOADING
   ========================================================================= */

// Fetches one JSON file and validates its shape. Throws a descriptive
// error on any failure so the caller can show a clear message.
async function loadDataset(path) {
  let response;
  try {
    response = await fetch(path);
  } catch (networkError) {
    throw new Error(`Network error while fetching ${path}: ${networkError.message}`);
  }

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} (${response.statusText}) while fetching ${path}`);
  }

  let data;
  try {
    data = await response.json();
  } catch (parseError) {
    throw new Error(`Malformed JSON in ${path}: ${parseError.message}`);
  }

  if (!Array.isArray(data) || data.length === 0) {
    throw new Error(`${path} loaded but contained no rows`);
  }

  return data;
}

// Loads every configured dataset in parallel and stores results in `state`.
// A failure in one dataset never blocks the others from loading.
async function loadAllDatasets() {
  const keys = Object.keys(DATASETS);
  const results = await Promise.allSettled(keys.map((key) => loadDataset(DATASETS[key].path)));

  results.forEach((result, index) => {
    const key = keys[index];
    if (result.status === "fulfilled") {
      state.datasets[key] = result.value;
    } else {
      state.datasets[key] = null;
      console.error(`Failed to load "${key}" dataset:`, result.reason);
    }
  });
}

/* =========================================================================
   FORMATTING HELPERS
   ========================================================================= */

// Finds the column that holds the metric name. The processed data is
// expected to use "metric", but we fall back to the first key just in
// case, rather than assuming a fixed schema.
function getMetricKey(row) {
  return "metric" in row ? "metric" : Object.keys(row)[0];
}

// Adds thousands separators to a number without changing its value.
// Percent-style metrics (name contains "%") get a trailing "%".
function formatNumber(rawValue, metricName) {
  if (rawValue === null || rawValue === undefined || rawValue === "") {
    return "—";
  }
  if (typeof rawValue !== "number") {
    return String(rawValue);
  }
  const formatted = rawValue.toLocaleString("en-US", { maximumFractionDigits: 2 });
  return metricName.includes("%") ? `${formatted}%` : formatted;
}

// Turns a raw Status cell into user-facing text plus a CSS class.
// Missing values are shown, never hidden.
function formatStatusValue(rawValue) {
  const value = (rawValue ?? "").toString().trim();
  const normalized = value.toLowerCase();

  if (normalized === "present") {
    return { text: "Present", className: "status-present" };
  }
  if (normalized === "source_missing") {
    return { text: "Source missing", className: "status-missing" };
  }
  if (normalized === "cleaning_missing") {
    return { text: "Cleaning issue", className: "status-warning" };
  }
  if (value === "") {
    return { text: "—", className: "status-missing" };
  }
  // Any other value is shown exactly as-is rather than swallowed.
  return { text: value, className: "" };
}

/* =========================================================================
   TABLE RENDERING
   One reusable function handles all five datasets, since they share the
   same wide shape: a metric column plus one column per period.
   ========================================================================= */
function renderFinancialTable(data, container) {
  container.innerHTML = "";

  if (!Array.isArray(data) || data.length === 0) {
    container.innerHTML = '<p class="empty-message">No data available for this dataset.</p>';
    return;
  }

  const metricKey = getMetricKey(data[0]);
  const periodColumns = Object.keys(data[0]).filter((key) => key !== metricKey);

  const table = document.createElement("table");
  table.className = "financial-table";

  // Header row: "Metric" followed by one column per period.
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");

  const metricHeader = document.createElement("th");
  metricHeader.scope = "col";
  metricHeader.className = "metric-column";
  metricHeader.textContent = "Metric";
  headRow.appendChild(metricHeader);

  periodColumns.forEach((period) => {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = period;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  // Body rows, kept in the exact order they appear in the processed data.
  const tbody = document.createElement("tbody");
  data.forEach((row) => {
    const metricName = String(row[metricKey] ?? "");
    const isStatusRow = metricName.trim().toLowerCase() === "status";

    const tr = document.createElement("tr");
    if (isStatusRow) tr.classList.add("status-row");

    const metricCell = document.createElement("th");
    metricCell.scope = "row";
    metricCell.className = "metric-column";
    metricCell.textContent = metricName;
    tr.appendChild(metricCell);

    periodColumns.forEach((period) => {
      const td = document.createElement("td");
      td.className = "numeric-cell";

      if (isStatusRow) {
        const { text, className } = formatStatusValue(row[period]);
        td.textContent = text;
        if (className) td.classList.add(className);
      } else {
        td.textContent = formatNumber(row[period], metricName);
      }

      tr.appendChild(td);
    });

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);

  const scrollWrapper = document.createElement("div");
  scrollWrapper.className = "table-scroll";
  scrollWrapper.appendChild(table);
  container.appendChild(scrollWrapper);
}

// Fills one panel's table container, showing an error message instead
// if that dataset failed to load.
function renderTablePanel(key, containerId) {
  const container = document.getElementById(containerId);
  const data = state.datasets[key];

  if (!data) {
    container.innerHTML = `<p class="error-message">Unable to load ${DATASETS[key].label} financial data.</p>`;
    return;
  }

  renderFinancialTable(data, container);
}

/* =========================================================================
   FAULT ISOLATION
   Runs one render step and swallows any error it throws, logging it
   instead. Without this, a single failing step (e.g. a chart erroring
   because Chart.js didn't load) would stop every step scheduled after
   it in init() — including tables that have nothing to do with charts.
   ========================================================================= */
function safeRun(label, fn) {
  try {
    fn();
  } catch (error) {
    console.error(`[dashboard] "${label}" failed and was skipped:`, error);
  }
}

/* =========================================================================
   CHART RENDERING
   Charts only ever display values that are already in the processed
   data — nothing is calculated here.
   ========================================================================= */

// Finds the first row whose metric name contains one of the given
// keywords (case-insensitive). Never matches the Status row.
function findMetricRow(data, keywords) {
  if (!Array.isArray(data)) return null;
  return (
    data.find((row) => {
      const metricKey = getMetricKey(row);
      const name = String(row[metricKey] ?? "").toLowerCase();
      if (name === "status") return false;
      return keywords.some((keyword) => name.includes(keyword));
    }) || null
  );
}

// Splits one metric row into { labels, values } for charting.
function extractSeries(row) {
  const metricKey = getMetricKey(row);
  const labels = Object.keys(row).filter((key) => key !== metricKey);
  const values = labels.map((label) => (typeof row[label] === "number" ? row[label] : null));
  return { labels, values };
}

// Draws a line chart from whichever of the requested series are actually
// present in the dataset. If none are found, the chart card is hidden
// rather than showing an empty chart.
function renderTrendChart(canvasId, cardId, data, seriesDefs) {
  const card = document.getElementById(cardId);
  const canvas = document.getElementById(canvasId);

  if (!card || !canvas) return;

  // Chart.js loads from a CDN via a separate <script> tag. If that
  // request is blocked or slow (offline testing, an ad-blocker, a
  // restrictive network), "Chart" won't exist yet. Hide the chart
  // instead of throwing — the financial tables must not depend on this.
  if (typeof Chart === "undefined") {
    console.warn(`[dashboard] Chart.js is not available; hiding "${canvasId}".`);
    card.classList.add("is-hidden");
    return;
  }

  if (!data) {
    card.classList.add("is-hidden");
    return;
  }

  const datasets = [];
  let labels = null;

  seriesDefs.forEach((def) => {
    const row = findMetricRow(data, def.keywords);
    if (!row) return; // Metric not present in this dataset — skip quietly.
    const series = extractSeries(row);
    if (!labels) labels = series.labels;
    datasets.push({
      label: def.label,
      data: series.values,
      borderColor: def.color,
      backgroundColor: def.color,
      tension: 0.15,
      spanGaps: true,
    });
  });

  if (datasets.length === 0 || !labels) {
    card.classList.add("is-hidden");
    return;
  }

  new Chart(canvas, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { boxWidth: 12, color: "#9aa4b2" },
        },
      },
      scales: {
        x: {
          ticks: { color: "#9aa4b2" },
          grid: { color: "rgba(255, 255, 255, 0.06)" },
        },
        y: {
          ticks: {
            color: "#9aa4b2",
            callback: (value) => Number(value).toLocaleString("en-US"),
          },
          grid: { color: "rgba(255, 255, 255, 0.06)" },
        },
      },
    },
  });
}

/* =========================================================================
   OVERVIEW PANEL
   ========================================================================= */

// The latest period is simply the last column in the data — the
// processed CSVs are assumed to already be in chronological order.
function getLatestPeriod(data) {
  const row = data[0];
  const metricKey = getMetricKey(row);
  const periods = Object.keys(row).filter((key) => key !== metricKey);
  return periods[periods.length - 1] || null;
}

function renderOverviewCards() {
  const data = state.datasets.quarterly;
  const latestPeriodEl = document.getElementById("latest-period");
  const cardsContainer = document.getElementById("summary-cards");

  if (!data) {
    latestPeriodEl.textContent = "Unavailable";
    cardsContainer.innerHTML =
      '<p class="error-message">Unable to load quarterly financial data for the summary cards.</p>';
    return;
  }

  const latestPeriod = getLatestPeriod(data);
  latestPeriodEl.textContent = latestPeriod || "Unavailable";

  const cardDefs = [
    { label: "Revenue / Sales", keywords: ["sales"] },
    { label: "Operating Profit", keywords: ["operating profit"] },
    { label: "Net Profit", keywords: ["net profit"] },
    { label: "EPS", keywords: ["eps"] },
  ];

  cardsContainer.innerHTML = "";
  cardDefs.forEach((def) => {
    const row = findMetricRow(data, def.keywords);
    const value = row && latestPeriod ? row[latestPeriod] : null;

    const card = document.createElement("div");
    card.className = "summary-card";
    card.innerHTML = `
      <p class="summary-card-label">${def.label}</p>
      <p class="summary-card-value">${formatNumber(value, def.label)}</p>
    `;
    cardsContainer.appendChild(card);
  });
}

function renderStatusPanel() {
  const list = document.getElementById("data-status-list");
  list.innerHTML = "";

  Object.keys(DATASETS).forEach((key) => {
    const loaded = Boolean(state.datasets[key]);
    const item = document.createElement("li");
    item.className = loaded ? "status-ok" : "status-fail";
    item.textContent = `${DATASETS[key].label}: ${loaded ? "Loaded" : "Failed to load"}`;
    list.appendChild(item);
  });
}

/* =========================================================================
   NAVIGATION
   Switches the visible panel without a page reload.
   ========================================================================= */
function setupNavigation() {
  const navButtons = document.querySelectorAll(".nav-link");
  const panels = document.querySelectorAll(".panel");
  const pageTitle = document.getElementById("page-title");

  navButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetId = button.dataset.target;

      panels.forEach((panel) => {
        panel.hidden = panel.id !== targetId;
      });

      navButtons.forEach((btn) => {
        const isActive = btn === button;
        btn.classList.toggle("is-active", isActive);
        btn.setAttribute("aria-current", isActive ? "page" : "false");
      });

      pageTitle.textContent = button.textContent.trim();
    });
  });
}

/* =========================================================================
   INIT
   ========================================================================= */
async function init() {
  setupNavigation();
  await loadAllDatasets();

  // Every step below runs through safeRun(), so a failure in any one of
  // them (most likely the optional chart) is logged to the console and
  // skipped, but never stops the remaining tables from rendering.

  // Overview
  safeRun("status panel", renderStatusPanel);
  safeRun("overview summary cards", renderOverviewCards);
  safeRun("overview quarterly trend chart", () =>
    renderTrendChart("overview-chart", "overview-chart-card", state.datasets.quarterly, [
      { keywords: ["sales"], label: "Sales", color: "#2fae87" },
      { keywords: ["operating profit"], label: "Operating Profit", color: "#5b9bd5" },
      { keywords: ["net profit"], label: "Net Profit", color: "#e0665a" },
    ])
  );

  // Quarterly — table only
  safeRun("quarterly table", () => renderTablePanel("quarterly", "quarterly-table"));

  // Profit & Loss — table only (no chart; charts are secondary per spec)
  safeRun("profit & loss table", () => renderTablePanel("profit_loss", "profit-loss-table"));

  // Balance Sheet — table only. Deliberately no "Assets vs Liabilities"
  // or any other analytical chart here.
  safeRun("balance sheet table", () => renderTablePanel("balance_sheet", "balance-sheet-table"));

  // Cash Flow — table only
  safeRun("cash flow table", () => renderTablePanel("cash_flow", "cash-flow-table"));

  // Ratios — table only
  safeRun("ratios table", () => renderTablePanel("ratios", "ratios-table"));
}

document.addEventListener("DOMContentLoaded", init);