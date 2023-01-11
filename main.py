from mtg_deck import MtgDeck


if __name__ == "__main__":

    deck = MtgDeck()

    # # Load the deck info from txt files
    # old = deck.load_deck_from_file("files/old.txt")
    # new = deck.load_deck_from_file("files/new.txt")
    # deck.compare_decks(old, new, write_to_file=False)

    # muldrotha = deck.load_deck_from_file("files/test.txt")
    # deck.show_tokens(muldrotha, write_to_file=True)

    deck_list = deck.load_deck_from_file("files/test.txt")
    # deck.calculate_basic_lands(deck_list)
    # deck.analyze_deck(deck_list)

    card = deck.get_card_information("Duergar Hedge-Mage")
    print(deck.count_mana_symbols_per_card(card))
    
