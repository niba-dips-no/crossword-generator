#!/usr/bin/env python3

import json
import os

# Load the word hints from the JSON file
with open('word_hints.json', 'r', encoding='utf-8') as f:
    word_hints = json.load(f)

print(f"Loaded {len(word_hints)} hints from word_hints.json")

# Read the current word file
with open('finnish_words.txt', 'r', encoding='utf-8') as f:
    words = [line.strip() for line in f if line.strip() and not line.startswith('#')]

print(f"Loaded {len(words)} words from finnish_words.txt")

# Create a new file with words and hints
with open('finnish_words_with_hints.txt', 'w', encoding='utf-8') as f:
    hint_count = 0
    for word in words:
        word_lower = word.lower()
        if word_lower in word_hints:
            # Add the hint to the word
            f.write(f"{word}: {word_hints[word_lower]}\n")
            hint_count += 1
        else:
            # Keep the word without a hint
            f.write(f"{word}\n")

print(f"Created finnish_words_with_hints.txt with hints for {hint_count} out of {len(words)} words")
