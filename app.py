from flask import Flask, render_template, request, jsonify
from crossword_generator import CrosswordGenerator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        size = int(data.get('size', 15))  # Default to 15x15
        language = data.get('language', 'fi')  # Default to Finnish
        
        # Load words
        words = []
        try:
            if language in ['fi', 'both']:
                with open('finnish_words.txt', 'r', encoding='utf-8') as f:
                    # Skip any line numbers and colons at the start of lines
                    words.extend(line.split(': ')[-1].strip() for line in f if line.strip() and not line.startswith('#'))
                print(f"Loaded {len(words)} Finnish words")
        except Exception as e:
            print(f"Error loading words: {e}")
            return jsonify({'error': 'Failed to load word list'}), 500

        if not words:
            return jsonify({'error': 'No words loaded'}), 500

        # Create generator with loaded words
        generator = CrosswordGenerator(size=size, language=language)
        generator.words = set(words)

        # Generate puzzle
        try:
            print(f"Starting puzzle generation with {len(generator.words)} words")
            try:
                grid, across, down, answer_key = generator.generate_puzzle()
                print(f"Grid dimensions: {len(grid)} x {len(grid[0]) if grid and len(grid) > 0 else 0}")
            except Exception as e:
                import traceback
                print(f"Error in generate_puzzle: {e}")
                traceback.print_exc()
                return jsonify({'error': f'Failed to generate puzzle: {str(e)}'}), 500
        except Exception as e:
            import traceback
            print(f"Error generating puzzle: {e}")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
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
            'answer_key': answer_key
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5013)
