# I would like to credit the supplementary parser provided on Brightspace (2024) for the CSCI 2115 Fall24 class.
# The code provided in that example was referenced heavily during the creation of this parser. Thank you!

# TokenType class taken from Part1 Scanner to help identify scanner output tokens
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

# Token class taken from Part1 Scanner to help identify scanner output tokens
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
        self.label = label # value of the node
        self.children = [] # child nodes of a node on the tree (leaves should have an empty list)
        self.is_leaf = is_leaf
        self.token_type = token_type  # token type to distinguish terminal symbols

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self, file, depth=0):
        indent = "    " * (depth)
        if self.is_leaf:  # terminal nodes like STRING, NUMBER, etc.
            file.write(f"{indent}{self.token_type}: {self.label}\n")
        else:
            file.write(f"{indent}{self.label}\n")  # internal nodes (e.g., value, dict, list)
            for child in self.children:
                child.print_tree(file,depth + 1)  
        

class Parser:
    def __init__(self, token_file):
        self.tokens = self.read_tokens(token_file)
        self.current_index = 0
        self.current_token = self.tokens[0] if self.tokens else None

    # have to read tokens somehow, so we do it quickly with this method
    # tokens are read from the "sample input" file which contains scanner output
    def read_tokens(self, token_file):
        tokens = []
        with open(token_file, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("<") and line.endswith(">"):
                    parts = line[1:-1].split(", ", 1)
                    tokenType = parts[0]
                    tokenValue = parts[1] if len(parts) > 1 else None
                    tokens.append(Token(tokenType, tokenValue))
        return tokens

    # start processing the next token in the stream
    def get_next_token(self):
        self.current_index += 1
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
        else:
            self.current_token = Token(TokenType.EOF)

    def eat(self, token_type, parent_node):
        if self.current_token.type == token_type:
            # add the current node to the parent node, we can assign leaf status later
            # setting leaf status to false now allows us to properly represent the "{", "}", ",", ":" etc elements in the tree
            label = self.current_token.type
            parent_node.add_child(Node(label=label, is_leaf=False, token_type=token_type))
            self.get_next_token()
        else:
            errors.append(f"Expected {token_type} but got {self.current_token.type} at Token {self.current_index}")
            self.get_next_token()

    def parse(self):
        node = Node()  # create a placeholder node, content to be decided by token!
        
        # THE FOLLOWING CONDITIONS CHECK FOR NODES THAT FALL UNDER "value"
        # IN THE PROVIDED JSON GRAMMAR
        # NOTE: "pair" is implicitly handled here since it falls under "dict"
        if self.current_token.type == TokenType.LBRACE:
            node.label = "value"
            node.add_child(self.dict())
        elif self.current_token.type == TokenType.LBRACKET:
            node.label = "value"
            node.add_child(self.list())
        elif self.current_token.type == TokenType.STRING:
            node.label = "value"
            node.add_child(self.leaf_node(TokenType.STRING))
        elif self.current_token.type == TokenType.NUMBER:
            node.label = "value"
            node.add_child(self.leaf_node(TokenType.NUMBER))
        elif self.current_token.type == TokenType.BOOL_TRUE:
            node.label = "value"
            node.add_child(self.leaf_node(TokenType.BOOL_TRUE))
        elif self.current_token.type == TokenType.BOOL_FALSE:
            node.label = "value"
            node.add_child(self.leaf_node(TokenType.BOOL_FALSE))
        elif self.current_token.type == TokenType.NULL:
            node.label = "value"
            node.add_child(self.leaf_node(TokenType.NULL))
        # THE ABOVE CONDITIONS CHECK FOR NODES THAT FALL UNDER "value"
        # IN THE PROVIDED JSON GRAMMAR

        # THE FOLLOWING CONDITIONS CHECK FOR NODES THAT FALL UNDER "list",
        # IN THE PROVIDED JSON GRAMMAR
        else:
            errors.append(f"Unexpected token {self.current_token.type} in value at Token {self.current_index}")
            self.get_next_token()
        return node 
        
    def dict(self):
        node = Node(label="dict")
        self.eat(TokenType.LBRACE, node)  # adds "{" as a node

        # eat as many pairs as necessary until we close the dict
        while self.current_token.type != TokenType.RBRACE:
            node.add_child(self.pair())
            if self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA, node)

        self.eat(TokenType.RBRACE, node)  # adds "}" as a node
        return node

    def pair(self):
        node = Node(label="pair")
        if self.current_token.type == TokenType.STRING:
            node.add_child(self.parse())  # adds the STRING key
            self.eat(TokenType.COLON, node)   # adds ":" as a node
            node.add_child(self.parse())      # adds the value node
        else:
            errors.append(f"Expected STRING in pair but got {self.current_token.type} at Token {self.current_index}")
            self.get_next_token()

        return node

    def list(self):
        node = Node(label="list")
        self.eat(TokenType.LBRACKET, node)  # opening square bracket [

        # eat as many pairs as necessary until we close the dict
        while self.current_token.type != TokenType.RBRACKET:
            node.add_child(self.parse())
            if self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA, node)

        self.eat(TokenType.RBRACKET, node)  # closing square bracket ]
        return node

    def leaf_node(self, token_type):
        label = self.current_token.parse
        node = Node(label=label, is_leaf=True, token_type=token_type) 
        self.eat(token_type, node)
        return node

if __name__ == "__main__":
    global errors
    errors = []
    token_file = "sample inputs parser/input1.txt"  # input token file generated by scanner
    error_output_file = "errors.txt"
    output_file = "output.txt"
    
    parser = Parser(token_file)
    parse_tree = parser.parse()
    with open(output_file, "w") as file:
        parse_tree.print_tree(file)
    
    with open(error_output_file, "w") as file:
        file.write("ERROR LIST:\n")
        for error in errors:
            file.write(error + "\n")
