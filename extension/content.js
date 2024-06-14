// Open the Log
function clickLogButton() {
    const logButton = document.querySelector("#canvas > div.game-column > div.game-main-container.four-color > div.aux-chat-bottom-buttons-ctn > div > button");
    if (logButton) {
        logButton.click();
        console.log('Clicked log button!');
        setupLogObserver();
    } else {
        console.log('Log button not found.');
    }
}

// Function to set up an observer for the log modal
function setupLogObserver() {
    const logModal = document.querySelector("#canvas > div.game-column > div.game-main-container.four-color > div.modal-overlay");

    if (logModal) {
        console.log("Log is open.")
        setTimeout(findLogEntry, 500);
    } else {
        console.log('Log modal not found.');
    }
}

// Function to find the desired log entry
function findLogEntry() {
    const entriesContainer = document.querySelector("#canvas > div.game-column > div.game-main-container.four-color > div.modal-overlay > div > div.modal-body > div.log-modal-body > div.log-modal-entries");
    if (entriesContainer) {
        const entries = entriesContainer.querySelectorAll("div.entry-ctn");
        for (let entry of entries) {
            if (entry.classList.contains("start-game")) {
                console.log("Found 'start-game entry-ctn':", entry);
                return;
            }
            console.log(entry);
        }
    } else {
        console.log("Log entries container not found.");
    }
}

// Observe whether or not it's my turn
const turnObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            mutation.addedNodes.forEach((node) => {
                const decisionElement = document.querySelector("#canvas > div.game-column > div.game-main-container.four-color > div.game-decisions-ctn > div > p");
                if (decisionElement) {
                    clickLogButton();
                }
            });
        }
    });
});

// Start observing the game table for changes indicating it's the user's turn
const targetNode = document.querySelector("#canvas > div.game-column > div.game-main-container.four-color > div.table");
if (targetNode) {
    turnObserver.observe(targetNode, { childList: true, subtree: true });
} else {
    console.log('Game table not found.');
}