#!/usr/bin/env python3
import argparse
import random
import json
import os
from typing import List, Tuple, Dict, Optional, Set

class CrosswordGenerator:
    def __init__(
        self,
        size=None,  # Can be an integer for square grids or None if width/height are provided
        width: int = None,
        height: int = None,
        language: str = "fi",
        words_file: Optional[str] = None,
        theme: Optional[str] = None,
        difficulty: str = "medium"
    ):
        # Handle different ways of specifying grid dimensions
        if size is not None:
            self.width = self.height = size  # Square grid
        elif width is not None and height is not None:
            self.width = width
            self.height = height
        else:
            self.width = self.height = 15  # Default to 15x15 grid
            
        # For backward compatibility with existing code that uses self.size
        self._size = max(self.width, self.height)
        
        # Initialize all instance variables
        self.language = language
        self.words_file = words_file
        self.theme = theme
        self.difficulty = difficulty
        self.words: Set[str] = set()
        # Create a grid with the specified dimensions
        self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.placed_words = []  # List of (word, row, col, horizontal, hint)
        # Initialize word hints dictionary (will be populated by app.py)
        self.word_hints = {}  
        self.word_numbers = {}
        self.current_number = 1        
    @property
    def size(self):
        # This property ensures backward compatibility with code that still uses self.size
        return self._size
        
    @size.setter
    def size(self, value):
        self._size = value
        # When size is set, we update both width and height (use for square grids)
        self.width = self.height = value

    def _load_word_hints(self) -> None:
        """Load word hints from a JSON file."""
        hints_file = os.path.join(os.path.dirname(__file__), 'word_hints.json')
        if os.path.exists(hints_file):
            try:
                with open(hints_file, 'r', encoding='utf-8') as f:
                    self.word_hints = json.load(f)
                print(f"Loaded {len(self.word_hints)} word hints from {hints_file}")
                # Print a few examples for debugging
                examples = list(self.word_hints.items())[:5]
                print(f"Example hints: {examples}")
            except Exception as e:
                print(f"Error loading word hints: {e}")
                self.word_hints = {}
        else:
            print(f"Word hints file not found: {hints_file}")
            self.word_hints = {}

    def load_words(self) -> None:
        """Load words from file or use default word list."""
        if self.words_file:
            with open(self.words_file, 'r', encoding='utf-8') as f:
                self.words = {line.strip().upper() for line in f if line.strip()}
        else:
            # Default sample words
            self.words = {
                'JÄRVI', 'SAARI', 'KALA', 'TALO', 'KIRJA',
                'FJORD', 'SKOG', 'BÅT', 'HUS', 'BOK'
            }

    def is_valid_word(self, word: str) -> bool:
        """Check if word is valid for the chosen language(s)."""
        if len(word) < 3 or len(word) > self.size:
            return False
            
        # Basic character validation for Finnish/Norwegian
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZÅØÆÄÖ')
        return all(c in valid_chars for c in word)

    def filter_words(self) -> List[str]:
        """Filter words based on language and validity."""
        valid_words = []
        print(f"Total words: {len(self.words)}")
        for word in self.words:
            # Skip empty words or non-string items
            if not isinstance(word, str) or not word.strip():
                continue

            # Convert word to uppercase and remove any trailing numbers
            word = word.split(':')[-1].strip().upper()
            
            # Only use words between 3 and 15 letters
            if 3 <= len(word) <= 15:
                # For Finnish, ensure word only contains valid Finnish characters
                if self.language == 'fi':
                    # Allow Ä, Ö, and basic Latin letters
                    valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖ')
                    if all(c in valid_chars for c in word):
                        # Additional quality checks for Finnish words
                        # Avoid words with too many consecutive consonants (likely gibberish)
                        consonants = 'BCDFGHJKLMNPQRSTVWXZ'
                        vowels = 'AEIOUYÄÖ'
                        
                        # Check for reasonable vowel-consonant patterns
                        max_consecutive_consonants = 0
                        current_consecutive = 0
                        
                        for char in word:
                            if char in consonants:
                                current_consecutive += 1
                                max_consecutive_consonants = max(max_consecutive_consonants, current_consecutive)
                            else:
                                current_consecutive = 0
                                
                        # Finnish rarely has more than 3 consecutive consonants
                        # Also ensure the word has at least one vowel
                        has_vowel = any(c in vowels for c in word)
                        
                        if max_consecutive_consonants <= 3 and has_vowel:
                            valid_words.append(word)
                elif self.language == 'no':
                    # Allow Å, Ø, Æ, and basic Latin letters
                    valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZÅØÆ')
                    if all(c in valid_chars for c in word):
                        # Additional quality checks for Norwegian words
                        # Avoid words with too many consecutive consonants (likely gibberish)
                        consonants = 'BCDFGHJKLMNPQRSTVWXZ'
                        vowels = 'AEIOUYÅØÆ'
                        
                        # Check for reasonable vowel-consonant patterns
                        max_consecutive_consonants = 0
                        current_consecutive = 0
                        
                        for char in word:
                            if char in consonants:
                                current_consecutive += 1
                                max_consecutive_consonants = max(max_consecutive_consonants, current_consecutive)
                            else:
                                current_consecutive = 0
                                
                        # Norwegian rarely has more than 3 consecutive consonants
                        # Also ensure the word has at least one vowel
                        has_vowel = any(c in vowels for c in word)
                        
                        if max_consecutive_consonants <= 3 and has_vowel:
                            valid_words.append(word)
                else:  # 'both' or any other language
                    valid_words.append(word)
        
        print(f"Valid words after filtering: {len(valid_words)}")
        if not valid_words:
            print("No valid words found after filtering!")
        
        # Sort words by length, with a mix of long and short words
        def word_priority(word):
            length = len(word)
            # Create three tiers of words:
            # Tier 1: Medium words (5-9 letters) - for main structure
            # Tier 2: Short words (3-4 letters) - for filling gaps
            # Tier 3: Long words (10+ letters) - for special placements
            if 5 <= length <= 9:
                return (0, -length)  # Medium words first, longer ones first within tier
            elif 3 <= length <= 4:
                return (1, -length)  # Short words second
            else:
                return (2, -length)  # Long words last
        
        valid_words.sort(key=word_priority)
        # Increase word limit for denser puzzles
        valid_words = valid_words[:500]  # Increased from 300 to 500 for even more word options
        # Shuffle medium and long words, but keep short words separate for gap filling
        medium_long_words = [w for w in valid_words if len(w) >= 5]
        short_words = [w for w in valid_words if len(w) < 5]
        very_short_words = [w for w in valid_words if len(w) == 3]  # Special category for 3-letter words
        random.shuffle(medium_long_words)
        random.shuffle(short_words)
        random.shuffle(very_short_words)
        # Increase proportion of short words to help fill gaps
        valid_words = medium_long_words + short_words * 2 + very_short_words * 3  # Triple very short words for maximum filling
        return valid_words

    def can_place_word(self, word: str, row: int, col: int, horizontal: bool) -> bool:
        """Check if a word can be placed at the given position with proper crossword rules."""
        # First, validate the input coordinates are within the grid
        if row < 0 or row >= self.height or col < 0 or col >= self.width:
            return False
            
        # Check if word fits within the grid
        if horizontal and col + len(word) > self.width:
            return False
        if not horizontal and row + len(word) > self.height:
            return False

        # Check if placement creates invalid words
        intersects = False
        has_adjacent = False
        
        # Check the space before the word (if not at the edge)
        if horizontal and col > 0:
            if self.grid[row][col-1] != ' ':
                return False  # Can't have a letter immediately before the word
        if not horizontal and row > 0:
            if self.grid[row-1][col] != ' ':
                return False  # Can't have a letter immediately above the word
        
        # Check the space after the word (if not at the edge)
        if horizontal and col + len(word) < self.width:
            if self.grid[row][col + len(word)] != ' ':
                return False  # Can't have a letter immediately after the word
        if not horizontal and row + len(word) < self.height:
            if self.grid[row + len(word)][col] != ' ':
                return False  # Can't have a letter immediately below the word
        
        # Check each position of the word
        for i in range(len(word)):
            current_row = row if horizontal else row + i
            current_col = col + i if horizontal else col
            
            # Ensure we're within grid bounds
            if current_row >= self.height or current_col >= self.width:
                return False

            # Check the cell itself - must be empty or match the letter
            if self.grid[current_row][current_col] not in [' ', word[i]]:
                return False
            
            # If this cell has a letter, it's an intersection
            if self.grid[current_row][current_col] == word[i]:
                intersects = True
            
            # Check for adjacent letters (which should only be at intersections)
            if horizontal:
                # Check above and below (with careful boundary checking)
                if current_row > 0 and current_row-1 < self.height and current_col < self.width and self.grid[current_row-1][current_col] != ' ':
                    # If we're not at an intersection, this is invalid
                    if self.grid[current_row][current_col] != word[i]:
                        return False
                    has_adjacent = True
                    
                if current_row+1 < self.height and current_col < self.width and self.grid[current_row+1][current_col] != ' ':
                    # If we're not at an intersection, this is invalid
                    if self.grid[current_row][current_col] != word[i]:
                        return False
                    has_adjacent = True
            else:
                # Check left and right
                if current_col > 0 and current_row < self.height and current_col-1 < self.width and self.grid[current_row][current_col-1] != ' ':
                    # If we're not at an intersection, this is invalid
                    if self.grid[current_row][current_col] != word[i]:
                        return False
                    has_adjacent = True
                    
                if current_col+1 < self.width and current_row < self.height and self.grid[current_row][current_col+1] != ' ':
                    # If we're not at an intersection, this is invalid
                    if self.grid[current_row][current_col] != word[i]:
                        return False
                    has_adjacent = True

        # Word must intersect with existing words (except first word)
        if self.placed_words:
            if not intersects and not has_adjacent:
                return False

        return True

    def place_word(self, word: str, row: int, col: int, horizontal: bool) -> None:
        """Place a word on the grid."""
        # We'll assign numbers in reading order later
        # Just record if this position is a start of a word
        if horizontal:
            if col == 0 or self.grid[row][col-1] == ' ':
                # Mark as a starting position for a horizontal word
                if (row, col) not in self.word_numbers:
                    self.word_numbers[(row, col)] = {'across': True}
                else:
                    self.word_numbers[(row, col)]['across'] = True
        else:
            if row == 0 or self.grid[row-1][col] == ' ':
                # Mark as a starting position for a vertical word
                if (row, col) not in self.word_numbers:
                    self.word_numbers[(row, col)] = {'down': True}
                else:
                    self.word_numbers[(row, col)]['down'] = True
            
        # Place the word on the grid
        for i in range(len(word)):
            # Make sure we're within grid boundaries
            if horizontal and 0 <= row < self.size and 0 <= col+i < self.size:
                self.grid[row][col+i] = word[i]
            elif not horizontal and 0 <= row+i < self.size and 0 <= col < self.size:
                self.grid[row+i][col] = word[i]
            else:
                # If we're out of bounds, don't place this part of the word
                # This should be prevented by can_place_word, but adding as a safeguard
                continue
                
        # Get hint for the word or use a default hint
        word_lower = word.lower()
        
        # Check if the word is in our hint dictionary
        if word_lower in self.word_hints:
            hint = self.word_hints[word_lower]
            print(f"Found hint for '{word_lower}': {hint}")
        else:
            # Try to find a partial match (e.g., if the word is a compound or inflected form)
            found_partial = False
            for hint_word, hint_text in self.word_hints.items():
                # If the word contains a known word from our hints dictionary
                if hint_word in word_lower and len(hint_word) >= 3:
                    hint = f"{hint_text} (related to '{hint_word}')".capitalize()
                    found_partial = True
                    print(f"Found partial hint for '{word_lower}' via '{hint_word}': {hint}")
                    break
            
            # If no match found, use a generic hint
            if not found_partial:
                hint = f"Definition for {word}"
                print(f"No hint found for '{word_lower}', using default")
                
        # Add to placed words list with hint
        self.placed_words.append((word, row, col, horizontal, hint))

    def _has_adjacent_words(self, row, col, horizontal, length):
        """Check if a word placement has adjacent or intersecting words."""
        # Check for intersections
        for i in range(length):
            r, c = (row, col + i) if horizontal else (row + i, col)
            if 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] != ' ':
                return True
                
        # Check for adjacent words
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        for i in range(length):
            r, c = (row, col + i) if horizontal else (row + i, col)
            if 0 <= r < self.height and 0 <= c < self.width:
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width and self.grid[nr][nc] != ' ':
                        return True
                        
        return False
        
    def assign_numbers_in_reading_order(self):
        """Assign numbers to the grid in reading order (top-to-bottom, left-to-right)."""
        # Create a new dictionary to store the final numbered positions
        numbered_positions = {}
        current_number = 1
        
        # Scan the grid from top to bottom, left to right
        for row in range(self.height):
            for col in range(self.width):
                # Skip empty cells
                if self.grid[row][col] == ' ':
                    continue
                    
                # Check if this position is a start of a word (already marked in self.word_numbers)
                if (row, col) in self.word_numbers:
                    # This is a starting position for at least one word
                    numbered_positions[(row, col)] = current_number
                    current_number += 1
        
        # Replace the old word_numbers with the new numbered_positions
        self.word_numbers = numbered_positions
        
    def _fills_isolated_area(self, row, col, horizontal, length):
        """Check if a word placement would fill an isolated area in the grid."""
        # Count empty cells around the proposed word placement
        empty_neighbors = 0
        filled_neighbors = 0
        
        # Check all cells that would be affected by this word
        for i in range(length):
            r = row if horizontal else row + i
            c = col + i if horizontal else col
            
            # Ensure we're within grid bounds
            if r >= self.height or c >= self.width:
                # Out of bounds - can't place word here
                return False
            
            # Skip if this cell already has a letter (intersection)
            if self.grid[r][c] != ' ':
                continue
                
            # Check all 8 neighbors of this cell
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    # Skip the cell itself
                    if dr == 0 and dc == 0:
                        continue
                        
                    # Check if neighbor is within grid bounds
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        if self.grid[nr][nc] == ' ':
                            empty_neighbors += 1
                        else:
                            filled_neighbors += 1
        
        # Word fills an isolated area if it has many filled neighbors and few empty ones
        # This indicates it's filling a gap surrounded by existing words
        return filled_neighbors >= length * 2 and empty_neighbors <= length * 3

    def fill_small_gaps(self):
        """Fill small gaps in the grid with short words."""
        # This is a simplified implementation of gap filling
        # It looks for small 2-3 letter gaps and tries to fill them
        short_words = [w for w in self.words if len(w) <= 3]
        
        # Try each position in the grid
        for row in range(self.height):
            for col in range(self.width):
                # Try horizontal gaps
                if col < self.width - 1 and self.grid[row][col] == ' ' and self.grid[row][col+1] == ' ':
                    # Found a potential horizontal gap, check length
                    gap_length = 0
                    for i in range(col, self.size):
                        if self.grid[row][i] == ' ':
                            gap_length += 1
                        else:
                            break
                            
                    if 2 <= gap_length <= 3:  # Small gap that can be filled
                        # Try to find a word that fits
                        for word in short_words:
                            if len(word) == gap_length and self.can_place_word(word, row, col, True):
                                self.place_word(word, row, col, True)
                                break
                
                # Try vertical gaps
                if row < self.height - 1 and self.grid[row][col] == ' ' and self.grid[row+1][col] == ' ':
                    # Found a potential vertical gap, check length
                    gap_length = 0
                    for i in range(row, self.height):
                        if self.grid[i][col] == ' ':
                            gap_length += 1
                        else:
                            break
                            
                    if 2 <= gap_length <= 3:  # Small gap that can be filled
                        # Try to find a word that fits
                        for word in short_words:
                            if len(word) == gap_length and self.can_place_word(word, row, col, False):
                                self.place_word(word, row, col, False)
                                break
    
    def generate_puzzle(self, fill_gaps=True) -> Tuple[List[List[dict]], List[str], List[str], List[List[str]]]:
        """Generate crossword puzzle with proper grid structure and clues."""
        # Reset grid and counters
        self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.placed_words = []
        self.word_numbers = {}

        valid_words = self.filter_words()
        if not valid_words:
            raise ValueError("No valid words found for the specified language")

        # Try to find a suitable first word (5-9 letters)
        first_word = None
        for word in valid_words:
            if 5 <= len(word) <= 9:
                first_word = word
                break
        
        if not first_word:
            first_word = valid_words[0]  # Fallback to first word if no suitable word found

        # Place first word in the middle
        start_row = self.height // 2
        start_col = (self.width - len(first_word)) // 2
        self.place_word(first_word, start_row, start_col, True)

        # First phase: Place medium and long words to create structure
        # Try to place remaining words by finding intersections
        attempts = 0
        max_attempts = 300  # Increased attempts for maximum density
        max_words = min(80, len(valid_words) // 2)  # Significantly increased word limit for maximum density
        
        while attempts < max_attempts and len(self.placed_words) < max_words:
            best_placement = None
            best_score = -1
            best_word = None

            # Try each remaining word
            for word in valid_words:
                if word in [w[0] for w in self.placed_words]:
                    continue
                    
                # For the first phase, prefer medium-length words, but allow more short words
                if len(self.placed_words) < 10 and len(word) < 3:
                    continue  # Only skip very short (3-letter) words in the very beginning

                # Try all possible positions
                for row in range(self.height):
                    for col in range(self.width):
                        for horizontal in [True, False]:
                            if self.can_place_word(word, row, col, horizontal):
                                # Count intersections
                                intersections = 0
                                for i in range(len(word)):
                                    r = row if horizontal else row + i
                                    c = col + i if horizontal else col
                                    if self.grid[r][c] == word[i]:
                                        intersections += 1
                                
                                # Score based on intersections and position
                                score = intersections * 10
                                # Prefer positions in the middle 60% of the grid
                                if self.size * 0.2 <= row <= self.size * 0.8 and self.size * 0.2 <= col <= self.size * 0.8:
                                    score += 5
                                # Extra points for perfect intersections (not just touching)
                                if intersections > 1:
                                    score += 10
                                    
                                # Bonus for filling gaps (more points for shorter words)
                                if len(self.placed_words) >= 10 and len(word) <= 4:
                                    score += 25 - (len(word) * 4)  # Even more aggressive bonus for shorter words
                                    
                                # Extra bonus for 3-letter words after initial structure is built
                                if len(self.placed_words) >= 15 and len(word) == 3:
                                    score += 15  # Increased bonus for 3-letter words to fill small gaps
                                    
                                # Additional bonus for words that fill isolated areas
                                if self._fills_isolated_area(row, col, horizontal, len(word)):
                                    score += 20  # Significant bonus for filling isolated areas
                                
                                if score > best_score:
                                    best_score = score
                                    best_placement = (word, row, col, horizontal)
                                    best_word = word

            # Place the best word found
            if best_placement:
                word, row, col, horizontal = best_placement
                self.place_word(word, row, col, horizontal)
            else:
                break

            attempts += 1
            
        # Second phase: Fill small gaps with short words
        # Specifically look for small gaps that can be filled
        if len(valid_words) > len(self.placed_words):
            # Get short words that haven't been placed yet
            short_words = [w for w in valid_words if len(w) <= 4 and w not in [placed[0] for placed in self.placed_words]]
            
            # Try to place short words in gaps
            gap_filling_attempts = 0
            max_gap_attempts = 250  # Increased from 150 to 250 for maximum gap filling
            
            # No limit on words for gap filling - try to fill as many gaps as possible
            while gap_filling_attempts < max_gap_attempts and short_words:
                placed_gap_word = False
                
                # Find gaps in the grid
                gaps = []
                for row in range(self.height):
                    for col in range(self.width):
                        # Look for horizontal gaps
                        if col < self.width - 2:  # Need at least 3 cells for a word
                            # Check if we have a potential horizontal gap
                            if self.grid[row][col] == ' ':
                                # Look for the length of this gap
                                gap_length = 0
                                for i in range(col, self.width):
                                    if self.grid[row][i] == ' ':
                                        gap_length += 1
                                    else:
                                        break
                                
                                if 3 <= gap_length <= 4:  # Good size for short words
                                    gaps.append((row, col, True, gap_length))
                        
                        # Look for vertical gaps
                        if row < self.height - 2:  # Need at least 3 cells for a word
                            # Check if we have a potential vertical gap
                            if self.grid[row][col] == ' ':
                                # Look for the length of this gap
                                gap_length = 0
                                for i in range(row, self.height):
                                    if self.grid[i][col] == ' ':
                                        gap_length += 1
                                    else:
                                        break
                                
                                if 3 <= gap_length <= 4:  # Good size for short words
                                    gaps.append((row, col, False, gap_length))
                
                # Sort gaps by size (smaller first)
                gaps.sort(key=lambda x: x[3])
                
                # Try to fill each gap with a word of matching length
                for gap_row, gap_col, horizontal, gap_length in gaps:
                    # Find words that match the gap length
                    matching_words = [w for w in short_words if len(w) == gap_length]
                    
                    if not matching_words:
                        continue
                    
                    # Try each matching word
                    for word in matching_words:
                        if self.can_place_word(word, gap_row, gap_col, horizontal):
                            # Check if it intersects with existing words
                            intersects = False
                            for i in range(len(word)):
                                r = gap_row if horizontal else gap_row + i
                                c = gap_col + i if horizontal else gap_col
                                if self.grid[r][c] != ' ' and self.grid[r][c] == word[i]:
                                    intersects = True
                                    break
                            
                            # Place the word if it can intersect or is adjacent to existing words
                            if intersects or self._has_adjacent_words(gap_row, gap_col, horizontal, len(word)):
                                self.place_word(word, gap_row, gap_col, horizontal)
                                short_words.remove(word)
                                placed_gap_word = True
                                break
                    
                    if placed_gap_word:
                        break
                
                # If we couldn't fill any gaps with exact matches, try more flexible placement
                if not placed_gap_word:
                    # Try each short word
                    for word in sorted(short_words, key=len):
                        if placed_gap_word:
                            break
                            
                        # Try all possible positions
                        for row in range(self.size):
                            for col in range(self.size):
                                for horizontal in [True, False]:
                                    if self.can_place_word(word, row, col, horizontal):
                                        # Check if it intersects or is adjacent to existing words
                                        if self._has_adjacent_words(row, col, horizontal, len(word)):
                                            self.place_word(word, row, col, horizontal)
                                            short_words.remove(word)
                                            placed_gap_word = True
                                            break
                                            
                                if placed_gap_word:
                                    break
                                    
                            if placed_gap_word:
                                break
                
                if not placed_gap_word:
                    break  # No more gap words could be placed
                    
                gap_filling_attempts += 1
                
        # Third phase: Try to fill any remaining gaps with very short words (3 letters)
        if len(valid_words) > len(self.placed_words):
            # Get very short words that haven't been placed yet
            very_short_words = [w for w in valid_words if len(w) == 3 and w not in [placed[0] for placed in self.placed_words]]
            
            # Try to place these words in any remaining small gaps
            final_gap_attempts = 0
            while final_gap_attempts < 200 and very_short_words:  # Doubled from 100 to 200 attempts
                placed_word = False
                
                # Try each very short word
                for word in very_short_words:
                    if placed_word:
                        break
                        
                    # Try all possible positions
                    for row in range(self.size):
                        for col in range(self.size):
                            for horizontal in [True, False]:
                                if self.can_place_word(word, row, col, horizontal):
                                    # Only place if it's adjacent to existing words
                                    if self._has_adjacent_words(row, col, horizontal, len(word)):
                                        self.place_word(word, row, col, horizontal)
                                        very_short_words.remove(word)
                                        placed_word = True
                                        break
                                        
                            if placed_word:
                                break
                                
                        if placed_word:
                            break
                            
                if not placed_word:
                    break
                    
                final_gap_attempts += 1

        # Try to place remaining words
        for word in valid_words[1:]:
            if len(self.placed_words) >= 60:  # Increased from 35 to 60 words total
                break
                
            placed = False
            # Try to intersect with existing words
            for placed_word in self.placed_words:
                if placed:
                    break
                    
                # Unpack the placed word tuple (word, row, col, horizontal, hint)
                w, r, c, h = placed_word[0], placed_word[1], placed_word[2], placed_word[3]
                
                # Try to find a letter in the new word that matches a letter in the placed word
                if h:  # If placed word is horizontal, try vertical placement
                    for i in range(len(w)):
                        for j in range(len(word)):
                            if w[i].lower() == word[j].lower():
                                # Calculate position for vertical placement
                                new_row = r - j
                                new_col = c + i
                                
                                # Check if placement is valid
                                if self.can_place_word(word, new_row, new_col, False):
                                    self.place_word(word, new_row, new_col, False)
                                    placed = True
                                    break
                        if placed:
                            break
                else:  # If placed word is vertical, try horizontal placement
                    for i in range(len(w)):
                        for j in range(len(word)):
                            if w[i].lower() == word[j].lower():
                                # Calculate position for horizontal placement
                                new_row = r + i
                                new_col = c - j
                                
                                # Check if placement is valid
                                if self.can_place_word(word, new_row, new_col, True):
                                    self.place_word(word, new_row, new_col, True)
                                    placed = True

        # Fill in any remaining gaps with short words
        if fill_gaps:
            self.fill_small_gaps()
            
        # Assign numbers in reading order (top-to-bottom, left-to-right)
        self.assign_numbers_in_reading_order()

        # Generate grid representation with cell details
        grid_data = []
        across_words = []
        down_words = []
        across_hints = []
        down_hints = []
        answer_grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Copy the filled grid to answer grid
        for row in range(self.height):
            for col in range(self.width):
                answer_grid[row][col] = self.grid[row][col]

        # Create grid with cell information and collect clues
        for row in range(self.height):
            grid_row = []
            for col in range(self.width):
                cell = {
                    'letter': self.grid[row][col],
                    'number': self.word_numbers.get((row, col), None),
                    'empty': self.grid[row][col] == ' '
                }
                grid_row.append(cell)
            grid_data.append(grid_row)

        # Generate clues and hints
        for placed_word in self.placed_words:
            # Unpack the placed word tuple safely
            if len(placed_word) >= 5:  # Make sure we have all components
                word, row, col, horizontal, hint = placed_word
                number = self.word_numbers.get((row, col))
                if number:
                    if horizontal:
                        across_words.append(f"{number}. {'_' * len(word)}")
                        across_hints.append(f"{number}. {hint}")
                    else:
                        down_words.append(f"{number}. {'_' * len(word)}")
                        down_hints.append(f"{number}. {hint}")

        # Sort clues and hints by number
        def sort_by_number(item):
            return int(item.split('.')[0])
            
        across_words.sort(key=sort_by_number)
        down_words.sort(key=sort_by_number)
        across_hints.sort(key=sort_by_number)
        down_hints.sort(key=sort_by_number)

        return grid_data, across_words, down_words, across_hints, down_hints, answer_grid

def main():
    parser = argparse.ArgumentParser(description='Generate a crossword puzzle')
    parser.add_argument('--size', type=int, default=15, help='Grid size')
    parser.add_argument('--language', choices=['fi', 'no', 'both'], default='fi',
                      help='Language choice')
    parser.add_argument('--words-file', help='Path to custom word list file')
    parser.add_argument('--theme', help='Optional theme for word selection')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'],
                      default='medium', help='Puzzle difficulty')

    args = parser.parse_args()

    generator = CrosswordGenerator(
        size=args.size,
        language=args.language,
        words_file=args.words_file,
        theme=args.theme,
        difficulty=args.difficulty
    )

    try:
        grid, across, down, across_hints, down_hints, answer_key = generator.generate_puzzle()
        
        print("\nCrossword Grid:")
        print(grid)
        
        print("\nAcross Clues:")
        for clue in across:
            print(clue)
            
        print("\nAcross Hints:")
        for hint in across_hints:
            print(hint)
            
        print("\nDown Clues:")
        for clue in down:
            print(clue)
            
        print("\nDown Hints:")
        for hint in down_hints:
            print(hint)
            
        print("\nAnswer Key:")
        print(answer_key)
        
    except Exception as e:
        print(f"Error generating puzzle: {e}")

if __name__ == '__main__':
    main()
