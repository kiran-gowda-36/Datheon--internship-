# Datheon Python Programming Internship

Python projects built for the Datheon Python Programming Internship (Batch 01).
All programs are written in Python 3 and run in the terminal.

## Projects

### Task 1: Hangman Word Guessing Game (`hangman.py`)
A terminal Hangman game.
- Picks a random word from `google-10000-english-no-swears.txt` (words of 5+ letters)
- Shows the word as a masked string, e.g. `_ A _ H E O N`
- Draws ASCII gallows art that updates after each wrong guess
- Allows 6 mistakes, tracks guessed letters, and never penalizes a repeated guess
- Shows victory and defeat screens, with a play-again option

**Run:** `python hangman.py`

### Task 2: Stock Portfolio Performance Tracker (`portfolio.py`)
A portfolio tracking utility.
- Enter ticker symbols, buy prices and share quantities (validated against the S&P 500 dataset `constituents.txt`)
- Stores positions in a dictionary and merges repeated buys of the same ticker
- Calculates total invested capital, current market value, and gain/loss % per holding and overall
- Prints a formatted report and logs each run to `portfolio_summary.csv` using the `csv` module
- Uses live prices through `yfinance` if installed; otherwise asks you to type the current price

**Run:** `python portfolio.py`
(Optional for live prices: `pip install yfinance`)

### Task 4: Rule-Based Interactive Terminal Chatbot (`chatbot.py`)
A customer-support style assistant for the Datheon internship.
- Understands keywords and regular expressions (business hours, project submission, certificates, thanks, help)
- Loads greetings and FAQ answers from `sample_faq.json`
- Handles several questions in one message (multi-intent matching)
- Tracks conversation state (greeting, intent, resolution, exit) and remembers the user's name
- Gives a polite fallback for unrecognised input and exits cleanly on `bye`, `exit` or `quit`

**Run:** `python chatbot.py`

## Files

| File | Purpose |
|------|---------|
| `hangman.py` | Task 1 game |
| `google-10000-english-no-swears.txt` | Word list used by Hangman |
| `portfolio.py` | Task 2 tracker |
| `constituents.txt` | S&P 500 dataset (tickers, companies, sectors) |
| `portfolio_summary.csv` | Generated log of portfolio runs |
| `chatbot.py` | Task 4 chatbot |
| `sample_faq.json` | Greetings and FAQ data used by the chatbot |

## Requirements
- Python 3 (only the standard library is needed)
