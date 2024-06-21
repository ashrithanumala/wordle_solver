import nltk
from nltk.corpus import words

# Download the 'words' corpus if not already downloaded
nltk.download('words')

# Example function to get frequency of a word in the NLTK words corpus
def get_word_frequency(word):
    if word in words.words():
        return words.words().count(word) / len(words.words())
    else:
        return 0.0

# Example usage
word_frequency = get_word_frequency("example")
print(f"Frequency of 'example' in NLTK words corpus: {word_frequency}")