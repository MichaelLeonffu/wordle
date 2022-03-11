# wordle.py TODO: Maybe write something here!
# Starts by generating all permutations (with replacement), cartisian product
# of all letters. Then filters out generated words to reduce.

from itertools import product
from os import path
import pprint

# All remaining letters
letters = list("qwetuioadfghjlzxvnm")

# Known positions, use spaces for unknown
green_known = " o  o"

# Rules (yellow letters in that column.)
rules = [
    '',
    '',
    'o',
    'n',
    ''
]

# Load dictionary
path_to_dictionary = 'sample_dictionary.txt'
use_dictionary = False and path.exists(path_to_dictionary)
dictionary = []

if use_dictionary:
    with open(path_to_dictionary) as f:
        dictionary = f.read().split('\n')
    print("{:>8} loaded from dictionary at {}".format(len(dictionary), path_to_dictionary))


# Generate all words
words = ["".join(word) for word in product(letters, repeat=5)]
print("{:>8} words permutations generated".format(len(words)))


# Product creates no duplicate words
# Remove duplicate words
# words = list(set(words))
# print("{:>8} words after removing duplicates".format(len(words)))


# Keep words that include green known letters
words = list(filter(lambda word: all(letter == " " or letter == word[i] for i, letter in enumerate(green_known)), words))
print("{:>8} words after removing words that do not contain the green letters".format(len(words)))


# Known letters
yellow_known = list(set("".join(rules)))

# Keep words that include all the needed letters
words = list(filter(lambda word: all(letter in word for letter in yellow_known), words))
print("{:>8} words after removing words that do not contain all of the yellow letters".format(len(words)))


# Remove words that don't follow rules
words = list(filter(lambda word: all(word[i] not in rule for i, rule in enumerate(rules)), words))
print("{:>8} words after removing words that do not follow yellow letter rules".format(len(words)))

# Remove all words that aren't in the dictionary
if use_dictionary:
    words_in_dictionary = list(set(words).intersection(set(dictionary)))

    # Only keep if there is at least one correct word found
    if len(words_in_dictionary) > 0:
        words = words_in_dictionary
    print("{:>8} words after removing words that are not in dictionary".format(len(words)))

# Results
words.sort()
pprint.pprint(words)
print(len(list(words)))


# Helper
def generate_dict():
    with open('sample_dictionary.txt') as f_in:
        with open('data/filtered_dictionary.txt', 'x') as f_out:
            for line in f_in:
                line = line.strip()
                if len(line) == 5:
                    # Make sure all letters are in english alpha lower cased
                    if line.isalpha() and line.islower():
                        f_out.write(line + '\n')