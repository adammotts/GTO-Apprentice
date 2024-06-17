from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask_cors import CORS
import time
import random

app = Flask(__name__)
CORS(app, supports_credentials=True)
driver = None

def get_driver():
    global driver
    if driver is None:
        options = Options()
        driver = webdriver.Chrome(options=options)

    return driver

@app.route('/login', methods=['POST'])
def login():
    driver = get_driver()
    driver.get("https://app.gtowizard.com/login")
    return jsonify(
        {
            "message": "Logged in successfully"
        }
    )

@app.route('/get_solution', methods=['POST'])
def get_solution():
    driver = get_driver()

    # print(request.get_json())

    data = request.get_json()
    preflop_actions = data['preflop_actions']
    hand = data['hand']
    driver.get(f"https://app.gtowizard.com/solutions?solution_type=gwiz&gmfs_solution_tab=ai_sols&gametype=CashHu500zSimple&depth=100&gmff_depth=100&gmfft_sort_key=0&gmfft_sort_order=desc&preflop_actions={'-'.join(preflop_actions)}&history_spot={len(preflop_actions)}")

    print(f"https://app.gtowizard.com/solutions?solution_type=gwiz&gmfs_solution_tab=ai_sols&gametype=CashHu500zSimple&depth=100&gmff_depth=100&gmfft_sort_key=0&gmfft_sort_order=desc&preflop_actions={'-'.join(preflop_actions)}&history_spot={len(preflop_actions)}")

    time.sleep(5)

    extract_stats_script = f'''
        return (function() {{
            function waitForElementAndReturnData() {{
                var checkCondition = function(resolve) {{
                    var container = document.querySelector('#hero_{hand} > div.rtc_graph_legend.no-scroll-track');
                    if (container && container.children.length > 0) {{
                        var map = {{}};
                        var children = container.children;
                        for (var i = 0; i < children.length; i++) {{
                            var keySpan = children[i].querySelector('span:nth-child(1)');
                            var valueSpan = children[i].querySelector('span:nth-child(2)');
                            if (keySpan && valueSpan) {{
                                var key = keySpan.textContent.trim();
                                var value = valueSpan.textContent.trim();

                                var parts = key.split(' ');
                                var lastPart = parts[parts.length - 1];
                                var numericValue = parseFloat(lastPart);

                                if (parts.length > 1) {{
                                    key = parts.slice(0, -1).join(' ');
                                }}

                                value = {{'amount': numericValue, 'percentage': parseFloat(value)}};
                                map[key] = value;
                            }}
                        }}
                        resolve(map);
                    }} else {{
                        setTimeout(function() {{ checkCondition(resolve); }}, 100);
                    }}
                }};

                return new Promise(checkCondition);
            }}

            document.querySelector('#hero_{hand}').click();

            return waitForElementAndReturnData();
        }})();
    '''

    try:
        stats = driver.execute_script(extract_stats_script)

    except:
        return jsonify(
            {
                "message": "Failed to retrieve solution"
            }
        )

    print(stats)

    cumulative_probability = 0
    action_probabilities = []
    for action, details in stats.items():
        if details['percentage'] > 0:
            cumulative_probability += details['percentage']
            action_probabilities.append((cumulative_probability, action))

    random_number = random.uniform(0, 100)
    selected_action = None
    for threshold, action in action_probabilities:
        if random_number <= threshold:
            selected_action = action
            selected_amount = stats[selected_action]['amount']
            break

    print(f'{preflop_actions}')
    print(f'{selected_action} {selected_amount}')

    return jsonify(
        {
            "selected_action": selected_action,
            "selected_amount": selected_amount,
            "message": "Solution retrieved successfully"
        }
    )

if __name__ == '__main__':
    app.run(debug=True)
