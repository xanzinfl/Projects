document.addEventListener('DOMContentLoaded', () => {
    const countdownTimerEl = document.getElementById('countdown-timer');
    const timezoneInfoEl = document.getElementById('timezone-info');
    const localTimeInfoEl = document.getElementById('local-time-info');
    const minimizeToTrayCheck = document.getElementById('minimize-to-tray');
    const runOnStartupCheck = document.getElementById('run-on-startup');
    const notificationTextEl = document.getElementById('notification-text');
    const saveBtn = document.getElementById('save-btn');

    let next420Info = null;
    let updateInterval;

    async function loadSettings() {
        const settings = await window.electronAPI.getSettings();
        minimizeToTrayCheck.checked = settings.minimizeToTray;
        runOnStartupCheck.checked = settings.runOnStartup;
        notificationTextEl.value = settings.notificationText;
    }

    function saveSettings() {
        const settings = {
            minimizeToTray: minimizeToTrayCheck.checked,
            runOnStartup: runOnStartupCheck.checked,
            notificationText: notificationTextEl.value,
        };
        window.electronAPI.saveSettings(settings);
        const originalText = saveBtn.textContent;
        saveBtn.textContent = 'Saved!';
        setTimeout(() => {
            saveBtn.textContent = originalText;
        }, 1500);
    }
    
    async function updateCountdown() {
        if (!next420Info) {
            timezoneInfoEl.textContent = 'Finding the next 4:20...';
            countdownTimerEl.textContent = '--:--:--';
            localTimeInfoEl.textContent = '';
            next420Info = await window.electronAPI.getNext420();
        }

        const next420Time = new Date(next420Info.next420TimeUtc);
        const timeUntil = next420Time - new Date();
        if (timeUntil > 0) {
            const hours = Math.floor(timeUntil / (1000 * 60 * 60));
            const minutes = Math.floor((timeUntil % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeUntil % (1000 * 60)) / 1000);

            countdownTimerEl.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            timezoneInfoEl.textContent = `The next 4:20 is in ${next420Info.timezone}`;
            localTimeInfoEl.textContent = `(That's ${next420Info.localTime} for you)`;

        } else {
            countdownTimerEl.textContent = "It's 4:20!";
            timezoneInfoEl.textContent = `Right now in ${next420Info.timezone}`;
            localTimeInfoEl.textContent = '';
            window.electronAPI.notify420(notificationTextEl.value);
            next420Info = null;
            clearInterval(updateInterval);
            setTimeout(startUpdates, 60000);
        }
    }

    function startUpdates() {
        updateCountdown();
        updateInterval = setInterval(updateCountdown, 1000);
    }

    saveBtn.addEventListener('click', saveSettings);
    loadSettings();
    startUpdates();
});