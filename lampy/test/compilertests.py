import unittest
import inspect
from .. import compiler
from .. import moo

class LampyTestFixture(unittest.TestCase):
    def setUp(self):
        self.parser = compiler.build_parser()

    def parse(self, txt, debug=0):
        try:
            res = self.parser.parse(txt, debug=debug)
        except:
            if not debug:
                self.parser.parse(txt, debug=1)
            raise
        return res.generate()
    
    def makeGlobals(self, gdict=None):
        if not gdict:
            gdict = globals()
        gdict.update({'moo': moo})
        gdict.update({'index': moo.index})
        return gdict

    def localEval(self, code, debug=0):
        code = self.LAMBDA + code
        ldict = self.execute(code, debug=debug)[2]
        return ldict

    def execute(self, lcode, gdict=None, ldict={}, debug=False):
        gdict = self.makeGlobals(gdict)
        if not lcode.endswith(';'):
            lcode += ';'
        pycode = self.parse(lcode, debug)
        self.assert_(pycode.strip(), "Python result is empty")
        if debug:
            print pycode
        cobj = compile(pycode, '<string>', 'exec')
        res = eval(cobj, gdict, ldict)
        return (res, gdict, ldict)

    def assertEval(self, lcode, expResult, debug=False):
        if not lcode.endswith(';'):
            lcode += ';'
        pycode = self.parse(lcode, debug)
        pycode = pycode.strip()
        self.assert_(pycode, "Python result is empty")
        if debug:
            print pycode
        #for char in pycode:
        #    print char, ord(char)
        gdict = self.makeGlobals()
        res = eval(pycode, gdict)
        self.assertEqual(expResult, res)

    def get_suite(cls):
        return unittest.TestLoader().loadTestsFromTestCase(cls)
    get_suite = classmethod(get_suite)


class CodeTests(LampyTestFixture):
    def testOdds(self):
        LAMBDA = \
"""odds = {1, 3, 5, 7, 9};
evens = {};
for n in (odds)
    evens = {@evens, n + 1};
endfor
"""
        ldict = self.execute(LAMBDA, debug=0)[2]
        self.assertEqual(ldict['evens'], [2, 4, 6, 8, 10])

class SimpleEvals(LampyTestFixture):
    def testBasicMath(self):
        self.assertEval("5 + 2", 7)
        self.assertEval("5 - 2", 3)
        self.assertEval("5 * 2", 10)
        self.assertEval("5 / 2", 2)
        self.assertEval("5.0 / 2.0", 2.5)
        self.assertEval("5 % 2", 1)
        self.assertEval("5.0 % 2.0", 1.0)
        self.assertEval("5 % -2", 1)
        self.assertEval("-5 % 2", -1)
        self.assertEval("-5 % -2", -1)
        self.assertEval("-(5 + 2)", -7)
        self.assertEval("(-5 % 2) % 3", -1)
        self.assertEval('{3 + 4, 3 - 4, 3 * 4}', [7, -1, 12])

    def testListIndex(self):
        self.assertEval('"fob"[1]', 'f')
        self.assertEval('"fob"[2]', 'o')
        self.assertEval('"fob"[3]', 'b')
        self.assertEval('"fob"[$]', 'b')
        self.assertEval('"fob"[$ + -1]', 'o')
        self.assertEval("{#12, #23, #34}[$ - 1]", moo.Object("23"))

    def testConditionalOp(self):
        self.assertEval("1 ? 0 | 2", 0)
        self.assertEval("1 ? 2 | 3", 2)
        self.assertEval("0 ? 2 | 3", 3)
        self.assertEval('"foo" ? 17 | {#34}', 17)

    def testNegateOp(self):
        self.assertEval('! "foo"', 0)
        self.assertEval('! (3 >= 4)', 1)

    def testExptMath(self): 
        self.assertEval("3 ^ 4", 81)
        self.assertEval("3.5 ^ 4", 3.5 ** 4)
        self.assertEval("3.5 ^ 4.5", 3.5 ** 4.5)

    def testComparison(self):
        self.assertEval("3 == 4", 0)
        self.assertEval("3 != 4", 1)
        self.assertEval("3 == 3.0", 0)
        self.assertEval('"foo" == "Foo"', 1)
        self.assertEval("#34 != #34", 0)
        self.assertEval('{1, #34, "foo"} == {1, #34, "FoO"}', 1)
        #self.assertEval("E_DIV == E_TYPE", 0)
        self.assertEval('3 != "foo"', 1)
        self.assertEval('"123\\\"" == "123\\\""', 1)
        self.assertEval("3 < 4", 1)
        #self.assertEval("3 < 4.0", error=E_TYPE)
        self.assertEval('#34 >= #32', 1)
        self.assertEval('"foo" <= "Boo"', 0)
        self.assertEval('"foo" < "Foo"', 0)
        self.assertEval('"foo" > "Foo"', 0)
        #self.assertEval('E_DIV > E_TYPE', 1)
        self.assertEval("1 && 1", 1)
        self.assertEval("0 && 1", 0)
        self.assertEval("0 && 0", 0)
        self.assertEval("1 || 1", 1)
        self.assertEval("0 || 1", 1)
        self.assertEval("0 || 0", 0)
        self.assertEval("17 <= 23  &&  23 <= 27", 1)
        self.assertEval("{3 < 4, 3 <= 4, 3 >= 4, 3 > 4}", [1, 1, 0, 0])

class ListAssignment(LampyTestFixture):
    LAMBDA = \
"""s = "foobar";
l = {1, 2, 3};
b = {"Foo", "Bar"};
n = {{1, 2, 3}, {4, 5, 6}, "foo"};
"""

    def myEval(self, code, debug=0):
        if not code.endswith(';'):
            code += ';'
        code = self.LAMBDA + code
        ldict = self.execute(code, debug=debug)[2]
        return ldict

    def testIndexAssignment(self):
        res = self.localEval("l[2] = l[2] + 3;")
        self.assertEqual(res['l'], [1, 5, 3])
        res = self.localEval('l[2] = "foo";')
        self.assertEqual(res['l'], [1, "foo", 3])
        res = self.localEval('s[2] = "u";')
        self.assertEqual(res['s'], "fuobar")
        res = self.localEval('s[$] = "z";')
        self.assertEqual(res['s'], "foobaz")

    def testNestedLists(self):
        res = self.localEval('n[2][2] = -n[2][2];')
        self.assertEqual(res['n'][1][1], -5)
        res = self.localEval('n[2] = "bar";\nn[2][$] = "z";')
        self.assertEqual(res['n'][1], "baz")

    def testFlattenList(self):
        res = self.localEval('r = {1, l, 5}')
        self.assertEqual(res['r'], [1, [1, 2, 3], 5])
        res = self.localEval('r = {1, @l, 5}')
        self.assertEqual(res['r'], [1, 1, 2, 3, 5])
        res = self.localEval('r = {@b, @l}')
        self.assertEqual(res['r'], ["Foo", "Bar", 1, 2, 3])
        res = self.localEval('r = {@b, @l, @b}')
        # case shift test as well
        self.assertEqual(res['r'], ["Foo", "Bar", 1, 2, 3, "foo", "bar"])
        res = self.localEval('r = {@l, 5}')
        self.assertEqual(res['r'], [1, 2, 3, 5])
        res = self.localEval('r = {5, @l}')
        self.assertEqual(res['r'], [5, 1, 2, 3])

    def testSpliceOperator(self):
        self.assertEval('"foobar"[2..$]', "oobar")
        self.assertEval('"foobar"[3..3]', "o")
        self.assertEval('"foobar"[17..12]', "")
        self.assertEval('{"one", "two", "three"}[$ - 1..$]', ["two", "three"])
        self.assertEval('{"one", "two", "three"}[3..3]', ["three"])
        self.assertEval('{"one", "two", "three"}[17..12]', [])

    def testSpliceAssignment(self):
        res = self.localEval("l[2..3] = {6, 7, 8, 9}")
        self.assertEqual(res['l'], [1, 6, 7, 8, 9])
        res = self.localEval('l[2..3] = {6, 7, 8, 9};\nl[2..1] = {10, "foo"}')
        self.assertEqual(res['l'], [1, 10, "foo", 6, 7, 8, 9])
        res = self.localEval('l[2..3] = {6, 7, 8, 9};\nl[2..1] = {10, "foo"};\nl[3][2..$] = "u";')
        self.assertEqual(res['l'], [1, 10, "fu", 6, 7, 8, 9])
        res = self.localEval('s[7..12] = "baz"')
        self.assertEqual(res['s'], "foobarbaz")
        res = self.localEval('s[7..12] = "baz"; \ns[1..3] = "fu";')
        self.assertEqual(res['s'], "fubarbaz")
        res = self.localEval('s[7..12] = "baz";\ns[1..3] = "fu";\ns[1..0] = "test";')
        self.assertEqual(res['s'], "testfubarbaz")
    
    def testInOperator(self):
        self.assertEval("2 in {5, 8, 2, 3}", 3)
        self.assertEval("7 in {5, 8, 2, 3}", 0)
        self.assertEval('"bar" in {"Foo", "Bar", "Baz"}', 2)

class StaticWhileAssign(LampyTestFixture):
    LAMBDA = \
"""
__VERB__ BlaBla()
vname = "bla1* bla2* bla3* bla4* ";
while (j = index(vname, "* "))
vname = tostr(vname[1..j - 1], "<anything>", vname[j + 1..$]);
endwhile
return vname;
endverb
"""
    def testWackyness(self):
        res = self.localEval("r = BlaBla()")
        self.assertEqual(res['r'], "bla1<anything> bla2<anything> bla3<anything> bla4<anything> ")


class CrazyAssignment(LampyTestFixture):
    LAMBDA = \
"""
__VERB__ WackyAssign()
todo = {1,2,3,4,5};
x = 0;
while ({?sfc, @todo} = todo)
    if (sfc == 5)
        todo = {@todo, 1, 2, 3};
    endif
    x = x + sfc;
endwhile
return x;
endverb
"""
    def testWackyAssignment(self):
        res = self.localEval("r = WackyAssign()")
        self.assertEqual(res['r'], 21)

class VerbConstruction(LampyTestFixture):
    LAMBDA = \
"""__VERB__ argtest()
b = c = e = 17;
{a, ?b, ?c = 8, @d, ?e = 9, f} = args;
return {a, b, c, d, e, f};
endverb
"""

    def testWackyAssignment(self):
        res = self.localEval("r = argtest(1, 2)")
        self.assertEqual(res['r'], [1, 17, 8, [], 9, 2])
        res = self.localEval("r = argtest(1, 2, 3)")
        self.assertEqual(res['r'], [1, 2, 8, [], 9, 3])
        res = self.localEval("r = argtest(1, 2, 3, 4)")
        self.assertEqual(res['r'], [1, 2, 3, [], 9, 4])
        res = self.localEval("r = argtest(1, 2, 3, 4, 5)")
        self.assertEqual(res['r'], [1, 2, 3, [], 4, 5])
        res = self.localEval("r = argtest(1, 2, 3, 4, 5, 6)")
        self.assertEqual(res['r'], [1, 2, 3, [4], 5, 6])
        res = self.localEval("r = argtest(1, 2, 3, 4, 5, 6, 7)")
        self.assertEqual(res['r'], [1, 2, 3, [4, 5], 6, 7])
        res = self.localEval("r = argtest(1, 2, 3, 4, 5, 6, 7, 8)")
        self.assertEqual(res['r'], [1, 2, 3, [4, 5, 6], 7, 8])

class ErrorHandling(LampyTestFixture):
    def testWackyInline(self):
        res = self.execute('r = `{1}[2] ! E_TYPE, E_RANGE => 2\'', debug=0)[2]
        self.assertEqual(res['r'], 2)
        res = self.execute('r = `"hi" + 1 ! E_TYPE => "hi"\'', debug=0)[2]
        self.assertEqual(res['r'], "hi")
        res = self.execute('r = `1 / 0 ! ANY\'', debug=0)[2]
        self.assertEqual(res['r'], None)

    def testTorture(self):
        res = self.execute("{a,b,c,d,e,f,w,y,q,r} = {1,2,3,4,5,6,2,{2},8,9};\nx = a < b && c > d + e * f ? w in y | - q - r", debug=0)[2]
        self.assertEqual(res['x'], -17)

def GetTestSuite():
    ts = []
    for obj in globals().values():
        try:
            ts.append(obj.get_suite())
        except:
            pass
    return unittest.TestSuite(ts)

if __name__ == '__main__':
    unittest.main()
