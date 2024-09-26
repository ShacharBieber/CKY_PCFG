This code simulates the [CKY](https://en.wikipedia.org/wiki/CYK_algorithm) algorithm using [PCFG](https://en.wikipedia.org/wiki/Probabilistic_context-free_grammar), given in near-CNF form.

For each sentence, the code will print its most probable grammatical tree and its probability, or announce that the sentence is impossible or parse.

## How to Run

1. Download or clone this repository.
2. Run the script in a Python environment:
   
   ```bash
   python cky.py -g <prammar_path> -s <sentences_path> 
3. About the parameters:
    - **-g (--grammar)**: a string representing a path to a file containing grammatical rules. Assuming valid input. An example is provided with the repo (grammar.txt)
    - **-s (--sentences)**: a string representing a path to a file containing (hopefully) grammatical sentences, separated by newlines. An example is provided in the repo (sentences.txt)

   
## Requirements
- Python 3.x
