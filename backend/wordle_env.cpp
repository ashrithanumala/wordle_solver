#include "cuckoo.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <sstream>
#include <algorithm>
#include <iostream>
#include <cmath>

namespace py = pybind11;

class WordleEnv {
public:
    const int PARTIAL_REWARD = 6;
    const int RIGHT_REWARD = 10;
    const int WRONG_PENALTY = -3;

    const int MAX_GUESSES = 6;

    WordleEnv(const std::string& target_word, const std::vector<std::string>& word_list, const std::vector<std::string>& common_words)
        : target_word(target_word), word_list(word_list), common_words(common_words), guesses(0) {

        // Initialize state and potential words
        state = std::vector<int>(target_word.size(), 0);
        potential_words = word_list;
        letter_probs = calculate_letter_frequencies(potential_words);

        // Initialize cuckoo filters for position, letter, and wrong letter tracking
        filter_by_position.resize(target_word.size(), CuckooFilter(10000, 4));
        filter_by_letter = CuckooFilter(10000, 4);
        filter_wrong_letters = CuckooFilter(10000, 4);

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

        // Reset filters
        for (auto& filter : filter_by_position) {
            filter = CuckooFilter(10000, 4);
        }
        filter_by_letter = CuckooFilter(10000, 4);
        filter_wrong_letters = CuckooFilter(10000, 4);

        return state;
    }

    std::tuple<std::vector<int>, int, bool> step(int action) {
        const std::string& guessed_word = word_list[action];
        guesses++;
        int reward = 0;
        bool done = false;
        std::vector<int> new_state = get_guess_state(guessed_word);
        // double turn_weight = 1.0 - (guesses - 1) * 0.1;

        // Update filters based on guessed word
        for (size_t i = 0; i < target_word.size(); ++i) {
            if (guessed_word[i] == target_word[i]) {
                reward += RIGHT_REWARD;
                correct_positions[i] = guessed_word[i];
                filter_by_position[i].insert(std::string(1, guessed_word[i]));
            } else if (target_word.find(guessed_word[i]) != std::string::npos) {
                reward += PARTIAL_REWARD;
                right_letter_wrong_positions[guessed_word[i]].push_back(i);
                filter_by_letter.insert(std::string(1, guessed_word[i]));
            } else {
                reward += WRONG_PENALTY;
                guessed_wrong_letters.insert(guessed_word[i]);
                filter_wrong_letters.insert(std::string(1, guessed_word[i]));
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
        oss << "] - REWARD - " << reward;
        logs.push_back(oss.str());

        if (guessed_word == target_word || guesses >= MAX_GUESSES) {
            done = true;
        }

        state = new_state;
        return std::make_tuple(new_state, reward, done);
    }

    std::vector<int> get_guess_state(const std::string& word) {
        std::vector<int> state(target_word.size(), 0);
        std::unordered_map<char, int> letter_count;

        // Count occurrences of each letter in the guessed word
        for (const auto& ch : word) {
            letter_count[ch]++;
        }

        for (size_t i = 0; i < word.size(); ++i) {
            char guessed_char = word[i];
            if (target_word[i] == guessed_char) {
                state[i] = 2; // Correct letter in the correct position
                letter_count[guessed_char]--; // Decrement count
            } else if (target_word.find(guessed_char) != std::string::npos) {
                if (letter_count[guessed_char] > 0) {
                    state[i] = 1; // Correct letter in the wrong position
                } else {
                    state[i] = -1; // Incorrect letter (but letter is in the target word)
                }
                letter_count[guessed_char]--; // Decrement count
            } else {
                state[i] = -1; // Incorrect letter
            }
        }
        return state;
    }

    std::vector<std::unordered_map<char, double>> calculate_letter_frequencies(const std::vector<std::string>& words) {
        std::vector<std::unordered_map<char, int>> letter_counts(target_word.size());
        std::vector<int> total_counts(target_word.size(), 0);

        for (const auto& word : words) {
            for (size_t i = 0; i < word.size(); ++i) {
                letter_counts[i][word[i]]++;
                total_counts[i]++;
            }
        }

        std::vector<std::unordered_map<char, double>> letter_probs(target_word.size());
        for (size_t i = 0; i < letter_counts.size(); ++i) {
            for (const auto& pair : letter_counts[i]) {
                letter_probs[i][pair.first] = static_cast<double>(pair.second) / total_counts[i];
            }
        }

        return letter_probs;
    }

    void update_potential_words() {
        std::vector<std::string> new_potential_words;

        for (const auto& word : potential_words) {
            bool valid = true;

            // Ensure correct letters are in the correct positions
            for (const auto& pos : correct_positions) {
                if (word[pos.first] != pos.second) {
                    valid = false;
                    break;
                }
            }

            // Ensure wrong letters are not present
            for (const auto& letter : guessed_wrong_letters) {
                if (word.find(letter) != std::string::npos) {
                    valid = false;
                    break;
                }
            }

            // Ensure right letters in wrong positions are present but not in those positions
            for (const auto& pair : right_letter_wrong_positions) {
                if (word.find(pair.first) == std::string::npos) {
                    valid = false;
                    break;
                }
                for (const auto& pos : pair.second) {
                    if (word[pos] == pair.first) {
                        valid = false;
                        break;
                    }
                }
                if (!valid) break;
            }

            // Ensure the word does not contain any tried letters
            for (const auto& letter : guessed_wrong_letters) {
                if (word.find(letter) != std::string::npos) {
                    valid = false;
                    break;
                }
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
            score *= 5; // Boost score for common words
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

    std::string get_target_word() const {
        return target_word;
    }

    std::vector<std::pair<std::string, double>> select_word_with_probabilities() {
        update_potential_words();
        std::vector<std::pair<std::string, double>> word_scores;

        std::vector<std::string> starter_words = {"crane", "slate", "trace", "crate", "caret"};
        
        if (guesses == 0) {
            for (const auto& word : word_list) {
                double score = calculate_word_score(word);
                
                // Use std::find with the vector
                if (std::find(starter_words.begin(), starter_words.end(), word) != starter_words.end()) {
                    score *= 50;
                }

                word_scores.emplace_back(word, score);
            }
        } else {
            for (const auto& word : potential_words) {
                double score = calculate_word_score(word);
                double pool_size_factor = 1.0 / std::sqrt(potential_words.size());
                score *= pool_size_factor;
                
                word_scores.emplace_back(word, score);
            }
        }

        auto word_probs = apply_softmax(word_scores);

        std::sort(word_probs.begin(), word_probs.end(),
                [](const std::pair<std::string, double>& a, const std::pair<std::string, double>& b) {
                    return a.second > b.second;
                });

        if (word_probs.size() > 10) {
            word_probs.resize(10);
        }

        return word_probs;
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

    // Cuckoo Filters
    std::vector<CuckooFilter> filter_by_position; // One filter for each position in the word
    CuckooFilter filter_by_letter; // Filter for managing letters
    CuckooFilter filter_wrong_letters; // Filter for managing wrong letters

    std::vector<std::pair<std::string, double>> apply_softmax(const std::vector<std::pair<std::string, double>>& scores) {
        double max_score = -std::numeric_limits<double>::infinity();
        for (const auto& pair : scores) {
            max_score = std::max(max_score, pair.second);
        }

        double sum_exp = 0.0;
        std::vector<std::pair<std::string, double>> probs;
        probs.reserve(scores.size());

        for (const auto& pair : scores) {
            double exp_score = std::exp(pair.second - max_score);
            sum_exp += exp_score;
            probs.emplace_back(pair.first, exp_score);
        }

        // Normalize probabilities
        for (auto& pair : probs) {
            pair.second /= sum_exp;
        }

        return probs;
    }
};

PYBIND11_MODULE(wordle_env, m) {
    py::class_<WordleEnv>(m, "WordleEnv")
        .def(py::init<const std::string&, const std::vector<std::string>&, const std::vector<std::string>&>())
        .def("reset", &WordleEnv::reset)
        .def("step", &WordleEnv::step)
        .def("get_guess_state", &WordleEnv::get_guess_state)
        .def("calculate_letter_frequencies", &WordleEnv::calculate_letter_frequencies)
        .def("update_potential_words", &WordleEnv::update_potential_words)
        .def("calculate_word_score", &WordleEnv::calculate_word_score)
        .def("select_word", &WordleEnv::select_word)
        .def("select_word_with_probabilities", &WordleEnv::select_word_with_probabilities)
        .def("get_target_word", &WordleEnv::get_target_word)
        .def("get_logs", &WordleEnv::get_logs);
}
