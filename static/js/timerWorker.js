// timerWorker.js

self.onmessage = function(e) {
    const { action, timeRemaining } = e.data;
    if (action === 'start') {
        let remaining = timeRemaining;
        const timer = setInterval(() => {
            remaining -= 1000;
            if (remaining <= 0) {
                clearInterval(timer);
                self.postMessage({ action: 'end' });
            } else {
                self.postMessage({ action: 'update', timeRemaining: remaining });
            }
        }, 1000);
    }
};
