let simulationCleanup = [];

function cleanupSimulations() {
  for (const cleanup of simulationCleanup) {
    cleanup();
  }
  simulationCleanup = [];
}

function createSimulation(root, manifest) {
  const image = root.querySelector("[data-simulation-image]");
  const slider = root.querySelector("[data-simulation-slider]");
  const frames = manifest.frames;
  const count = frames.length;
  const resumeDelayMs = 2200;
  const cMax = frames[0].c;
  const cMin = frames[count - 1].c;
  const progressValues = frames.map((frame) => (cMax - frame.c) / (cMax - cMin));

  let index = 0;
  let autoplayTimer = null;
  let resumeTimer = null;

  slider.min = "0";
  slider.max = "1";
  slider.step = "0.001";
  slider.value = String(progressValues[0]);

  function clearTimers() {
    if (autoplayTimer !== null) {
      window.clearTimeout(autoplayTimer);
      autoplayTimer = null;
    }
    if (resumeTimer !== null) {
      window.clearTimeout(resumeTimer);
      resumeTimer = null;
    }
  }

  function render(nextIndex) {
    index = nextIndex;
    const frame = frames[index];
    image.src = `assets/simulation/${frame.image}`;
    image.alt = `Simulation frame ${frame.index}`;
    slider.value = String(progressValues[index]);
  }

  function nearestFrameIndex(targetProgress) {
    let nearestIndex = 0;
    let nearestDistance = Math.abs(progressValues[0] - targetProgress);
    for (let candidate = 1; candidate < count; candidate += 1) {
      const distance = Math.abs(progressValues[candidate] - targetProgress);
      if (distance < nearestDistance) {
        nearestIndex = candidate;
        nearestDistance = distance;
      }
    }
    return nearestIndex;
  }

  function scheduleAutoplay() {
    autoplayTimer = window.setTimeout(() => {
      const nextIndex = (index + 1) % count;
      render(nextIndex);
      scheduleAutoplay();
    }, manifest.durations_ms[index]);
  }

  function restartAutoplaySoon() {
    clearTimers();
    resumeTimer = window.setTimeout(() => {
      scheduleAutoplay();
    }, resumeDelayMs);
  }

  slider.addEventListener("input", () => {
    clearTimers();
    render(nearestFrameIndex(Number(slider.value)));
    restartAutoplaySoon();
  });

  render(index);

  for (const frame of frames.slice(1)) {
    const preload = new Image();
    preload.src = `assets/simulation/${frame.image}`;
  }

  scheduleAutoplay();

  return clearTimers;
}

document$.subscribe(() => {
  cleanupSimulations();

  const roots = document.querySelectorAll("[data-simulation-root]");
  for (const root of roots) {
    fetch("assets/simulation/manifest.json")
      .then((response) => response.json())
      .then((manifest) => {
        simulationCleanup.push(createSimulation(root, manifest));
      });
  }
});
