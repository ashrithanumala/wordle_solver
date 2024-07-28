import random
import torch
import sys
from model import DQN
import wordle_env

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test.py TARGET_WORD or python3 test.py all")
        sys.exit(1)

    target_arg = sys.argv[1]
    with open('data/past_wordle_answers.txt') as f:
        past_answers = [line.strip() for line in f]
    
    with open('data/wordle_words.txt') as f:
        word_list = [line.strip() for line in f]
    
    with open('data/common_words.txt') as f:
        common_words = [line.strip() for line in f]
    
    if target_arg == "all":
        total_rewards = 0
        rewards = []
        sample_size = int(0.4 * len(past_answers))
        sampled_answers = random.sample(past_answers, sample_size)
        guesses = 0

        for target_word in sampled_answers:
            env = wordle_env.WordleEnv(target_word, word_list, common_words)
            dqn = DQN(len(target_word), len(word_list))
            dqn.load_state_dict(torch.load("dqn_wordle.pth"))
            reward = test_dqn(env, dqn, word_list)
            rewards.append(reward)
            total_rewards += reward
            guesses += len(env.get_logs())
        
        average_reward = total_rewards / len(past_answers)
        max_reward = max(rewards)
        min_reward = min(rewards)
        print(f"Average Test Reward: {average_reward}")
        print(f"Average Guesses: {guesses / len(past_answers)}")
    else:
        target_word = target_arg
        
        env = wordle_env.WordleEnv(target_word, word_list, common_words)
        dqn = DQN(len(target_word), len(word_list))
        dqn.load_state_dict(torch.load("dqn_wordle.pth"))
        reward = test_dqn(env, dqn, word_list)
        print(f"Test Reward for {target_word}: {reward}")
        logs = env.get_logs()
        for log in logs:
            print(log)