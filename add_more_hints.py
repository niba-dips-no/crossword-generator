#!/usr/bin/env python3

import json
import os
import random

# Define some generic hint templates
generic_hints = [
    "A common Finnish word",
    "Used in everyday Finnish language",
    "A Finnish term for {}",
    "A word related to {}",
    "A Finnish expression",
    "A term used in Finnish culture",
    "A word from Finnish vocabulary",
    "A Finnish concept",
    "A word commonly used in Finland",
    "A traditional Finnish term"
]

# Categories to associate with words
categories = [
    "nature", "culture", "food", "technology", "family", 
    "travel", "work", "education", "sports", "weather",
    "home", "animals", "plants", "emotions", "time",
    "communication", "transportation", "clothing", "health", "art"
]

# Load the existing word hints from the JSON file
with open('word_hints.json', 'r', encoding='utf-8') as f:
    existing_hints = json.load(f)

print(f"Loaded {len(existing_hints)} existing hints from word_hints.json")

# Read the current word file with hints
with open('finnish_words_with_hints.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Count words with and without hints
words_with_hints = [line.strip() for line in lines if ':' in line]
words_without_hints = [line.strip() for line in lines if ':' not in line]

print(f"Found {len(words_with_hints)} words with hints and {len(words_without_hints)} without hints")

# Select a subset of words to add hints to (limit to 100 for now)
num_words_to_add_hints = min(100, len(words_without_hints))
words_to_add_hints = random.sample(words_without_hints, num_words_to_add_hints)

# Create a new file with additional hints
with open('finnish_words_with_more_hints.txt', 'w', encoding='utf-8') as f:
    # First write all words that already have hints
    for line in lines:
        if ':' in line:
            f.write(line)
        else:
            word = line.strip()
            if word in words_to_add_hints:
                # Generate a random hint for this word
                category = random.choice(categories)
                hint_template = random.choice(generic_hints)
                hint = hint_template.format(category) if '{}' in hint_template else hint_template
                f.write(f"{word}: {hint}\n")
            else:
                # Keep the word without a hint
                f.write(line)

print(f"Created finnish_words_with_more_hints.txt with {len(words_with_hints) + num_words_to_add_hints} hints")
