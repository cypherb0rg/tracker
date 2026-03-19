// Update header timeline from API response
function updateTimeline(tl) {
    if (!tl) return;
    const projected = document.querySelector('.timeline-projected');
    if (projected) projected.textContent = tl.projected_end;

    const delayEl = document.querySelector('.timeline-delay');
    const onTrack = document.querySelector('.timeline-on-track');

    if (tl.delay_days > 0) {
        if (delayEl) {
            delayEl.textContent = '+' + tl.delay_days + 'd';
            delayEl.className = 'timeline-delay delay-' + tl.delay_level;
        } else if (onTrack) {
            // Switch from "on track" to delay badge
            onTrack.textContent = '+' + tl.delay_days + 'd';
            onTrack.className = 'timeline-delay delay-' + tl.delay_level;
        }
    } else {
        if (delayEl) {
            delayEl.textContent = 'on track';
            delayEl.className = 'timeline-on-track';
        }
        if (onTrack) {
            onTrack.textContent = 'on track';
        }
    }
}

// Toggle item checkbox via AJAX
async function toggleItem(itemId) {
    const checkbox = document.querySelector(`input[data-id="${itemId}"]`);
    try {
        const response = await fetch(`/api/item/${itemId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' }
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
        const response = await fetch(`/api/mastery/${masteryId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' }
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

document.querySelectorAll('.reflection-textarea').forEach(textarea => {
    const blockId = textarea.dataset.blockId;
    const statusEl = document.getElementById(`status-${blockId}`);

    textarea.addEventListener('input', () => {
        clearTimeout(reflectionDebounce[blockId]);
        statusEl.textContent = 'Saving...';
        statusEl.classList.remove('saved');
        statusEl.classList.add('saving');

        reflectionDebounce[blockId] = setTimeout(async () => {
            try {
                const response = await fetch(`/api/block/${blockId}/reflection`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reflection: textarea.value })
                });
                if (response.ok) {
                    statusEl.textContent = 'Saved ✓';
                    statusEl.classList.remove('saving');
                    statusEl.classList.add('saved');
                    setTimeout(() => statusEl.textContent = '', 2000);
                }
            } catch (error) {
                statusEl.textContent = 'Save failed';
                statusEl.classList.add('saving');
            }
        }, 800);
    });
});

// Phase sidebar toggle
function togglePhase(phaseId) {
    const group = document.querySelector(`[data-phase-id="${phaseId}"]`);
    const weeksList = group.querySelector('.weeks-list');
    const phaseBtn = group.querySelector('.phase-btn');

    weeksList.classList.toggle('show');
    group.classList.toggle('active');
}

// Theme toggle
(function () {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    // Sync checkbox to current theme
    toggle.checked = document.documentElement.getAttribute('data-theme') === 'dark';

    toggle.addEventListener('change', () => {
        const dark = toggle.checked;
        document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
        localStorage.setItem('theme', dark ? 'dark' : 'light');
    });
})();

// Auto-expand current phase
document.addEventListener('DOMContentLoaded', () => {
    const activeWeek = document.querySelector('.week-link.active');
    if (activeWeek) {
        const weeksList = activeWeek.closest('.weeks-list');
        if (weeksList) {
            const group = weeksList.closest('.phase-group');
            group.classList.add('active');
            weeksList.classList.add('show');
        }
    }
});
