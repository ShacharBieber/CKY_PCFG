This code simulates the [CKY](https://en.wikipedia.org/wiki/CYK_algorithm) algorithm using [PCFG](https://en.wikipedia.org/wiki/Probabilistic_context-free_grammar), given in near-CNF form.

For each sentence, the code will print its most probable grammatical tree and its probability, or announce that the sentence is impossible or parse.

## How to Run

1. Download or clone this repository.
2. Run the script in a Python environment:
   
   ```bash
   python weaver_solver.py -s <source_word> -t <target_word> -l <word_length> -p <custom_dict_path>
4. About the parameters:
    - **-g (--grammar)**: a string representing a path to a file containing grammatical rules. Assuming valid input.
    - **-s (--sentences)**: a string representing a path to a file containing (hopefully) grammatical sentences, separated by newlines.

   
## Requirements
- Python 3.x
