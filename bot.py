import requests
import yaml
from web3 import Web3

class ConfigManager:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def get_blacklists(self):
        return self.config.get('blacklists', {})

    def get_apis(self):
        return self.config.get('apis', {})

    def get_filters(self):
        return self.config.get('filters', {})

    def get_alerts(self):
        return self.config.get('alerts', {})

def verify_token_with_rugcheck(token_address, api_key):
    url = f"https://api.rugcheck.com/verify?token={token_address}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code}")

def fetch_pocket_universe_analysis(token_address, api_key):
    url = f"https://api.pocketuniverse.app/token-analysis?token={token_address}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code}")

def is_supply_bundled(token_holders):
    top_holder_percentage = sum(holder['percentage'] for holder in token_holders[:5])
    return top_holder_percentage > 50  # Example threshold

def blacklist_token_and_dev(token_address, dev_address, blacklists):
    blacklists['tokens'].append(token_address)
    blacklists['developers'].append(dev_address)
    print(f"Blacklisted token: {token_address} and developer: {dev_address}")

def send_alert(message, alerts):
    if alerts.get('telegram', {}).get('enabled', False):
        bot_token = alerts['telegram']['bot_token']
        chat_id = alerts['telegram']['chat_id']
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload)

def analyze_token(token_address, dev_address, token_holders, config):
    rugcheck_api_key = config.get_apis().get('rugcheck')
    pocket_universe_api_key = config.get_apis().get('pocket_universe')
    blacklists = config.get_blacklists()

    # Step 1: Verify token with Rugcheck
    rugcheck_data = verify_token_with_rugcheck(token_address, rugcheck_api_key)
    if rugcheck_data.get('status') != 'good':
        print(f"Unverified token: {token_address}")
        return

    # Step 2: Check supply bundling
    if is_supply_bundled(token_holders):
        blacklist_token_and_dev(token_address, dev_address, blacklists)
        send_alert(f"Blacklisted token: {token_address}", config.get_alerts())
        return

    # Step 3: Analyze with Pocket Universe
    pocket_universe_data = fetch_pocket_universe_analysis(token_address, pocket_universe_api_key)
    if pocket_universe_data.get('risk_score') > 0.8:
        send_alert(f"High-risk token detected: {token_address}", config.get_alerts())
        return

    # Step 4: Proceed with trading
    print(f"Token {token_address} is safe to interact with.")
    # Integrate Toxi Bot trading logic here
    # Example: toxi_bot.buy(token_address)

# Example usage
config = ConfigManager('config.yaml')
token_address = "0xTokenAddress"
dev_address = "0xDevAddress"
token_holders = [
    {"address": "0xHolder1", "percentage": 40},
    {"address": "0xHolder2", "percentage": 20},
    {"address": "0xHolder3", "percentage": 10},
]
analyze_token(token_address, dev_address, token_holders, config)
