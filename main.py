from mtg_deck import MtgDeck


if __name__ == "__main__":

    deck = MtgDeck()

    # Compare two decks to see what to bring in and what to remove
    old = deck.load_deck_from_file("files/old.txt")
    new = deck.load_deck_from_file("files/new.txt")

    deck.compare_decks(old, new, write_to_file=False)
    
    # See what tokens the deck requires
    myDeck = deck.load_deck_from_file("files/deck.txt")
    deck.show_tokens(myDeck)

    # After building your deck and adding all the non basic lands
    # Get a recommendation on which and how many basic lands to add
    deck_list = deck.load_deck_from_file("files/test.txt")
    deck.calculate_basic_lands(deck_list)

    # Hybrid way to get both tokens and basic lands
    # This wil only be 1 round opf api calls instead of 2
    deck_list = deck.load_deck_from_file("files/test.txt")
    deck.analyze_deck(deck_list)
