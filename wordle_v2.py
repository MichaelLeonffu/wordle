# wordle_v2.py TODO: Maybe write something here!

# Starts with dictonary and uses regex to find the words that match.

from os import path
import re
import pprint

# All remaining letters
letters = list("qwtadfhjkzxcvb")

# Known positions, use spaces for unknown
green_known = " a  h"

# Rules (yellow letters in that column.)
rules = [
    '',
    '',
    'c',
    'h',
    ''
]

yellow_known = list(set("".join(rules)))

# Load dictionary
path_to_dictionary = 'data/filtered_dictionary'
use_dictionary = True or path.exists(path_to_dictionary)
dictionary = []

if use_dictionary:
    with open(path_to_dictionary) as f:
        dictionary = f.read().split('\n')
    print("{:>8} loaded from dictionary at {}".format(len(dictionary), path_to_dictionary))

# Create regex string

# Returns the regex for a single character given by the pos
def char_regex(pos):

    # Green: known letter is in that position.
    if green_known[pos] != ' ':
        return green_known[pos]

    # Yellow: yellow known letters cannot be in that position.
    elif rules[pos] != '':
        return "[{}]".format("".join(set(letters) - set(rules[pos])))

    # Blank: any letter in the letter bank.
    else:
        return "[{}]".format("".join(letters))

# For each of the positions in the final letter create regex
regex_exp = "".join([char_regex(i) for i in range(0, 5)])
print("Generated regex: ", regex_exp)


# Use regex
result = re.findall(regex_exp, "\n".join(dictionary))

# Filter out words which don't contain all the known letters
result = list(filter(lambda word: all(letter in word for letter in yellow_known), result))


print("Found {} words".format(len(list(result))))
pprint.pprint(result)


# Helper
def generate_dict():
    with open('sample_dictionary') as f_in:
        with open('data/filtered_dictionary', 'x') as f_out:
            for line in f_in:
                line = line.strip()
                if len(line) == 5:
                    # Make sure all letters are in english alpha lower cased
                    if line.isalpha() and line.islower():
                        f_out.write(line + '\n')