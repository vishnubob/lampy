import ply.lex as lex

# List of token names.   This is always required
tokens = (
   'NUMBER', 'COLON', 'FLOAT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'PERCENT',
   'CARET', 'EROTEME', 'EQUALS', 'LCHEVRON', 'RCHEVRON', 'LPAREN', 'RPAREN',
   'LBRACE', 'RBRACE', 'APOSTROPHE', 'BACKTICK', 'LBRACKET', 'RBRACKET',
   'COMMA', 'SEMICOLON', 'ATSIGN', 'DOLLARSIGN', 'BANG', 'PIPE', 'PERIOD', 
   'ID', 'ERROR', 'OBJ', 'STRING', 'RANGE', 'ARROW', 'OR', 'AND', 'NE', 'EQ', 
   'GE', 'LE', 
)

reserved = {
    'if'        : 'IF',
    'elseif'    : 'ELSEIF',
    'else'      : 'ELSE',
    'in'        : 'IN',
    'endif'     : 'ENDIF',
    'for'       : 'FOR',
    'endfor'    : 'ENDFOR',
    'while'     : 'WHILE',
    'endwhile'  : 'ENDWHILE',
    'continue'  : 'CONTINUE',
    'break'     : 'BREAK',
    '__VERB__'  : 'VERB',
    'endverb'   : 'ENDVERB',
    'return'    : 'RETURN',
    'fork'      : 'FORK',
    'endfork'   : 'ENDFORK',
    'try'       : 'TRY',
    'endtry'    : 'ENDTRY',
    'except'    : 'EXCEPT',
    'finally'   : 'FINALLY',
    'any'       : 'ANY',
}

tokens = tokens + tuple(reserved.values())

# Regular expression rules for simple tokens
t_APOSTROPHE= r'\''
t_COLON     = r':'
t_BACKTICK  = r'`'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_PERCENT   = r'\%'
t_CARET     = r'\^'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'{'
t_RBRACE    = r'}'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_EQUALS    = r'='
t_LCHEVRON  = r'<'
t_RCHEVRON  = r'>'
t_COMMA     = r','
t_SEMICOLON = r';'
t_ATSIGN    = r'@'
t_PERIOD    = r'\.'
t_DOLLARSIGN = r'\$'
t_EROTEME   = r'\?'
t_BANG      = r'!'
t_PIPE      = r'\|'
#t_NUMBER    = r'\d+'
#t_FLOAT     = r'\d+\.\d+'
t_ARROW     = r'=>'
t_OBJ       = r'\#-?\d+'
t_STRING    = r'\"([^\\\n]|(\\.))*?\"'
t_RANGE     = r'\.\.'
t_OR        = r'\|\|'
t_AND       = r'&&'
t_NE        = r'!='
t_EQ        = r'=='
t_GE        = r'>='
t_LE        = r'<='

def t_NUMBER(t):
    r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
    if '.' in t.value:
        t.type = "FLOAT"
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value == "__VERB__":
        t.lexer.lineno = 0
    if t.value == "tostr":
        t.value = "moo.String"
    if t.value.startswith("E_"):
        t.type = "ERROR"
    else:
        t.type = reserved.get(t.value, 'ID')
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Build the lexer
def build_lexer():
    return lex.lex()
lexer = build_lexer()

