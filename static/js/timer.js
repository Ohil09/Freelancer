// Timer persistence using localStorage
// Stores the start timestamp so elapsed time survives page navigation

const TIMER_KEY = 'freelancer_timer_start';
const TIMER_PROJECT_KEY = 'freelancer_timer_project';

let timerInterval = null;

// Get current project ID from the page (set by time.html)
const currentProjectId = window.TIMER_PROJECT_ID || null;

function pad(n) {
    return String(n).padStart(2, '0');
}

function getElapsedSeconds() {
    const startTime = localStorage.getItem(TIMER_KEY);
    if (!startTime) return 0;
    return Math.floor((Date.now() - parseInt(startTime)) / 1000);
}

function updateDisplay() {
    const elapsed = getElapsedSeconds();
    const h = Math.floor(elapsed / 3600);
    const m = Math.floor((elapsed % 3600) / 60);
    const s = elapsed % 60;

    const display = document.getElementById('timer');
    if (display) {
        display.innerHTML = h + 'h ' + pad(m) + 'm ' + pad(s) + 's';
    }
}

function startTimer() {
    // If already running, do nothing
    if (localStorage.getItem(TIMER_KEY)) {
        return;
    }

    // Store start time and project ID
    localStorage.setItem(TIMER_KEY, Date.now().toString());
    if (currentProjectId) {
        localStorage.setItem(TIMER_PROJECT_KEY, currentProjectId);
    }

    beginTicking();
    updateButtonStates(true);
}

function stopTimer() {
    if (!localStorage.getItem(TIMER_KEY)) return;

    const elapsed = getElapsedSeconds();
    const totalHours = (elapsed / 3600).toFixed(2);

    // Fill the hours input if it exists on this page
    const hoursInput = document.getElementById('hoursInput');
    if (hoursInput) {
        hoursInput.value = totalHours;
    }

    // Clear stored timer
    localStorage.removeItem(TIMER_KEY);
    localStorage.removeItem(TIMER_PROJECT_KEY);

    // Stop ticking
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    updateButtonStates(false);
}

function beginTicking() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(updateDisplay, 1000);
    updateDisplay();
}

function updateButtonStates(running) {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const indicator = document.getElementById('timerIndicator');

    if (startBtn) startBtn.disabled = running;
    if (stopBtn) stopBtn.disabled = !running;
    if (indicator) {
        if (running) {
            indicator.classList.remove('hidden');
        } else {
            indicator.classList.add('hidden');
        }
    }
}

// On page load — resume ticking if timer was already running
document.addEventListener('DOMContentLoaded', function () {
    const isRunning = !!localStorage.getItem(TIMER_KEY);

    if (isRunning) {
        beginTicking();
    }

    updateButtonStates(isRunning);
});
