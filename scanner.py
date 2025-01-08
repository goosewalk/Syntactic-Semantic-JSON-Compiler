# I would like to credit the supplementary scanner provided on Brightspace (2024) for the CSCI 2115 Fall24 class.
# The code provided in that example was referenced for things like creating tokens and my lexer. Thank you!

class TokenType: # JSON token types
    LBRACE = '{' # '{'
    RBRACE = '}' # '}'
    LBRACKET = '[' # '['
    RBRACKET = ']' # ']'
    COMMA = ',' # ','
    COLON = ':' # ':'
    STRING = 'STRING' # strings
    NUMBER = 'NUMBER' # numeric values
    BOOL_TRUE = 'BOOL_TRUE' # true
    BOOL_FALSE = 'BOOL_FALSE' # false
    NULL = 'NULL' # null
    EOF = 'EOF' # end of input

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f"<{self.type}, {self.value}>"
        return f"<{self.type}>"

class LexerError(Exception):
    def __init__(self, position, character):
        self.position = position
        self.character = character
        super().__init__(f"Invalid character '{character}' at position {position}!")

# dfa class that reads input using a lexer object
# uses dfas to recognize numbers and strings (other types are trivial)
# the assumption is that by completing a method and returning a token without encountering an error,
# a dfa has reached a final state given its subsection of the input that it was tasked with scanning.
# then, we continue creating tokens with the full input by using either the same or other dfa(s) repeatedly.
class DFA:
    def recognize_string(self, lexer):
        result = ''
        lexer.advance() # skip opening quote
        while lexer.current_char is not None and lexer.current_char != '"':
            result += lexer.current_char
            lexer.advance()
        lexer.advance() # skip closing quote
        return Token(TokenType.STRING, result)
    
    def recognize_number(self, lexer):
        result = ''
        while lexer.current_char is not None and (lexer.current_char.isdigit() or lexer.current_char in ['.', 'e', 'E', '-', '+']):
            result += lexer.current_char
            lexer.advance()
        return Token(TokenType.NUMBER, result)
    
    def useDFA(self, lexer):
        while lexer.current_char is not None:
            if lexer.current_char.isspace():
                lexer.skip_whitespace()
                continue
            if lexer.current_char == '[':
                lexer.advance()
                return Token(TokenType.LBRACKET)
            if lexer.current_char == ']':
                lexer.advance()
                return Token(TokenType.RBRACKET)
            if lexer.current_char == '{':
                lexer.advance()
                return Token(TokenType.LBRACE)
            if lexer.current_char == '}':
                lexer.advance()
                return Token(TokenType.RBRACE)
            if lexer.current_char == ':':
                lexer.advance()
                return Token(TokenType.COLON)
            if lexer.current_char == ',':
                lexer.advance()
                return Token(TokenType.COMMA)
            if lexer.current_char == '"':
                return self.recognize_string(lexer)
            if lexer.current_char.isdigit() or lexer.current_char in ['.', 'e', 'E', '-', '+']:
                return self.recognize_number(lexer)
            if lexer.current_char == 't' and lexer.input_text[lexer.position:lexer.position + 4] == 'true':
                lexer.position += 4
                lexer.current_char = lexer.input_text[lexer.position] if lexer.position < len(lexer.input_text) else None
                return Token(TokenType.BOOL_TRUE, 'true')
            if lexer.current_char == 'f' and lexer.input_text[lexer.position:lexer.position + 5] == 'false':
                lexer.position += 5
                lexer.current_char = lexer.input_text[lexer.position] if lexer.position < len(lexer.input_text) else None
                return Token(TokenType.BOOL_FALSE, 'false')
            if lexer.current_char == 'n' and lexer.input_text[lexer.position:lexer.position + 4] == 'null':
                lexer.position += 4
                lexer.current_char = lexer.input_text[lexer.position] if lexer.position < len(lexer.input_text) else None
                return Token(TokenType.NULL, 'null')
            raise LexerError(lexer.position, lexer.current_char)
        return Token(TokenType.EOF)
    
    def tokenize(self, lexer):
        tokens = []
        while True:
            try:
                token = self.useDFA(lexer)
                if token.type == TokenType.EOF:
                    break
                tokens.append(token)
            except LexerError as e:
                errors.append(f"Lexer Error: {e}")
                lexer.advance()
        return tokens

# lexer class used to read over json input
# utilized by DFA class to receive input
class Lexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.position = 0
        self.current_char = self.input_text[self.position] if self.input_text else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def advance(self):
        self.position += 1
        if self.position >= len(self.input_text):
            self.current_char = None
        else:
            self.current_char = self.input_text[self.position]

    

# scanner reads input from the "sample inputs" folder
# creates a lexer and DFA objects
# uses lexer object to pass information to DFA
# tokens are sent to output.txt
# lexer errors are printed to terminal
if __name__ == "__main__":
    global errors
    errors = []
    input_string = ""
    json_location = "sample inputs scanner\input1.json" 
    output_location = "output.txt"

    with open(json_location, 'r') as file:
        for line in file:
            input_string += line.strip()
    lexer = Lexer(input_string)
    tokens = DFA() # need to create the DFA object separately first so python can send the "self" argument to tokens.tokenize()
    tokens = tokens.tokenize(lexer)
    
    # send each token on its own line to output.txt
    with open(output_location, 'w') as file:
        for i in range(0,len(tokens)):
            if i < len(tokens) - 1:
                file.write(tokens[i].__repr__() + "\n")
            else: file.write(tokens[i].__repr__())
    
    # print all lexer errors to terminal
    for error in errors:
        print(error)
