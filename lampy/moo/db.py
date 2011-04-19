import re
import sys

PlayerFlags = {
    1 : 'Player',
    2 : 'Programmer',
    4 : 'Wizard',
    8 : '(obsolete)',
    16 : '+r',
    32 : '+w',
    64 : '(obselete)',
    128 : '+f',
}

VerbPermissions = {
    1 : '+r',
    2 : '+w',
    4 : '+x',
    8 : '+d',
    16 : 'dobj=any',
    32 : 'dobj=this',
    64 : 'iobj=any',
    128 : 'iobj=this',
    1024 : '-o',
}

VerbPreposition = {
    -2 : 'any',
    -1 : 'none',
    0 : 'with/using',
    1 : 'at/to',
    2 : 'in front of',
    3 : 'in/inside/into',
    4 : 'on top of/on/onto/upon',
    5 : 'out of/from inside/from',
    6 : 'over',
    7 : 'through',
    8 : 'under/underneath/beneath',
    9 : 'behind',
    10 : 'beside',
    11 : 'for/about',
    12 : 'is',
    13 : 'as',
    14 : 'off/off of ',
}

PropertyPermissions = {
    1 : '+r',
    2 : '+w',
    4 : '+c', 
}

PropertyTypeMap = {
    0 : int,
    1 : int,
    2 : str,
    3 : str,
    4 : list,
    5 : None,
    9 : float,
}

MooErrors = [
    'E_NONE', 'E_TYPE', 'E_DIV', 'E_PERM', 'E_PROPNF', 'E_VERBNF', 'E_VARNF',
    'E_INVIND', 'E_RECMOVE', 'E_MAXREC', 'E_RANGE', 'E_ARGS', 'E_NACC',
    'E_INVARG', 'E_QUOTA', 'E_FLOAT'
]

class LambdaVerb(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def get_txt(self):
        txt = ''
        for key in self.__dict__:
            txt += '" %s: %s\n' % (key, self.__dict__[key])
        return txt
            
class LambdaProperty(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def get_txt(self):
        txt = ''
        for key in self.__dict__:
            txt += '" %s: %s\n' % (key, self.__dict__[key])
        return txt

class LambdaObject(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __cmp__(self, other):
        return cmp(self.id, other.id)

    def get_verb(self, verbid):
        assert(verbid < len(self.verbs))
        verb = self.verbs[verbid]
        return verb

    def write(self):
        f = open(str(self.id) + '.moo', 'w')
        f.write(str(self.get_txt()))

    def get_txt(self):
        txt = ''
        for key in self.__dict__:
            obj = self.__dict__[key]
            if key == 'properties':
                txt += '" %s:\n' % key
                for prop in obj:
                    txt += prop.get_txt()
            elif key == 'verbs':
                txt += '" %s:\n' % key
                for verb in obj:
                    txt += verb.get_txt()
            else:
                txt += '" %s: %s\n' % (key, obj)
        return txt

class LambdaMooDB(object):
    def __init__(self, fn):
        self.fn = fn
        self.db = open(fn)

    def parse_debug(self):
        try:
            self.parse()
        except:
            print self.db.tell()
            raise

    def parse(self):
        self.parse_intro_block()
        self.parse_player_block()
        self.parse_object_blocks()
        self.parse_verbs()
        #self.parse_status_block()
        #self.write()

    def write(self):
        for obj in self.objects.itervalues():
            obj.write()

    def parse_status_block(self):
        self.status = {}
        line_re = re.compile('(\d+) (\w+)')
        for linecnt in range(4):
            line = self.db.readline().strip()
            print line
            m = line_re.match(line)
            if m:
                self.status[m.group(0)] = int(m.group(1))
        print self.status
    
    def parse_verbs(self):
        for _verbidx in range(self.verbCount):
            verb = self.get_verb_by_name(self.db.readline())
            body = ''
            nodot = True
            while nodot:
                line = self.db.readline()
                body += line
                if line.strip() == '.':
                    nodot = False
            verb.body = body

    def get_verb_by_name(self, verbname):
        if verbname.startswith('#'):
            verbname = verbname[1:]
        objid, verbid = map(int, verbname.split(':'))
        return self.objects[objid].get_verb(verbid)

    def parse_intro_block(self):
        hdr_re = re.compile('\*\* LambdaMOO Database, Format Version (\d+) \*\*')
        line = self.db.readline()
        m = hdr_re.match(line)
        if m:
            self.version = int(m.group(1))
        else:
            raise ValueError, "Bad header: %s" % line
        self.objectCount = int(self.db.readline())
        self.verbCount = int(self.db.readline())
        self.db.readline() # dummyline
        self.playerCount = int(self.db.readline())

    def parse_player_block(self):
        self.playerNumbers = []
        for player in range(self.playerCount):
            self.playerNumbers.append(int(self.db.readline()))

    def parse_object_blocks(self):
        self.objects = {}
        for _objidx in range(self.objectCount):
            obj = LambdaObject()
            # skip the '#'
            objid = self.db.readline()[1:].strip()
            if objid.endswith(' recycled'):
                continue
            obj.id = int(objid)
            obj.name = self.db.readline().strip()
            self.db.readline() # dummyline
            obj.flags = int(self.db.readline())
            obj.owner_id = int(self.db.readline())
            obj.location_id = int(self.db.readline())
            obj.contents_first_obj = int(self.db.readline())
            obj.location_contents_next_obj = int(self.db.readline())
            obj.parent_id = int(self.db.readline())
            obj.child_list_first_object = int(self.db.readline())
            obj.parents_child_list_first_object = int(self.db.readline())
            obj.verbs = self.parse_verb_definitions()
            obj.properties = self.parse_property_definitions()
            self.objects[obj.id] = obj
            #obj.write()

    def parse_verb_definitions(self):
        verbs = []
        verbCnt = int(self.db.readline())
        for _verbidx in range(verbCnt):
            verb = LambdaVerb()
            verb.name = self.db.readline().strip()
            verb.owner_id = int(self.db.readline())
            verb.perms = int(self.db.readline())
            self.preposition = int(self.db.readline())
            verbs.append(verb)
        return verbs

    def parse_property_definitions(self):
        props = []
        propCnt = int(self.db.readline())
        for _propidx in range(propCnt):
            prop = LambdaProperty()
            prop.name = self.db.readline().strip()
            props.append(prop)
        _propCnt = int(self.db.readline())
        for _propIdx in range(_propCnt):
            if _propIdx < len(props):
                prop = props[_propIdx]
            else:
                prop = LambdaProperty()
                props.append(prop)
            prop.value = self.parse_variable()
            prop.owner = int(self.db.readline())
            prop.perms = int(self.db.readline())
        return props

    def parse_variable(self):
        _typ = int(self.db.readline())
        if _typ == 0:
            return int(self.db.readline())
        if _typ in (1, 2, 3, 7, 8):
            return self.db.readline().strip()
        if _typ == 9:
            return float(self.db.readline())
        if _typ == 4:
            _len = int(self.db.readline())
            return [self.parse_variable() for x in range(_len)]
        if _typ in (5, 6):
            return None
        return None

if __name__ == '__main__':
    db = LambdaMooDB(sys.argv[1])
    db.parse_debug()
