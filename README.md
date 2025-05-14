# Crossword Generator

A Python-based crossword puzzle generator that supports Finnish and Norwegian languages. This tool creates crossword puzzles with empty clues, allowing users to fill them in later with words or images.

## Features

- Generates crossword puzzles in Finnish and/or Norwegian
- Supports custom word lists
- Configurable grid sizes
- Proper handling of special characters (å, ø, æ, ä, ö)
- Outputs puzzle grid, empty clue placeholders, and answer key
- Optional theme-based puzzle generation

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the generator:
```bash
python crossword_generator.py [options]
```

Options:
- `--size`: Grid size (default: 15)
- `--language`: Language choice ("fi", "no", or "both")
- `--words-file`: Path to custom word list file
- `--theme`: Optional theme for word selection
- `--difficulty`: Puzzle difficulty (easy, medium, hard)
