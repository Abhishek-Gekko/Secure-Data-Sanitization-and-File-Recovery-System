/**
 * Sanitization Engine & Remanence Verifier Frontend Logic
 */

let selectedMethod = "dod_5220_22_m";
let pendingSanitizeRequest = null;

document.addEventListener("DOMContentLoaded", () => {
  // Method selection cards
  const methodCards = document.querySelectorAll("#sanitization-method-grid .method-card");
  methodCards.forEach((card) => {
    card.addEventListener("click", () => {
      methodCards.forEach((c) => c.classList.remove("selected"));
      card.classList.add("selected");
      selectedMethod = card.getAttribute("data-method");
    });
  });

  // Sandbox picker sync with target input
  const sandboxPicker = document.getElementById("sanitize-sandbox-picker");
  const targetInput = document.getElementById("sanitize-target-input");
  if (sandboxPicker && targetInput) {
    sandboxPicker.addEventListener("change", () => {
      if (sandboxPicker.value) {
        targetInput.value = sandboxPicker.value;
      }
    });
  }

  // Sanitization button click -> opens safety modal
  const btnTrigger = document.getElementById("btn-trigger-sanitization");
  const modal = document.getElementById("sanitization-confirm-modal");
  const modalTargetDisplay = document.getElementById("modal-target-path-display");
  const modalMethodDisplay = document.getElementById("modal-method-display");
  const btnCancelModal = document.getElementById("btn-cancel-modal");
  const btnConfirmWipe = document.getElementById("btn-confirm-wipe");

  btnTrigger.addEventListener("click", () => {
    const target = targetInput.value.trim();
    if (!target) {
      showToast("Please enter or select a target file path", "error");
      return;
    }

    pendingSanitizeRequest = {
      target: target,
      method: selectedMethod,
      confirm: true,
      nullify_metadata: document.getElementById("sanitize-opt-metadata")?.checked ?? false,
      delete: document.getElementById("sanitize-opt-delete")?.checked ?? false,
    };

    modalTargetDisplay.textContent = target;
    modalMethodDisplay.textContent = selectedMethod.toUpperCase();
    modal.classList.add("active");
  });

  btnCancelModal.addEventListener("click", () => {
    modal.classList.remove("active");
    pendingSanitizeRequest = null;
  });

  btnConfirmWipe.addEventListener("click", async () => {
    modal.classList.remove("active");
    if (!pendingSanitizeRequest) return;

    try {
      showToast(`Initiating ${pendingSanitizeRequest.method} wipe...`, "info");
      const res = await fetch("/api/sanitization/wipe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pendingSanitizeRequest),
      });
      const data = await res.json();

      if (!data.success) {
        showToast(data.error || "Sanitization failed", "error");
        return;
      }

      showToast("File sanitized and verified successfully!", "success");
      renderSanitizationResult(data.data);
      // Reload sandbox to update file states/sizes
      loadSandboxFiles();
    } catch (err) {
      showToast(`Wipe execution error: ${err.message}`, "error");
    } finally {
      pendingSanitizeRequest = null;
    }
  });

  // Remanence Verifier Setup
  setupRemanenceVerifier();
});

// Render Sanitization Results
function renderSanitizationResult(result) {
  document.getElementById("sanitize-empty-state").style.display = "none";
  document.getElementById("sanitize-result-content").style.display = "block";

  const score = result.confidence_score || 0;
  const radial = document.getElementById("sanitize-score-radial");
  if (radial) {
    radial.style.strokeDashoffset = 163 - (163 * score / 100);
  }
  const scoreText = document.getElementById("sanitize-score-text");
  if (scoreText) scoreText.textContent = `${score}%`;

  const verdict = result.details?.verdict || (score >= 90 ? "CONFIRMED" : score >= 70 ? "PROBABLE" : "UNCERTAIN");
  const verdictBadge = document.getElementById("sanitize-verdict-badge");
  if (verdictBadge) {
    verdictBadge.className = `type-pill ${getVerdictClass(verdict)}`;
    verdictBadge.textContent = verdict;
  }

  const tag = document.getElementById("sanitize-verdict-tag");
  if (tag) {
    tag.textContent = verdict;
    tag.className = `type-pill ${verdict === "CONFIRMED" ? "recovery" : "analysis"}`;
  }

  const bytesVal = document.getElementById("sanitize-bytes-val");
  if (bytesVal) bytesVal.textContent = formatBytes(result.bytes_overwritten);

  const entVal = document.getElementById("sanitize-entropy-val");
  if (entVal) entVal.textContent = (result.entropy ?? 0).toFixed(2);

  const stateVal = document.getElementById("sanitize-state-val");
  if (stateVal) {
    stateVal.textContent = result.is_sanitized ? "PASSED" : "FAILED";
    stateVal.style.color = result.is_sanitized ? "var(--emerald)" : "var(--coral-red)";
  }

  // Breakdown bars
  const comps = result.details?.confidence_components || {};
  const pat = comps.pattern_uniformity ?? (result.details?.pattern_uniformity ? result.details.pattern_uniformity * 35 : 0);
  const car = comps.negative_carving ?? (result.details?.carved_artifacts === 0 ? 30 : 0);
  const ent = comps.entropy_compliance ?? (result.details?.entropy_compliance ? result.details.entropy_compliance * 25 : 0);
  const met = comps.metadata_destruction ?? (result.details?.metadata_nullified ? 10 : 0);

  setBar("bar-sanitize-pattern", "sanitize-comp-pattern", pat, 35);
  setBar("bar-sanitize-carving", "sanitize-comp-carving", car, 30);
  setBar("bar-sanitize-entropy", "sanitize-comp-entropy", ent, 25);
  setBar("bar-sanitize-metadata", "sanitize-comp-metadata", met, 10);
}

function setBar(barId, textId, scoreVal, maxVal) {
  const bar = document.getElementById(barId);
  const text = document.getElementById(textId);
  if (bar) bar.style.width = `${Math.min(100, (scoreVal / maxVal) * 100)}%`;
  if (text) text.textContent = `${scoreVal} / ${maxVal} pts`;
}

// Remanence Verifier Setup
function setupRemanenceVerifier() {
  const dropzone = document.getElementById("remanence-dropzone");
  const fileInput = document.getElementById("remanence-file-input");
  const targetPath = document.getElementById("remanence-target-path");
  const btnRun = document.getElementById("btn-run-remanence-check");

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      dropzone.querySelector(".dropzone-title").textContent = `Selected: ${e.dataTransfer.files[0].name}`;
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
      dropzone.querySelector(".dropzone-title").textContent = `Selected: ${fileInput.files[0].name}`;
    }
  });

  btnRun.addEventListener("click", async () => {
    const method = document.getElementById("remanence-expected-method").value;
    const formData = new FormData();
    formData.append("method", method);

    if (fileInput.files.length) {
      formData.append("file", fileInput.files[0]);
    } else if (targetPath.value.trim()) {
      formData.append("target", targetPath.value.trim());
    } else {
      showToast("Please upload a file or specify a local target path", "error");
      return;
    }

    try {
      showToast("Running remanence scan...", "info");
      const res = await fetch("/api/sanitization/verify", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!data.success) {
        showToast(data.error || "Remanence scan failed", "error");
        return;
      }
      showToast("Remanence analysis completed", "success");
      renderRemanenceResult(data.data);
    } catch (err) {
      showToast(`Scan failed: ${err.message}`, "error");
    }
  });
}

function renderRemanenceResult(result) {
  document.getElementById("remanence-empty-state").style.display = "none";
  document.getElementById("remanence-result-content").style.display = "block";

  const score = result.confidence_score || 0;
  const radial = document.getElementById("remanence-score-radial");
  radial.style.setProperty("--score-pct", score);
  document.getElementById("remanence-score-text").textContent = `${score}%`;

  const verdict = result.details?.verdict || "FAILED";
  const badge = document.getElementById("remanence-verdict-badge");
  badge.className = `verdict-badge ${getVerdictClass(verdict)}`;
  badge.textContent = verdict;

  document.getElementById("remanence-badge").textContent = result.is_sanitized ? "ZERO REMANENCE" : "LEAKAGE DETECTED";
  document.getElementById("remanence-badge").className = `badge-tag ${result.is_sanitized ? "txt" : "zip"}`;

  document.getElementById("remanence-carved-val").textContent = result.details?.carved_artifacts ?? 0;
  document.getElementById("remanence-signatures-val").textContent = result.details?.detected_signatures?.length ?? 0;
  document.getElementById("remanence-entropy-val").textContent = (result.entropy ?? 0).toFixed(4);

  const pat = (result.details?.pattern_uniformity ?? 0) * 100;
  const car = result.details?.carved_artifacts === 0 ? 100 : 0;
  const ent = (result.details?.entropy_compliance ?? 0) * 100;

  document.getElementById("remanence-bar-pattern").style.width = `${pat}%`;
  document.getElementById("remanence-bar-text-pattern").textContent = `${pat.toFixed(1)}%`;

  document.getElementById("remanence-bar-carving").style.width = `${car}%`;
  document.getElementById("remanence-bar-text-carving").textContent = `${car}%`;

  document.getElementById("remanence-bar-entropy").style.width = `${ent}%`;
  document.getElementById("remanence-bar-text-entropy").textContent = `${ent.toFixed(1)}%`;
}
