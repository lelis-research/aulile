import json
import re

json_data = json.load(open("a_bus_iteration_program.json"))

# count = 1
# for entry in json_data["89"]:
#     print("program" + str(count) + " = " + entry["Program"])
#     count += 1

class ProgramParser:
    def parse_program(self, program_str):
        tokens = self.tokenize(program_str)
        parsed_program, _ = self.parse_tokens(tokens)
        return parsed_program

    def tokenize(self, program_str):
        # Step 1: Find all quoted strings and replace them with placeholders
        placeholders = {}
        def replace_with_placeholder(match):
            placeholder = f"__QUOTED{len(placeholders)}__"
            placeholders[placeholder] = match.group(0)
            return placeholder

        program_str = re.sub(r'"[^"]*"', replace_with_placeholder, program_str)

        # Step 2: Remove all commas and periods outside of quotes
        program_str = re.sub(r'(?<!\w)[,.](?!\w)', '', program_str)

        # Step 3: Replace placeholders with the original quoted strings
        for placeholder, quoted_str in placeholders.items():
            program_str = program_str.replace(placeholder, quoted_str)

        # Tokenize the modified string, including arithmetic operators
        tokens = re.findall(r'"[^"]*"|\w+|[\+\-\*/%]|\(|\)|\,|\.', program_str)
        return tokens

    def parse_tokens(self, tokens):
        parsed_program = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in ['.', ',', '(', ')']:
                # Directly add punctuation tokens
                parsed_program.append(token)
                i += 1
            elif token.startswith('"') and token.endswith('"'):
                # Add string literals as is
                parsed_program.append(token)
                i += 1
            elif token.isalpha() or re.match(r'[\w\+\-\*/]', token):
                # Handle function names and variables
                if i + 1 < len(tokens) and tokens[i + 1] == '(':
                    # If the next token is '(', it's a function call
                    function_name = token
                    i += 2  # Move past function name and '('
                    args, new_index = self.parse_arguments(tokens, i)
                    i = new_index
                    parsed_program.append((function_name, args))
                else:
                    # Otherwise, it's a variable or standalone token
                    parsed_program.append(token)
                    i += 1
            else:
                # Unrecognized token
                i += 1
        return parsed_program, i

    def parse_arguments(self, tokens, start_index):
        args = []
        current_arg = []
        i = start_index
        while i < len(tokens) and tokens[i] != ')':
            if tokens[i] == ',':
                if current_arg:
                    args.append(current_arg)
                    current_arg = []
            else:
                current_arg.append(tokens[i])
            i += 1
        if current_arg:
            args.append(current_arg)
        return args, i + 1  # Return position after closing ')'

def remove_commas_periods(obj):
    if isinstance(obj, list):
        return [remove_commas_periods(x) for x in obj if x not in [',', '.']]
    elif isinstance(obj, tuple):
        # Apply the function to each element of the tuple
        return tuple(remove_commas_periods(x) for x in obj)
    else:
        return obj


list_operations = ['concat', 'replace', 'upper', 'lower', 'Substr', 'IndexOf', 'Length', 'CharAt', '+', '-', '*', '/', '%', 'Contain', 'Equal', 'if', 'then', 'else', 'SuffixOf', 'PrefixOf', 'StrToInt', 'IntToStr']

def process_program_stack(program_object, stack_operators, stack_operands):
    for item in program_object:
        if isinstance(item, list):
            # Recursive call for nested structures
            process_program_stack(item, stack_operators, stack_operands)
        elif isinstance(item, tuple):
            # Increment count for the function call
            stack_operators.append(item[0])
            process_program_stack(item[1], stack_operators, stack_operands)
        elif item in list_operations:
            stack_operators.append(item)
        elif item == '(' or item == ')':
            # Increment count for parentheses
            stack_operands.append(item)
        else:
            # Increment count for operands
            stack_operands.append(item)

def process_program_object(program_object):
    node_count = 0
    i = 0
    while i < len(program_object):
        item = program_object[i]
        if isinstance(item, list):
            # Recursive call for nested structures
            node_count += process_program_object(item)
        elif isinstance(item, tuple):
            # Special handling for 'if .. then .. else' construct
            if item[0] == 'if' and i + 4 < len(program_object) and program_object[i + 2] == 'then' and program_object[i + 4] == 'else':
                node_count += 1  # Count the entire 'if .. then .. else' as one node
                node_count += process_program_object(item[1])  # Count the condition
                node_count += process_program_object(program_object[i + 3])  # Count the 'then' part
                node_count += process_program_object(program_object[i + 5])  # Count the 'else' part
                i += 6  # Skip past the entire 'if .. then .. else' construct
            else:
                # Count the operator itself
                node_count += 1
                # Count the arguments of the operator
                node_count += process_program_object(item[1])
        elif item in list_operations:
            # Count the operation
            node_count += 1
        elif isinstance(item, str) and not item in ['(', ')', ',', '.']:
            # Count operands (excluding parentheses, commas, and periods)
            node_count += 1
        else:
            i += 1
            continue  # Skip non-countable items
        i += 1

    return node_count


# Example usage
parser = ProgramParser()

count = 1

for entry in json_data["89"]:
    parser = ProgramParser()
    program_str = entry["Program"]
    try:
        program_object = parser.parse_program(program_str)
        count_then_else = program_str.count('then') + program_str.count('else')
        # remove all the , and . from the program_object list that are not inside the quotes
        program_object = remove_commas_periods(program_object)
        # print(program_object)

        stack_operators = []
        stack_operands = []

        process_program_stack(program_object, stack_operators, stack_operands)
        # print("Operators:", stack_operators)
        # print("Operands:", stack_operands)

        total_nodes = process_program_object(program_object) - count_then_else
        print("Size_" + str(count) + " = " + str(total_nodes))

    except:
        print("Error in program " + str(count))
    count += 1

