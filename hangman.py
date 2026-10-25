"""Hangman - a terminal word-guessing game.

Run with:  python hangman.py
"""

import os
import random

MAX_MISTAKES = 6

WORD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "google-10000-english-no-swears.txt")
MIN_WORD_LENGTH = 5

# Used only if the word list file is missing.
FALLBACK_WORDS = ["python", "variable", "function", "keyboard", "program",
                  "algorithm", "database", "compiler", "terminal", "console"]


def load_words():
    """Load words from the word list file (one word per line)."""
    try:
        with open(WORD_FILE, encoding="utf-8") as f:
            words = [w.strip().lower() for w in f]
    except OSError:
        print("(Word list not found - using the built-in list.)")
        return FALLBACK_WORDS
    words = [w for w in words if w.isalpha() and len(w) >= MIN_WORD_LENGTH]
    return words or FALLBACK_WORDS


WORDS = load_words()

# One ASCII gallows picture per mistake count (0 to 6).
STAGES = [
    """
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========""",
]


def mask_word(word, guessed):
    """Return the word with unguessed letters hidden, e.g. '_ A _ H E O N'."""
    return " ".join(ch.upper() if ch in guessed else "_" for ch in word)


def get_guess(guessed):
    """Ask until the player enters a single new letter."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter (a-z).")
        elif guess in guessed:
            print(f"You already guessed '{guess}'. Try a different letter.")
        else:
            return guess


def show_victory(word):
    print("\n*****************************")
    print("*        YOU WIN!           *")
    print("*****************************")
    print(f"The word was: {word.upper()}\n")


def show_defeat(word):
    print("\n*****************************")
    print("*        GAME OVER          *")
    print("*****************************")
    print(f"The word was: {word.upper()}\n")


def play_round():
    word = random.choice(WORDS)
    guessed = set()   # every letter tried (right or wrong)
    mistakes = 0

    while mistakes < MAX_MISTAKES:
        print(STAGES[mistakes])
        print("\nWord:   ", mask_word(word, guessed))
        wrong = sorted(ch for ch in guessed if ch not in word)
        print("Wrong:  ", ", ".join(wrong) if wrong else "-")
        print(f"Lives:   {MAX_MISTAKES - mistakes}\n")

        guess = get_guess(guessed)
        guessed.add(guess)

        if guess in word:
            print(f"Good guess! '{guess}' is in the word.")
            if all(ch in guessed for ch in word):
                print(STAGES[mistakes])
                print("\nWord:   ", mask_word(word, guessed))
                show_victory(word)
                return
        else:
            mistakes += 1
            print(f"Sorry, '{guess}' is not in the word.")

    print(STAGES[MAX_MISTAKES])
    show_defeat(word)


def main():
    print("=== HANGMAN ===")
    while True:
        play_round()
        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
