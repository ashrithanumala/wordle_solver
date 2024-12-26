from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import wordle_env

app = Flask(__name__)
CORS(app)

# Global variables to maintain game state
current_env = None
word_list = []
common_words = []
past_answers = []

# Load word lists
def load_word_lists():
    global word_list, common_words, past_answers
    with open('data/past_wordle_answers.txt') as f:
        past_answers = [line.strip() for line in f]
    with open('data/wordle_words.txt') as f:
        word_list = [line.strip() for line in f]
    with open('data/common_words.txt') as f:
        common_words = [line.strip() for line in f]

@app.route('/api/start-game', methods=['POST'])
def start_game():
    global current_env
    target_word = random.choice(past_answers)
    current_env = wordle_env.WordleEnv(target_word, word_list, common_words)
    current_env.reset()
    
    suggestions = current_env.select_word_with_probabilities()
    return jsonify({
        'status': 'success',
        'suggestions': [{'word': word, 'probability': float(prob)} for word, prob in suggestions]
    })

@app.route('/api/make-guess', methods=['POST'])
def make_guess():
    global current_env
    if not current_env:
        return jsonify({'error': 'No active game'}), 400
    
    data = request.get_json()
    guess = data.get('guess', '').lower()
    
    if guess not in word_list:
        return jsonify({'error': 'Invalid word'}), 400
    
    action = word_list.index(guess)
    state, reward, done = current_env.step(action)
    
    # Convert numpy arrays to lists for JSON serialization
    state_list = state.tolist() if hasattr(state, 'tolist') else state
    
    suggestions = current_env.select_word_with_probabilities()
    
    response = {
        'state': state_list,
        'reward': float(reward),
        'done': done,
        'suggestions': [{'word': word, 'probability': float(prob)} for word, prob in suggestions]
    }
    
    if done:
        response['target_word'] = current_env.get_target_word()
    
    return jsonify(response)

if __name__ == '__main__':
    load_word_lists()
    app.run(debug=True, port=5000)