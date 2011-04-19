import ply.yacc as yacc
from lexer import tokens
from ast import *

precedence = (
    ('right', 'EQUALS'),
    ('nonassoc', 'EROTEME', 'PIPE'),
    ('left', 'OR', 'AND'),
    ('left', 'EQ', 'NE', 'LCHEVRON', 'RCHEVRON', 'LE', 'GE', 'IN'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'PERCENT'),
    ('right', 'CARET'),
    ('right', 'BANG', 'UMINUS'),
    ('nonassoc', 'PERIOD', 'COLON', 'LBRACKET', 'DOLLARSIGN'),
)

# Globals

dollars_ok = 0

### Program
###

def p_program_statement(p):
    'program : statements'
    p[0] = Program(p[1])

### Statements
###

def p_statements_empty(p):
    'statements : empty'
    p[0] = Statements()

def p_statements_statement(p):
    'statements : statements statement'
    if not (p[1]):
        p[1] = Statements()
    p[1].add(p[2])
    p[0] = p[1]

### Statement
###

def p_expr_verb_define(p):
    'statement : VERB id LPAREN arglist RPAREN statements ENDVERB'
    p[0] = StmtVerb(p[2], ArgList(p[4]), p[6])

def p_statement_if(p):
    'statement : IF LPAREN expr RPAREN statements elseifs elsepart ENDIF'
    p[0] = StmtCond(p[3], p[5], p[6], p[7])

def p_elseifs(p):
    'elseifs : elseifs ELSEIF LPAREN expr RPAREN statements'
    p[0] = p[1] + [ElseIfClause(p[4], p[6])]

def p_elseifs_empty(p):
    'elseifs : empty'
    p[0] = []

def p_elsepart(p):
    'elsepart : ELSE statements'
    p[0] = ElseClause(p[2])

def p_elsepart_empty(p):
    'elsepart : empty'
    pass

# Comment
def p_comment(p):
    'statement : STRING SEMICOLON'
    p[0] = StmtComment(p[1])

# Fork
def p_fork(p):
    'statement : FORK LPAREN expr RPAREN statements ENDFORK'
    p[0] = StmtFork(p[3], p[5])

def p_fork_id(p):
    'statement : FORK id LPAREN expr RPAREN statements ENDFORK'
    p[0] = StmtFork(p[4], p[6], p[2])

# Try / Except / Finally
def p_try_except(p):
    'statement : TRY statements excepts ENDTRY'
    p[0] = StmtTryExcept(p[2], p[3])

def p_try_except_finally(p):
    'statement : TRY statements FINALLY statements ENDTRY'
    p[0] = StmtTryFinally(p[2], p[4])

# excepts
def p_excepts(p):
    'excepts : EXCEPT except_clause'
    p[0] = [p[2]]

def p_excepts_except(p):
    'excepts : excepts EXCEPT except_clause'
    p[0] = p[1] + [p[3]]

# except clause
def p_except_clause(p):
    'except_clause : opt_id LPAREN codes RPAREN statements'
    p[0] = ExceptClause(p[3], p[5], p[1])

# opt_id
def p_opt_empty(p):
    'opt_id : empty'
    pass

def p_opt_id(p):
    'opt_id : id'
    p[0] = p[1]

# Loops 
def p_for_loop(p):
    'statement : FOR id IN LPAREN expr RPAREN statements ENDFOR'
    p[0] = StmtFor(p[2], p[5], p[7])

def p_for_loop_range(p):
    'statement : FOR id IN LBRACKET expr RANGE expr RBRACKET statements ENDFOR'
    expr = ExprRange(p[5], p[7])
    p[0] = StmtFor(p[2], expr, p[9])

def p_while_loop(p):
    'statement : WHILE LPAREN expr RPAREN statements ENDWHILE'
    p[0] = StmtWhile(p[3], p[5])

def p_while_loop_id(p):
    'statement : WHILE id LPAREN expr RPAREN statements ENDWHILE'
    p[0] = StmtWhile(p[4], p[6], p[2])

def p_break(p):
    'statement : BREAK SEMICOLON'
    p[0] = StmtBreak()

def p_break_id(p):
    'statement : BREAK id SEMICOLON'
    p[0] = StmtBreak(p[2])

def p_continue(p):
    'statement : CONTINUE SEMICOLON'
    p[0] = StmtContinue()

def p_continue_id(p):
    'statement : CONTINUE id SEMICOLON'
    p[0] = StmtContinue(p[2])

def p_stmt_expr_semicolon(p):
    'statement : expr SEMICOLON'
    p[0] = p[1]

def p_stmt_semicolon(p):
    'statement : SEMICOLON'
    p[0] = NoOp()

# Return
def p_return_value(p):
    'statement : RETURN expr SEMICOLON'
    p[0] = StmtReturn(p[2])

def p_return(p):
    'statement : RETURN SEMICOLON'
    p[0] = StmtReturn()

###
### Expression
###

def p_expr_integer(p):
    'expr : NUMBER'
    p[0] = TypeInt(p[1])

def p_expr_float(p):
    'expr : FLOAT'
    p[0] = TypeFloat(p[1])

def p_expr_string(p):
    'expr : STRING'
    p[0] = TypeString(p[1])

def p_expr_object(p):
    'expr : OBJ'
    p[0] = TypeObject(p[1])

def p_expr_error(p):
    'expr : ERROR'
    p[0] = TypeError(p[1])

def p_id_ID(p):
    'id : ID'
    p[0] = ExprId(p[1])

def p_expr_id(p):
    'expr : id'
    p[0] = p[1]

def p_expr_parens(p):
    'expr : LPAREN expr RPAREN'
    p[0] = ExprParen(p[2])

def p_expr_core_property(p):
    'expr : DOLLARSIGN id'
    p[0] = ExprProperty(TypeObject(0), p[2])

def p_expr_period_id(p):
    'expr : expr PERIOD id'
    p[0] = ExprProperty(p[1], p[3])

def p_expr_period_parens_id(p):
    'expr : expr PERIOD LPAREN expr RPAREN'
    p[0] = ExprProperty(p[1], ExprParen(p[4]))

def p_expr_verb_call(p):
    'expr : expr COLON id LPAREN arglist RPAREN'
    p[0] = ExprVerb(p[1], p[3], ArgList(p[5]))

def p_expr_verb_call_global(p):
    'expr : id LPAREN arglist RPAREN'
    p[0] = ExprVerbGlobal(p[1], ArgList(p[3]))

def p_expr_verb_expr_call(p):
    'expr : expr COLON LPAREN expr RPAREN LPAREN arglist RPAREN'
    p[0] = ExprVerb(p[1], p[4], ArgList(p[7]))

def p_expr_verb_call_corify(p):
    'expr : DOLLARSIGN id LPAREN arglist RPAREN'
    p[0] = ExprVerb(TypeObject(0), p[2], ArgList(p[4]))

def p_expr_assignment(p):
    'expr : expr EQUALS expr'
    p[0] = ExprAssign(p[1], p[3])

def p_expr_assignment_scatter(p):
    'expr : LBRACE scatter RBRACE EQUALS expr'
    p[0] = ExprAssignScatter(p[2], p[5])

# list
def p_expr_list(p):
    'expr : LBRACE arglist RBRACE'
    p[0] = ExprList(p[2])

# arglist
def p_arglist_empty(p):
    'arglist : empty'
    pass

def p_arglist(p):
    'arglist : ne_arglist'
    p[0] = p[1]
    
def p_ne_arglist_expr(p):
    'ne_arglist : expr'
    p[0] = [ArgNormal(p[1])]

def p_ne_arglist_splice(p):
    'ne_arglist : ATSIGN expr'
    p[0] = [ArgSplice(p[2])]

def p_ne_arglist_comma_expr(p):
    'ne_arglist : ne_arglist COMMA expr'
    p[0] = p[1] + [ArgNormal(p[3])]

def p_ne_arglist_comma_splice(p):
    'ne_arglist : ne_arglist COMMA ATSIGN expr'
    p[0] = p[1] + [ArgSplice(p[4])]

# Scatter
def p_scatter_ne_arglist(p):
    'scatter : ne_arglist COMMA scatter_item'
    p[0] = p[1] + p[3]

def p_scatter_scatter_item_comma(p):
    'scatter : scatter COMMA scatter_item'
    p[0] = p[1] + p[3]

def p_scatter_id_comma(p):
    'scatter : scatter COMMA id'
    p[0] = p[1] + [ArgNormal(p[3])]

def p_scatter_atsign_id_comma(p):
    'scatter : scatter COMMA ATSIGN id'
    p[0] = p[1] + [ArgSplice(p[4])]

def p_scatter_single(p):
    'scatter : scatter_item'
    p[0] = p[1]

def p_scatter_item_optional(p):
    'scatter_item : EROTEME id'
    p[0] = [ArgOptional(p[2])]

def p_scatter_item_optional_with_default(p):
    'scatter_item : EROTEME id EQUALS expr'
    p[0] = [ArgOptional(p[2], p[4])]

# Index Operators
def p_expr_index(p):
    'expr : expr LBRACKET dollars_up expr RBRACKET'
    global dollars_ok
    dollars_ok -= 1
    p[0] = ExprIndex(p[1], p[4])

def p_expr_range(p):
    'expr : expr LBRACKET dollars_up expr RANGE expr RBRACKET'
    global dollars_ok
    dollars_ok -= 1
    p[0] = ExprIndex(p[1], p[4], p[6])

def p_expr_dollarsign(p):
    'expr : DOLLARSIGN'
    global dollars_ok
    if (not dollars_ok):
        raise ValueError, "Illegal context for '$' expression"
    p[0] = ExprLength()

### Operators
def p_expr_uminus(p):
    'expr : MINUS expr %prec UMINUS'
    p[0] = ExprNeg(p[2])

def p_expr_plus(p):
    'expr : expr PLUS expr'
    p[0] = ExprAdd(p[1], p[3])

def p_expr_minus(p):
    'expr : expr MINUS expr'
    p[0] = ExprSub(p[1], p[3])

def p_expr_times(p):
    'expr : expr TIMES expr'
    p[0] = ExprMul(p[1], p[3])

def p_expr_div(p):
    'expr : expr DIVIDE expr'
    p[0] = ExprDiv(p[1], p[3])

def p_expr_mod(p):
    'expr : expr PERCENT expr'
    p[0] = ExprMod(p[1], p[3])

def p_expr_exp(p):
    'expr : expr CARET expr'
    p[0] = ExprExp(p[1], p[3])

def p_negate_op(p):
    'expr : BANG expr'
    p[0] = ExprNot(p[2])

def p_expr_and(p):
    'expr : expr AND expr'
    p[0] = ExprAnd(p[1], p[3])

def p_expr_or(p):
    'expr : expr OR expr'
    p[0] = ExprOr(p[1], p[3])

def p_expr_equality(p):
    'expr : expr EQ expr'
    p[0] = ExprEQ(p[1], p[3])

def p_expr_lt(p):
    'expr : expr LCHEVRON expr'
    p[0] = ExprLT(p[1], p[3])

def p_expr_gt(p):
    'expr : expr RCHEVRON expr'
    p[0] = ExprGT(p[1], p[3])

def p_expr_le(p):
    'expr : expr LE expr'
    p[0] = ExprLE(p[1], p[3])

def p_expr_ge(p):
    'expr : expr GE expr'
    p[0] = ExprGE(p[1], p[3])

def p_expr_inequality(p):
    'expr : expr NE expr'
    p[0] = ExprNE(p[1], p[3])

def p_in_expr(p):
    'expr : expr IN expr'
    p[0] = ExprIn(p[1], p[3])

# Conditional Operator
def p_expr_condop(p):
    'expr : expr EROTEME expr PIPE expr'
    p[0] = ExprCond(p[1], p[3], p[5])

# Errors
def p_error_operator(p):
    'expr : BACKTICK expr BANG codes default APOSTROPHE'
    p[0] = ExprCatch(p[2], p[4], p[5])

def p_codes_any(p):
    'codes : ANY'
    p[0] = 0

def p_codes(p):
    'codes : ne_arglist'
    p[0] = p[1]

def p_default_empty(p):
    'default : empty'
    pass

def p_default(p):
    'default : ARROW expr'
    p[0] = p[2]

# Meta
def p_empty(p):
    'empty :'
    pass

def p_dollars_up(p):
    'dollars_up : empty'
    global dollars_ok
    dollars_ok += 1

# Error rule for syntax errors
def p_error(p):
    msg = "Syntax error on line: " + str(p.lineno)
    raise SyntaxError, msg

# Build the parser
def build_parser():
    global dollars_ok
    dollars_ok = 0
    return yacc.yacc()
