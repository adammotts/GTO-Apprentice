from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time

CHROME_DRIVER_PATH = "/Users/ma/Desktop/chromedriver-mac-x64/chromedriver"
POKERNOW_URL = "https://www.pokernow.club/games/pgl9iiD1zJai2oQ2wWedG_zIj"
GTO_WIZARD_URL = "https://app.gtowizard.com/solutions?solution_type=gwiz&gmfs_solution_tab=ai_sols&gametype=CashHu500zSimple&depth=100&gmfft_sort_key=0&gmfft_sort_order=desc"

service_pokernow = Service(executable_path=CHROME_DRIVER_PATH)
driver_pokernow = webdriver.Chrome(service=service_pokernow)
driver_pokernow.get(POKERNOW_URL)

service_gto = Service(executable_path=CHROME_DRIVER_PATH)
driver_gto = webdriver.Chrome(service=service_gto)
driver_gto.get(GTO_WIZARD_URL)

username = input("Log Into Your Accounts and Enter Your Username When Ready: ")

driver_gto.get(GTO_WIZARD_URL)

body = driver_pokernow.find_element(By.TAG_NAME, 'body')
action_monitor_element = driver_pokernow.find_element(By.XPATH, '/html/body/div/div/div[1]/div[3]')
previous_text = ''
last_gto_url = ''

SUIT_MAP = {
    "♠": "s",
    "♣": "c",
    "♦": "d",
    "♥": "h"
}

RANK_MAP = {
    "A": 14,
    "K": 13,
    "Q": 12,
    "J": 11,
    "T": 10,
    "9": 9,
    "8": 8,
    "7": 7,
    "6": 6,
    "5": 5,
    "4": 4,
    "3": 3,
    "2": 2
}

while True:
    current_text = action_monitor_element.text
    if current_text != previous_text:
        body.send_keys('l')
        time.sleep(0.5)
        log_text = body.text
        time.sleep(0.5)
        body.send_keys(Keys.ESCAPE)
        log_lines = [
            line for line in log_text.split('-- starting hand', 1)[0].split('Session Log')[1].split('\n') if
                'Your hand is' in line or
                'posts' in line or
                'raises' in line or
                'calls' in line or
                'checks' in line or
                'bets' in line or
                'Flop' in line or
                'Turn' in line or
                'River' in line
        ][::-1]

        hand = ''
        full_hand = ''
        big_blind = 0
        history_spot = 0
        preflop_actions = []
        flop_actions = []
        river_actions = []
        board = ''

        for line in log_lines:
            if 'Your hand is' in line:
                hand = [card.strip().replace('10', 'T') for card in line.split('Your hand is ')[1].split(',')]
                full_hand = ''.join(sorted([f'{card[0]}{SUIT_MAP[card[-1]]}' for card in hand], key=lambda x: -RANK_MAP[x[0]]))
                hand = f"{full_hand[0]}{full_hand[2]}{'s' if full_hand[1] == full_hand[3] else '' if full_hand[0] == full_hand[2] else 'o'}"

            elif 'posts' in line:
                if 'big blind' in line:
                    big_blind = int(line.split('posts a big blind of')[1].strip())

            elif 'raises' in line:
                preflop_actions.append(f'R{min(int(line.split("raises to ")[1].strip())/big_blind, 100)}')

            elif 'calls' in line:
                preflop_actions.append(f'C')

        history_spot = len(preflop_actions)


        gto_url = f'{GTO_WIZARD_URL}&history_spot={history_spot}&preflop_actions={"-".join(preflop_actions)}'

        # Can't do postflop solutions yet without premium?
        if 'Flop' not in "".join(log_lines) and gto_url != last_gto_url:
            driver_gto.get(gto_url)

            time.sleep(4)

            if hand and username not in log_lines[-1]:
                css_selector = f"#hero_{hand}"
                print(css_selector)
                driver_gto.execute_script(f"document.querySelector('{css_selector}').click();")

            last_gto_url = gto_url

        previous_text = current_text
    time.sleep(1)