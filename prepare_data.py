# save this script as prepare_data.py
import numpy as np
from sklearn.model_selection import train_test_split

def load_words(file_path):
    with open(file_path, 'r') as f:
        return [line.strip().upper() for line in f]

# Load words
words = load_words('data/wordle_words.txt')
past_answers = set(load_words('data/past_wordle_answers.txt'))
words = [word for word in words if word not in past_answers]

# Split into training and multiple testing datasets
train_words, test_words_1 = train_test_split(words, test_size=0.2, random_state=42)
_, test_words_2 = train_test_split(words, test_size=0.2, random_state=43)
_, test_words_3 = train_test_split(words, test_size=0.2, random_state=44)

# Save the splits
with open('data/train_words.txt', 'w') as f:
    f.write('\n'.join(train_words))
with open('data/test_words_1.txt', 'w') as f:
    f.write('\n'.join(test_words_1))
with open('data/test_words_2.txt', 'w') as f:
    f.write('\n'.join(test_words_2))
with open('data/test_words_3.txt', 'w') as f:
    f.write('\n'.join(test_words_3))