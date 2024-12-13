from flask import Flask, request, jsonify
import wordle_env
import torch
import random
from model import DQN
import sys

app = Flask(__name__)

dqn.load_state_dict(torch.load("dqn_wordle.pth"))

word_list = []
common_words = []
with open('data/wordle_words.txt') as f:
    word_list = [line.strip() for line in f]

with open('data/common_words.txt') as f:
    common_words = [line.strip() for line in f]

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    target_word = data.get('target_word', 'crane')  
    env = wordle_env.WordleEnv(target_word, word_list, common_words)
    return jsonify({"message": "Game started", "target_word": target_word})


@app.route('/make_guess', methods=['POST'])
def make_guess():
    data = request.get_json()
    target_word = data.get('target_word', 'crane')
    guessed_word = data.get('guessed_word')
    
    env = wordle_env.WordleEnv(target_word, word_list, common_words)
    action = word_list.index(guessed_word)
    next_state, reward, done = env.step(action)
    
    response = {
        "next_state": next_state,
        "reward": reward,
        "done": done,
        "logs": env.get_logs()
    }
    
    return jsonify(response)


@app.route('/test_model', methods=['POST'])
def test_model():
    data = request.get_json()
    target_word = data.get('target_word', 'crane')
    env = wordle_env.WordleEnv(target_word, word_list, common_words)
    reward = test_dqn(env, dqn, word_list)
    return jsonify({"test_reward": reward})


def test_dqn(env, dqn, word_list):
    total_reward = 0
    state = env.reset()
    while True:
        # Use frequency analysis and heuristics to select actions
        candidate_words = env.select_word()
        guessing_word = random.choice(candidate_words)
        action = word_list.index(guessing_word)
        
        next_state, reward, done = env.step(action)
        total_reward += reward
        state = next_state
        
        if done:
            break
    
    return total_reward

if __name__ == '__main__':
    app.run(debug=True)
