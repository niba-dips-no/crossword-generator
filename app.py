from flask import Flask, render_template, request, jsonify
import os
import json
import traceback
from crossword_generator import CrosswordGenerator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        size_input = data.get('size', '15')  # Get size as string (may include dimensions like '25x15')
        language = data.get('language', 'fi')  # Default to Finnish
        
        # Parse size - could be a number or 'WIDTHxHEIGHT' format
        if 'x' in size_input:
            width, height = map(int, size_input.split('x'))
        else:
            width = height = int(size_input)  # Square grid
        
        # Load words
        words = []
        word_hints = {}
        max_words = 200  # Limit number of words to process
        
        try:
            if language in ['fi', 'both']:
                # Use the single word file with hints
                word_file = 'finnish_words_with_hints.txt' if os.path.exists('finnish_words_with_hints.txt') else 'finnish_words.txt'
                print(f"Using word file: {word_file}")
                
                with open(word_file, 'r', encoding='utf-8') as f:
                    # Process each line in the word file
                    for line in f:
                        if len(words) >= max_words:
                            break
                            
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                            
                        # Check if line contains a hint (format: word: hint)
                        if ':' in line:
                            parts = line.split(':', 1)  # Split only on first colon
                            word = parts[0].strip()
                            if len(word) < 3:  # Skip very short words
                                continue
                            hint = parts[1].strip()
                            word_hints[word.lower()] = hint
                        else:
                            word = line.strip()
                            if len(word) < 3:  # Skip very short words
                                continue
                            
                        # Basic validation: only include words with valid characters
                        valid_chars = set('abcdefghijklmnopqrstuvwxyzäö')
                        if all(c.lower() in valid_chars for c in word):
                            words.append(word)
                            
                        # Debug: Print progress
                        if len(words) % 50 == 0:
                            print(f"Loaded {len(words)} words...")
                                
                print(f"Loaded {len(words)} Finnish words")
                
            if language in ['no', 'both']:
                # Use the Norwegian word file with hints
                word_file = 'norwegian_words_with_hints.txt' if os.path.exists('norwegian_words_with_hints.txt') else None
                if word_file:
                    print(f"Using Norwegian word file: {word_file}")
                    
                    with open(word_file, 'r', encoding='utf-8') as f:
                        # Process each line in the word file
                        for line in f:
                            if line.strip() and not line.startswith('#'):
                                # Check if line contains a hint (format: word: hint)
                                if ':' in line:
                                    parts = line.split(':', 1)  # Split only on first colon
                                    word = parts[0].strip()
                                    hint = parts[1].strip()
                                    word_hints[word.lower()] = hint
                                else:
                                    word = line.strip()
                                    
                                # Basic validation: only include words with valid characters
                                valid_chars = set('abcdefghijklmnopqrstuvwxyzåøæ')
                                if all(c.lower() in valid_chars for c in word):
                                    words.append(word)
                    
                    print(f"Loaded {len(words)} words total (Finnish and/or Norwegian)")
                else:
                    print("Norwegian word file not found")
                    
            # Print some sample hints
            print("=== Sample hints from word file ===")
            hint_count = 0
            for word, hint in word_hints.items():
                print(f"{word}: {hint}")
                hint_count += 1
                if hint_count >= 10:
                    break
        except Exception as e:
            print(f"Error loading words: {e}")
            return jsonify({'error': 'Failed to load word list'}), 500

        if not words:
            return jsonify({'error': 'No words loaded'}), 500

        # Create generator with loaded words
        generator = CrosswordGenerator(width=width, height=height, language=language)
        generator.words = set(words)
        
        # Set the word hints in the generator
        generator.word_hints = word_hints
        
        # Debug word hints
        print(f"Word hints loaded: {len(generator.word_hints)}")
        if generator.word_hints:
            # Print a few examples
            sample_keys = list(generator.word_hints.keys())[:5]
            for key in sample_keys:
                print(f"Sample hint: {key} -> {generator.word_hints[key]}")
        else:
            print("No word hints loaded!")

        # Generate puzzle
        try:
            print(f"Starting puzzle generation with {len(generator.words)} words")
            print(f"Grid dimensions: width={generator.width}, height={generator.height}")
            # Add traceback for easier debugging
            import traceback
            try:
                grid, across, down, across_hints, down_hints, answer_key = generator.generate_puzzle()
            except Exception as e:
                print(f"Error in generate_puzzle with full traceback:\n{traceback.format_exc()}")
                raise e
            print(f"Grid dimensions: {len(grid)} x {len(grid[0]) if grid and len(grid) > 0 else 0}")
            
            # Debug output for hints
            print("\n=== Hints for placed words ===")
            print(f"Across hints: {len(across_hints)}")
            for i, hint in enumerate(across_hints):
                print(f"Across {i+1}: {across[i]} - {hint}")
                
            print(f"Down hints: {len(down_hints)}")
            for i, hint in enumerate(down_hints):
                print(f"Down {i+1}: {down[i]} - {hint}")
            
        except Exception as e:
            print(f"Error in generate_puzzle: {e}")
            traceback.print_exc()
            return jsonify({'error': f'Failed to generate puzzle: {str(e)}'}), 500

        # Ensure grid is properly serialized for JSON
        serialized_grid = []
        if grid and isinstance(grid, list):
            for row in grid:
                if isinstance(row, list):
                    serialized_row = []
                    for cell in row:
                        if isinstance(cell, dict):
                            serialized_row.append({
                                'letter': cell.get('letter', ' '),
                                'number': cell.get('number'),
                                'empty': cell.get('empty', False)
                            })
                        else:
                            # Fallback for non-dict cells
                            serialized_row.append({
                                'letter': ' ',
                                'number': None,
                                'empty': True
                            })
                    serialized_grid.append(serialized_row)
        
        return jsonify({
            'grid': serialized_grid,
            'across': across,
            'down': down,
            'across_hints': across_hints,
            'down_hints': down_hints,
            'answer_key': answer_key
        })
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5014)
