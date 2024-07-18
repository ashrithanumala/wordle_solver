import random
import numpy as np
import pandas as pd
from collections import defaultdict

class WordleEnv:
    PARTIAL_REWARD = 6
    RIGHT_REWARD = 10
    WRONG_PENALTY = -3
    MAX_GUESSES = 6

    def __init__(self, target_word, word_list):
        self.target_word = target_word
        self.word_list = self.create_word_df(word_list)
        self.potential_words = self.word_list.copy()
        self.state = [0, 0, 0, 0, 0]
        self.guesses = 0
        self.guessed_wrong_letters = set()
        self.right_letter_wrong_positions = defaultdict(list)
        self.correct_positions = {}
        self.letter_probs = []

    def create_word_df(self, word_list):
        df = pd.DataFrame({'word': word_list})
        for i in range(5):
            df[i] = df['word'].str[i]
        return df

    def reset(self):
        self.state = [0] * len(self.target_word)
        self.guesses = 0
        self.guessed_wrong_letters = set()
        self.right_letter_wrong_positions = defaultdict(list)
        self.potential_words = self.word_list.copy()
        self.letter_probs = self.calculate_letter_frequencies(self.potential_words)
        return self.state

    def get_guess_state(self, word):
        state = []
        for i, char in enumerate(word):
            if char == self.target_word[i]:
                state.append(2)  # Correct letter in the correct position
            elif char in self.target_word:
                state.append(1)  # Correct letter in the wrong position
                self.right_letter_wrong_positions[char].append(i)
            else:
                state.append(-1)  # Incorrect letter
                self.guessed_wrong_letters.add(char)
        return state

    def calculate_letter_frequencies(self, word_df):
        letter_freqs = [defaultdict(int) for _ in range(5)]
        total_counts = [0] * 5

        for index, row in word_df.iterrows():
            for i in range(5):
                char = row[i]
                letter_freqs[i][char] += 1
                total_counts[i] += 1

        letter_probs = []
        for i in range(5):
            letter_probs.append({char: count / total_counts[i] for char, count in letter_freqs[i].items()})

        return letter_probs

    def update_potential_words(self):
        new_potential_words = self.potential_words.copy()

        for index, row in self.potential_words.iterrows():
            word = row['word']
            if any(word[pos] != char for char, pos in self.correct_positions.items()):
                new_potential_words = new_potential_words.drop(index)
            elif any(char in self.guessed_wrong_letters for char in word):
                new_potential_words = new_potential_words.drop(index)
            elif any(word[pos] == char for char, pos_list in self.right_letter_wrong_positions.items() for pos in pos_list):
                new_potential_words = new_potential_words.drop(index)
        
        self.potential_words = new_potential_words
        self.letter_probs = self.calculate_letter_frequencies(self.potential_words)

    def calculate_word_score(self, word):
        score = 1.0
        for i, char in enumerate(word):
            score *= self.letter_probs[i].get(char, 1e-6)  # Use a small value for unseen letters
        return score

    def select_word(self):
        if self.guesses == 0:
            return ['crane', 'slate', 'trace', 'crate', 'caret']
        self.update_potential_words()

        word_scores = [(row['word'], self.calculate_word_score(row['word'])) for index, row in self.potential_words.iterrows()]

        word_scores.sort(key=lambda x: x[1], reverse=True)

        top_10_words = [word for word, score in word_scores[:10]]
        return top_10_words

    def step(self, action):
        guessed_word = self.word_list.loc[action, 'word']
        self.guesses += 1
        reward = 0
        done = False
        new_state = self.get_guess_state(guessed_word)
        print(f"Guess number {self.guesses}: {guessed_word}, {new_state}")
        for i in range(len(self.target_word)):
            if guessed_word[i] == self.target_word[i]:
                reward += self.RIGHT_REWARD
            elif guessed_word[i] in self.target_word:
                reward += self.PARTIAL_REWARD
            else:
                reward += self.WRONG_PENALTY
        
        if guessed_word == self.target_word or self.guesses >= self.MAX_GUESSES:
            done = True
        
        self.state = new_state
        return new_state, reward, done