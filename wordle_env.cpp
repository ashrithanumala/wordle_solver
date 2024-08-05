#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <string>
#include <algorithm>
#include <iostream>
#include <sstream>

namespace py = pybind11;

class WordleEnv {
public:
    const int PARTIAL_REWARD = 6;
    const int RIGHT_REWARD = 10;
    const int WRONG_PENALTY = -3;
    const int MAX_GUESSES = 6;

    WordleEnv(const std::string& target_word, const std::vector<std::string>& word_list, const std::vector<std::string>& common_words)
        : target_word(target_word), word_list(word_list), common_words(common_words), guesses(0) {
        state = std::vector<int>(target_word.size(), 0);
        potential_words = word_list;
        letter_probs = calculate_letter_frequencies(potential_words);
    }

    std::vector<int> reset() {
        state = std::vector<int>(target_word.size(), 0);
        guesses = 0;
        guessed_wrong_letters.clear();
        right_letter_wrong_positions.clear();
        correct_positions.clear();
        potential_words = word_list;
        letter_probs = calculate_letter_frequencies(potential_words);
        logs.clear();
        return state;
    }

    std::tuple<std::vector<int>, int, bool> step(int action) {
        const std::string& guessed_word = word_list[action];
        guesses++;
        int reward = 0;
        bool done = false;
        std::vector<int> new_state = get_guess_state(guessed_word);
    
        
        for (size_t i = 0; i < target_word.size(); ++i) {
            if (guessed_word[i] == target_word[i]) {
                reward += RIGHT_REWARD;
                correct_positions[i] = guessed_word[i];
            } else if (target_word.find(guessed_word[i]) != std::string::npos) {
                reward += PARTIAL_REWARD;
                right_letter_wrong_positions[guessed_word[i]].push_back(i);
            } else {
                reward += WRONG_PENALTY;
                guessed_wrong_letters.insert(guessed_word[i]);
            }
        }

        std::ostringstream oss;
        oss << "GUESS: \"" << guessed_word << "\" - STATE - [";
        for (size_t i = 0; i < state.size(); ++i) {
            oss << state[i];
            if (i < state.size() - 1) {
                oss << ", ";
            }
        }
        oss << "] - REWARD - " << static_cast<int>(reward);
        
        logs.push_back(oss.str());

        if (guessed_word == target_word || guesses >= MAX_GUESSES) {
            done = true;
        }

        state = new_state;
        return std::make_tuple(new_state, reward, done);
    }

    std::vector<int> get_guess_state(const std::string& word) {
        std::vector<int> state(target_word.size(), 0);
        for (size_t i = 0; i < word.size(); ++i) {
            if (word[i] == target_word[i]) {
                state[i] = 2; // Correct letter in the correct position
            } else if (target_word.find(word[i]) != std::string::npos) {
                state[i] = 1; // Correct letter in the wrong position
            } else {
                state[i] = -1; // Incorrect letter
            }
        }
        return state;
    }

    std::vector<std::unordered_map<char, double>> calculate_letter_frequencies(const std::vector<std::string>& words) {
        std::vector<std::unordered_map<char, int>> letter_counts(5);
        std::vector<int> total_counts(5, 0);

        for (const auto& word : words) {
            for (size_t i = 0; i < word.size(); ++i) {
                letter_counts[i][word[i]]++;
                total_counts[i]++;
            }
        }

        std::vector<std::unordered_map<char, double>> letter_probs(5);
        for (size_t i = 0; i < 5; ++i) {
            for (auto it = letter_counts[i].begin(); it != letter_counts[i].end(); ++it) {
                letter_probs[i][it->first] = static_cast<double>(it->second) / total_counts[i];
            }
        }

        return letter_probs;
    }

    void update_potential_words() {
        std::vector<std::string> new_potential_words;

        for (const auto& word : potential_words) {
            bool valid = true;

            // Ensure correct letters are in the correct positions
            for (auto it = correct_positions.begin(); it != correct_positions.end(); ++it) {
                if (word[it->first] != it->second) {
                    valid = false;
                    break;
                }
            }

            // Ensure wrong letters are not present
            for (auto it = guessed_wrong_letters.begin(); it != guessed_wrong_letters.end(); ++it) {
                if (word.find(*it) != std::string::npos) {
                    valid = false;
                    break;
                }
            }

            // Ensure right letters in wrong positions are present but not in those positions
            for (auto it = right_letter_wrong_positions.begin(); it != right_letter_wrong_positions.end(); ++it) {
                if (word.find(it->first) == std::string::npos) {
                    valid = false;
                    break;
                }
                for (const auto& pos : it->second) {
                    if (word[pos] == it->first) {
                        valid = false;
                        break;
                    }
                }
                if (!valid) break;
            }

            if (valid) new_potential_words.push_back(word);
        }

        potential_words = new_potential_words;
        letter_probs = calculate_letter_frequencies(potential_words);
    }


    double calculate_word_score(const std::string& word) {
        double score = 1.0;
        for (size_t i = 0; i < word.size(); ++i) {
            score *= letter_probs[i][word[i]];
        }
        if (std::find(common_words.begin(), common_words.end(), word) != common_words.end()) {
            score *= 1.5; // Boost score for common words
        }
        return score;
    }

    std::vector<std::string> select_word() {
        if (guesses == 0) {
            return {"crane", "slate", "trace", "crate", "caret"};
        }
        update_potential_words();

        std::vector<std::pair<std::string, double>> word_scores;
        for (const auto& word : potential_words) {
            word_scores.emplace_back(word, calculate_word_score(word));
        }

        std::sort(word_scores.begin(), word_scores.end(),
                  [](const std::pair<std::string, double>& a, const std::pair<std::string, double>& b) {
                      return a.second > b.second;
                  });

        std::vector<std::string> top_10_words;
        for (size_t i = 0; i < std::min(static_cast<size_t>(10), word_scores.size()); ++i) {
            top_10_words.push_back(word_scores[i].first);
        }

        return top_10_words;
    }

    const std::vector<std::string>& get_logs() const {
        return logs;
    }

private:
    std::string target_word;
    std::vector<std::string> word_list;
    std::vector<std::string> common_words;
    std::vector<std::string> potential_words;
    std::vector<int> state;
    int guesses;
    std::unordered_set<char> guessed_wrong_letters;
    std::unordered_map<char, std::vector<int>> right_letter_wrong_positions;
    std::unordered_map<int, char> correct_positions;
    std::vector<std::unordered_map<char, double>> letter_probs;
    std::vector<std::string> logs;
};

PYBIND11_MODULE(wordle_env, m) {
    py::class_<WordleEnv>(m, "WordleEnv")
        .def(py::init<const std::string&, const std::vector<std::string>&, const std::vector<std::string>&>())
        .def("reset", &WordleEnv::reset)
        .def("step", &WordleEnv::step)
        .def("select_word", &WordleEnv::select_word)
        .def("get_logs", &WordleEnv::get_logs);
}
