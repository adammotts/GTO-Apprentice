// Function to fetch the log from the given URL
const fetchLog = async (pokernowUrl) => {
    const logUrl = `${pokernowUrl}/log`;
    console.log('Fetching log:', logUrl);
    try {
        const response = await fetch(logUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();

        const filteredLogs = [];
        for (const log of data.logs) {
            if (log.msg.includes("starting hand")) {
                break;
            }

            filteredLogs.push(log);
        }
        
        return filteredLogs.reverse();
    } catch (error) {
        console.error('Error fetching log:', error);
        return null;
    }
};

const getHand = (logMessage) => {
    const handRegex = /Your hand is (\d{1,2}|[JQKA])([♠♣♥♦]), (\d{1,2}|[JQKA])([♠♣♥♦])/;
    const match = logMessage.match(handRegex);

    let card1Rank = match[1];
    let card1Suit = match[2];
    let card2Rank = match[3];
    let card2Suit = match[4];

    const rankToString = (rank) => {
        if (rank === '10') {
            return 'T';
        }
        return rank;
    };

    const rankOrder = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'];

    let highRank, lowRank;
    if (rankOrder.indexOf(rankToString(card1Rank)) > rankOrder.indexOf(rankToString(card2Rank))) {
        highRank = card1Rank;
        lowRank = card2Rank;
    } else {
        highRank = card2Rank;
        lowRank = card1Rank;
    }

    // Determine suited or offsuit
    let suited = '';
    if (card1Rank !== card2Rank) {
        suited = card1Suit === card2Suit ? 's' : 'o';
    }

    // Construct the final hand string
    const handString = `${rankToString(highRank)}${rankToString(lowRank)}${suited}`;

    return handString;
};

const getBigBlindAmount = (logMessage) => {
    const bigBlindRegex = /big blind of (\d+)/;
    const match = logMessage.match(bigBlindRegex);

    return match[1];
}

const getRaiseAmount = (logMessage) => {
    const raiseRegex = /raises to (\d+)/;
    const match = logMessage.match(raiseRegex);

    return match[1];
}

// Observe whether or not it's my turn
const turnObserver = new MutationObserver((mutations) => {
    mutations.forEach(async (mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            mutation.addedNodes.forEach(async (node) => {
                const decisionElement = document.querySelector("#canvas > div.game-column > div.game-main-container.four-color > div.game-decisions-ctn > div > p");
                if (decisionElement) {
                    const logs = await fetchLog(window.location.href);
                    console.log('Returned log data:', logs);

                    let hand = null;
                    let bigBlindAmount = null;
                    let preflopActions = [];

                    for (const log of logs) {
                        logMessage = log.msg;
                        
                        // For getting hole cards
                        if (logMessage.includes("Your hand is")) {
                            hand = getHand(logMessage);
                        }

                        // For getting big blind amount
                        if (logMessage.includes("big blind of")) {
                            bigBlindAmount = getBigBlindAmount(logMessage);
                        }

                        // For getting preflop actions
                        if (logMessage.includes("raises to")) {
                            preflopActions.push(`R${getRaiseAmount(logMessage) / bigBlindAmount}`);
                        }

                        if (logMessage.includes("calls")) {
                            preflopActions.push('C');
                        }
                    }

                    console.log('Hand:', hand);
                    console.log("Big blind amount:", bigBlindAmount);
                    console.log('Preflop actions:', preflopActions);
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