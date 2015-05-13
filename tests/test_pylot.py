
import pytest
from pylot import Pylot

# Pylot.extends_
def test_extends_():

    class A(Pylot):
        name = "A"

    class AA(Pylot):
        v = "JJ"

    a = A()
    aa = AA()

    @a.extends_
    class B(object):
        CONST = "CONSTANT"
        def b(self):
            return "B"

    @a.extends_
    @aa.extends_  # Remember the order of the placement
    class C(object):
        def c(self):
            self.context_(WHO="WHO")
            return "C"

    @aa.extends_
    class D(object):
        def d(self):
            return "D"

    @a.extends_  # Extends a function
    def hello(self):
        return "HELLO"

    # Assert A
    assert a.b() == "B"
    assert a.c() == "C"
    assert a.hello() == "HELLO"
    assert a.CONST == "CONSTANT"
    assert a._context.get("WHO") == "WHO"

    # Assert AA
    assert aa.c() == "C"
    assert aa.d() == "D"

    # Exceptions
    with pytest.raises(AttributeError):
        # @aa didn't get attached to B, because it was called before @a was extended
        assert aa.CONST == "CONSTANT"
        assert aa.hello() == "HELLO"


# Pylot.meta_
def test_meta_():
    class A(Pylot):
        def __init__(self):
            self.meta_(title="TITLE")
            self.meta_(description="DESCRIPTION")

        def get_meta(self, k):
            return self._context.get("META")[k]
    a = A()

    assert a.get_meta("title") == "TITLE"
    assert a.get_meta("description") == "DESCRIPTION"

# Pylot.bind_
def test_bind_():
    pass


@Pylot.bind_
class DB():
    pass
