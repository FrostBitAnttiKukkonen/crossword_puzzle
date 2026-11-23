"""
Idea: crossword puzzle

We start without window
    - easy to test
    - we see errors early

We need: words

"""

import random

# Word data
# WORD_BANK is master list of words
# we pick 20 words from this list
WORD_BANK = [
    "apple", "tiger", "house", "water", "green",
    "happy", "chair", "bread", "clock", "smile",
    "river", "cloud", "stone", "ghost", "plant",
    "queen", "zebra", "money", "night", "light",
    "dance", "snake", "train", "beach", "horse",
    "bridge", "yellow", "winter", "garden", "window",
    "castle", "silver", "orange", "pencil", "monkey",
    "rocket", "candle", "dragon", "island", "forest",
    "piano", "ocean", "mountain", "elephant", "triangle",
]

VOWELS = "aeiou"

MIN_WORDS = 10
MAX_WORDS = 20

MIN_LEN = 3
MAX_LEN = 10

def count_vowels(word):
    """ Return how many vowels the word has.
    (a, e, i, o, u)
    """

    vowel_count = 0

    for letter in word.lower():
        if letter in VOWELS:
            vowel_count += 1

    return vowel_count

def filter_valid_words(words):
    """ Keep only words that are safe to
    draw in a puzzle.
    """

    checked_words = []

    return [w for w in words
            if w.isalpha() and w.islower() and 3 <= len(w) <= 10]

    for word in words:
        correct_length = len(word) >= MIN_LEN and len(word) <= MAX_LEN

        if word.islower() and word.isalpha() and correct_length:
            checked_words += word

    return checked_words

def pick_words(count, valid_list):
    """ Pick differet word each time when creating
    the puzzle.
    """
    
    random_pick = random.sample(valid_list, count)

    return random_pick

# Console output
def ask_amount():
    """ Ask the user how many words to generate. """
    answer = input(f"How many words? ({MIN_WORDS}-{MAX_WORDS})")

    try:
        # try to convert to int
        how_many = int(answer)
    except:
        print("Not a number")
        how_many = 15

    # select_words = pick_words(how_many)

def show_words_on_console(words):
    """ Print chosen words """

    valid_words = filter_valid_words(words)

    random_list = pick_words(15, valid_words)

    for number, word in enumerate(random_list, start=1):
        # vowels = count_vowels(word)
        vowel_count = count_vowels(word)
        print(f"{number}: {word}, vowel count {vowel_count}")


if __name__ == "__main__":
    show_words_on_console(WORD_BANK)

