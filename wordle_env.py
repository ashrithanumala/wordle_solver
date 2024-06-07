import random
import numpy as np
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity

class WordleEnv:
    PARTIAL_REWARD = 6
    RIGHT_REWARD = 10
    WRONG_PENALTY = -3

    def __init__(self, target_word, word_list):
        self.target_word = target_word
        self.word_list = [word for word in word_list]
        self.state = [0] * len(target_word)
        self.guesses = 0
        self.max_guesses = 6
        self.guessed_letters = set()
        self.freq_counter = Counter(''.join(self.word_list))  # Frequency counter of letters in the word list
        self.word_embeddings = self.get_word_embeddings()  # Word embeddings for the word list

    def reset(self):
        self.state = [0] * len(self.target_word)
        self.guesses = 0
        self.guessed_letters = set()
        return self.state
    
    def preprocess_word(self, word):
        state = []
        for i, char in enumerate(word):
            if char == self.target_word[i]:
                state.append(2)  # Correct letter in the correct position
            elif char in self.target_word:
                state.append(1)  # Correct letter in the wrong position
            else:
                state.append(-1)  # Incorrect letter
                self.guessed_letters.add(char)  # Add to guessed letters
        return state

    def get_word_embeddings(self):
        # Dummy function to generate word embeddings (replace with actual implementation)
        return np.random.rand(len(self.word_list), 100)

    def select_word(self):
        candidate_words = []
        for word in self.word_list:
            valid = True
            for i, char_state in enumerate(self.state):
                if char_state == 2 and word[i] != self.target_word[i]:  # Correct letter in the wrong position
                    valid = False
                    break
                elif char_state == -1 and word[i] in self.guessed_letters:  # Incorrect letter
                    valid = False
                    break
            if valid:
                for i, char in enumerate(word):
                    if char == self.target_word[i] and self.state[i] != 2:
                        candidate_words.append(word)
                        break
        return candidate_words

    def step(self, action):
        guessed_word = self.word_list[action]
        self.guesses += 1
        
        reward = 0
        done = False
        new_state = self.preprocess_word(guessed_word)
        
        for i in range(len(self.target_word)):
            if guessed_word[i] == self.target_word[i]:
                reward += self.RIGHT_REWARD
            elif guessed_word[i] in self.target_word:
                reward += self.PARTIAL_REWARD
            else:
                reward += self.WRONG_PENALTY
        
        if guessed_word == self.target_word or self.guesses >= self.max_guesses:
            done = True
        
        self.state = new_state
        return new_state, reward, done

if __name__ == "__main__":
    with open('data/past_wordle_answers.txt') as f:
        past_answers = [line.strip() for line in f]
    
    with open('data/wordle_words.txt') as f:
        word_list = [line.strip() for line in f]
    
    target_word = random.choice(past_answers)
    env = WordleEnv(target_word, word_list)
    
    state = env.reset()
    print("Initial state:", state)
    
    for _ in range(6):
        action = random.randint(0, len(word_list) - 1)
        new_state, reward, done = env.step(action)
        print("Guessed word:", word_list[action], "New state:", new_state, "Reward:", reward, "Done:", done)
        if done:
            break