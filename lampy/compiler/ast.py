from .. import moo

def indent(_str, level=1, spaces=4):
    if not _str.strip():
        return _str
    unit = ' ' * spaces
    ind = unit * level
    return ind + _str

class Node(object):
    def __init__(self, value=None):
        self.value = value

    def compile(self):
        return self.value

class Program(Node):
    def generate(self):
        code = self.value.compile()
        res = code.generate()
        res = str.join('\n', filter(lambda X: bool(X.strip()), res.split('\n')))
        return res

class Statements(Node):
    def __init__(self, statement=None):
        self.statements = []
        if statement:
            self.add(statement) 

    def add(self, statement):
        self.statements.append(statement)

    def compile(self):
        code = Code()
        for statement in self.statements:
            code += statement.compile()
            code.append('\n')
        return code
    
class Stmt(Node):
    pass

class NoOp(Node):
    def compile(self):
        return ''

class Expr(Node):
    pass

class ExprId(Expr):
    pass

class ExprOp(Expr): 
    Symbol = None

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def compile(self):
        return Code(self.left.compile(), self.Symbol, self.right.compile())
##
## Concrete

class StmtCond(Stmt):
    def __init__(self, expr, body, elseifs, elsepart):
        self.expr = expr
        self.body = body
        self.elseifs = elseifs
        self.elsepart = elsepart

    def compile(self):
        code = Code("if ", self.expr.compile(), ":\n")
        code.append(Scope(self.body.compile()))
        if self.elseifs:
            for _elif in self.elseifs:
                code.append(_elif.compile())
        if self.elsepart:
            code.append(self.elsepart.compile())
        return code

class ElseIfClause(Node):
    def __init__(self, expr, body):
        self.expr = expr
        self.body = body

    def compile(self):
        code = Code("elif ", self.expr.compile(), ":\n")
        code.append(Scope(self.body.compile()))
        return code

class ElseClause(Node): 
    def __init__(self, body):
        self.body = body

    def compile(self):
        code = Code()
        code.append("else:\n")
        code.append(Scope(self.body.compile()))
        return code

class StmtVerb(Stmt):
    def __init__(self, id, arglist, body):
        self.id = id
        self.arglist = arglist
        self.body = body

    def compile(self):
        tail = ArgNormal(ExprId("*args"))
        self.arglist.value.append(tail)
        code = Code("def ", self.id.compile(), "(", self.arglist.compile(), "):\n", Scope(self.body.compile()))
        return code

class StmtFor(Stmt):
    def __init__(self, id, expr, body):
        self.id = id
        self.expr = expr
        self.body = body

    def compile(self):
        code = Code("for ",self.id.compile()," in ",self.expr.compile(),":\n")
        code.append(Scope(self.body.compile()))
        return code

class StmtWhile(Stmt):
    def __init__(self, expr, body, id=None):
        self.id = id
        self.expr = expr
        self.body = body

    def compile(self):
        if isinstance(self.expr, ExprAssignScatter):
            testexpr = self.expr.true_rv.compile()
            code = Code("while ",testexpr,":\n")
            code.append(Scope(self.expr.compile(), self.body.compile()))
        elif isinstance(self.expr, ExprAssign):
            testexpr = self.expr.left.compile()
            code = Code()
            code.append(self.expr.compile())
            code.append('\n')
            code.append("while "+testexpr+":\n")
            code.append(Scope(self.body.compile(), self.expr.compile(), '\n'))
        else:
            testexpr = self.expr.compile()
            code = Code("while ",self.expr.compile(),":\n")
            code.append(Scope(self.body.compile()))
        return code

class StmtBreak(Stmt):
    def __init__(self, id=None):
        self.id = id

    def compile(self):
        return "break"

class StmtContinue(Stmt): 
    def __init__(self, id=None):
        self.id = id

    def compile(self):
        return "continue"

class StmtReturn(Stmt): 
    def __init__(self, value=None):
        self.value = value

    def compile(self):
        if self.value:
            return Code("return ", self.value.compile())
        return "return"

class StmtComment(Stmt): 
    def compile(self):
        if self.value:
            return Code("#", self.value)
        return ""

class TypeInt(Expr): 
    def compile(self):
        return Code("moo.Int(", self.value, ")")

class TypeFloat(Expr): 
    def compile(self):
        return Code("moo.Float(", self.value, ")")

class TypeString(Expr): 
    def compile(self):
        return Code("moo.String(", self.value, ")")

class TypeObject(Expr): 
    def compile(self):
        objid = str(self.value)
        if objid.startswith("#"):
            objid = objid[1:]
        return Code("moo.Object(", objid, ")")

class TypeError(Expr): 
    ErrorLookup = {
        'E_TYPE': "TypeError",
        'E_RANGE': "IndexError",
        'ANY': "ANY",
    }

    def compile(self):
        return self.ErrorLookup.get(self.value, "ANY")

class ExprParen(Expr): 
    def compile(self):
        return Code("(", self.value.compile(), ")")

class ArgList(Expr): 
    def __init__(self, value=None):
        if value == None:
            value = []
        self.value = value

    def compile(self):
        code = Code()
        for val in self.value[:-1]:
            if isinstance(val.value, ExprAssign):
                #p = Proxy(val.value.left.compile(), Code(val.value.right.compile()))
                p = Proxy("PPPPP", Code(val.value.compile()))
                code.append(p)
            else:
                code.append(val.compile())
            code.append(", ")
        if self.value:
            val = self.value[-1]
            if isinstance(val.value, ExprAssign):
                p = Proxy(val.value.left.compile(), Code(val.value.right.compile()))
                code.append(p)
            else:
                code.append(val.compile())
        return code
        
class ExprList(Expr): 
    def compile(self):
        code = Code()
        code.append('[')
        if self.value:
            for val in self.value[:-1]:
                if isinstance(val, ArgSplice):
                    code.append("] + ")
                    code.append(val.compile())
                    code.append(" + [")
                else:
                    code.append(val.compile())
                    code.append(", ")
            if isinstance(self.value[-1], ArgSplice):
                code.append("] + ")
                code.append(self.value[-1].compile())
                code.append(" + [")
            else:
                code.append(self.value[-1].compile())
        code.append(']')
        return code

class ExprProperty(Expr): 
    def __init__(self, base, prop):
        self.base = base
        self.prop = prop
    
    def compile(self):
        return Code(self.base.compile(), ".", self.prop.compile())

class ExprVerb(Expr): 
    def __init__(self, base, verb, arglist):
        self.base = base
        self.verb = verb
        self.arglist = arglist

    def compile(self):
        return Code(self.base.compile(), ".", self.verb.compile(), "(", self.arglist.compile(), ")")

class ExprVerbGlobal(Expr): 
    def __init__(self, verb, arglist):
        self.verb = verb
        self.arglist = arglist

    def compile(self):
        return Code(self.verb.compile(), "(", self.arglist.compile(), ")")

class ArgNormal(Expr):
    def compile(self):
        return self.value.compile()

class ArgSplice(Expr): 
    def compile(self):
        return self.value.compile()

class ArgOptional(Expr): 
    def __init__(self, value, default=None):
        self.value = value
        self.default = default
        if self.default == None:
            self.default = value

class ExprRange(Expr):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
    
    def compile(self):
        return Code("range(", self.head.compile(), ", ", self.tail.compile(), ")") 

class ExprIndex(Expr):
    def __init__(self, base, start, end=None):
        self.base = base
        self.start = start
        self.end = end

    def compile(self):
        base = self.base.compile()
        start = self.start.compile()
        try:
            code = start
            if type(code) != str:
                code = code.generate()
            start = int(eval(code, {"moo":moo})) - 1
        except:
            start = Code([start, " - 1"])
        if self.end:
            end = self.end.compile()
            code = end
            if type(end) != str:
                code = code.generate()
            try:
                end = int(eval(code, {"moo":moo}))
                if isinstance(self.end, ExprLength) and end == 0:
                    end = ""
            except:
                pass
            ret = Code(base, "[",start,":",end,"]")
        else:
            ret = Code(base, "[",start,"]")
        return ret
        
class ExprLength(Expr): 
    def compile(self):
        return "0"

class ExprNot(Expr):
    def compile(self):
        return Code("not ", self.value.compile())

class ExprNeg(Expr):
    def compile(self):
        return Code("- ", self.value.compile())

class ExprAssign(ExprOp): 
    Symbol = " = "

    def compile(self):
        if isinstance(self.left, (ExprList, ArgList)):
            return ExprAssignScatter(self.left, self.right).compile()
        return super(ExprAssign, self).compile()

class ExprAdd(ExprOp):
    Symbol = " + "
class ExprSub(ExprOp):
    Symbol = " - "
class ExprMul(ExprOp):
    Symbol = " * "
class ExprDiv(ExprOp):
    Symbol = " / "
class ExprMod(ExprOp):
    Symbol = " % "
class ExprExp(ExprOp):
    Symbol = " ** "
class ExprAnd(ExprOp):
    Symbol = " and "
class ExprOr(ExprOp):
    Symbol = " or "
class ExprEQ(ExprOp):
    Symbol = " == "
class ExprLT(ExprOp):
    Symbol = " < "
class ExprGT(ExprOp):
    Symbol = " > "
class ExprLE(ExprOp):
    Symbol = " <= "
class ExprGE(ExprOp):
    Symbol = " >= "
class ExprNE(ExprOp):
    Symbol = " != "
class ExprIn(ExprOp):
    def compile(self):
        L = self.left.compile()
        R = self.right.compile()
        code = Code("(", L, " in ", R, " and [", R, ".index(", L, ") + 1] or [0])[0]")
        return code

class ExprCond(Expr): 
    def __init__(self, condition, consequent, alternate):
        self.condition = condition
        self.consequent = consequent
        self.alternate = alternate

    def compile(self):
        return Code("((", self.condition.compile(), ") and [", self.consequent.compile(), "] or [", self.alternate.compile(), "])[0]")

class ExprCatch(Expr): 
    def __init__(self, trybody, codes, alternate):
        self.trybody = trybody
        self.codes = codes
        self.alternate = alternate
        self.target = "__catch"

    def compile(self):
        code = Code("try:\n")
        code.append(Scope(self.target, " =  ", self.trybody.compile(), "\n"))
        if not self.alternate:
            alt = "None"
        else:
            alt = self.alternate.compile()
        if self.codes:
            for err in self.codes:
                err = err.compile()
                if err == "ANY":
                    code.append("except:\n")
                    code.append(Scope(self.target, " =  ", alt,  "\n"))
                else:
                    code.append("except " + err + ":\n")
                    code.append(Scope(self.target, " =  ", alt, "\n"))
        else:
            code.append("except:\n")
            code.append(Scope(self.target, " = 0\n"))
        return Proxy(self.target, code)

class StmtFork(Stmt):
    def __init__(self, expr, body, id=None):
        self.expr = expr
        self.body = body
        self.id = id

    def compile(self):
        forkdef = Code("def __fork():\n")
        body = Scope(self.body.compile())
        forkdef.append(body)
        # XXX: copy locals?
        if self.id:
            forkcall = Code("fork(", self.expr.compile(), "__fork", self.id.compile(), ")\n")
        else:
            forkcall = Code("fork(", self.expr.compile(), ", __fork)")
        return forkdef + forkcall

class StmtTryExcept(Stmt):
    def __init__(self, trybody, excepts):
        self.trybody = trybody
        self.excepts = excepts

    def compile(self):
        trydef = Code("try:\n")
        trybody = Scope(self.trybody.compile())
        trydef.append(trybody)
        exceptps = Code()
        for _exc in self.excepts:
            exceptps.append(_exc.compile())
        return Code(trydef + exceptps)

class StmtTryFinally(Stmt): 
    def __init__(self, trybody, fclause):
        self.trybody = trybody
        self.fclause = fclause

    def compile(self):
        trydef = Code("try:\n")
        trybody = Scope(self.trybody.compile())
        fdef = Code("finally:\n")
        fclause = Scope(self.fclause.compile())
        return trydef + trybody + fdef + fclause

class ExceptClause(Stmt): 
    def __init__(self, codes, body, id=None):
        self.codes = codes
        self.body = body
        self.id = id

    def compile(self):
        code = Code()
        if self.codes:
            for err in self.codes:
                err = err.compile()
                if err == "ANY":
                    code.append("except:\n")
                    code.append(Scope(self.body.compile()))
                else:
                    code.append("except " + err + ":\n")
                    code.append(Scope(self.body.compile()))
        else:
            code.append("except:\n")
            code.append(Scope(self.body.compile()))
        return code
    
class ExprAssignScatter(Expr):
    def __init__(self, lv, rv):
        if isinstance(lv, ExprList):
            self.lv = lv.value
        else:
            self.lv = lv
        self.true_rv = rv
        self.rv = "__xaa"

    def pythonNormal(self, arg, idx):
        return Code(arg.value.compile(), " = ", self.rv, ".pop(", idx, ")\n")
    def pythonSplice(self, arg, idx):
        return Code(arg.value.compile(), " = ", self.rv, "\n")
    def pythonOptional(self, arg, idx):
        return Code(arg.value.compile(), " =  (", self.rv, " and [", self.rv, ".pop(", idx, ")] or [", arg.default.compile(), "])[0]\n")

    def compile(self):
        pop_index = 0
        nArgs = [[], []]
        oArgs = [[], []]
        rArg = []
        for arg in self.lv:
            if isinstance(arg, ArgNormal):
                nArgs[pop_index].append(self.pythonNormal(arg, pop_index))
            elif isinstance(arg, ArgOptional):
                oArgs[pop_index].append(self.pythonOptional(arg, pop_index))
            elif isinstance(arg, ArgSplice):
                rArg.append(self.pythonSplice(arg, pop_index))
                pop_index = -1
        nArgs[-1].reverse()
        oArgs[-1].reverse()
        prefix = Code(self.rv, " = list(", self.true_rv.compile(), ")\n")
        code = Code()
        code.append( prefix + nArgs[0] + nArgs[-1] + oArgs[0] + oArgs[-1] + rArg)
        return code

###
### Code
###

class Code(list):
    def __init__(self, *args):
        if not args:
            super(Code, self).__init__()
        else:
            super(Code, self).__init__(args)

    # Two pass flatten
    def flatten(self):
        roughblock = []
        for elem in self:
            if type(elem) in (list, tuple):
                elem = Code(*elem)
            if hasattr(elem, "flatten"):
                roughblock += elem.flatten()
            else:
                roughblock.append(str(elem))
        smoothblock = []
        txt = ''
        for elem in roughblock:
            if type(elem) == str:
                txt += elem
            else:
                if txt:
                    smoothblock.append(txt)
                    txt = ''
                smoothblock.append(elem)
        if txt:
            smoothblock.append(txt)
        return smoothblock

    # Generate, responsible for all code, proxies and scopes
    def generate(self, code=None):
        if code == None:
            code = self.flatten()
        txt = ['']
        for elem in code:
            if type(elem) == str:
                _code = elem.split('\n')
                lineglue = txt[-1] + _code[0]
                txt = txt[:-1] + [lineglue] + _code[1:]
            elif type(elem) == tuple:
                # Proxy
                if elem[0] == 'Proxy':
                    _code = self.generate(code=elem[2])
                    _code = _code.split('\n')
                    txt = txt[:-1] + _code + txt[-1:]
                    pname = " %s " % elem[1]
                    txt[-1] = txt[-1] + pname
                # Scope
                elif elem[0] == 'Scope':
                    _code = self.generate(code=elem[1])
                    _code = _code.split('\n')
                    _code = map(lambda X: indent(X, level=1), _code)
                    txt += _code
        return str.join('\n', txt)

    #def __str__(self):
    #    return self.flatten()

class Scope(Code):
    def flatten(self):
        block = super(Scope, self).flatten()
        return [('Scope', block)]

class Proxy(Code):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def flatten(self):
        block = self.body.flatten()
        return [('Proxy', self.name, block)]
