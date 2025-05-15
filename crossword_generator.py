#!/usr/bin/env python3
import argparse
import random
from typing import List, Optional, Set, Tuple
import unidecode

class CrosswordGenerator:
    def __init__(
        self,
        size: int = 15,  # Default to 15x15 grid
        language: str = "fi",
        words_file: Optional[str] = None,
        theme: Optional[str] = None,
        difficulty: str = "medium"
    ):
        self.size = size
        self.language = language
        self.words_file = words_file
        self.theme = theme
        self.difficulty = difficulty
        self.words: Set[str] = set()
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]
        self.placed_words = []
        self.word_numbers = {}
        self.current_number = 1

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
                        valid_words.append(word)
                elif self.language == 'no':
                    # Allow Å, Ø, Æ, and basic Latin letters
                    valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZÅØÆ')
                    if all(c in valid_chars for c in word):
                        valid_words.append(word)
                else:  # 'both' or any other language
                    valid_words.append(word)
        
        print(f"Valid words after filtering: {len(valid_words)}")
        if not valid_words:
            print("No valid words found after filtering!")
        
        # Sort words by length, but prioritize 4-6 letter words
        def word_priority(word):
            length = len(word)
            if 5 <= length <= 10:
                return (0, -length)  # Prioritize 4-6 letter words, longer ones first
            return (1, -length)  # Other lengths come after
        
        valid_words.sort(key=word_priority)
        # Limit to 100 words for better performance
        valid_words = valid_words[:100]
        # Shuffle to get different combinations
        random.shuffle(valid_words)
        return valid_words

    def can_place_word(self, word: str, row: int, col: int, horizontal: bool) -> bool:
        """Check if a word can be placed at the given position with proper crossword rules."""
        # Check if word fits
        if horizontal and col + len(word) > self.size:
            return False
        if not horizontal and row + len(word) > self.size:
            return False

        # Check if placement creates invalid words
        intersects = False
        for i in range(len(word)):
            current_row = row if horizontal else row + i
            current_col = col + i if horizontal else col

            # Check the cell itself
            if self.grid[current_row][current_col] not in [' ', word[i]]:
                return False
            
            # If this cell has a letter, it's an intersection
            if self.grid[current_row][current_col] == word[i]:
                intersects = True

            # Check for proper word separation
            # For horizontal words, check left and right
            if horizontal:
                # Check left (if not at the beginning of the word)
                if i == 0 and col > 0 and self.grid[current_row][current_col-1] != ' ':
                    return False  # Can't have a letter immediately before the word
                
                # Check right (if at the end of the word)
                if i == len(word) - 1 and col + len(word) < self.size and self.grid[current_row][current_col+1] != ' ':
                    return False  # Can't have a letter immediately after the word
                
                # Check cells above and below (these should only have letters at intersections)
                if self.grid[current_row][current_col] == ' ':  # Only check for empty cells
                    if (current_row > 0 and self.grid[current_row-1][current_col] != ' ') or \
                       (current_row < self.size-1 and self.grid[current_row+1][current_col] != ' '):
                        return False  # Can't have adjacent letters without intersection
            
            # For vertical words, check above and below
            else:
                # Check above (if not at the beginning of the word)
                if i == 0 and row > 0 and self.grid[current_row-1][current_col] != ' ':
                    return False  # Can't have a letter immediately above the word
                
                # Check below (if at the end of the word)
                if i == len(word) - 1 and row + len(word) < self.size and self.grid[current_row+1][current_col] != ' ':
                    return False  # Can't have a letter immediately below the word
                
                # Check cells left and right (these should only have letters at intersections)
                if self.grid[current_row][current_col] == ' ':  # Only check for empty cells
                    if (current_col > 0 and self.grid[current_row][current_col-1] != ' ') or \
                       (current_col < self.size-1 and self.grid[current_row][current_col+1] != ' '):
                        return False  # Can't have adjacent letters without intersection

        # Word must intersect with existing words (except first word)
        if self.placed_words and not intersects:
            return False

        return True

    def place_word(self, word: str, row: int, col: int, horizontal: bool) -> None:
        """Place a word on the grid and assign numbers to starting positions."""
        # Check if this position needs a number
        needs_number = False
        if horizontal:
            if col == 0 or self.grid[row][col-1] == ' ':
                needs_number = True
        else:
            if row == 0 or self.grid[row-1][col] == ' ':
                needs_number = True

        if needs_number:
            self.word_numbers[(row, col)] = self.current_number
            self.current_number += 1

        # Place the word
        if horizontal:
            for i in range(len(word)):
                self.grid[row][col + i] = word[i]
        else:
            for i in range(len(word)):
                self.grid[row + i][col] = word[i]

        self.placed_words.append((word, row, col, horizontal))

    def generate_puzzle(self) -> Tuple[List[List[dict]], List[str], List[str], List[List[str]]]:
        """Generate crossword puzzle with proper grid structure and clues."""
        # Reset grid and counters
        self.grid = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.placed_words = []
        self.word_numbers = {}
        self.current_number = 1

        valid_words = self.filter_words()
        if not valid_words:
            raise ValueError("No valid words found for the specified language")

        # Try to find a suitable first word (4-10 letters)
        first_word = None
        for word in valid_words:
            if 4 <= len(word) <= 10:
                first_word = word
                break
        
        if not first_word:
            first_word = valid_words[0]  # Fallback to first word if no suitable word found

        # Place first word in the middle
        start_row = self.size // 2
        start_col = (self.size - len(first_word)) // 2
        self.place_word(first_word, start_row, start_col, True)

        # Try to place remaining words by finding intersections
        attempts = 0
        max_attempts = 100  # Prevent infinite loops
        while attempts < max_attempts and len(self.placed_words) < 20:  # Limit to 20 words total
            best_placement = None
            best_score = -1
            best_word = None

            # Try each remaining word
            for word in valid_words:
                if word in [w[0] for w in self.placed_words]:
                    continue

                # Try all possible positions
                for row in range(self.size):
                    for col in range(self.size):
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

        # Try to place remaining words
        for word in valid_words[1:]:
            if len(self.placed_words) >= 20:  # Limit to 20 words total
                break
                
            placed = False
            # Try to intersect with existing words
            for w, r, c, h in self.placed_words:
                if placed:
                    break
                    
                # Try to find a letter in the new word that matches a letter in the placed word
                if h:  # If placed word is horizontal, try vertical placement
                    for i in range(len(w)):
                        for j in range(len(word)):
                            if word[j] == w[i]:
                                # Calculate position for vertical placement
                                new_row = r - j
                                new_col = c + i
                                
                                # Verify placement is valid
                                if (new_row >= 0 and new_row + len(word) <= self.size and
                                    self.can_place_word(word, new_row, new_col, False)):
                                    # Place the word vertically
                                    self.place_word(word, new_row, new_col, False)
                                    placed = True
                                    break
                        if placed:
                            break
                            
                else:  # If placed word is vertical, try horizontal placement
                    for i in range(len(w)):
                        for j in range(len(word)):
                            if word[j] == w[i]:
                                # Calculate position for horizontal placement
                                new_row = r + i
                                new_col = c - j
                                
                                # Verify placement is valid
                                if (new_col >= 0 and new_col + len(word) <= self.size and
                                    self.can_place_word(word, new_row, new_col, True)):
                                    # Place the word horizontally
                                    self.place_word(word, new_row, new_col, True)
                                    placed = True
                                    break
                        if placed:
                            break

        # Generate grid data and clues
        grid_data = []
        across_words = []
        down_words = []
        answer_grid = [[' ' for _ in range(self.size)] for _ in range(self.size)]

        # Copy the filled grid to answer grid
        for row in range(self.size):
            for col in range(self.size):
                answer_grid[row][col] = self.grid[row][col]

        # Create grid with cell information and collect clues
        for row in range(self.size):
            grid_row = []
            for col in range(self.size):
                cell = {
                    'letter': self.grid[row][col],
                    'number': self.word_numbers.get((row, col), None),
                    'empty': self.grid[row][col] == ' '
                }
                grid_row.append(cell)
            grid_data.append(grid_row)

        # Generate clues
        for word, row, col, horizontal in self.placed_words:
            number = self.word_numbers.get((row, col))
            if number:
                if horizontal:
                    across_words.append(f"{number}. {'_' * len(word)}")
                else:
                    down_words.append(f"{number}. {'_' * len(word)}")

        # Sort clues by number
        across_words.sort(key=lambda x: int(x.split('.')[0]))
        down_words.sort(key=lambda x: int(x.split('.')[0]))

        return grid_data, across_words, down_words, answer_grid

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
        grid, across, down, answer_key = generator.generate_puzzle()
        
        print("\nCrossword Grid:")
        print(grid)
        
        print("\nAcross Clues:")
        for clue in across:
            print(clue)
            
        print("\nDown Clues:")
        for clue in down:
            print(clue)
            
        print("\nAnswer Key:")
        print(answer_key)
        
    except Exception as e:
        print(f"Error generating puzzle: {e}")

if __name__ == '__main__':
    main()
