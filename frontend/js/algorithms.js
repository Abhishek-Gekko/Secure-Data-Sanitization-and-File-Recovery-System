/**
 * Test Lab, Sandbox Generator & Algorithm Utilities Frontend Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  const btnGenerateSamples = document.getElementById("btn-generate-sandbox-samples");
  if (btnGenerateSamples) {
    btnGenerateSamples.addEventListener("click", async () => {
      try {
        btnGenerateSamples.disabled = true;
        btnGenerateSamples.textContent = "Generating Artifacts...";
        showToast("Generating forensic test disk image & sample files...", "info");

        const res = await fetch("/api/algorithm/sandbox/generate", {
          method: "POST",
        });
        const data = await res.json();

        if (!data.success) {
          showToast(data.error || "Failed to generate samples", "error");
          return;
        }

        showToast(`Successfully created ${data.files.length} test files & disk image!`, "success");
        await loadSandboxFiles();
      } catch (err) {
        showToast(`Error generating samples: ${err.message}`, "error");
      } finally {
        btnGenerateSamples.disabled = false;
        btnGenerateSamples.innerHTML = `⚡ Generate Sample Forensic Evidence`;
      }
    });
  }
});
