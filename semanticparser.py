class TokenType:  # JSON token types
    LBRACE = '{'  # '{'
    RBRACE = '}'  # '}'
    LBRACKET = '['  # '['
    RBRACKET = ']'  # ']'
    COMMA = ','  # ','
    COLON = ':'  # ':'
    STRING = 'STRING'  # strings
    NUMBER = 'NUMBER'  # numeric values
    BOOL_TRUE = 'BOOL_TRUE'  # true
    BOOL_FALSE = 'BOOL_FALSE'  # false
    NULL = 'NULL'  # null
    EOF = 'EOF'  # end of input

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.parse = value

    def __repr__(self):
        if self.parse is not None:
            return f"<{self.type}, {self.parse}>"
        return f"<{self.type}>"

class Node:
    def __init__(self, label=None, is_leaf=False, token_type=None):
        self.label = label
        self.children = []
        self.is_leaf = is_leaf
        self.token_type = token_type  # token type to distinguish terminal symbols

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self, file, depth=0):
        indent = "    " * (depth)
        if self.is_leaf:  # terminal nodes like STRING, NUMBER, etc.
            file.write(f"{indent}{self.label}\n")
        else:
            file.write(f"{indent}{self.label}\n")  # internal nodes (e.g., value, dict, list)
            for child in self.children:
                child.print_tree(file,depth + 1)  
        

class Parser:
    def __init__(self, token_file):
        self.tokens = self.read_tokens(token_file)
        self.current_index = 0
        self.current_token = self.tokens[0] if self.tokens else None

    # have to create token objects somehow, so we do it quickly with this method
    # tokens are read from the "sample input" file which contains scanner output
    def read_tokens(self, token_file):
        tokens = []
        with open(token_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('<') and line.endswith('>'):
                    parts = line[1:-1].split(', ', 1)
                    tokenType = parts[0]
                    tokenValue = parts[1] if len(parts) > 1 else None
                    tokens.append(Token(tokenType, tokenValue))
        return tokens

    def get_next_token(self):
        self.current_index += 1
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
        else:
            self.current_token = Token(TokenType.EOF)

    # for the AST, the eat method is modified since we don't want terminals
    # instead of adding terminals to the tree, skip over them
    def eat(self):
        self.get_next_token()

    # parse method is also modified from Part 2 since we're outputting an AST
    # we can now just directly return the result of whatever production we're
    # using since we want to cut unnecessary information from the parse tree
    # this leaves us with what we need for our AST and nothing in between
    def parse(self):
        
        if self.current_token.type == TokenType.LBRACE:
            return self.dict()
        elif self.current_token.type == TokenType.LBRACKET:
            return self.list()
        
        # if it's not not a dict or a list: 
        # we can just make leaf node directly out of whatever type the token is
        elif self.current_token.type in {
            TokenType.STRING,
            TokenType.NUMBER,
            TokenType.BOOL_TRUE,
            TokenType.BOOL_FALSE,
            TokenType.NULL,
        }:
            return self.leaf_node(self.current_token.type)
        
    def dict(self):
        node = Node(label="dict")
        self.eat()
        seen_keys = []

        # eat as many pairs as necessary until we close the dict
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.STRING:
                key = self.current_token.parse
                
                # checking for Type 5 Error: No Duplicate Keys in Dictionary
                if key in seen_keys:
                    errors.append(f"Type 5 Error: Duplicate key '{key}' at Token {self.current_index}")
                else:
                    seen_keys.append(key)

            node.add_child(self.pair())
            if self.current_token.type == TokenType.COMMA:
                self.eat()

        self.eat()
        return node

    def pair(self):
        node = Node(label="pair")
        if self.current_token.type == TokenType.STRING:
            key_value = self.current_token.parse

            # checking for Type 4 Error: Reserved Words as Dictionary Key
            if self.current_token.parse == "true" or self.current_token.parse == "false" or self.current_token.parse == "null":
                errors.append(f"Type 4 Error: Reserved word '{self.current_token.parse}' cannot be a dictionary key at Token {self.current_index}")
            
            # checking for Type 2 Error: Empty key
            # either null or just completely blank
            if not key_value or all(char == ' ' for char in key_value):
                errors.append(f"Type 2 Error: Empty dictionary key at Token {self.current_index}")

            node.add_child(self.parse())  # adds the STRING key
            self.eat() 
            node.add_child(self.parse())  # adds the value node
        else:
            self.get_next_token()
        return node

    def list(self):
        node = Node(label="list")
        self.eat()
        first_type = None  # used to track the type to be stored in our list (i.e STRING, NUMBER, etc)
        incorrect_types = False

        # eat as many pairs as necessary until we close the dict
        while self.current_token.type != TokenType.RBRACKET:
            
            # checking for Type 6 Error: Consistent Types for List Elements
            if first_type is None:  
                first_type = self.current_token.type # set the type of the list to its first element's type
            elif self.current_token.type != first_type and not incorrect_types:
                errors.append(f"Type 6 Error: Inconsistent types in list at Token {self.current_index}. Expected {first_type} and got {self.current_token.type}.")
                incorrect_types = True  # boolean to prevent spamming errors list with this error
            
            node.add_child(self.parse())
            if self.current_token.type == TokenType.COMMA:
                self.eat()

        self.eat()
        return node

    def leaf_node(self, token_type):
        label = self.current_token.parse
        node = Node(label=label, is_leaf=True, token_type=token_type)

        # checking for Type 1 Error: Invalid Decimal Numbers
        if token_type == TokenType.NUMBER and '.' in label:
            parts = label.split('.')
            if len(parts) != 2 or (not parts[0].isdigit() and '-' not in parts[0]) or not parts[1].isdigit():
                    errors.append(f"Type 1 Error: Invalid decimal number '{label}'")
            
            # accounting for the case where we have a number like 00.14159 or something. INVALID!
            elif len(parts[0]) > 1 and all(char == '0' for char in parts[0]):
                errors.append(f"Type 1 Error: Invalid decimal number '{label}'")
        
        # checking for Type 3 Error: Invalid Numbers
        if token_type == TokenType.NUMBER:
            if label.startswith('0') and len(label) > 1 and '.' not in label:
                errors.append(f"Type 3 Error: Leading zeros in number '{label}'")
            elif label.startswith('+') and "e" not in label.lower(): # checking for both e and E 
                errors.append(f"Type 3 Error: Leading '+' in number '{label}'")
        
        # checking for Type 7 Error: Reserved Words as Strings
        if token_type == TokenType.STRING and self.current_token.parse in ["true", "false"]:
            errors.append(f"Type 7 Error: Reserved word '{self.current_token.parse}' cannot be used as a string at Token {self.current_index}")

        self.eat()
        return node


if __name__ == "__main__":
    global errors
    errors = []
    token_file = "sample inputs semantic parser/input8.txt"  # input token file generated by scanner
    error_output_file = "errors.txt"
    output_file = "output.txt"
    
    parser = Parser(token_file)
    parse_tree = parser.parse()
    
    with open(error_output_file, 'w') as file:
        file.write("ERROR LIST:\n")
        for error in errors:
            file.write(error + "\n")
    
    # printing errors in addition to providing a file
    # contingency just in case since printing is mentioned in the rubric
    for error in errors:
        print(error)
    
    if(len(errors) == 0): # create AST only if there are no errors
        with open(output_file, 'w') as file:
            parse_tree.print_tree(file)
    else: # errors found!
        open(output_file, 'w').close() # erase content of output file in case a previous trial had AST output
        
