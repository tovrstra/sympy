from sympy import sin, cos, atan2, gamma, integrate, symbols, raises
from sympy import Catalan, EulerGamma, E, GoldenRatio, I, pi
from sympy import Function, Rational, Integer

from sympy.printing import fcode


def test_printmethod():
    x = symbols('x')
    class nint(Function):
        def _fcode_(self):
            return "nint(%s)" % fcode(self.args[0])
    assert fcode(nint(x)) == "nint(x)"

def test_fcode_Pow():
    x, y = symbols('xy')
    assert fcode(x**3) == "x**3"
    assert fcode(x**(y**3)) == "x**(y**3)"
    assert fcode(1/(sin(x)*3.5)**(x - y**x)/(x**2 + y)) == \
        "(3.5*sin(x))**(-x + y**x)/(y + x**2)"

def test_fcode_Rational():
    assert fcode(Rational(3,7)) == "3.0/7.0"
    assert fcode(Rational(18,9)) == "2"
    assert fcode(Rational(3,-7)) == "-3.0/7.0"
    assert fcode(Rational(-3,-7)) == "3.0/7.0"

def test_fcode_Integer():
    assert fcode(Integer(67)) == "67"
    assert fcode(Integer(-1)) == "-1"

def test_fcode_functions():
    x, y = symbols('xy')
    assert fcode(sin(x) ** cos(y)) == "sin(x)**cos(y)"

def test_fcode_NumberSymbol():
    assert fcode(Catalan) == '0.915965594177219'
    assert fcode(EulerGamma) == '0.577215664901533'
    assert fcode(E) == '2.71828182845905'
    assert fcode(GoldenRatio) == '1.61803398874989'
    assert fcode(pi) == '3.14159265358979'
    assert fcode(pi,5) == '3.1416'

def test_fcode_complex():
    assert fcode(I) == "cmplx(0,1)"
    x = symbols('x')
    assert fcode(4*I) == "cmplx(0,4)"
    assert fcode(3+4*I) == "cmplx(3,4)"
    assert fcode(3+4*I+x) == "cmplx(3,4) + x"
    assert fcode(I*x) == "cmplx(0,1)*x"
    assert fcode(3+4*I-x) == "cmplx(3,4) - x"
    x = symbols('x', imaginary=True)
    assert fcode(5*x) == "5*x"
    assert fcode(I*x) == "cmplx(0,1)*x"

def test_implicit():
    x, y = symbols('xy')
    assert fcode(sin(x)) == "sin(x)"
    assert fcode(atan2(x,y)) == "atan2(x, y)"
    raises(NotImplementedError, 'fcode(gamma(x))')
    raises(NotImplementedError, 'fcode(integrate(sin(x)/x,x))')
    g = Function('g')
    raises(NotImplementedError, 'fcode(g(x))')

