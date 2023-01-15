# MTG Deck
Do some basic analysis on your Magic decks (mainly aimed at commander)

## Can be imported as

    from mtg_deck import MtgDeck


## Supports comparing two decks
Supply a file path for an old deck and a new deck, then see what the changes are.

Supported Formats

    1 Card One
    12 Card Two
or

    Card Name

### Example

    deck = MtgDeck()

    # Load the deck info from txt files
    old = deck.load_deck_from_file("files/old.txt")
    new = deck.load_deck_from_file("files/new.txt")

    deck.compare_decks(old, new, write_to_file=False)

## Find tokens the deck requires
Iterates through the deck and find the tokens the deck require

    deck = MtgDeck()

    # Load the deck info from txt files
    myDeck = deck.load_deck_from_file("files/deck.txt")
    deck.show_tokens(myDeck)

## To Get A Recommendation of basic lands to get

    deck = MtgDeck()

    deck_list = deck.load_deck_from_file("files/test.txt")
    full_deck = deck.separate_cards(deck_list)
    deck.calculate_basic_lands(full_deck)

## You can also get a basic analysis which will combine the tokens and basic lands

    deck = MtgDeck()

    deck_list = deck.load_deck_from_file("files/test.txt")
    full_deck = deck.separate_cards(deck_list)
    deck.calculate_basic_lands(full_deck)

