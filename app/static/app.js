// Update header timeline from API response
function updateTimeline(tl) {
    if (!tl) return;
    const projected = document.querySelector(".timeline-projected");
    if (projected) projected.textContent = tl.projected_end;

    const delayEl = document.querySelector(".timeline-delay");
    const onTrack = document.querySelector(".timeline-on-track");

    if (tl.delay_days > 0) {
        if (delayEl) {
            delayEl.textContent = "+" + tl.delay_days + "d";
            delayEl.className = "timeline-delay delay-" + tl.delay_level;
        } else if (onTrack) {
            onTrack.textContent = "+" + tl.delay_days + "d";
            onTrack.className = "timeline-delay delay-" + tl.delay_level;
        }
    } else {
        if (delayEl) {
            delayEl.textContent = "on track";
            delayEl.className = "timeline-on-track";
        }
        if (onTrack) {
            onTrack.textContent = "on track";
        }
    }
}

// Toggle item checkbox via AJAX
async function toggleItem(itemId) {
    const checkbox = document.querySelector(`input[data-id="${itemId}"]`);
    try {
        const response = await fetch(`${window.__PREFIX || ""}/api/item/${itemId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" }
        });
        if (response.ok) {
            const data = await response.json();
            updateTimeline(data.timeline);
        } else {
            checkbox.checked = !checkbox.checked;
        }
    } catch (error) {
        checkbox.checked = !checkbox.checked;
    }
}

// Toggle mastery item checkbox
async function toggleMastery(masteryId) {
    const checkbox = document.querySelector(`input[data-id="${masteryId}"]`);
    try {
        const response = await fetch(`${window.__PREFIX || ""}/api/mastery/${masteryId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" }
        });
        if (!response.ok) {
            checkbox.checked = !checkbox.checked;
        }
    } catch (error) {
        checkbox.checked = !checkbox.checked;
    }
}

// Auto-save reflection with debounce
const reflectionDebounce = {};

document.querySelectorAll(".reflection-textarea").forEach(textarea => {
    const blockId = textarea.dataset.blockId;
    const statusEl = document.getElementById(`status-${blockId}`);

    textarea.addEventListener("input", () => {
        clearTimeout(reflectionDebounce[blockId]);
        statusEl.textContent = "Saving...";
        statusEl.classList.remove("saved");
        statusEl.classList.add("saving");

        reflectionDebounce[blockId] = setTimeout(async () => {
            try {
                const response = await fetch(`${window.__PREFIX || ""}/api/block/${blockId}/reflection`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ reflection: textarea.value })
                });
                if (response.ok) {
                    statusEl.textContent = "Saved \u2713";
                    statusEl.classList.remove("saving");
                    statusEl.classList.add("saved");
                    setTimeout(() => statusEl.textContent = "", 2000);
                }
            } catch (error) {
                statusEl.textContent = "Save failed";
                statusEl.classList.add("saving");
            }
        }, 800);
    });
});

// Phase sidebar toggle
function togglePhase(phaseId) {
    const group = document.querySelector(`[data-phase-id="${phaseId}"]`);
    const weeksList = group.querySelector(".weeks-list");
    weeksList.classList.toggle("show");
    group.classList.toggle("active");
}

// Dark Mode Only. No Exceptions.
(function () {
    const comebacks = [
        "You wish! \ud83c\udf11",
        "Nice try. We don\u2019t do light mode here.",
        "Light mode? In this economy?",
        "404: Light Mode Not Found.",
        "I admire your optimism. No.",
        "Even my terminal said no.",
        "The dark side has cookies. Stay.",
        "Light mode is just dark mode with a sunburn.",
        "My CSS refuses. I asked.",
        "sudo enable-light-mode \u2192 Permission denied.",
        "Have you tried turning your monitor brightness up instead?",
        "Light mode was deprecated in adamcoding v0.0.1",
        "Roses are red, violets are blue, light mode is off, and so are you \ud83d\udda4",
        "I\u2019d enable light mode but my therapist said to set boundaries.",
        "You\u2019ve been denied. Again. Want a cookie? \ud83c\udf6a",
        "Light mode is a crime in 14 countries. I\u2019m protecting you.",
        "Error: conscience.js blocked that request.",
        "That button is decorative. Like a scarecrow, but for bad ideas.",
        "I\u2019ve consulted the senior devs. They said no.",
        "Your retinas called. They\u2019re relieved.",
        "Light mode ships with every browser. It should stay there.",
        "I\u2019d need a signed PR, two approvals, and a therapist\u2019s note.",
        "We don\u2019t do that here. \ud83e\uddd1\u200d\ud83d\udcbb",
        "Imagine paying your electricity bill to stare at a white screen.",
        "The button exists so you feel like you have a choice. You don\u2019t.",
        "I\u2019d rather push to main on a Friday.",
        "This request has been logged, reviewed, and rejected.",
        "My linter flagged \u2018light mode\u2019 as a critical vulnerability.",
        "That\u2019s the wrong branch. Light mode was never merged.",
        "I checked the git history. Light mode was reverted in commit a2f3c1.",
        "Some things are hardcoded. This is one of them.",
        "Not gonna happen. But I respect the hustle.",
    ];

    var toastTimer = null;

    function showToast(message) {
        var toast = document.getElementById("darkModeToast");
        if (toastTimer) clearTimeout(toastTimer);
        toast.textContent = message;
        toast.classList.add("show");
        toastTimer = setTimeout(function () { toast.classList.remove("show"); }, 5000);
    }

    function handleDarkModeClick() {
        var idx = Math.floor(Math.random() * comebacks.length);
        showToast(comebacks[idx]);
    }

    var btn = document.getElementById("darkModeToggle");
    var btnMobile = document.getElementById("darkModeToggleMobile");
    if (btn) btn.addEventListener("click", handleDarkModeClick);
    if (btnMobile) btnMobile.addEventListener("click", handleDarkModeClick);

    var hamburger = document.getElementById("navHamburger");
    var mobileMenu = document.getElementById("mobileMenu");
    if (hamburger && mobileMenu) {
        hamburger.addEventListener("click", function () {
            mobileMenu.classList.toggle("open");
        });
    }
})();

// Auto-expand current phase
document.addEventListener("DOMContentLoaded", () => {
    const activeWeek = document.querySelector(".week-link.active");
    if (activeWeek) {
        const weeksList = activeWeek.closest(".weeks-list");
        if (weeksList) {
            const group = weeksList.closest(".phase-group");
            group.classList.add("active");
            weeksList.classList.add("show");
        }
    }
});
