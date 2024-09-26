from pcfg import *
import argparse


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-g',
        '--grammar',
        type=str,
        default=None,
        help='Path to a file containing grammatical rules. Assuming valid input.'
    )
    parser.add_argument(
        '-s',
        '--sentences',
        type=str,
        default=None,
        help='Path to a file containing (hopefully) grammatical sentences, separated by newlines.'
    )
    return parser.parse_args()


def main():
    parsed_arguments = parse_arguments()
    grammar_file = parsed_arguments.grammar
    sentences_file = parsed_arguments.sentences
    with open(grammar_file) as f:
        content = f.readlines()
    lines = [i.strip() for i in content]

    # Initializing the PCFG
    ruleset = PCFG()
    is_lexicon = 0
    for line in lines:
        if line == '# Lexicon #':
            is_lexicon = 1
        if line.startswith('#') or line == '':
            continue
        else:
            line_list = line.split()
            if is_lexicon == 0:  # Handling the non-lexicon rules
                if line_list[0] == '!start_variable':
                    ruleset.start_variable = line_list[1]
                else:
                    variable = line_list[0]
                    probability = float(line_list[-1][1:-1])
                    derivation = ()
                    for i in range(2, len(line_list)-1):
                        derivation += (line_list[i],)
                    rule = PRule(variable, derivation, probability)
                    ruleset.add_rule(rule)
                    
            if is_lexicon == 1:  # Handling the lexicon rules
                variable = line_list[0]
                split_line = line.split("|")
                for rule in split_line:
                    rule_line = rule.split()
                    if rule_line[1] == '->':
                        rule_line = rule_line[2:]
                    derivation = rule_line[0][1:-1]
                    probability = float(rule_line[1][1:-1])
                    rule = PRule(variable, (derivation,), probability)
                    ruleset.add_rule(rule)
                    
    ruleset = ruleset.to_near_cnf()

    with open(sentences_file) as f:
        content = f.readlines()
    raw_sentences = [i.strip() for i in content if i != '']
    sentences = [sentence for sentence in raw_sentences if sentence != '']
    
    for sentence in sentences:
        tree = ruleset.cky_parser(sentence)
        if tree:
            print(f"Found the following tree with probability {tree.probability}")
            print(tree.root.children[0])
        else:
            print(f"Could not find a tree for the following sentence: {sentence}")

            
if __name__ == "__main__":
    main()
