import random
import torch
from model import DQN
from wordle_env import WordleEnv
import sys

def test_dqn(env, dqn, word_list):
    total_reward = 0
    state = env.reset()
    while True:
        # Use frequency analysis and heuristics to select actions
        candidate_words = env.select_word()
        guessing_word = random.choice(candidate_words)
        action = word_list.index(guessing_word)
        
        next_state, reward, done = env.step(action)
        print(next_state, guessing_word, env.target_word)
        total_reward += reward
        state = next_state
        
        if done:
            break
    
    print("Test Reward:", total_reward)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test.py TARGET_WORD")
        sys.exit(1)

    target_word = sys.argv[1]
    with open('data/past_wordle_answers.txt') as f:
        past_answers = [line.strip() for line in f]
    
    with open('data/wordle_words.txt') as f:
        word_list = [line.strip() for line in f]
    
    env = WordleEnv(target_word, word_list)
    dqn = DQN(len(target_word), len(word_list))
    dqn.load_state_dict(torch.load("dqn_wordle.pth"))
    
    test_dqn(env, dqn, word_list)