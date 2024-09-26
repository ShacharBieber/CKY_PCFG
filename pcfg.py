import copy
import itertools
from ptree import *


def get_combinations(word, char):
    count = word.count(char)
    indexes = ''
    for i in range(len(word)):
        if word[i] == char:
            indexes += str(i)
    returned_combinations = []
    # Length one: (separated for code simplicity)
    for i in indexes:
        returned_combinations.append(word[:int(i)] + word[int(i) + 1:])
    # Length > 1:
    numeral_combinations = []
    for i in range(2, count + 1):
        numeral_combinations.append(list(itertools.combinations(indexes, i)))
    for amount_list in numeral_combinations:
        for combo in amount_list:
            new_list = []
            for i in range(len(combo)):
                if i == 0:
                    new_list.append(word[:int(combo[i])])
                elif i == len(combo) - 1:
                    new_list.append(word[int(combo[i - 1]) + 1:int(combo[i])] + word[int(combo[i]) + 1:])
                else:
                    new_list.append(word[int(combo[i - 1]) + 1:int(combo[i])])
            returned_combinations.append(new_list)
    returned_combinations.append(word)

    # Replacing empty strings with EPSILON:

    for i in range(len(returned_combinations)):
        if returned_combinations[i] == '':
            returned_combinations[i] = 'EPSILON'

    # Combining the sublists somehow created above:
    for item in returned_combinations:
        item_index = returned_combinations.index(item)
        if item:
            if type(item[0]) == list:
                new_list = []
                for sublist in item:
                    new_list += sublist
                returned_combinations[item_index] = new_list

    # Removing doubles:
    final_returned_combinations = []
    for sublist in returned_combinations:
        if sublist not in final_returned_combinations:
            final_returned_combinations.append(sublist)

    return final_returned_combinations


class PRule(object):
    def __init__(self, variable, derivation, probability):
        self.variable = str(variable)
        self.derivation = tuple(derivation)
        self.probability = float(probability)

    def derivation_length(self):
        return len(self.derivation)

    def __repr__(self):
        compact_derivation = " ".join(self.derivation)
        return self.variable + ' -> ' + compact_derivation + ' (' + str(self.probability) + ')'

    def __eq__(self, other):
        try:
            return self.variable == other.variable and self.derivation == other.derivation
        except:
            return False

    def simplified(self):
        simplified_rule = [self.variable, self.derivation]
        return simplified_rule

    def get_node(self):
        key = self.variable
        children = list(self.derivation)
        returned_node = Node(key)
        returned_node.children = children
        return returned_node


class PCFG(object):
    def __init__(self, start_variable='S', rules=None):
        if rules is None:
            self.rules = {}
        else:
            self.rules = copy.deepcopy(rules)  # rules is a dictionary that maps a str object to a list of PRule objects
        # start symbol of the grammar
        self.start = start_variable

    def add_rule(self, rule):
        """
        adds a rule to dictionary of rules in grammar
        """
        if rule.variable not in self.rules:
            self.rules[rule.variable] = []
        self.rules[rule.variable].append(rule)

    def remove_rule(self, rule):
        """
        removes a rule from dictionary of rules in grammar
        """
        try:
            self.rules[rule.variable].remove(rule)
        except KeyError:
            pass
        except ValueError:
            pass

    def to_near_cnf(self):
        """
        creates an equivalent near-CNF grammar
        """
        near_cnf = PCFG(rules=self.rules)

        # Step 1: Adding a new start variable
        S0 = PRule('S0', self.start, 1.0)
        near_cnf.add_rule(S0)
        near_cnf.start = 'S0'

        # Step 2: Removing ɛ (e) rules
        e_rules_list = []
        removed_e_rules_list = []
        for var_index in near_cnf.rules.values():
            for rule in var_index:
                if list(rule.derivation) == ['EPSILON']:
                    e_rules_list.append(rule)
                    removed_e_rules_list.append(rule.simplified())
                    near_cnf.remove_rule(rule)

        while len(e_rules_list) > 0:
            new_rules = []
            for deleted_rule in e_rules_list:
                var = deleted_rule.variable
                # Avoiding Python copying issues:
                current_rules = []
                for i in near_cnf.rules.values():
                    current_rules.append(i)
                for altered_rules_list in current_rules:
                    for altered_rule in altered_rules_list:
                        if var in altered_rule.derivation:
                            new_derivations = get_combinations(list(altered_rule.derivation), var)
                            # Creating the new rules:
                            for new_derivation in new_derivations:
                                var1 = altered_rule.probability
                                var2 = deleted_rule.probability ** (len(altered_rule.derivation) - len(new_derivation))
                                var3 = (1 - deleted_rule.probability) ** (new_derivation.count(var))
                                new_probability = var1 * var2 * var3
                                if not new_derivation:
                                    new_derivation = ('EPSILON',)
                                new_rule = PRule(altered_rule.variable, new_derivation, new_probability)
                                if new_rule.simplified() not in removed_e_rules_list:
                                    new_rules.append(new_rule)

                # Adding the new rules:
                old_rules_list = []
                for i in near_cnf.rules.values():
                    for j in i:
                        old_rules_list.append(j)

                for new_rule in new_rules:
                    for old_rule in old_rules_list:
                        if new_rule.simplified() == old_rule.simplified():
                            near_cnf.remove_rule(old_rule)
                            near_cnf.add_rule(new_rule)
                            break
                    new_rules_list = []
                    for i in near_cnf.rules.values():
                        for j in i:
                            new_rules_list.append(j)
                    if new_rule not in new_rules_list:
                        near_cnf.add_rule(new_rule)

                # Fixing deletion probabilities:
                for deleted_rule_internal in e_rules_list:
                    for rule_group in near_cnf.rules:
                        if rule_group == deleted_rule_internal.variable:
                            for rule in near_cnf.rules[rule_group]:
                                if rule.probability < 1.0:
                                    rule.probability += deleted_rule_internal.probability / len(
                                        near_cnf.rules[rule_group])

            # Recheking for new e rules
            e_rules_list = []
            for var_index in near_cnf.rules.values():
                for rule in var_index:
                    if rule.derivation == ('EPSILON',) and rule.variable != near_cnf.start:
                        e_rules_list.append(rule)
                        removed_e_rules_list.append(rule.simplified())
                        near_cnf.remove_rule(rule)

        variable_naming_counter = 0  # This is the new variable naming count, used for steps 3 & 4.

        # Step 3: Shortening long rules

        rules = near_cnf.get_rules_list()
        long_rules_list = []
        for rule in rules:
            if len(rule.derivation) > 2:
                long_rules_list.append(rule)

        while len(long_rules_list) > 0:
            for rule in long_rules_list:
                # Removing the old rule
                near_cnf.remove_rule(rule)
                # Handling the shortened rule
                short_derivation = (rule.derivation[0], str(variable_naming_counter))
                shortened_rule = PRule(rule.variable, short_derivation, rule.probability)
                near_cnf.add_rule(shortened_rule)
                # Handling the new rule
                new_rule = PRule(str(variable_naming_counter), rule.derivation[1:], 1.0)
                near_cnf.add_rule(new_rule)

                variable_naming_counter += 1
                # Flow control:
                long_rules_list.remove(rule)
                if len(new_rule.derivation) > 2:
                    long_rules_list.append(new_rule)

        # Step 4: removing terminals from binary rules:

        # Getting the binary rules list
        rules = near_cnf.get_rules_list()
        binary_rules = []
        for rule in rules:
            if len(rule.derivation) == 2:
                binary_rules.append(rule)

        # Getting the terminals list
        terminals = []
        variables = list(near_cnf.rules.keys())
        for rule in rules:
            for item in rule.derivation:
                if item not in variables and item not in terminals:
                    terminals.append(item)

        # Terminating the terminals (great song name)
        for rule in binary_rules:

            # If both items in derivations are terminals:
            if rule.derivation[0] in terminals and rule.derivation[1] in terminals:
                rule1 = PRule(str(variable_naming_counter), rule.derivation[0], 1.0)
                variable_naming_counter += 1
                rule2 = PRule(str(variable_naming_counter), rule.derivation[1], 1.0)
                variable_naming_counter += 1
                new_rule = PRule(rule.variable, (rule1.variable, rule2.variable), rule.probability)

                near_cnf.remove_rule(rule)
                near_cnf.add_rule(rule1)
                near_cnf.add_rule(rule2)
                near_cnf.add_rule(new_rule)

            # If the first item in derivation is a terminal
            elif rule.derivation[0] in terminals:
                rule1 = PRule(str(variable_naming_counter), (rule.derivation[0],), 1.0)
                variable_naming_counter += 1
                new_rule = PRule(rule.variable, (rule1.variable, rule.derivation[1]), rule.probability)
                near_cnf.remove_rule(rule)
                near_cnf.add_rule(rule1)
                near_cnf.add_rule(new_rule)

            # If the second item in derivation is a terminal    
            elif rule.derivation[1] in terminals:
                print(rule.derivation[1])
                rule1 = PRule(str(variable_naming_counter), (rule.derivation[1],), 1.0)
                variable_naming_counter += 1
                new_rule = PRule(rule.variable, (rule.derivation[0], rule1.variable), rule.probability)
                near_cnf.remove_rule(rule)
                near_cnf.add_rule(rule1)
                near_cnf.add_rule(new_rule)

        return near_cnf

    def display(self):
        for rule in self.rules.values():
            for actual_rule in rule:
                print(actual_rule)

    def get_rules_list(self):
        returned_list = []
        for rule_group in self.rules.values():
            for rule in rule_group:
                returned_list.append(rule)
        return returned_list

    def cky_parser(self, string):
        """
        Parses the input string given the grammar, using a  version of the CKY algorithm.
        If the string has been generated by the grammar - returns a most likely parse tree for the input string.
        Otherwise - returns None.
        The CFG is given in near-CNF.
        """
        rules = self.rules
        ruleset = self.get_rules_list()
        words = string.split()
        n = len(words)
        # Generating the CKY tables:
        variables_table = []  # The table as we drew it in class.
        nodes_table = []  # Rather than building the syntax tree after filling the table, I kept another table of nodes.
        # With this table, the tree is built while filling the table. All possible trees are built along the way.

        for i in range(0, n + 1):
            variables_table.append([])
            nodes_table.append([])
            for j in range(0, n + 1):
                variables_table[i].append([])
                nodes_table[i].append([])

        # Parsing:
        for i in range(0, n + 1):
            for j in range(n, -1, -1):
                if i > j:
                    # Handling the leaves (the secondary-upper diagonal)
                    if len(words[j:i]) == 1:
                        for variable in rules:
                            for rule in rules[variable]:
                                if str(words[j:i][0]) in rule.derivation:
                                    variables_table[j][i].append(rule.variable)
                                    nodes_table[j][i].append((rule.get_node(), rule.probability))

                        # Unit rules handling:
                        changed = True
                        while changed:
                            changed = False
                            for rule in ruleset:
                                for item in nodes_table[j][i]:
                                    if rule.derivation == (item[0].key,):
                                        new_node = Node(rule.variable)
                                        new_node.children = [item[0]]
                                        new_item = (new_node, rule.probability * item[1])
                                        if new_item[0] not in [i[0] for i in nodes_table[j][i]]:
                                            nodes_table[j][i].append(new_item)
                                            variables_table[j][i].append(rule.variable)
                                            changed = True
                    else:  # Non-leaves
                        for k in range(j + 1, i):
                            first_half = variables_table[j][k]
                            second_half = variables_table[k][i]
                            for variable1 in first_half:
                                for variable2 in second_half:
                                    for rule in rules:
                                        for actual_rule in rules[rule]:
                                            if (variable1, variable2) == actual_rule.derivation:
                                                if actual_rule.variable not in variables_table[j][i]:
                                                    variables_table[j][i].append(actual_rule.variable)
                                                node_key = actual_rule.variable
                                                new_node = Node(node_key)
                                                new_node.children = [0, 1]
                                                if len(nodes_table[j][k]) > 1:
                                                    max_probability_0 = 0
                                                    for node in nodes_table[j][k]:
                                                        if (node[0].key == actual_rule.derivation[0]
                                                                and node[1] > max_probability_0):
                                                            new_node.children[0] = node[0]
                                                            max_probability_0 = node[1]
                                                else:
                                                    new_node.children[0] = nodes_table[j][k][0][0]
                                                    max_probability_0 = nodes_table[j][k][0][1]

                                                if len(nodes_table[k][i]) > 1:
                                                    max_probability_1 = 0
                                                    for node in nodes_table[k][i]:
                                                        if (node[0].key == actual_rule.derivation[1]
                                                                and node[1] > max_probability_1):
                                                            new_node.children[1] = node[0]
                                                            max_probability_1 = node[1]
                                                else:
                                                    new_node.children[1] = nodes_table[k][i][0][0]
                                                    max_probability_1 = nodes_table[j][k][0][1]

                                                nodes_table[j][i].append(
                                                    (
                                                        new_node,
                                                        max_probability_0 * max_probability_1 * actual_rule.probability
                                                    )
                                                )
                        # Unit rules handling
                        changed = True
                        while changed:
                            changed = False
                            for rule in ruleset:
                                for item in nodes_table[j][i]:
                                    if rule.derivation == (item[0].key,):
                                        new_node = Node(rule.variable)
                                        new_node.children = [item[0]]
                                        new_item = (new_node, rule.probability * item[1])
                                        if new_item[0] not in [i[0] for i in nodes_table[j][i]]:
                                            nodes_table[j][i].append(new_item)
                                            variables_table[j][i].append(rule.variable)
                                            changed = True

        if self.start not in variables_table[0][n]:
            return None
        else:
            for root in nodes_table[0][n]:
                if root[0].key == self.start:
                    return PTree(root[0], root[1])
        return PTree()

    def is_valid_grammar(self):
        """
        validates that the grammar is legal (meaning - the rules of each variable sum to 1)
        """
        alpha = 0.001
        sums = {}
        for var in self.rules:
            sums[var] = 0
            for rule in self.rules[var]:
                sums[var] += rule.probability
        for var in sums:
            if abs(sums[var] - 1) > alpha:
                print('problem with ', var, ': ', sums[var])
                print(self.rules[var])
                return False
        return True
