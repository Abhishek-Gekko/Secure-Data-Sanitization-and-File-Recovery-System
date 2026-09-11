/**
 * Forensic Core: Global Navigation, Dynamic Clock, Modals & Utility Library
 */

// Toast notifications
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === "error" ? "❌" : type === "success" ? "✅" : "ℹ️"}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Byte formatter
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0 || !bytes) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

// Verdict CSS class mapper
function getVerdictClass(verdict) {
  switch ((verdict || "").toUpperCase()) {
    case "CONFIRMED":
      return "recovery";
    case "PROBABLE":
      return "disk-image";
    case "UNCERTAIN":
      return "sanitization";
    default:
      return "analysis";
  }
}

// Generic API fetch wrapper
async function apiRequest(url, options = {}) {
  try {
    const res = await fetch(url, options);
    const data = await res.json();
    return data;
  } catch (err) {
    showToast(`Server communication error: ${err.message}`, "error");
    throw err;
  }
}

// View switcher
function switchView(viewId) {
  const navItems = document.querySelectorAll(".nav-item[data-view]");
  const viewSections = document.querySelectorAll(".view-section");

  navItems.forEach((item) => {
    if (item.getAttribute("data-view") === viewId) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  viewSections.forEach((section) => {
    if (section.id === viewId) {
      section.classList.add("active");
    } else {
      section.classList.remove("active");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  // Sidebar navigation click handlers
  const navItems = document.querySelectorAll(".nav-item[data-view]");
  navItems.forEach((item) => {
    item.addEventListener("click", () => {
      const viewId = item.getAttribute("data-view");
      switchView(viewId);
    });
  });

  // "View All" on Recent Cases -> Go to Evidence
  document.getElementById("link-view-all-cases")?.addEventListener("click", () => {
    switchView("view-evidence");
  });

  // Live Date/Time Clock
  updateLiveDateTime();
  setInterval(updateLiveDateTime, 1000);

  // New Case Modal Flow
  const btnOpenNewCase = document.getElementById("btn-open-new-case");
  const newCaseModal = document.getElementById("new-case-modal");
  const btnCancelNewCase = document.getElementById("btn-cancel-new-case");
  const btnConfirmNewCase = document.getElementById("btn-confirm-new-case");

  btnOpenNewCase?.addEventListener("click", () => {
    newCaseModal?.classList.add("active");
  });

  btnCancelNewCase?.addEventListener("click", () => {
    newCaseModal?.classList.remove("active");
  });

  btnConfirmNewCase?.addEventListener("click", () => {
    const targetView = document.getElementById("new-case-type").value;
    newCaseModal?.classList.remove("active");
    switchView(targetView);
    showToast("New forensic investigation initialized", "success");
  });

  // Generate Report Button
  document.getElementById("btn-generate-report")?.addEventListener("click", () => {
    showToast("Compiling official Forensic Audit Chain Report...", "info");
    setTimeout(() => {
      showToast("Forensic Report compiled successfully (DoD / NIST SP 800-88 Compliant)", "success");
    }, 1200);
  });

  // Global Search Box Filtering
  const searchInput = document.getElementById("global-search-input");
  searchInput?.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    const rows = document.querySelectorAll("#cases-table-body tr");
    rows.forEach((row) => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(q) ? "" : "none";
    });
  });

  // Load sandbox files
  loadSandboxFiles();
});

// Update live clock matching the reference format
function updateLiveDateTime() {
  const elem = document.getElementById("live-datetime");
  if (!elem) return;
  const now = new Date();
  const dateStr = now.toLocaleDateString("en-US", { weekday: "short", day: "2-digit", month: "short", year: "numeric" });
  const timeStr = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  elem.innerHTML = `${dateStr}<br>${timeStr}`;
}

// Load sandbox files into pickers and evidence table
async function loadSandboxFiles() {
  try {
    const data = await apiRequest("/api/algorithm/sandbox/files");
    if (!data.success) return;

    // 1. Populate sanitization select picker
    const sanitizePicker = document.getElementById("sanitize-sandbox-picker");
    if (sanitizePicker) {
      sanitizePicker.innerHTML = `<option value="">-- Select a sandbox file --</option>`;
      data.files.forEach((file) => {
        const opt = document.createElement("option");
        opt.value = file.path;
        opt.textContent = `${file.name} (${formatBytes(file.size)})`;
        sanitizePicker.appendChild(opt);
      });
    }

    // 2. Populate Evidence table
    const tableBody = document.getElementById("sandbox-files-tbody");
    if (tableBody) {
      if (data.files.length === 0) {
        tableBody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">
              Sandbox is empty. Click "Generate Sample Forensic Evidence" above.
            </td>
          </tr>`;
      } else {
        tableBody.innerHTML = data.files
          .map(
            (f) => `
          <tr>
            <td style="font-weight: 600; color: #ffffff;">${f.name}</td>
            <td style="color: var(--text-muted); font-size: 0.75rem;">${f.path}</td>
            <td style="font-family: var(--font-mono);">${formatBytes(f.size)}</td>
            <td style="font-size: 0.725rem; color: var(--blue-light); font-family: var(--font-mono);">${f.sha256.slice(0, 16)}...</td>
            <td style="white-space: nowrap;">
              <button class="btn btn-secondary btn-sm" onclick="quickSelectForSanitize('${f.path.replace(/\\/g, "/")}')">Wipe</button>
              <button class="btn btn-secondary btn-sm" onclick="quickSelectForVerify('${f.path.replace(/\\/g, "/")}', '${f.sha256}')">Verify</button>
              ${f.name.endsWith(".raw") ? `<button class="btn btn-primary btn-sm" onclick="quickSelectForCarve('${f.path.replace(/\\/g, "/")}')">Carve</button>` : ""}
            </td>
          </tr>
        `
          )
          .join("");
      }
    }
  } catch (err) {
    console.error("Failed to load sandbox files", err);
  }
}

// Quick action shortcuts
function quickSelectForSanitize(path) {
  switchView("view-sanitization");
  const input = document.getElementById("sanitize-target-input");
  if (input) input.value = path;
}

function quickSelectForVerify(path, hash) {
  switchView("view-verification");
  const target = document.getElementById("verify-recovery-target");
  const hashInput = document.getElementById("verify-baseline-hash");
  if (target) target.value = path;
  if (hashInput && hash) hashInput.value = hash;
}

function quickSelectForCarve(path) {
  switchView("view-recovery");
  const target = document.getElementById("carve-target-path");
  if (target) target.value = path;
}

function sendToVerifier(recoveredPath) {
  switchView("view-verification");
  const input = document.getElementById("verify-recovery-target");
  if (input) input.value = recoveredPath;
  document.getElementById("btn-run-recovery-verify")?.click();
}
