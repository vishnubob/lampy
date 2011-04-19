#!/usr/bin/python

import lampy
import optparse 

def indent(_str, level=1, spaces=4):
    if not _str.strip():
        return _str
    unit = ' ' * spaces
    ind = unit * level
    return ind + _str

def shift(txt, level=1, spaces=4):
    txt = txt.split('\n')
    _txt = ''
    for line in txt:
        line = indent(line, level=level, spaces=spaces)
        _txt += line + '\n'
    return _txt

class Converter(object):
    def __init__(self, fn):
        self.db = lampy.moo.db.LambdaMooDB(fn)
        self.db.parse()
        lcnt = rcnt = 0
        for objid in self.db.objects:
            self.convert_object(objid)

    def convert_object(self, objid):
        obj = self.db.objects[objid]
        for verb in obj.verbs:
            if not hasattr(verb, 'body'):
                continue
            pycode = self.convert_verb_body(verb.body)
            names = verb.name.split(' ')
            verb_name = names[0]
            verb_aliases = names[1:]
            print verb_name, verb_aliases
            print verb.perms, verb.owner_id
            print pycode

    def convert_verb_body(self, body):
        parser = lampy.compiler.build_parser()
        body = body.strip()
        if body.endswith('.'):
            body = body[:-1]
        ast = parser.parse(body)
        return ast.generate()

def get_cli():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--db", dest="dbfilename",
                      help="Moo databse file to convert")
    (options, args) = parser.parse_args()
    options = eval(str(options))  
    return (options, args)

if __name__ == '__main__':
    options, args = get_cli()
    c = Converter(options['dbfilename'])

