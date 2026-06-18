/* ── State ─────────────────────────────────────────────────────── */
let releases = [];
let lastFetched = null;

/* ── DOM refs ─────────────────────────────────────────────────── */
const feedContainer = document.getElementById("feed");
const refreshBtn = document.getElementById("btn-refresh");
const countEl = document.getElementById("count");
const timestampEl = document.getElementById("timestamp");
const toastEl = document.getElementById("toast");

/* ── Bootstrap ────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  fetchReleases();
  refreshBtn.addEventListener("click", fetchReleases);
});

/* ── Fetch releases from Flask API ────────────────────────────── */
async function fetchReleases() {
  // Prevent double-click
  if (refreshBtn.classList.contains("loading")) return;

  refreshBtn.classList.add("loading");
  showLoading();

  try {
    const res = await fetch("/api/releases");
    const data = await res.json();

    if (data.status === "success") {
      releases = data.entries;
      lastFetched = new Date();
      renderCards();
      showToast("Feed refreshed successfully");
    } else {
      showError(data.message || "Unknown error");
    }
  } catch (err) {
    showError("Could not reach the server. Please try again.");
  } finally {
    refreshBtn.classList.remove("loading");
  }
}

/* ── Render helpers ───────────────────────────────────────────── */
function showLoading() {
  feedContainer.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Fetching BigQuery release notes…</p>
    </div>`;
  countEl.textContent = "";
  timestampEl.textContent = "";
}

function showError(message) {
  feedContainer.innerHTML = `
    <div class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Something went wrong</h3>
      <p>${escapeHtml(message)}</p>
    </div>`;
}

function renderCards() {
  if (releases.length === 0) {
    feedContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>No release notes found</h3>
        <p>Try refreshing in a moment.</p>
      </div>`;
    return;
  }

  countEl.innerHTML = `<strong>${releases.length}</strong> release notes`;
  timestampEl.textContent = `Updated ${formatTime(lastFetched)}`;

  feedContainer.innerHTML = releases
    .map((entry, i) => cardHTML(entry, i))
    .join("");

  // Stagger the entrance animation
  document.querySelectorAll(".card").forEach((card, i) => {
    card.style.animationDelay = `${i * 0.04}s`;
  });
}

function cardHTML(entry, index) {
  const dateStr = formatDate(entry.updated);
  const tweetText = composeTweet(entry);
  const tweetURL = `https://twitter.com/intent/tweet?text=${encodeURIComponent(tweetText)}`;

  return `
    <article class="card" data-index="${index}">
      <div class="card-header">
        <h2 class="card-title">
          <a href="${escapeAttr(entry.link)}" target="_blank" rel="noopener">${escapeHtml(entry.title)}</a>
        </h2>
        <time class="card-date">${dateStr}</time>
      </div>
      <div class="card-content" id="content-${index}">${entry.content}</div>
      <div class="card-footer">
        <button class="btn-expand" onclick="toggleExpand(${index})">Show more</button>
        <a class="btn-tweet" href="${tweetURL}" target="_blank" rel="noopener" title="Post on X / Twitter">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
          </svg>
          <span>Post</span>
        </a>
      </div>
    </article>`;
}

/* ── Expand / Collapse ────────────────────────────────────────── */
function toggleExpand(index) {
  const content = document.getElementById(`content-${index}`);
  const btn = content.closest(".card").querySelector(".btn-expand");
  const isExpanded = content.classList.toggle("expanded");
  btn.textContent = isExpanded ? "Show less" : "Show more";
}

/* ── Compose a tweet ──────────────────────────────────────────── */
function composeTweet(entry) {
  const title = entry.title || "BigQuery Release Note";
  const link = entry.link || "";
  return `📢 ${title}\n\n${link}\n\n#BigQuery #GoogleCloud #DataEngineering`;
}

/* ── Toast notification ───────────────────────────────────────── */
function showToast(message) {
  toastEl.textContent = message;
  toastEl.classList.add("visible");
  setTimeout(() => toastEl.classList.remove("visible"), 2500);
}

/* ── Utilities ────────────────────────────────────────────────── */
function formatDate(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatTime(date) {
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function escapeAttr(str) {
  return str.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#39;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
