import random
import torch
import torch.optim as optim
import torch.nn.functional as F
from model import DQN
from replay_buffer import ReplayBuffer
import wordle_env
import sys

def train_dqn(word_list, past_answers, common_words, num_episodes=2000, batch_size=64, gamma=0.99):
    input_dim = 5
    output_dim = len(word_list)
    
    dqn = DQN(input_dim, output_dim)
    target_dqn = DQN(input_dim, output_dim)
    target_dqn.load_state_dict(dqn.state_dict())
    target_dqn.eval()
    
    optimizer = optim.Adam(dqn.parameters())
    replay_buffer = ReplayBuffer(10000)
    
    for episode in range(num_episodes):
        target_word = random.choice(past_answers)
        env = wordle_env.WordleEnv(target_word, word_list, common_words)
        
        state = env.reset()
        total_reward = 0
        
        while True:
            # Use frequency analysis and heuristics to select actions
            candidate_words = env.select_word()
            action = word_list.index(candidate_words[0])
            
            next_state, reward, done = env.step(action)
            replay_buffer.push(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            
            if done:
                break
            
            if len(replay_buffer) >= batch_size:
                batch_state, batch_action, batch_reward, batch_next_state, batch_done = replay_buffer.sample(batch_size)
                
                batch_state = torch.FloatTensor(batch_state)
                batch_action = torch.LongTensor(batch_action)
                batch_reward = torch.FloatTensor(batch_reward)
                batch_next_state = torch.FloatTensor(batch_next_state)
                batch_done = torch.FloatTensor(batch_done)
                
                q_values = dqn(batch_state).gather(1, batch_action.unsqueeze(1)).squeeze(1)
                next_q_values = target_dqn(batch_next_state).max(1)[0]
                target_q_values = batch_reward + gamma * next_q_values * (1 - batch_done)
                
                loss = F.mse_loss(q_values, target_q_values.detach())
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
        
        if episode % 100 == 0:
            target_dqn.load_state_dict(dqn.state_dict())
            print(f"Episode {episode}, Total Reward: {total_reward}")
    
    return dqn

def main():
    with open('data/past_wordle_answers.txt', 'r') as f:
        past_answers = [line.strip() for line in f]
    
    with open('data/wordle_words.txt', 'r') as f:
        word_list = [line.strip() for line in f]
    
    with open('data/common_words.txt', 'r') as f:
        common_words = [line.strip() for line in f]
    
    dqn = train_dqn(
        word_list=word_list, 
        past_answers=past_answers, 
        common_words=common_words
    )
    
    torch.save(dqn.state_dict(), "dqn_wordle.pth")
    print("Training complete. Model saved to dqn_wordle.pth")

if __name__ == "__main__":
    main()