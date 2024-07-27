import wordle_env

# Example word list and target word
word_list = ["crane", "slate", "trace", "crate", "caret", "apple", "grape", "berry", "melon", "peach"]
target_word = "crate"

# Create WordleEnv instance
env = wordle_env.WordleEnv(target_word, word_list)

# Reset the environment
state = env.reset()
print("Initial state:", state)

# Make a guess
new_state, reward, done = env.step(word_list.index("crane"))
print("New state:", new_state, "Reward:", reward, "Done:", done)

# Select a word
top_words = env.select_word()
print("Top words:", top_words)
