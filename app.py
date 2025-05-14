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
            grid, across, down, answer_key = generator.generate_puzzle()
        except Exception as e:
            print(f"Error generating puzzle: {e}")
            return jsonify({'error': str(e)}), 500
        return jsonify({
            'grid': grid,
            'across': across,
            'down': down,
            'answer_key': answer_key
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5013)
