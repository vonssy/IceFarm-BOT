import requests
import json
import os
from urllib.parse import parse_qs, unquote
from colorama import *
from datetime import datetime
import time
import pytz

wib = pytz.timezone('Asia/Jakarta')

class IceFarm:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Host': 'hockey-tap.laborx.io',
            'Origin': 'https://tapsport.laborx.io',
            'Pragma': 'no-cache',
            'Referer': 'https://tapsport.laborx.io/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Ice Farm - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def extract_user_data(self, query: str) -> str:
        parsed_query = parse_qs(query)
        user_data = parsed_query.get('user', [None])[0]

        if user_data:
            user_json = json.loads(unquote(user_data))
            return str(user_json.get('first_name', 'Unknown'))
        return 'Unknown'

    def load_tokens(self):
        try:
            if not os.path.exists('tokens.json'):
                return {"accounts": []}

            with open('tokens.json', 'r') as file:
                data = json.load(file)
                if "accounts" not in data:
                    return {"accounts": []}
                return data
        except json.JSONDecodeError:
            return {"accounts": []}

    def save_tokens(self, tokens):
        with open('tokens.json', 'w') as file:
            json.dump(tokens, file, indent=4)

    def generate_tokens(self, queries: list):
        tokens_data = self.load_tokens()
        accounts = tokens_data["accounts"]

        for idx, query in enumerate(queries):
            account_name = self.extract_user_data(query)

            existing_account = next((acc for acc in accounts if acc["first_name"] == account_name), None)

            if not existing_account:
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Token Is None{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Generating Token... {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                    end="\r", flush=True
                )
                time.sleep(1)

                token = self.user_auth(query)['token']
                if token:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Successfully Generated Token {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                    )
                    accounts.insert(idx, {"first_name": account_name, "token": token})
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}Query Is Expired{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Failed to Generate Token {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                    )

                time.sleep(1)
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}" * 75)

        self.save_tokens({"accounts": accounts})

    def renew_token(self, account_name):
        tokens_data = self.load_tokens()
        accounts = tokens_data.get("accounts", [])
        
        account = next((acc for acc in accounts if acc["first_name"] == account_name), None)
        
        if account and "token" in account:
            token = account["token"]
            if not self.user_balance(token):
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Token Isn't Valid{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Regenerating Token... {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                    end="\r", flush=True
                )
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                time.sleep(1)
                
                accounts = [acc for acc in accounts if acc["first_name"] != account_name]
                
                query = next((query for query in self.load_queries() if self.extract_user_data(query) == account_name), None)
                if query:
                    new_token = self.user_auth(query)['token']
                    if new_token:
                        accounts.append({"first_name": account_name, "token": new_token})
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Query Is Valid{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} Successfully Generated Token {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                        )
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}Query Is Expired{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Failed to Generate Token {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Query Is None. Skipping {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                    )

                time.sleep(1)
        
        self.save_tokens({"accounts": accounts})

    def load_queries(self):
        with open('query.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]

    def user_auth(self, query: str):
        url = 'https://hockey-tap.laborx.io/auth'
        data = json.dumps({'initData':query, 'platform':'tdesktop'})
        self.headers.update({
            'Content-Type': 'application/json'
        })

        response = self.session.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'ok':
                return result['result']
            else:
                return None
        else:
            return None
        
    def user_balance(self, token: str):
        url = 'https://hockey-tap.laborx.io/balance'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'ok':
                return result['result']
            else:
                return None
        else:
            return None
        
    def game_spin(self, token: str):
        url = 'https://hockey-tap.laborx.io/game/spin'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        response = self.session.post(url, headers=self.headers)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'ok':
                return result['result']
            else:
                return None
        else:
            return None
                
    def game_shot(self, token: str):
        url = 'https://hockey-tap.laborx.io/game/shot'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        response = self.session.post(url, headers=self.headers)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'ok':
                return result['result']
            else:
                return None
        else:
            return None

    def game_upgrade(self, token: str, attribute: str):
        url = 'https://hockey-tap.laborx.io/game/upgrade'
        data = json.dumps({'attribute':attribute})
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        response = self.session.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'ok':
                return result['result']
            else:
                return None
        else:
            return None
        
    def question(self):
        while True:
            game_upgrade = input("Auto Upgarde Player Attribute? [y/n] -> ").strip().lower()
            if game_upgrade in ["y", "n"]:
                game_upgrade = game_upgrade == "y"
                break
            else:
                print(f"{Fore.RED+Style.BRIGHT}Invalid Input.{Fore.WHITE+Style.BRIGHT} Choose 'y' to Yes or 'n' to Skip.{Style.RESET_ALL}")

        attributes = []
        attributes_list = ['stamina', 'accuracy', 'regeneration', 'strength']
        if game_upgrade:
            while True:
                print("Select The Attributes to Upgrade [ex: 1,3,4]")
                for i, attr in enumerate(attributes_list, 1):
                    print(f"{i}. {attr.capitalize()}")
                choices = input("Choose Attributes [1-4, Max 4 Attributes] -> ").strip()
                
                try:
                    selected_indices = [int(c) for c in choices.split(',') if c.isdigit()]
                    if any(i < 1 or i > 4 for i in selected_indices) or len(selected_indices) > 4:
                        print(f"{Fore.RED}Invalid input. Please Choose Numbers Between 1 - 4, With a Maximum of 4 Attributes{Style.RESET_ALL}")
                        continue
                    attributes = [attributes_list[i - 1] for i in selected_indices]
                    if attributes:
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print(f"{Fore.RED}Invalid Input. Choose Numbers Between 1 - 4, Separated by Commas [ex: 1,3,4]{Style.RESET_ALL}")

        return game_upgrade, attributes
        
    def process_query(self, query: str, game_upgrade: bool, attributes: list):
        account_name = self.extract_user_data(query)
    
        tokens_data = self.load_tokens()
        accounts = tokens_data.get("accounts", [])

        exist_account = next((acc for acc in accounts if acc["first_name"] == account_name), None)
        if not exist_account:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}Token Not Found in tokens.json{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
            return
        
        if exist_account and "token" in exist_account:
            token = exist_account["token"]

            user = self.user_balance(token)
            if not user:
                self.renew_token(account_name)
                tokens_data = self.load_tokens()
                new_account = next((acc for acc in tokens_data["accounts"] if acc["first_name"] == account_name), None)
                
                if new_account and "token" in new_account:
                    new_token = new_account["token"] 
                    user = self.user_balance(new_token)

            if user:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {user['balance']} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
                time.sleep(1)

                spin = self.game_spin(new_token if 'new_token' in locals() else token)
                if spin:
                    spin_count = spin['lastSpinCount']
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Game Spin{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Is Success {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Reward{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {spin['reward']} $ICE {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Chances{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {spin_count} Left {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    time.sleep(1)

                    spin_count = self.user_auth(query)['user']['lastSpinCount']
                    if spin_count > 0:
                        while spin_count > 0:
                            spin = self.game_spin(new_token if 'new_token' in locals() else token)
                            if spin:
                                spin_count = spin['lastSpinCount']
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Game Spin{Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT} Is Success {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}] [ Reward{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {spin['reward']} $ICE {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}] [ Chances{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {spin_count} Left {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                )
                            else:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Game Spin{Style.RESET_ALL}"
                                    f"{Fore.RED + Style.BRIGHT} Isn't Success {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                )
                                time.sleep(1)

                        if spin_count == 0:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Game Spin{Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT} Is Stopped {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} No Chance Left {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                            time.sleep(1)
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Game Spin{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} Is Skipped {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} No Chance Left {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                    time.sleep(1)
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Game Spin{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Is Skipped {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} No Chance Left {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                time.sleep(1)

                shot = self.game_shot(new_token if 'new_token' in locals() else token)
                if shot:
                    stamina_count = shot['staminaValue']
                    if shot['result']:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Game Shot{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} Result Is Goal {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {shot['balance']} $ICE {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}] [ Chances{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {stamina_count} Left {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        time.sleep(1)

                    stamina_count = self.user_auth(query)['user']['staminaValue']
                    if stamina_count >= 10:
                        while stamina_count >= 10:
                            shot = self.game_shot(new_token if 'new_token' in locals() else token)
                            if shot:
                                stamina_count = shot['staminaValue']
                                if shot['result']:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}[ Game Shot{Style.RESET_ALL}"
                                        f"{Fore.GREEN + Style.BRIGHT} Result Is Goal {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {shot['balance']} $ICE {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Chances{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {stamina_count} Left {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                    )
                                else:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}[ Game Shot{Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT} Result Isn't Goal {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {shot['balance']} $ICE {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Chances{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {stamina_count} Left {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                    )
                                    time.sleep(1)
                            else:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Game Shot{Style.RESET_ALL}"
                                    f"{Fore.RED + Style.BRIGHT} Is Failed to Play {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                )
                                time.sleep(1)

                        if stamina_count == 0:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Game Shot{Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT} Is Stopped {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} No Chance Left {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                            time.sleep(1)
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Game Shot{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} Is Skipped {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} No Chance Left {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                    time.sleep(1)
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Game Shot{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Is Skipped {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} No Chance Left {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                time.sleep(1)

                attribute_map = {
                    'stamina': 'staminaValue',
                    'accuracy': 'accuracyValue',
                    'regeneration': 'intellectValue',
                    'strength': 'strengthValue'
                }

                if game_upgrade:
                    for attribute in attributes:
                        upgrade_result = self.game_upgrade(new_token if 'new_token' in locals() else token, attribute)
                        if upgrade_result:
                            upgraded_value = upgrade_result.get(attribute_map[attribute], "N/A")
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Upgrade Atrributes{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {attribute} {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Is Success{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ] [ Value{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {upgraded_value} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Upgrade Atrributes{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {attribute} {Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT}Isn't Success{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reason{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} No Enough $ICE {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        time.sleep(1)
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Upgrade Atrributes{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Is Skipped {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                
    def main(self):
        self.clear_terminal()
        try:
            queries = self.load_queries()
            self.generate_tokens(queries)

            game_upgrade, attributes = self.question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(queries)}{Style.RESET_ALL}"
                )
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

                for query in queries:
                    if query:
                        self.process_query(query, game_upgrade, attributes)
                        self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                        time.sleep(3)

                seconds = 1800
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    time.sleep(1)
                    seconds -= 1

        except KeyboardInterrupt:
            self.log(f"{Fore.RED + Style.BRIGHT}[ EXIT ] Ice Farm - BOT{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    bot = IceFarm()
    bot.main()