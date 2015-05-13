
import inspect
import wrapt

def inject(**kwargs):
    pass


class Pylot(object):

    @classmethod
    def extends_(cls, kls):
        if inspect.isclass(kls):
            for _name, _val in kls.__dict__.items():
                if not _name.startswith("__"):
                    setattr(cls, _name, _val)
        elif inspect.isfunction(kls):
            setattr(cls, kls.__name__, kls)
        return cls


class Q(Pylot):
    def nice(self):
        return "NICE"

class P(Pylot):
    def set_name(self, name):
        self.name = name

p = P()
q = Q()
#print p.__dict__

@q.extends_
@p.extends_
def yo(self, name):
    self.set_name(name)
    print "I'm in self with %s in YO()  " % self.name

@cache
@p.extends_
class A(object):
    phone = "123-2453-4343"
    CONST = 54

    @classmethod
    def c2(cls):
        return None

    def hello(self):
        print "This is hello"

    def index(self, name):
        self.set_name(name)
        print "I'm in self with %s " % self.name
        self.hello()

#print dir(p)
#print p.__dict__
p.hello()
p.yo("Koe")
p.index("Lola")
p.index("Nice One")

q.yo("Jones")
q.hello()
print p.phone
print p.CONST

#print f(name="Jones")
exit()


import functools

def deco(model, **kwargs):
    def wrapper(f):
        print f.__name__
        print model
        print kwargs
        return f
    return wrapper


@deco("my model", name="Jbeats")
class Global(object):
    pass


Global()
exit()




s1 = set([])
s2 = set(["B", "C", "W"])

deleted_s = s1 - s2
new_s = s2 - s1

print deleted_s
print new_s
temp3 = [x for x in s1 if x not in s2]

print temp3
exit()
from pylot import utils

class Struct:
    def __init__(self, **entries): self.__dict__.update(entries)

a = Struct(Name="Macxis", Location="Charlotte")

print a.Name
a.Name = "Jose"
print a.Name
print a.Location

print type(a)
def test_mailer_ses():
    pass

def Mailer():
    pass


mailer = Pylot.bind_(Mailer.init_app())()