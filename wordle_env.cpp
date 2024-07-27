#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <random>

namespace py = pybind11;

class WordleEnv {
public:
    static const int PARTIAL_REWARD = 6;
    static const int RIGHT_REWARD = 10;
    static const int WRONG_PENALTY = -3;
    static const int MAX_GUESSES = 6;

    WordleEnv(const std::string& target_word, const std::vector<std::string>& word_list)
        : target_word(target_word), word_list(word_list) {
        reset();
    }

    void reset() {
        state = {0, 0, 0, 0, 0};
        guesses = 0;
        guessed_wrong_letters.clear();
        right_letter_wrong_positions.clear();
        potential_words = word_list;
        calculate_letter_frequencies();
    }

    std::vector<int> get_guess_state(const std::string& word) {
        std::vector<int> state;
        for (size_t i = 0; i < word.size(); ++i) {
            if (word[i] == target_word[i]) {
                state.push_back(2);  // Correct letter in the correct position
            } else if (target_word.find(word[i]) != std::string::npos) {
                state.push_back(1);  // Correct letter in the wrong position
                right_letter_wrong_positions[word[i]].push_back(i);
            } else {
                state.push_back(-1);  // Incorrect letter
                guessed_wrong_letters.insert(word[i]);
            }
        }
        return state;
    }

    void calculate_letter_frequencies() {
        letter_probs.clear();
        std::vector<std::unordered_map<char, int>> letter_counts(5);
        std::vector<int> total_counts(5, 0);

        for (const auto& word : potential_words) {
            for (size_t i = 0; i < 5; ++i) {
                char c = word[i];
                letter_counts[i][c]++;
                total_counts[i]++;
            }
        }

        for (size_t i = 0; i < 5; ++i) {
            std::unordered_map<char, double> probs;
            for (const auto& p : letter_counts[i]) {
                probs[p.first] = static_cast<double>(p.second) / total_counts[i];
            }
            letter_probs.push_back(probs);
        }
    }

    void update_potential_words() {
        auto new_potential_words = potential_words;

        // Filter based on correct positions
        for (const auto& cp : correct_positions) {
            new_potential_words.erase(std::remove_if(new_potential_words.begin(), new_potential_words.end(),
                                                     [&](const std::string& word) { return word[cp.second] != cp.first; }),
                                      new_potential_words.end());
        }

        // Filter out words with guessed wrong letters
        for (const char c : guessed_wrong_letters) {
            new_potential_words.erase(std::remove_if(new_potential_words.begin(), new_potential_words.end(),
                                                     [&](const std::string& word) { return word.find(c) != std::string::npos; }),
                                      new_potential_words.end());
        }

        // Filter out words with right letters in wrong positions
        for (const auto& rlwp : right_letter_wrong_positions) {
            for (const int pos : rlwp.second) {
                new_potential_words.erase(std::remove_if(new_potential_words.begin(), new_potential_words.end(),
                                                         [&](const std::string& word) { return word[pos] == rlwp.first; }),
                                          new_potential_words.end());
            }
        }

        potential_words = new_potential_words;
        calculate_letter_frequencies();
    }

    double calculate_word_score(const std::string& word) {
        double score = 1.0;
        for (size_t i = 0; i < word.size(); ++i) {
            score *= letter_probs[i].count(word[i]) ? letter_probs[i][word[i]] : 1e-6;  // Use a small value for unseen letters
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

        std::sort(word_scores.begin(), word_scores.end(), [](const auto& a, const auto& b) { return a.second > b.second; });

        std::vector<std::string> top_10_words;
        for (size_t i = 0; i < 10 && i < word_scores.size(); ++i) {
            top_10_words.push_back(word_scores[i].first);
        }
        return top_10_words;
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
            } else if (target_word.find(guessed_word[i]) != std::string::npos) {
                reward += PARTIAL_REWARD;
            } else {
                reward += WRONG_PENALTY;
            }
        }

        if (guessed_word == target_word || guesses >= MAX_GUESSES) {
            done = true;
        }

        state = new_state;
        return std::make_tuple(new_state, reward, done);
    }

private:
    std::string target_word;
    std::vector<std::string> word_list;
    std::vector<std::string> potential_words;
    std::vector<int> state;
    int guesses;
    std::unordered_set<char> guessed_wrong_letters;
    std::unordered_map<char, std::vector<int>> right_letter_wrong_positions;
    std::unordered_map<char, int> correct_positions;
    std::vector<std::unordered_map<char, double>> letter_probs;
};

PYBIND11_MODULE(wordle_env, m) {
    py::class_<WordleEnv>(m, "WordleEnv")
        .def(py::init<const std::string&, const std::vector<std::string>&>())
        .def("reset", &WordleEnv::reset)
        .def("get_guess_state", &WordleEnv::get_guess_state)
        .def("calculate_letter_frequencies", &WordleEnv::calculate_letter_frequencies)
        .def("update_potential_words", &WordleEnv::update_potential_words)
        .def("calculate_word_score", &WordleEnv::calculate_word_score)
        .def("select_word", &WordleEnv::select_word)
        .def("step", &WordleEnv::step);
};