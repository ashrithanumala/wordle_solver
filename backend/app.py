from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import wordle_env
import logging


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}}, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"])

current_env = None
word_list = []
common_words = []
past_answers = []

def load_word_lists():
    global word_list, common_words, past_answers
    try:
        with open('data/past_wordle_answers.txt') as f:
            past_answers = [line.strip() for line in f]
        with open('data/wordle_words.txt') as f:
            word_list = [line.strip() for line in f]
        with open('data/common_words.txt') as f:
            common_words = [line.strip() for line in f]
    except FileNotFoundError as e:
        print(f"Error loading word lists: {e}")
        return False
    return True

@app.route('/api/start-game', methods=['POST', 'OPTIONS'])
def start_game():
    global current_env
    if not word_list and not load_word_lists():
        return jsonify({'error': 'Word lists not loaded'}), 500
    
    target_word = random.choice(past_answers)
    current_env = wordle_env.WordleEnv(target_word, word_list, common_words)
    current_env.reset()
    
    suggestions = current_env.select_word_with_probabilities()
    print(suggestions)
    return jsonify({
        'status': 'success',
        'suggestions': [{'word': word, 'probability': float(prob)} for word, prob in suggestions]
    })

@app.route('/api/make-guess', methods=['POST', 'OPTIONS'])
def make_guess():
    if request.method == 'OPTIONS':
        return '', 204
    
    global current_env
    if not current_env:
        return jsonify({'error': 'No active game'}), 400
    
    data = request.get_json()
    guess = data.get('guess', '').lower()
    
    if guess not in word_list:
        return jsonify({'error': 'Invalid word'}), 400
    
    action = word_list.index(guess)
    state, reward, done = current_env.step(action)
    
    state_list = state.tolist() if hasattr(state, 'tolist') else state
    suggestions = current_env.select_word_with_probabilities()
    
    response = {
        'state': state_list,
        'reward': float(reward),
        'done': done,
        'suggestions': [{'word': word, 'probability': float(prob)} for word, prob in suggestions],
        'current_row': int(current_env.get_guesses())
    }
    
    if done:
        response['target_word'] = current_env.get_target_word()
    
    return jsonify(response)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

@app.before_request
def log_request_info():
    app.logger.debug(f"Request Headers: {request.headers}")
    app.logger.debug(f"Request Body: {request.get_data(as_text=True)}")

@app.route('/api/test-cors', methods=['GET'])
def test_cors():
    return jsonify({"message": "CORS works!"})

if __name__ == '__main__':
    if load_word_lists():
        app.run(debug=True, port=5001)
    else:
        print("Failed to load word lists. Exiting.")
        exit(1)