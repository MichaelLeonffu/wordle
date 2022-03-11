# reversle.py TODO: Maybe write something here!

# Starts with a share of a wrodle and generates the guesses

from os import path
import re
import pprint
# import json
import pickle
import bz2
import itertools

wordle_const = {
    # letter to emoji
    'g': ['🟩'],
    'y': ['🟨'],
    'b': ['⬛', '⬜'],

    # emoji to letter
    '🟩': 'g',
    '🟨': 'y',
    '⬛': 'b',
    '⬜': 'b',
}

# Load dictionary
path_to_dictionary = './data/filtered_dictionary'
use_dictionary = True or path.exists(path_to_dictionary)
dictionary = []

if use_dictionary:
    with open(path_to_dictionary) as f:
        dictionary = f.read().split('\n')
    print("{:>8} loaded from dictionary at {}".format(len(dictionary), path_to_dictionary))


# Load linking
path_to_linking = './data/linking.pkl'
path.exists(path_to_linking)
linking = {}

if path.exists(path_to_linking):
    with bz2.open(path_to_linking, 'rb') as f:
        # linking = json.load(f)
        linking = pickle.load(f)
    print("{:>8} loaded from linking at {}".format(len(linking), path_to_linking))

else:

    print("No linking file found... generating...")

    # Generate word linking
    # dictionary = dictionary[:100]
    linking = {d: {} for d in dictionary}

    # Set this value if you know the green
    # linking = {'swell': {}}

    # total size
    total_size = len(dictionary)
    tenth = (total_size//10)

    for i, key in enumerate(linking):

        # print progress
        if i % tenth == 0:
            print("{:>6} of {:>6}".format(i, total_size))

        # Converts word to symbol
        green_word = key
        def word_to_symbol(word):
            # Run this in context of a green word

            # Error
            if len(word) != 5:
                print("word_to_symbol error: word not length 5")
                return "error"

            basic_symbol = "".join(['g' if word[i] == letter else 'y' if word[i] in green_word else 'b' for i, letter in enumerate(green_word)])

            # Basic_symbol needs to be corrected sometimes
            # Anna Li found that the word 'emote' and the green word 'lapse'
            # yeilds 'bbbbg' but basic_symbol is 'ybbbg'
            # TODO: make this better
            # TODO fix this case:
            # - 'maims' and 'comet' should yeild 'ybbyb' but it gives 'ybbyb'

            if 'g' in basic_symbol and 'y' in basic_symbol:
                all_found_g_position = [i for i in range(0, len(green_word)) if basic_symbol[i] == 'g']
                all_found_y_position = [i for i in range(0, len(green_word)) if basic_symbol[i] == 'y']

                flip_pos = []
                for g_pos in all_found_g_position:
                    green_letter = green_word[g_pos]
                    for y_pos in all_found_y_position:

                        # A yellow and green exist for same letter
                        if green_letter == word[y_pos]:
                            if not green_word.count(green_word[g_pos]) > 1:
                                flip_pos.append(y_pos)

                # Flip all y in flip_pos to b
                for pos in flip_pos:
                    list_basic_symbol = list(basic_symbol)
                    list_basic_symbol[pos] = 'b'
                    basic_symbol = "".join(list_basic_symbol)

            return basic_symbol

        for word in dictionary:
            symbol = word_to_symbol(word)

            # Optimization: skip all `bbbbb` and `ggggg`
            # if symbol == 'bbbbb' or symbol == 'ggggg':
            #     continue

            if symbol not in linking[key]:
                linking[key][symbol] = []
            linking[key][symbol].append(word)

    print("Done making linking!")

    # Save linking
    with bz2.open(path_to_linking, 'wb') as f:
        # f.write(json.dumps(linking))
        pickle.dump(linking, f)
    with open("./not_compressed.pkl", 'wb') as f:
        pickle.dump(linking, f)

    print("{:>8} saved linking at {}".format(len(linking), path_to_linking))

# Minimize solution space
# First generate all particular solutions
# - guesses for each row that satisfies the rules
# Find the particular solution which:
# - reuses as few blacked words
# - too many repeated letters
# - uses the most unique vowels
# - total diversity of letters (a.k.a unique black letters)
def best_green_solution(green_word, rules, linking):

    # All row of guesses
    row_guesses = [linking[green_word][rule] if rule in linking[green_word] else [] for rule in rules]

    print("Row guesses size: ", [len(row) for row in row_guesses])


    # Generate all combinations of row guesses
    particular_solutions = {solution: {} for solution in itertools.product(*row_guesses)}

    # Rate each solution
    green_letters = set(green_word)
    vowels = set("aeuioy")

    print("{:>8} Particular solutions to rank".format(len(particular_solutions)))

    # total size
    total_size = len(particular_solutions)
    tenth = (total_size//10)
    i = 0

    print("{:>8} Particular solutions to rate".format(total_size))
    for solution_key, solution in particular_solutions.items():

        # print progress
        if i % tenth == 0:
            print("{:>8} of {:>8}".format(i, total_size))
        i += 1

        # solution_key will be in the form of ('range', 'louis', 'maple')
        # solution is the dict it points to
        solution_set = set("".join(solution_key))

        # Number of reused blacked letters
        

        # Number of unique used vowels
        solution['unique_used_vowels'] = len(vowels) - len(vowels - solution_set)

        # Total unique letters
        solution['unique_letters'] = len(solution_set)


    # Minimize and Maximize ratings
    # - Numer of reused blacked letters
    # - Number of repeated letters
    # + Numer of unique used vowels
    # + Total unique letters
    scores = [
        {
            'field': 'unique_used_vowels',
            'method': max,
        },
        {
            'field': 'unique_letters',
            'method': max,
        }
    ]

    # Keeps track of best solution
    best_solutions = []

    # Initalize scores
    for score in scores:
        if score['method'] == max:
            score['score'] = 0
        else:
            score['score'] = 1000

    # pprint.pprint(particular_solutions)

    i = 0
    print("{:>8} Particular solutions to rank".format(total_size))
    for solution_key, solution in particular_solutions.items():

        # Print progress
        if i % tenth == 0:
            print("{:>8} of {:>8}".format(i, total_size))
        i += 1
        
        # If a new best solution is found
        updated = False
        same_as_best = True

        for score in scores:
            method = score['method']
            new_score = method(solution[score['field']], score['score'])

            # If the new score isn't the same as the current, then it's a new best
            if new_score != score['score']:
                score['score'] = new_score
                updated = True

            if solution[score['field']] != score['score']:
                same_as_best = False

        # Equal to best found
        if same_as_best:
            best_solutions.append(solution_key)

        # New best found
        if updated:
            best_solutions = []
            best_solutions.append(solution_key)

    # Group best solutions per row
    best_solutions_dict = {solution[0]: {} for solution in best_solutions}

    return (best_solutions, scores)


# Interactively check for potential wordle games
while True:

    known_green_word = ""
    print("If you know the green word type it else press enter:")
    known_green_word = input()

    # Some light validation
    known_green_word = known_green_word.lower()
    if len(known_green_word) != 5 or len(set(known_green_word) - set("qwertyuiopasdfghjklzxcvbnm")) > 0 or known_green_word not in linking:
        print("Word failed validation.")
        known_green_word = ""


    print("Enter your discord share:")
    wordle_share_discord = []
    while True:
        try:
            line = input()
        except EOFError:
            print("Accepted!")
            break
        if line == "":
            print("Accepted!")
            break
        wordle_share_discord.append(line)

    # Convert to rules: from emojis to letters
    rules = []
    try:
        rules = ["".join([wordle_const[letter] for letter in row]) for row in wordle_share_discord]
    except KeyError:
        print("Bad key! Try again")
        continue

    print("rules:")
    pprint.pprint(rules)

    # Find all linkings which satisfy rule
    valid_green_words = []
    if known_green_word == "":
        for green_word in linking:
            if all(rule in linking[green_word] for rule in rules):
                valid_green_words.append(green_word)
        
         # Report number of green words
        print("{:>8} many valid green_words.".format(len(valid_green_words)))
    else:
        valid_green_words.append(known_green_word)

    # Minimize solution space
    # Find the solution which reuses as little blacked letters


    # Print solutions

    def print_with_color(word, rule):
        GREEN_COLOR = "\u001b[32m"
        RED_COLOR = "\u001b[31m"
        CYAN_COLOR = "\u001b[36m"
        RESET = "\033[0m"
        mapping = {
            'g': GREEN_COLOR,
            'y': CYAN_COLOR,
            'b': RED_COLOR,
        }
        return " ".join(mapping[r] + word[i] for i, r in enumerate(rule)) + RESET

    print("One solution is: ")
    # Show one potential solution
    for rule in rules:
        if rule not in linking[valid_green_words[0]]:
            print("   0 many solutions for: {}".format(rule))
            continue    
        sol = linking[valid_green_words[0]][rule]
        print("{:>4} many solutions one is: {}".format(len(sol), print_with_color(sol[0], rule)))

    # print("The best solution is: ")
    # # Show the best solution
    # solution, score = best_green_solution('lapse', ['bbbbg', 'yyybb', 'bggyg', 'ggggg'], linking)
    # for rule in rules:
    #     if rule not in linking[solution[-1]]:
    #         print("   0 many solutions for: {}".format(rule))
    #         continue    
    #     sol = linking[solution[-1]][rule]
    #     print("{:>4} many solutions one is: {}".format(len(sol), print_with_color(sol[0], rule)))

    # pprint.pprint(best_green_solution(valid_green_words[0], rules, linking))

    print()
