from columnar import columnar
from click import style
import re
from mtg_api import MtgApi


class MtgDeck(MtgApi):

    def __init__(self) -> None:
        super().__init__()

    def load_deck_from_file(self, filename):
        '''
        Create a dictionary mapping of the deck with name and qty
        Return them in alphabetical order
        ex {CardName: 1}
        '''
        deck_data = {}
        with open(filename) as f:
            for card in f:
                # If there are empty lines just ignore them
                if card == "\n":
                    continue
                card = card.replace("\n", "")
                # If values are not supplied we will assume that there is one of each
                try:
                    if int(card[0]):
                        # List will display 1 Card Name. Only split at the first space
                        card_info = card.split(" ", 1)
                        deck_data[card_info[1]] = int(card_info[0])
                except ValueError:
                    deck_data[card] = 1
        # Sort the dict keys in to alphabetical order
        sorted_deck = list(deck_data.keys())
        sorted_deck.sort()
        return {i: deck_data[i] for i in sorted_deck}

    def separate_cards(self, deck: dict):
        '''
        Creates a list of all the cards in the deck
        If there are multiple copies each one will be added separately in the list
        Returns a list with all the cards

        example: {card1: 1, card2: 2}
        --> ["card1", "card2_0", "card2_1"]
        '''
        deck_list = []
        for k, v in deck.items():
            if v > 1:
                # Add multiple copies of the same card
                for i in range(v):
                    # Assign a number to each basic land to have a unique card
                    deck_list.append(k + f"_{i}")
            else:
                # If it is a basic land we need to append a unique number to it
                if k.lower() in ["plains", "island", "swamp", "mountain", "forest"]:
                    deck_list.append(k + "_0")
                else:
                    deck_list.append(k)
        return deck_list

    def compare_decks(self, deck1, deck2, write_to_file=False):
        '''
        Takes two decks as input and check what is the difference
        Prints  out the result
        Additionally you can write to file to an external file by setting the flag to True
        '''

        old = self.separate_cards(deck1)
        new = self.separate_cards(deck2)

        # Iterate through the two deck and see which card are incoming and which cards are outgoing
        incoming = []
        outgoing = []

        for card in new:
            if card not in old:
                incoming.append(card)

        for card in old:
            if card not in new:
                outgoing.append(card)

        # Print the results
        data = []
        for a, b in zip(incoming, outgoing):
            data.append([a, b])

        patterns = [
            ('Incoming', lambda text: style(text, fg='green')),
            ('Outgoing', lambda text: style(text, fg='red'))
        ]

        table = columnar(
            data, headers=[f"Incoming ({len(incoming)})", f"Outgoing ({len(outgoing)})"], patterns=patterns, justify="c")
        print(table)

        if write_to_file:
            with open(f"./deck_changes.txt", "w") as f:
                f.write(table)

    def get_card_information(self, name: str):
        '''
        Takes a string as input and return the card data as a list.
        If card cannot be found return an empty list
        '''

        card = self.find_card_by_name(name)
        return card

    def show_tokens(self,  deck: list, write_to_file=False):
        '''
        Creates a list of all the tokens required for a specified deck
        If none an empty list is returned
        '''

        creature_token = r'\d+/\d+(\s+([a-zA-Z]+\s+)+)token+.*'
        other_tokens = r'(?!c|r|e|a|t|u|r|e)[a-zA-Z]+ token+'
        emblem_tokens = r'emblem [a-z]+.*'
        tokens = []
        status_count = 0

        for card in deck:
            # Status count for user feedback
            status_count += 1
            print(f"Checking card {status_count}/{len(deck)}")
            card_info = self.get_card_information(card)
            card_text = card_info["text"]

            # Check for creature tokens
            matched_creature_token = re.search(creature_token, card_text)
            if matched_creature_token != None:
                # tokens.append(
                #     f"{card_info['name']} - {matched_creature_token.group(0)}")
                tokens.append(
                    [card_info["name"], matched_creature_token.group(0)])

            # Check for non-creature tokens
            matched_other_token = re.search(other_tokens, card_text)
            if matched_other_token != None:
                # tokens.append(
                #     f"{card_info['name']} - {matched_other_token.group(0)}")
                tokens.append(
                    [card_info["name"], matched_other_token.group(0)])

            # Check for emblems
            matched_emblem_token = re.search(emblem_tokens, card_text)
            if matched_emblem_token != None:
                # tokens.append(
                #     f"{card_info['name']} - {matched_emblem_token.group(0)}")
                tokens.append(
                    [card_info["name"], matched_emblem_token.group(0)])

        patterns = [
            ('Card', lambda text: style(text, fg='green')),
            ('Token', lambda text: style(text, fg='red'))
        ]

        # If we have no tokens just add none to all
        if len(tokens) == 0:
            tokens = [["None", "None"]]
        table = columnar(
            tokens, headers=["Card", "Token"], patterns=patterns, justify="c")
        print(table)

        if write_to_file:
            with open(f"./tokens.txt", "w") as f:
                f.write(table)

    def count_mana_symbols_per_card(self, card: dict):
        '''
        Takes a card as input and counts the mana symbols in the mana cost.
        Return the numbers as a dict
        Limitation: Mana Symbols in abilities are not counted
        '''
        mana_symbols = {
            "W": 0,
            "U": 0,
            "B": 0,
            "R": 0,
            "G": 0
        }

        # If the card is a land or has 0 cmc do nothing
        if "land" not in card["type"].lower() and card["cmc"] > 0:
            # manaCost: "{4}{W}{U}{B}{R}{G}"
            # Remove the brackets and phyrexian symbols (/P) and replace them by spaces to create a list
            mana = card["manaCost"].replace(
                "}", " ").replace("{", " ").replace("/P", " ").split()
            for symbol in mana:
                if symbol.isalpha():
                    mana_symbols[symbol] += 1
            return mana_symbols

    def calculate_basic_lands(self, deck: list):
        """
        Count the number of mana symbols in the deck and work out the percentage.
        This percentage is then used to recommend the number of basic lands required of each color.
        Note: None basic lands are not considered. 
        It only recommends how many basic lands are required based on how many spaces are left
        """
        mana_symbols = {
            "W": 0,
            "U": 0,
            "B": 0,
            "R": 0,
            "G": 0
        }

        for card in deck:
            card_info = self.find_card_by_name(card)
            mana_count = (self.count_mana_symbols_per_card(card_info))
            if mana_count:
                for k, v in mana_count.items():
                    mana_symbols[k] += v

        # Total number of each mana symbol
        w = mana_symbols["W"]
        u = mana_symbols["U"]
        b = mana_symbols["B"]
        r = mana_symbols["R"]
        g = mana_symbols["G"]
        total_cmc = w + u + b + r + g

        # Percentage of each mana symbol
        per_w = round(w / total_cmc * 100)
        per_u = round(u / total_cmc * 100)
        per_b = round(b / total_cmc * 100)
        per_r = round(r / total_cmc * 100)
        per_g = round(g / total_cmc * 100)

        # How many lands are required
        lands_req = 100 - len(deck)

        def calculate_lands(req, land_per):
            return (land_per / 100) * req

        lands_req = {
            "W": round(calculate_lands(lands_req, per_w)),
            "U": round(calculate_lands(lands_req, per_u)),
            "B": round(calculate_lands(lands_req, per_b)),
            "R": round(calculate_lands(lands_req, per_r)),
            "G": round(calculate_lands(lands_req, per_g))
        }
        output = "Lands Required:\n"

        # Create string to be printed
        if lands_req["W"] > 0:
            output += f"Plains: {lands_req['W']}\n"
        if lands_req["U"] > 0:
            output += f"Islands: {lands_req['U']}\n"
        if lands_req["B"] > 0:
            output += f"Swamps: {lands_req['B']}\n"
        if lands_req["R"] > 0:
            output += f"Mountains: {lands_req['R']}\n"
        if lands_req["G"] > 0:
            output += f"Forests: {lands_req['G']}\n"

        print(output)

    def analyze_deck(self,  deck_list: list):
        '''
        Does a Basic analysis of the deck.
        Does a mix of some of the functions above but only one api call is required to do all
        '''

        tokens = []
        status_count = 0
        mana_symbols = {
            "W": 0,
            "U": 0,
            "B": 0,
            "R": 0,
            "G": 0
        }

        creature_token = r'\d+/\d+(\s+([a-zA-Z]+\s+)+)token+.*'
        other_tokens = r'(?!c|r|e|a|t|u|r|e)[a-zA-Z]+ token+'
        emblem_tokens = r'emblem [a-z]+.*'

        for card in deck_list:
            # Status count for user feedback
            status_count += 1
            print(f"Checking card {status_count}/{len(deck_list)}")
            card_info = self.get_card_information(card)
            card_text = card_info["text"]
            mana_count = (self.count_mana_symbols_per_card(card_info))
            if mana_count:
                for k, v in mana_count.items():
                    mana_symbols[k] += v

            # Check for creature tokens
            matched_creature_token = re.search(creature_token, card_text)
            if matched_creature_token != None:
                # tokens.append(
                #     f"{card_info['name']} - {matched_creature_token.group(0)}")
                tokens.append(
                    [card_info["name"], matched_creature_token.group(0)])

            # Check for non-creature tokens
            matched_other_token = re.search(other_tokens, card_text)
            if matched_other_token != None:
                # tokens.append(
                #     f"{card_info['name']} - {matched_other_token.group(0)}")
                tokens.append(
                    [card_info["name"], matched_other_token.group(0)])

            # Check for emblems
            matched_emblem_token = re.search(emblem_tokens, card_text)
            if matched_emblem_token != None:
                # tokens.append(
                #     f"{card_info['name']} - {matched_emblem_token.group(0)}")
                tokens.append(
                    [card_info["name"], matched_emblem_token.group(0)])

        ## TOKENS ##
        patterns = [
            ('Card', lambda text: style(text, fg='green')),
            ('Token', lambda text: style(text, fg='red'))
        ]

        # If we have no tokens just add none to all
        if len(tokens) == 0:
            tokens = [["None", "None"]]
        table = columnar(
            tokens, headers=["Card", "Token"], patterns=patterns, justify="c")
        print(table)

        ### MANA ##
        # Total number of each mana symbol
        w = mana_symbols["W"]
        u = mana_symbols["U"]
        b = mana_symbols["B"]
        r = mana_symbols["R"]
        g = mana_symbols["G"]
        total_cmc = w + u + b + r + g

        # Percentage of each mana symbol
        per_w = round(w / total_cmc * 100)
        per_u = round(u / total_cmc * 100)
        per_b = round(b / total_cmc * 100)
        per_r = round(r / total_cmc * 100)
        per_g = round(g / total_cmc * 100)

        # How many lands are required
        lands_req = 100 - len(deck_list)

        def calculate_lands(req, land_per):
            return (land_per / 100) * req

        lands_req = {
            "W": round(calculate_lands(lands_req, per_w)),
            "U": round(calculate_lands(lands_req, per_u)),
            "B": round(calculate_lands(lands_req, per_b)),
            "R": round(calculate_lands(lands_req, per_r)),
            "G": round(calculate_lands(lands_req, per_g))
        }
        output = "Lands Required:\n"

        # Create string to be printed
        if lands_req["W"] > 0:
            output += f"Plains: {lands_req['W']}\n"
        if lands_req["U"] > 0:
            output += f"Islands: {lands_req['U']}\n"
        if lands_req["B"] > 0:
            output += f"Swamps: {lands_req['B']}\n"
        if lands_req["R"] > 0:
            output += f"Mountains: {lands_req['R']}\n"
        if lands_req["G"] > 0:
            output += f"Forests: {lands_req['G']}\n"

        print(output)
