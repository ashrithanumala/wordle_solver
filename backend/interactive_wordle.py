import random
import sys
import torch
import wordle_env


def interactive_guess(env, word_list):
    state = env.reset()
    print("Game on, start guessing")

    while True:
        
        print("\nCurrent State:", state)

        # Use the updated method to get word suggestions based on probabilities
        word_probs = env.select_word_with_probabilities()
        
        # Extract the word suggestions and their probabilities from the word_probs list
        suggestions = [word for word, _ in word_probs]
        probabilities = [prob for _, prob in word_probs]
        
        # Print both words and their corresponding probabilities
        print("Suggestions for next guess and their probabilities:")
        for word, prob in zip(suggestions, probabilities):
            print(f"{word}: {prob:.4f}")  # Display the probability with 4 decimal places

        guessed_word = input("Enter your guess: ").strip().lower()

        while guessed_word not in word_list:
            print("Invalid word. Please guess a valid word from the list.")
            guessed_word = input("Enter your guess: ").strip().lower()

        action = word_list.index(guessed_word)
        next_state, reward, done = env.step(action)

        print(f"Reward for '{guessed_word}': {reward}")
        state = next_state

        if done:
            print("\nGame Over!")
            if guessed_word == env.get_target_word():
                print("Congratulations! You guessed the word!")
            else:
                print(f"Better luck next time. The word was: {env.target_word()}")
            break


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 interactive_wordle.py TARGET_WORD or python3 interactive_wordle.py interactive")
        sys.exit(1)

    target_arg = sys.argv[1]

    with open('data/past_wordle_answers.txt') as f:
        past_answers = [line.strip() for line in f]

    with open('data/wordle_words.txt') as f:
        word_list = [line.strip() for line in f]

    with open('data/common_words.txt') as f:
        common_words = [line.strip() for line in f]

    if target_arg == "interactive":
        target_word = random.choice(past_answers)
        env = wordle_env.WordleEnv(target_word, word_list, common_words)
        interactive_guess(env, word_list)
    else:
        target_word = target_arg
        if target_word not in past_answers:
            print(f"The word '{target_word}' isn't a valid wordle word")
            sys.exit(1)

        env = wordle_env.WordleEnv(target_word, word_list, common_words)
        interactive_guess(env, word_list)


if __name__ == "__main__":
    main()
