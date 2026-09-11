/**
 * Forensic Carving & Recovery Verifier Frontend Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  setupCarvingEngine();
  setupExtentsRestorer();
  setupRecoveryVerifier();
});

// Setup File Carving Engine
function setupCarvingEngine() {
  const dropzone = document.getElementById("carve-dropzone");
  const fileInput = document.getElementById("carve-file-input");
  const targetPath = document.getElementById("carve-target-path");
  const btnCarve = document.getElementById("btn-execute-carve");
  const btnLoadSample = document.getElementById("btn-load-sample-disk");

  if (btnLoadSample) {
    btnLoadSample.addEventListener("click", () => {
      targetPath.value = "data/sandbox/forensic_disk_image.raw";
      showToast("Loaded sample disk image path", "info");
    });
  }

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

  btnCarve.addEventListener("click", async () => {
    const formData = new FormData();
    if (fileInput.files.length) {
      formData.append("file", fileInput.files[0]);
    } else if (targetPath.value.trim()) {
      formData.append("target", targetPath.value.trim());
    } else {
      showToast("Please select a disk image or provide a target path", "error");
      return;
    }

    try {
      showToast("Executing signature-based file carving...", "info");
      btnCarve.disabled = true;
      btnCarve.textContent = "Carving Sectors...";

      const res = await fetch("/api/recovery/carve", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!data.success) {
        showToast(data.error || "Carving failed", "error");
        return;
      }

      showToast(`Carving finished! Recovered ${data.count} file(s)`, "success");
      renderCarvedArtifacts(data.artifacts, data.overall);
    } catch (err) {
      showToast(`Carving error: ${err.message}`, "error");
    } finally {
      btnCarve.disabled = false;
      btnCarve.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        Start Signature Carving`;
    }
  });
}

// Render Carved Artifacts Table and Overall Scorecard
function renderCarvedArtifacts(artifacts, overall) {
  const tbody = document.getElementById("carved-artifacts-tbody");
  const badge = document.getElementById("carved-count-badge");
  const overallCard = document.getElementById("carving-overall-score-card");

  badge.textContent = `${artifacts ? artifacts.length : 0} ARTIFACTS`;

  // Populate Overall Scorecard if present
  if (overall && overallCard) {
    overallCard.style.display = "block";
    const radial = document.getElementById("disk-score-radial");
    if (radial) {
      radial.style.strokeDashoffset = 188 - (188 * (overall.score || 0) / 100);
    }

    const scoreText = document.getElementById("disk-score-text");
    if (scoreText) scoreText.textContent = `${overall.score || 0}%`;

    const verdictBadge = document.getElementById("disk-verdict-badge");
    if (verdictBadge) {
      verdictBadge.className = `type-pill ${getVerdictClass(overall.verdict)}`;
      verdictBadge.textContent = overall.verdict || "UNKNOWN";
    }

    const verdictTag = document.getElementById("disk-verdict-tag");
    if (verdictTag) {
      verdictTag.textContent = overall.verdict || "ANALYZED";
      verdictTag.className = `type-pill ${getVerdictClass(overall.verdict)}`;
    }

    const totalVal = document.getElementById("disk-total-val");
    if (totalVal) totalVal.textContent = overall.total_artifacts;

    const completeVal = document.getElementById("disk-complete-val");
    if (completeVal) completeVal.textContent = `${overall.complete_percentage}% (${overall.complete_count}/${overall.total_artifacts})`;

    const structVal = document.getElementById("disk-struct-val");
    if (structVal) structVal.textContent = `${overall.struct_percentage}% (${overall.struct_count}/${overall.total_artifacts})`;

    const parserVal = document.getElementById("disk-parser-val");
    if (parserVal) parserVal.textContent = `${overall.parser_percentage}% (${overall.parser_count}/${overall.total_artifacts})`;
  }

  if (!artifacts || artifacts.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; color: var(--rose-primary); padding: 2rem;">
          No recoverable signatures detected in this image.
        </td>
      </tr>`;
    return;
  }

  tbody.innerHTML = artifacts
    .map(
      (art) => `
    <tr>
      <td style="color: var(--text-muted);">${art.id}</td>
      <td><span class="badge-tag ${art.file_type}">${art.file_type.toUpperCase()}</span></td>
      <td>${art.offset} <span style="color: var(--text-muted); font-size: 0.75rem;">(0x${art.offset.toString(16).toUpperCase()})</span></td>
      <td>${formatBytes(art.length)}</td>
      <td>
        <span class="badge-tag ${art.complete ? "txt" : "zip"}">
          ${art.complete ? "COMPLETE" : "FRAGMENTED"}
        </span>
      </td>
      <td>
        <span class="badge-tag ${art.confidence_score >= 80 ? 'txt' : art.confidence_score >= 60 ? 'png' : 'zip'}">
          ${art.confidence_score ?? 0}%
        </span>
        <span style="font-size: 0.7rem; color: var(--text-muted); margin-left: 0.25rem;">(${art.verdict})</span>
      </td>
      <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
        ${art.preview ? `<span style="color: var(--text-muted); font-style: italic;">"${art.preview}"</span>` : art.filename}
      </td>
      <td style="white-space: nowrap;">
        <a href="${art.download_url}" class="btn btn-secondary btn-sm" download>Download</a>
        <button class="btn btn-primary btn-sm" onclick="sendToVerifier('data/recovered/${art.filename}')">Verify</button>
      </td>
    </tr>
  `
    )
    .join("");
}

// Quick action: send carved artifact directly to Recovery Verifier tab
function sendToVerifier(recoveredPath) {
  document.getElementById("tab-btn-recovery-verify")?.click();
  const input = document.getElementById("verify-recovery-target");
  if (input) input.value = recoveredPath;
  document.getElementById("btn-run-recovery-verify")?.click();
}

// Setup Extents Restorer
function setupExtentsRestorer() {
  const btn = document.getElementById("btn-restore-extents");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const image = document.getElementById("extents-image-path").value.trim();
    const extentsRaw = document.getElementById("extents-list-input").value.trim();
    const destName = document.getElementById("extents-dest-name").value.trim();

    if (!image || !extentsRaw) {
      showToast("Please provide image path and extents list", "error");
      return;
    }

    let parsedExtents;
    try {
      parsedExtents = JSON.parse(extentsRaw);
      if (!Array.isArray(parsedExtents)) throw new Error("Must be an array of [offset, length]");
    } catch (err) {
      showToast("Invalid extents JSON format. Example: [[512, 1024], [4096, 512]]", "error");
      return;
    }

    try {
      showToast("Reassembling extents...", "info");
      const res = await fetch("/api/recovery/restore-extents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image: image,
          extents: parsedExtents,
          destination_name: destName,
        }),
      });
      const data = await res.json();
      if (!data.success) {
        showToast(data.error || "Extents restoration failed", "error");
        return;
      }

      showToast(`Restored ${formatBytes(data.size)} to ${data.filename}`, "success");
      sendToVerifier(data.restored_path);
    } catch (err) {
      showToast(`Restoration failed: ${err.message}`, "error");
    }
  });
}

// Setup Independent Recovery Verifier
function setupRecoveryVerifier() {
  const btnVerify = document.getElementById("btn-run-recovery-verify");
  if (!btnVerify) return;

  btnVerify.addEventListener("click", async () => {
    const target = document.getElementById("verify-recovery-target").value.trim();
    const baselineHash = document.getElementById("verify-baseline-hash").value.trim();
    const expectedSize = document.getElementById("verify-expected-size").value.trim();

    if (!target) {
      showToast("Please specify a recovered file path", "error");
      return;
    }

    const formData = new FormData();
    formData.append("target", target);
    if (baselineHash) formData.append("baseline_hash", baselineHash);
    if (expectedSize) formData.append("expected_size", expectedSize);

    try {
      showToast("Running recovery structural & parser verification...", "info");
      const res = await fetch("/api/recovery/verify", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!data.success) {
        showToast(data.error || "Verification failed", "error");
        return;
      }

      showToast("Recovery integrity evaluated", "success");
      renderRecoveryResult(data.data);
    } catch (err) {
      showToast(`Verification error: ${err.message}`, "error");
    }
  });
}

// Render Recovery Verification Results
function renderRecoveryResult(result) {
  document.getElementById("recovery-empty-state").style.display = "none";
  document.getElementById("recovery-result-content").style.display = "block";

  const score = result.confidence_score ?? 0;
  const radial = document.getElementById("recovery-score-radial");
  if (radial) {
    radial.style.strokeDashoffset = 163 - (163 * score / 100);
  }
  const scoreText = document.getElementById("recovery-score-text");
  if (scoreText) scoreText.textContent = `${score}%`;

  const verdict = result.details?.verdict || (score >= 90 ? "CONFIRMED" : score >= 70 ? "PROBABLE" : "UNCERTAIN");
  const badge = document.getElementById("recovery-verdict-badge");
  if (badge) {
    badge.className = `type-pill ${getVerdictClass(verdict)}`;
    badge.textContent = verdict;
  }

  const magicVal = document.getElementById("recovery-magic-val");
  if (magicVal) {
    magicVal.textContent = result.details?.magic_valid ? "VALID" : "INVALID";
    magicVal.style.color = result.details?.magic_valid ? "var(--emerald)" : "var(--coral-red)";
  }

  const structVal = document.getElementById("recovery-struct-val");
  if (structVal) {
    structVal.textContent = result.details?.structural_valid ? "PASSED" : "CORRUPT";
    structVal.style.color = result.details?.structural_valid ? "var(--emerald)" : "var(--coral-red)";
  }

  const parserVal = document.getElementById("recovery-parser-val");
  if (parserVal) {
    parserVal.textContent = result.details?.parser_valid ? "PASSED" : "FAILED";
    parserVal.style.color = result.details?.parser_valid ? "var(--emerald)" : "var(--coral-red)";
  }

  document.getElementById("recovery-calc-hash").textContent = result.recovered_hash || "N/A";

  // Progress bars
  const comps = result.details?.confidence_components || {};
  const hashScore = comps.hash_integrity ?? 0;
  const structScore = comps.structural_validation ?? 0;
  const parserScore = comps.parser_load ?? 0;
  const compScore = comps.completeness ?? 0;

  setBar("bar-recovery-hash", "recovery-comp-hash", hashScore, 40);
  setBar("bar-recovery-struct", "recovery-comp-struct", structScore, 30);
  setBar("bar-recovery-parser", "recovery-comp-parser", parserScore, 20);
  setBar("bar-recovery-complete", "recovery-comp-complete", compScore, 10);
}
