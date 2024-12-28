from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
import random
import wordle_env
import logging
import uuid
import requests
import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}}, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"])

cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 86400})

class GameSession:
    def __init__(self, env, is_daily):
        self.env = env
        self.is_daily = is_daily

game_sessions = {}
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

@cache.cached(timeout=86400, key_prefix='daily_word')
def get_daily_word():
    try:
        date = datetime.date.today()
        url = f"https://www.nytimes.com/svc/wordle/v2/{date:%Y-%m-%d}.json"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['solution'].lower()
    except Exception as e:
        print(f"Error fetching daily word: {e}")
        return None

@app.route('/api/start-game-random', methods=['POST', 'OPTIONS'])
def start_game_random():
    global game_sessions
    if not word_list and not load_word_lists():
        return jsonify({'error': 'Word lists not loaded'}), 500
    
    target_word = random.choice(past_answers)
    new_env = wordle_env.WordleEnv(target_word, word_list, common_words)
    new_env.reset()
    
    session_id = str(uuid.uuid4())
    game_sessions[session_id] = GameSession(new_env, False)
    
    suggestions = new_env.select_word_with_probabilities()
    return jsonify({
        'status': 'success',
        'session_id': session_id,
        'suggestions': [{'word': word, 'probability': float(prob)} for word, prob in suggestions]
    })


@app.route('/api/start-game-daily', methods=['POST', 'OPTIONS'])
def start_game_daily():
    global game_sessions
    if not word_list and not load_word_lists():
        return jsonify({'error': 'Word lists not loaded'}), 500
    
    target_word = get_daily_word()
    if not target_word:
        return jsonify({'error': 'Could not fetch daily word'}), 500
    
    new_env = wordle_env.WordleEnv(target_word, word_list, common_words)
    new_env.reset()
    
    session_id = str(uuid.uuid4())
    game_sessions[session_id] = GameSession(new_env, True)
    
    suggestions = new_env.select_word_with_probabilities()
    return jsonify({
        'status': 'success',
        'session_id': session_id,
        'suggestions': [{'word': word, 'probability': float(prob)} for word, prob in suggestions]
    })

@app.route('/api/make-guess', methods=['POST', 'OPTIONS'])
def make_guess():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        session_id = data.get('session_id')
        guess = data.get('guess', '').lower()
        
        if not session_id or session_id not in game_sessions:
            return jsonify({'error': 'Invalid session'}), 400
            
        game_session = game_sessions[session_id]
        current_env = game_session.env  # This is already the WordleEnv instance
        
        if guess not in word_list:
            return jsonify({'error': 'Invalid word'}), 400
            
        action = word_list.index(guess)
        state, reward, done = current_env.step(action)  # Call methods directly on current_env
        
        state_list = state.tolist() if hasattr(state, 'tolist') else state
        suggestions = current_env.select_word_with_probabilities()
        
        response = {
            'state': state_list,
            'reward': float(reward),
            'done': done,
            'suggestions': [{'word': word, 'probability': float(prob)} for word, prob in suggestions],
            'current_row': int(current_env.get_guesses()),
            'is_daily': game_session.is_daily
        }
        
        if done:
            response['target_word'] = current_env.get_target_word()
            del game_sessions[session_id]
            
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in make_guess: {str(e)}")
        return jsonify({'error': 'Server error'}), 500


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